import sys
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

sys.path.append(str(Path(__file__).resolve().parent.parent))

from infra.sheet_client import get_contacts_rows, update_contacts_fields, update_contact_extra_fields
from core.followup import build_followup_body
from core.gmail_draft import create_gmail_reply_draft

TZ = ZoneInfo("Europe/Paris")


from random import randint


def next_business_day_random():
    dt = datetime.now(TZ) + timedelta(days=1)

    while dt.weekday() >= 5:  # 5 = samedi, 6 = dimanche
        dt += timedelta(days=1)

    dt = dt.replace(
        hour=8,
        minute=randint(0, 59),
        second=0,
        microsecond=0,
    )
    return dt.strftime("%d/%m/%Y %H:%M")


def main():
    credentials_path = "secrets/gmail_oauth_client.json"
    token_path = "secrets/gmail_token.json"

    for c in get_contacts_rows():
        status = (c.get("status") or "").strip().upper()

        if status == "SCHEDULED":
            continue

        if (c.get("delivery_status") or "").strip() != "✅":
            continue

        if (c.get("relance") or "").strip().upper() != "PROGRAMME":
            continue

        if (c.get("réponse") or "").strip() != "Aucune":
            continue

        if (c.get("followup_1_date") or "").strip():
            continue

        thread_id = c.get("thread_id") or ""
        if not thread_id:
            continue

        row = c["row"]
        company = c.get("company") or ""
        desk = c.get("desk") or ""
        first_name = c.get("first_name")
        language = c.get("language") or "EN"

        #print("FOLLOWUP DEBUG desk =", desk)
        body = build_followup_body(company, desk, first_name, language)
        #print("FOLLOWUP DEBUG body =", body)

        reply_draft = create_gmail_reply_draft(
            thread_id=thread_id,
            body=body,
            credentials_path=credentials_path,
            token_path=token_path,
        )

        reply_draft_id = reply_draft["id"]
        gmail_link = f"https://mail.google.com/mail/u/1/#drafts?compose={reply_draft_id}"

        update_contacts_fields(row, "SCHEDULED", "", gmail_link)
        update_contact_extra_fields(row, {
            "date_prévue": next_business_day_random(),
        })


if __name__ == "__main__":
    main()