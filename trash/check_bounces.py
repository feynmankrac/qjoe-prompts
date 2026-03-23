import os
from infra.gmail_client import get_gmail_service
from infra.sheet_client import get_contacts_rows, update_contacts_fields

def main():

    import os

    credentials_path = os.getenv("GMAIL_OAUTH_CREDENTIALS", "secrets/gmail_oauth_client.json")
    token_path = os.getenv("GMAIL_OAUTH_TOKEN", "secrets/gmail_token.json")

    service = get_gmail_service(credentials_path, token_path)

    # Gmail query: tous les messages Mailer-Daemon
    query = 'from:mailer-daemon OR subject:"Delivery Status Notification"'

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
        headers = payload.get("headers", [])

        body_text = str(payload)

        for c in contacts:

            email = c["email"]
            row = c["row"]

            if email and email in body_text:
                print("Bounce detected:", email)

                update_contacts_fields(
                    row,
                    "bounced",
                    "",
                    ""
                )

if __name__ == "__main__":
    main()