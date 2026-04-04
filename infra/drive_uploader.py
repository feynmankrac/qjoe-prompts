import os
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import pickle

BASE_DIR = Path(__file__).resolve().parent.parent

SCOPES = ["https://www.googleapis.com/auth/drive"]

CREDENTIALS_FILE = BASE_DIR / "secrets" / "client_secret.json"
TOKEN_FILE = BASE_DIR / "secrets" / "drive_token.pickle"

FOLDER_ID = "1rtNuVKYKhphn7_yDA29zaO6NNhM7ZyfH"


def get_drive_service():
    creds = None

    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
#            creds = flow.run_local_server(port=0)
            creds = flow.run_local_server(
                host="localhost",
                port=8080,
                open_browser=False
            )

        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    service = build("drive", "v3", credentials=creds)

    return service


def upload_to_drive(file_path: str) -> str:
    service = get_drive_service()

    file_name = os.path.basename(file_path)

    file_metadata = {
        "name": file_name,
        "parents": [FOLDER_ID],
    }

    media = MediaFileUpload(file_path, mimetype="application/pdf")

    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, webViewLink"
    ).execute()

    link = uploaded_file["webViewLink"]

    # DELETE LOCAL FILE (safe)
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"DELETE FAILED: {file_path} → {e}")

    return link
