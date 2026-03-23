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
from config import GOOGLE_SHEET_ID
from core.logger import get_logger
from core.pipeline import run_generate_application

logger = get_logger("spontaneous", "spontaneous.log")


API_BASE = os.getenv("QJOE_API_BASE", "http://localhost:8000")
DRY_RUN = os.getenv("DRY_RUN", "0") == "1"
print("DEBUG DRY_RUN ENV =", os.getenv("DRY_RUN"))
print("DEBUG DRY_RUN BOOL =", DRY_RUN)

def main():
    contacts = get_contacts_rows()  # doit renvoyer liste dict: row, company, email, first_name, desk, status

    groups = {}

    for c in contacts:
        gid = c.get("group_id") or "DEFAULT"
        groups.setdefault(gid, []).append(c)

    headers = {}
    token = os.getenv("QJOE_API_TOKEN")
    if token:
        headers["x-api-key"] = token

    #for c in contacts:
    for group_id, group_contacts in groups.items():
        eligible = [c for c in group_contacts if (c.get("status") or "") not in ("ready", "ERROR")]

        if not eligible:
            continue

        selected = eligible[:7]
        
        emails = [c.get("email") for c in selected if c.get("email")]

        to_email = os.getenv("GMAIL_FROM_EMAIL") or os.getenv("GMAIL_SENDER")
       # to_email = os.getenv("GMAIL_SENDER")
       # to_email = emails[0]
        bcc_emails = emails

        c = selected[0]
 
        row = c["row"]
        status = c.get("status") or ""

 #       if status in ("ready", "ERROR"):
  #          continue

        company = c.get("company") or ""
        contact_email = c.get("email") or ""
       # to_email = c.get("email") or ""
       # first_name = c.get("first_name")
        first_name = None
        desk = c.get("desk") or ""
        language = c.get("language") or "EN"
        group_id = c.get("group_id") or ""

        if not contact_email:
            update_contacts_fields(row, "SKIP_NO_EMAIL", "", "")
            continue

        if "@" not in contact_email:
            update_contacts_fields(row, "SKIP_INVALID_EMAIL", "", "")
            continue

        print("Processing:", company, "| row:", row)

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
       # print("DEBUG API RESPONSE =", gen.json())
        g = gen.json()["generation"]
        cv_local_path = g["artifacts"]["cv_pdf_path"]
        email_subject = g["email"]["subject"]
        email_body = g["email"]["body"]
        
        print("DEBUG DRY_RUN =", DRY_RUN)
        print("DEBUG CV PATH =", cv_local_path)
       
        gmail_link = ""
        cv_link = ""

        # create draft gmail + attach cv
        if not DRY_RUN and cv_local_path:
            r = requests.post(
                f"{API_BASE}/create_gmail_draft",
                json={
                    "to_email": to_email,
                    "bcc_emails": bcc_emails,
                    "subject": email_subject,
                    "body": email_body,
                    "attachment_path": cv_local_path
                },
                headers=headers,
                timeout=60,
            )
            r.raise_for_status()
            draft_id = r.json()["draft"]["id"]
            gmail_link = f'=HYPERLINK("https://mail.google.com/mail/u/1/#drafts?compose={draft_id}";"open")'
        else:
            gmail_link = "DRY_RUN"

        # write sheet
        cv_cell = ""

        for contact in selected:
            update_contacts_fields(contact["row"], "ready", cv_cell, gmail_link)
       # update_contacts_fields(row, "ready", cv_cell, gmail_link)

        # cleanup local
        if cv_local_path and os.path.exists(cv_local_path):
            os.remove(cv_local_path)

if __name__ == "__main__":

    lock = FileLock(config.LOCK_PATH, timeout=1)

    try:
        with lock:
            main()

    except Timeout:
        print("Batch already running. Exiting.")
