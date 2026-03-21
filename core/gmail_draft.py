# core/gmail_draft.py
from __future__ import annotations
from email.mime.base import MIMEBase
from email import encoders

import base64
from email.message import EmailMessage
from typing import Optional

from infra.gmail_client import get_gmail_service


def _to_rfc2822_base64url(msg: EmailMessage) -> str:
    raw_bytes = msg.as_bytes()
    return base64.urlsafe_b64encode(raw_bytes).decode("utf-8")


def create_gmail_draft(
    *,
    to_email: str,
    subject: str,
    body: str,
    from_email: Optional[str],
    credentials_path: str,
    token_path: str,
    attachment_path: Optional[str] = None,
    bcc_emails: Optional[list[str]] = None,
) -> dict:
    svc = get_gmail_service(credentials_path, token_path)

    if bcc_emails is None:
        bcc_emails = []

    msg = EmailMessage()
    msg["To"] = to_email
    if bcc_emails:
        msg["Bcc"] = ", ".join(bcc_emails)

    msg["Subject"] = subject
    if from_email:
        msg["From"] = from_email
    msg.set_content(body)
    if attachment_path:
        with open(attachment_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())

        encoders.encode_base64(part)
        filename = attachment_path.split("/")[-1]
        part.add_header(
            "Content-Disposition",
            f'attachment; filename="{filename}"'
        )

        msg.add_attachment(
            open(attachment_path, "rb").read(),
            maintype="application",
            subtype="pdf",
            filename=filename
        )

    raw = _to_rfc2822_base64url(msg)

    print("TO:", to_email)
    print("SUBJECT:", subject)
    print("BCC:", bcc_emails)
    print("BODY:", body[:100])
    print("ATTACHMENT:", attachment_path)

    draft = svc.users().drafts().create(
        userId="me",
        body={"message": {"raw": raw}},
    ).execute()

    # Gmail renvoie notamment: id, message.id, message.threadId
    return draft
