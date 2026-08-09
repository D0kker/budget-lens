import json
import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _first(root: ET.Element, name: str) -> Optional[str]:
    for element in root.iter():
        if _local(element.tag) == name and element.text:
            return element.text.strip()
    return None


def _number(value: Optional[str]) -> float:
    return float(value or 0)


def parse_invoice_xml(xml_path: str) -> Dict:
    root = ET.parse(xml_path).getroot()
    items: List[Dict] = []
    for item in root.iter():
        if _local(item.tag) != "gItem":
            continue
        values = {_local(child.tag): child.text.strip() for child in item.iter() if child.text and _local(child.tag) in {"dDescProd", "dValTotItem", "dPrItem", "dValITBMS"}}
        items.append({"description": values.get("dDescProd", ""), "amount": _number(values.get("dValTotItem")), "tax": _number(values.get("dValITBMS"))})
    return {
        "provider": _first(root, "dNombEm") or "Proveedor desconocido",
        "invoice_number": _first(root, "dNroDF") or Path(xml_path).stem,
        "issue_date": (_first(root, "dFechaEm") or "")[:10] or None,
        "total": _number(_first(root, "dVTot")),
        "currency": "PAB",
        "status": "pending_payment",
        "source_xml": Path(xml_path).name,
        "source_pdf": None,
        "items": items,
    }


def register_invoice(connection: sqlite3.Connection, xml_path: str, pdf_path: Optional[str] = None) -> Dict:
    invoice = parse_invoice_xml(xml_path)
    invoice["source_pdf"] = Path(pdf_path).name if pdf_path else None
    duplicate = connection.execute("SELECT id FROM invoices WHERE provider=? AND invoice_number=?", (invoice["provider"], invoice["invoice_number"])).fetchone()
    if duplicate:
        return {"id": duplicate[0], "created": False, **invoice}
    cursor = connection.execute(
        """INSERT INTO invoices
        (provider, invoice_number, issue_date, total, currency, status, source_xml, source_pdf, details_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (invoice["provider"], invoice["invoice_number"], invoice["issue_date"], invoice["total"], invoice["currency"], invoice["status"], invoice["source_xml"], invoice["source_pdf"], json.dumps(invoice["items"])),
    )
    connection.commit()
    return {"id": cursor.lastrowid, "created": True, **invoice}
