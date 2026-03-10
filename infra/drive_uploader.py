import os
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

BASE_DIR = Path(__file__).resolve().parent.parent

SERVICE_ACCOUNT_FILE = BASE_DIR / "secrets" / "qjoe-service-account.json"

SCOPES = ["https://www.googleapis.com/auth/drive"]

FOLDER_ID = "1rtNuVKYKhphn7_yDA29zaO6NNhM7ZyfH"

def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
    )
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
        fields="id, webViewLink",
        supportsAllDrives=True
    ).execute()

    return uploaded_file["webViewLink"]
