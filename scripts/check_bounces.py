import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import os
import base64
from infra.gmail_client import get_gmail_service
from infra.sheet_client import get_contacts_rows, update_contacts_fields
from infra.sheet_client import update_delivery_status

def extract_body(payload):
    try:
        if "parts" in payload:
            for part in payload["parts"]:
                data = part.get("body", {}).get("data")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
        else:
            data = payload.get("body", {}).get("data")
            if data:
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    except:
        pass
    return ""

def extract_body(payload):
    texts = []

    def walk(part):
        data = part.get("body", {}).get("data")
        if data:
            try:
                texts.append(
                    base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                )
            except:
                pass

        for subpart in part.get("parts", []):
            walk(subpart)

    walk(payload)
    return "\n".join(texts)


def main():

    credentials_path = os.getenv("GMAIL_OAUTH_CREDENTIALS", "secrets/gmail_oauth_client.json")
    token_path = os.getenv("GMAIL_OAUTH_TOKEN", "secrets/gmail_token.json")

    service = get_gmail_service(credentials_path, token_path)

    query = 'from:mailer-daemon newer_than:1d'

    results = service.users().messages().list(
        userId="me",
        q=query
    ).execute()

    messages = results.get("messages", [])

    if not messages:
        print("No bounces detected")
        return

    contacts = get_contacts_rows()

    for msg in messages:

        message = service.users().messages().get(
            userId="me",
            id=msg["id"]
        ).execute()

        payload = message["payload"]

        body_text = extract_body(payload)

        print("HAS_ACTION =", "Action: WAS NOT DELIVERED" in body_text)
        print("BODY_LEN =", len(body_text))
        print(body_text[:2000])

        for c in contacts:

            email = c["email"]
            row = c["row"]

            if "Action: failed" not in body_text and "user does not exist" not in body_text:
                continue

            if email and email.lower() in body_text.lower():
                print("Bounce detected:", email)
                update_delivery_status(row, "❌")

if __name__ == "__main__":
    main()