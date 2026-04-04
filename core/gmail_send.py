from __future__ import annotations

from infra.gmail_client import get_gmail_service

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
) -> bool:
    draft_id = extract_draft_id(draft_link)

    if not draft_id:
        print("Invalid draft_link:", draft_link)
        return False

    svc = get_gmail_service(credentials_path, token_path)

    try:
        svc.users().drafts().send(
            userId="me",
            body={"id": draft_id}
        ).execute()
        return True
    except Exception as e:
        print(f"Send failed for draft {draft_id}: {e}")
        return False
