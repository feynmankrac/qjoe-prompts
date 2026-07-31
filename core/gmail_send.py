from __future__ import annotations

import re
from infra.gmail_client import get_gmail_service


def extract_draft_id(draft_link: str) -> str | None:
    if not draft_link:
        return None

    match = re.search(r"compose=([a-zA-Z0-9\-]+)", draft_link)
    if match:
        return match.group(1)

    return None


def send_draft(
    *,
    draft_link: str,
    credentials_path: str,
    token_path: str,
) -> dict:
    draft_id = extract_draft_id(draft_link)

    if not draft_id:
        print("Invalid draft_link:", draft_link)
        return {"ok": False, "thread_id": "", "message_id": ""}

    svc = get_gmail_service(credentials_path, token_path)

    try:
        sent = svc.users().drafts().send(
            userId="me",
            body={"id": draft_id}
        ).execute()

        return {
            "ok": True,
            "thread_id": sent.get("threadId", ""),
            "message_id": sent.get("id", "")
        }

    except Exception as e:
        print(f"Send failed for draft {draft_id}: {e}")
        return {"ok": False, "thread_id": "", "message_id": ""}