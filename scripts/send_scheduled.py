import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import os
from datetime import datetime
from zoneinfo import ZoneInfo

from infra.sheet_client import get_contacts_rows, update_contacts_fields
from core.gmail_send import send_draft
from core.logger import get_logger
from infra.sheet_client import update_contact_extra_fields
from infra.sheet_client import update_delivery_status


logger = get_logger("send_scheduled", "send_scheduled.log")
LOCK_FILE = "/tmp/qjoe_send.lock"

TZ = ZoneInfo("Europe/Paris")


def parse_send_at(value: str):
    try:
        return datetime.strptime(value.strip(), "%d/%m/%Y %H:%M").replace(tzinfo=TZ)
    except:
        return None


def is_ready(row, now):
    status = (row.get("status") or "").strip().upper()
    send_at_raw = (row.get("date_prévue") or "").strip()

    if status not in ["SCHEDULED", "CANCELLED"]:
        return False

    if status == "CANCELLED":
        return False

    if not send_at_raw:
        return False

    try:
        dt = datetime.strptime(send_at_raw, "%d/%m/%Y %H:%M").replace(tzinfo=TZ)
    except:
        return False

    if now < dt:
        return False

    return True



def main():
    print("SEND_SCHEDULED RUNNING", datetime.now(TZ))
    if os.path.exists(LOCK_FILE):
        logger.warning("LOCK FILE EXISTS → EXIT")
        return

    open(LOCK_FILE, "w").close()

    try:
        contacts = get_contacts_rows()
        now = datetime.now(TZ)

        sent_count = 0
        MAX_SEND = 5

        credentials_path = "secrets/gmail_oauth_client.json"
        token_path = "secrets/gmail_token.json"

        for c in contacts:
            try:
                print(f"CHECK row {c['row']} status={c.get('status')} date={c.get('date_prévue')}")
                
                if not is_ready(c, now):
                    if c.get("date_prévue"):
                        logger.info(f"WAIT row {c['row']} until {c['date_prévue']}")
                    continue

                # 🔥 RATE LIMIT AVANT TOUT
                if sent_count >= MAX_SEND:
                    logger.info("RATE LIMIT REACHED")
                    break

                draft_link = c.get("draft_link") or ""
                row = c["row"]

                email = c.get("email") or ""
                if not email:
                    logger.warning(f"NO EMAIL row {row}")
                    continue

                if not draft_link:
                    logger.warning(f"NO DRAFT LINK row {row}")
                    continue

                # 🔒 LOCK
                update_contacts_fields(row, "SENDING", "", draft_link)

                logger.info(f"DRAFT LINK row {row} = {draft_link}")

                print(f"READY TO SEND row {row}")
                ok = send_draft(
                    draft_link=draft_link,
                    credentials_path=credentials_path,
                    token_path=token_path,
                )

                print(f"SEND RESULT row {row} = {ok}")

                logger.info(f"SEND RESULT row {row} = {ok}")

                if ok:
                    sent_count += 1

                    update_contacts_fields(row, "SENT", "", draft_link)

                    update_contact_extra_fields(row, {
                        "date_réelle": datetime.now(TZ).strftime("%d/%m/%Y %H:%M")
                    })

                    update_contact_extra_fields(row, {
                        "schedule": "",
                    })
                    update_delivery_status(row, "✅")

                    logger.info(f"SENT row {row}")

                else:
                    logger.warning(f"FAILED row {row}")

                    update_contacts_fields(row, "FAILED", "", draft_link)
                    update_delivery_status(row, "❌")

            except Exception as e:
                logger.error(f"ERROR row {c.get('row')}: {e}")
                continue

    finally:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
        import glob

        for f in glob.glob("artifacts/*"):
            if not f.endswith(".pdf"):
                try:
                    os.remove(f)
                except:
                    pass


if __name__ == "__main__":
    main()
