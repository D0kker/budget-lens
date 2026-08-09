import json
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
try:
    from .email_ingest import fetch_documents
except ImportError:
    from email_ingest import fetch_documents

DB_PATH = os.environ.get("BUDGET_LENS_DB", os.path.join(os.path.dirname(__file__), "budget-lens.sqlite"))
HOST = os.environ.get("BUDGET_LENS_HOST", "0.0.0.0")
PORT = int(os.environ.get("BUDGET_LENS_PORT", "8000"))
CORS_ORIGIN = os.environ.get("BUDGET_LENS_CORS_ORIGIN", "*")

def db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.executescript("""
    CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY, name TEXT NOT NULL, kind TEXT NOT NULL DEFAULT 'cash', balance REAL NOT NULL DEFAULT 0, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS debts (id INTEGER PRIMARY KEY, name TEXT NOT NULL, balance REAL NOT NULL DEFAULT 0, interest_rate REAL NOT NULL DEFAULT 0, minimum_payment REAL NOT NULL DEFAULT 0, due_day INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS recurring_cashflow (id INTEGER PRIMARY KEY, name TEXT NOT NULL, kind TEXT NOT NULL CHECK(kind IN ('income','expense')), amount REAL NOT NULL DEFAULT 0, due_day INTEGER, provider TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS savings_goals (id INTEGER PRIMARY KEY, name TEXT NOT NULL, target REAL NOT NULL DEFAULT 0, current REAL NOT NULL DEFAULT 0, due_date TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS email_documents (
        id INTEGER PRIMARY KEY,
        message_key TEXT NOT NULL,
        sender TEXT NOT NULL,
        subject TEXT,
        received_at TEXT,
        original_filename TEXT NOT NULL,
        stored_path TEXT NOT NULL,
        sha256 TEXT NOT NULL UNIQUE,
        status TEXT NOT NULL DEFAULT 'pending_review',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """)
    columns = {row[1] for row in connection.execute("PRAGMA table_info(recurring_cashflow)").fetchall()}
    if "due_day" not in columns: connection.execute("ALTER TABLE recurring_cashflow ADD COLUMN due_day INTEGER")
    if "provider" not in columns: connection.execute("ALTER TABLE recurring_cashflow ADD COLUMN provider TEXT")
    return connection

def summary():
    connection = db()
    accounts = [dict(row) for row in connection.execute("SELECT id,name,kind,balance FROM accounts ORDER BY name").fetchall()]
    debts = [dict(row) for row in connection.execute("SELECT id,name,balance,interest_rate,minimum_payment,due_day FROM debts ORDER BY interest_rate DESC, balance DESC").fetchall()]
    income = float(connection.execute("SELECT COALESCE(SUM(amount), 0) FROM recurring_cashflow WHERE kind='income'").fetchone()[0])
    expenses = float(connection.execute("SELECT COALESCE(SUM(amount), 0) FROM recurring_cashflow WHERE kind='expense'").fetchone()[0])
    cashflow = [dict(row) for row in connection.execute("SELECT id,name,kind,amount,due_day,provider FROM recurring_cashflow ORDER BY kind,name").fetchall()]
    goals = [dict(row) for row in connection.execute("SELECT id,name,target,current,due_date FROM savings_goals ORDER BY name").fetchall()]
    assets = sum(account["balance"] for account in accounts)
    debt = sum(item["balance"] for item in debts)
    minimums = sum(item["minimum_payment"] for item in debts)
    connection.close()
    surplus = income - expenses
    return {"assets": assets, "debt": debt, "available": assets - minimums, "monthly_income": income, "monthly_expenses": expenses, "monthly_surplus": surplus, "recommended_debt_payment": minimums + max(0, surplus - minimums), "accounts": accounts, "debts": debts, "cashflow": cashflow, "goals": goals}

def email_documents():
    connection = db()
    documents = [dict(row) for row in connection.execute("SELECT id,sender,subject,received_at,original_filename,status,created_at FROM email_documents ORDER BY created_at DESC").fetchall()]
    connection.close()
    return documents

class Handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", CORS_ORIGIN)
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self): self._send(204, {})
    def do_GET(self):
        if self.path == "/healthz": self._send(200, {"status": "ok"})
        elif self.path == "/api/summary": self._send(200, summary())
        elif self.path == "/api/email/documents": self._send(200, {"documents": email_documents()})
        else: self._send(404, {"error": "not_found"})
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        try: data = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError: return self._send(400, {"error": "invalid_json"})
        if self.path == "/api/email/sync":
            connection = db()
            try:
                imported = fetch_documents(connection, limit=min(max(int(data.get("limit", 20)), 1), 100))
                return self._send(200, {"ok": True, "imported": imported, "count": len(imported)})
            except (OSError, RuntimeError, ValueError) as error:
                connection.rollback(); return self._send(400, {"error": str(error)})
            finally:
                connection.close()
        connection = db()
        if self.path == "/api/accounts":
            if not data.get("name"): return self._send(400, {"error": "name_required"})
            connection.execute("INSERT INTO accounts(name,kind,balance) VALUES(?,?,?)", (data["name"], data.get("kind", "cash"), float(data.get("balance", 0))))
        elif self.path == "/api/debts":
            if not data.get("name"): return self._send(400, {"error": "name_required"})
            connection.execute("INSERT INTO debts(name,balance,interest_rate,minimum_payment,due_day) VALUES(?,?,?,?,?)", (data["name"], float(data.get("balance", 0)), float(data.get("interest_rate", 0)), float(data.get("minimum_payment", 0)), int(data.get("due_day", 1))))
        elif self.path in ("/api/incomes", "/api/expenses"):
            if not data.get("name"): return self._send(400, {"error": "name_required"})
            kind = "income" if self.path.endswith("incomes") else "expense"
            connection.execute("INSERT INTO recurring_cashflow(name,kind,amount,due_day,provider) VALUES(?,?,?,?,?)", (data["name"], kind, float(data.get("amount", 0)), data.get("due_day"), data.get("provider")))
        elif self.path == "/api/goals":
            if not data.get("name"): return self._send(400, {"error": "name_required"})
            connection.execute("INSERT INTO savings_goals(name,target,current,due_date) VALUES(?,?,?,?)", (data["name"], float(data.get("target", 0)), float(data.get("current", 0)), data.get("due_date") or None))
        else:
            connection.close(); return self._send(404, {"error": "not_found"})
        connection.commit(); connection.close(); self._send(201, {"ok": True})

if __name__ == "__main__":
    print(f"Budget Lens API: http://{HOST}:{PORT}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
