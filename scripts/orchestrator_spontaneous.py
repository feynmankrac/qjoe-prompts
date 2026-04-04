import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

sys.path.append(str(Path(__file__).resolve().parent.parent))

import config
from filelock import FileLock, Timeout

from infra.sheet_client import get_contacts_rows, update_contacts_fields
from core.logger import get_logger

logger = get_logger("spontaneous", "spontaneous.log")

API_BASE = os.getenv("QJOE_API_BASE", "http://localhost:8000")
DRY_RUN = os.getenv("DRY_RUN", "0") == "1"

print("DEBUG DRY_RUN ENV =", os.getenv("DRY_RUN"))
print("DEBUG DRY_RUN BOOL =", DRY_RUN)


def main():
    contacts = get_contacts_rows()

    headers = {}
    token = os.getenv("QJOE_API_TOKEN")
    if token:
        headers["x-api-key"] = token

    for c in contacts:

        status = (c.get("status") or "").strip().upper()
        if status != "":
            continue

        row = c["row"]
        company = c.get("company") or ""
        to_email = c.get("email") or ""
        first_name = c.get("first_name")
        desk = c.get("desk") or ""
        language = c.get("language") or "EN"

        if not to_email:
            update_contacts_fields(row, "SKIP_NO_EMAIL", "", "")
            continue

        if "@" not in to_email:
            update_contacts_fields(row, "SKIP_INVALID_EMAIL", "", "")
            continue

        print("Processing:", company, "| row:", row)
        print("TO:", to_email)

        # 1. Generate content
        gen = requests.post(
            f"{API_BASE}/generate_spontaneous",
            json={
                "company": company,
                "to_email": to_email,
                "first_name": first_name,
                "desk": desk,
                "language": language,
            },
            headers=headers,
            timeout=60,
        )
        gen.raise_for_status()

        g = gen.json()["generation"]
        cv_local_path = g["artifacts"]["cv_pdf_path"]
        email_subject = g["email"]["subject"]
        email_body = g["email"]["body"]

        print("DEBUG CV PATH =", cv_local_path)

        gmail_link = ""

        # 2. Create draft
        if not DRY_RUN and cv_local_path:
            r = requests.post(
                f"{API_BASE}/create_gmail_draft",
                json={
                    "to_email": to_email,
                    "subject": email_subject,
                    "body": email_body,
                    "attachment_path": cv_local_path
                },
                headers=headers,
                timeout=60,
            )
            r.raise_for_status()

            draft_id = r.json()["draft"]["id"]
            gmail_link = f"https://mail.google.com/mail/u/1/#drafts?compose={draft_id}"
        else:
            gmail_link = "DRY_RUN"

        # 3. Update sheet
        update_contacts_fields(row, "ready", "", gmail_link)

        # 4. Cleanup
        if cv_local_path and os.path.exists(cv_local_path):
            os.remove(cv_local_path)


if __name__ == "__main__":

    lock = FileLock(config.LOCK_PATH, timeout=1)

    try:
        with lock:
            main()

    except Timeout:
        print("Batch already running. Exiting.")