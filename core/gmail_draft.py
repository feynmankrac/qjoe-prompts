from __future__ import annotations

import base64
from email.message import EmailMessage
from typing import Optional

from core.gmail_send import extract_draft_id
from infra.gmail_client import get_gmail_service


def _to_rfc2822_base64url(msg: EmailMessage) -> str:
    raw_bytes = msg.as_bytes()
    return base64.urlsafe_b64encode(raw_bytes).decode("utf-8")


def _get_header(headers: list[dict], name: str) -> str:
    for h in headers or []:
        if (h.get("name") or "").lower() == name.lower():
            return h.get("value", "")
    return ""


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
        import os

        if not os.path.exists(attachment_path):
            raise Exception(f"Attachment not found: {attachment_path}")

        filename = attachment_path.split("/")[-1]
        with open(attachment_path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="pdf",
                filename=filename
            )

    raw = _to_rfc2822_base64url(msg)

    draft = svc.users().drafts().create(
        userId="me",
        body={"message": {"raw": raw}},
    ).execute()

    return draft


def create_gmail_reply_draft(
    *,
    thread_id: str,
    body: str,
    credentials_path: str,
    token_path: str,
    from_email: Optional[str] = None,
) -> dict:
    svc = get_gmail_service(credentials_path, token_path)

    if not thread_id:
        raise Exception("Missing thread_id")

    thread = svc.users().threads().get(
        userId="me",
        id=thread_id,
        format="metadata",
        metadataHeaders=["Message-ID", "Subject", "From", "To", "Cc", "References", "In-Reply-To"]
    ).execute()

    messages = thread.get("messages", [])
    if not messages:
        raise Exception("Empty thread")

    last_msg = messages[-1]
    payload = last_msg.get("payload", {})
    headers = payload.get("headers", [])

    subject = _get_header(headers, "Subject") or "Re:"
    message_id_header = _get_header(headers, "Message-ID")
    references = _get_header(headers, "References")
    in_reply_to = _get_header(headers, "In-Reply-To")
    to_header = _get_header(headers, "To")
    cc_header = _get_header(headers, "Cc")

    msg = EmailMessage()
    msg["To"] = to_header
    if cc_header:
        msg["Cc"] = cc_header
    msg["Subject"] = subject
    if from_email:
        msg["From"] = from_email

    if message_id_header:
        msg["In-Reply-To"] = message_id_header
        msg["References"] = f"{references} {message_id_header}".strip() if references else message_id_header
    elif in_reply_to:
        msg["In-Reply-To"] = in_reply_to
        msg["References"] = f"{references} {in_reply_to}".strip() if references else in_reply_to

    msg.set_content(body)

    raw = _to_rfc2822_base64url(msg)

    reply_draft = svc.users().drafts().create(
        userId="me",
        body={
            "message": {
                "threadId": thread_id,
                "raw": raw,
            }
        },
    ).execute()

    return reply_draft