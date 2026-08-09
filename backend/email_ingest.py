import email
import hashlib
import imaplib
import os
import re
from email.header import decode_header
from email.message import Message
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Optional


ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}


def _setting(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def _allowed_senders() -> set[str]:
    return {item.strip().lower() for item in _setting("BUDGET_LENS_EMAIL_ALLOWED_SENDERS").split(",") if item.strip()}


def _decode(value: Optional[str]) -> str:
    if not value:
        return ""
    parts = []
    for chunk, charset in decode_header(value):
        if isinstance(chunk, bytes):
            parts.append(chunk.decode(charset or "utf-8", errors="replace"))
        else:
            parts.append(chunk)
    return "".join(parts)


def _safe_filename(filename: str) -> str:
    name = Path(filename).name
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._") or "attachment"
    return name[:180]


def _sender(message: Message) -> str:
    address = email.utils.parseaddr(message.get("From", ""))[1]
    return address.lower()


def _received_at(message: Message) -> Optional[str]:
    try:
        return parsedate_to_datetime(message.get("Date", "")).isoformat()
    except (TypeError, ValueError, OverflowError):
        return None


def _message_key(message: Message, uid: str) -> str:
    return (message.get("Message-ID") or f"imap:{uid}").strip()


def _attachments(message: Message):
    for part in message.walk():
        filename = part.get_filename()
        if filename and part.get_content_disposition() == "attachment":
            yield _decode(filename), part.get_payload(decode=True) or b""


def fetch_documents(connection, limit: int = 20) -> list[dict]:
    host = _setting("BUDGET_LENS_IMAP_HOST")
    username = _setting("BUDGET_LENS_EMAIL_USER")
    password = os.environ.get("BUDGET_LENS_EMAIL_PASSWORD", "")
    folder = _setting("BUDGET_LENS_IMAP_FOLDER", "INBOX")
    allowed_senders = _allowed_senders()
    if not host or not username or not password:
        raise RuntimeError("Configura BUDGET_LENS_IMAP_HOST, BUDGET_LENS_EMAIL_USER y BUDGET_LENS_EMAIL_PASSWORD")
    if not allowed_senders:
        raise RuntimeError("Configura BUDGET_LENS_EMAIL_ALLOWED_SENDERS antes de sincronizar")

    inbox = Path(_setting("BUDGET_LENS_EMAIL_INBOX", "data/email-inbox"))
    inbox.mkdir(parents=True, exist_ok=True)
    mail = imaplib.IMAP4_SSL(host, int(_setting("BUDGET_LENS_IMAP_PORT", "993")))
    try:
        mail.login(username, password)
        status, _ = mail.select(folder, readonly=True)
        if status != "OK":
            raise RuntimeError(f"No se pudo abrir la carpeta IMAP {folder}")
        status, data = mail.search(None, "UNSEEN")
        if status != "OK":
            raise RuntimeError("No se pudieron consultar los mensajes no leídos")
        uids = data[0].split()[-limit:]
        imported = []
        for raw_uid in uids:
            uid = raw_uid.decode("ascii", errors="replace")
            status, message_data = mail.fetch(raw_uid, "(RFC822)")
            if status != "OK":
                continue
            raw_message = next((item[1] for item in message_data if isinstance(item, tuple)), None)
            if not raw_message:
                continue
            message = email.message_from_bytes(raw_message)
            sender = _sender(message)
            if sender not in allowed_senders:
                continue
            message_key = _message_key(message, uid)
            if connection.execute("SELECT 1 FROM email_documents WHERE message_key=?", (message_key,)).fetchone():
                continue
            for filename, content in _attachments(message):
                extension = Path(filename).suffix.lower()
                if extension not in ALLOWED_EXTENSIONS or not content:
                    continue
                digest = hashlib.sha256(content).hexdigest()
                if connection.execute("SELECT 1 FROM email_documents WHERE sha256=?", (digest,)).fetchone():
                    continue
                stored_name = f"{digest[:16]}-{_safe_filename(filename)}"
                destination = inbox / stored_name
                destination.write_bytes(content)
                received_at = _received_at(message)
                connection.execute(
                    """INSERT INTO email_documents
                    (message_key, sender, subject, received_at, original_filename, stored_path, sha256, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'pending_review')""",
                    (message_key, sender, _decode(message.get("Subject")), received_at, filename, str(destination), digest),
                )
                imported.append({"sender": sender, "subject": _decode(message.get("Subject")), "received_at": received_at, "filename": filename, "status": "pending_review"})
        connection.commit()
        return imported
    finally:
        try:
            mail.close()
        except imaplib.IMAP4.error:
            pass
        mail.logout()
