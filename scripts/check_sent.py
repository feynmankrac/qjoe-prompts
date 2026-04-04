import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from infra.sheet_client import get_contacts_rows, update_delivery_status


def main():
    contacts = get_contacts_rows()

    for c in contacts:
        status = (c.get("status") or "").upper()
        row = c["row"]

        delivery = (c.get("delivery_status") or "").strip()

        if status == "SENT" and delivery != "❌":
            update_delivery_status(row, "✅")
   #print("CHECK_SENT RUNNING")
    exit()


if __name__ == "__main__":
    main()