from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.readonly"
]

flow = InstalledAppFlow.from_client_secrets_file(
    "secrets/gmail_oauth_client.json",
    SCOPES
)

creds = flow.run_local_server(port=0)

with open("gmail_token.json", "w") as f:
    f.write(creds.to_json())

print("Token saved -> gmail_token.json")