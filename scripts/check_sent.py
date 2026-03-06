import os
from infra.gmail_client import get_gmail_service
from infra.sheet_client import get_contacts_rows, update_delivery_status

def main():

    credentials_path = os.getenv("GMAIL_OAUTH_CREDENTIALS", "secrets/gmail_oauth_client.json")
    token_path = os.getenv("GMAIL_OAUTH_TOKEN", "secrets/gmail_token.json")

    service = get_gmail_service(credentials_path, token_path)

    contacts = get_contacts_rows()

    for c in contacts:

        email = c["email"]
        row = c["row"]

        query = f"to:{email} in:sent newer_than:7d"

        res = service.users().messages().list(
            userId="me",
            q=query
        ).execute()

        if res.get("messages"):
            update_delivery_status(row, "sent")
            print("Sent detected:", email)

if __name__ == "__main__":
    main()