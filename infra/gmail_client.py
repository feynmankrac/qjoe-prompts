# infra/gmail_client.py
from __future__ import annotations

import os
from typing import List, Optional

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.readonly"
]


def _load_creds(
    credentials_path: str,
    token_path: str,
) -> Credentials:
    creds: Optional[Credentials] = None

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
        return creds

    if creds and creds.valid:
        return creds
#    creds = flow.run_local_server(port=0)
    raise Exception("Gmail token missing. Run setup manually.")


def get_gmail_service(
    credentials_path: str,
    token_path: str,
):
    creds = _load_creds(credentials_path, token_path)
    return build("gmail", "v1", credentials=creds, cache_discovery=False)
