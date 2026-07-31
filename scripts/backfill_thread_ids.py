import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from infra.sheet_client import get_contacts_rows, batch_update_contact_fields
from infra.gmail_client import get_gmail_service
from core.spontaneous import build_spontaneous_email_subject, desk_to_human


def find_sent_thread_id(service, *, to_email: str, subject: str) -> str:
    queries = [
        f'in:sent to:{to_email} subject:"{subject}" newer_than:180d',
        f'in:sent "{to_email}" subject:"{subject}" newer_than:180d',
        f'in:sent to:{to_email} newer_than:180d',
        f'in:sent "{to_email}" newer_than:180d',
    ]

    for q in queries:
        resp = service.users().messages().list(
            userId="me",
            q=q,
            maxResults=10,
        ).execute()

        messages = resp.get("messages", [])
        if messages:
            return messages[0].get("threadId", "")

    return ""


def main():
    credentials_path = "secrets/gmail_oauth_client.json"
    token_path = "secrets/gmail_token.json"

    svc = get_gmail_service(credentials_path, token_path)

    rows_updates = []

    print("START BACKFILL")

    for c in get_contacts_rows():
        row = c["row"]

        delivery_status = (c.get("delivery_status") or "").strip()
        thread_id = (c.get("thread_id") or "").strip()
        to_email = (c.get("email") or "").strip()
        company = (c.get("company") or "").strip()
        desk_raw = (c.get("desk") or "").strip()
        language = (c.get("language") or "EN").strip()

        print(
            "CHECK",
            row,
            "| delivery_status=", repr(c.get("delivery_status")),
            "| thread_id=", repr(c.get("thread_id")),
            "| email=", repr(c.get("email")),
            "| company=", repr(c.get("company")),
            "| desk=", repr(c.get("desk")),
            "| language=", repr(c.get("language")),
        )

        if delivery_status != "✅":
            print(f"SKIP row {row} delivery_status")
            continue

        if thread_id:
            print(f"SKIP row {row} thread_id already filled")
            continue

        if not to_email or "@" not in to_email:
            print(f"SKIP row {row} invalid email")
            continue

        desk_label = desk_to_human(desk_raw.upper())
        subject = build_spontaneous_email_subject(company, desk_label, language)

        found_thread_id = find_sent_thread_id(
            svc,
            to_email=to_email,
            subject=subject,
        )

        print(
            f"ROW {row} | email={to_email} | subject={subject} | thread_id={found_thread_id or 'NOT_FOUND'}"
        )

        if found_thread_id:
            rows_updates.append((
                row,
                {"thread_id": found_thread_id}
            ))

    print("ROWS_UPDATES =", rows_updates)

    if rows_updates:
        batch_update_contact_fields(rows_updates)
        print(f"BATCH UPDATED: {len(rows_updates)} rows")
    else:
        print("NO UPDATES")


if __name__ == "__main__":
    main()