from google.oauth2 import service_account
from googleapiclient.discovery import build
from pathlib import Path
from dotenv import load_dotenv
import os
from config import GOOGLE_SHEET_ID

load_dotenv()


from google.oauth2.service_account import Credentials

#SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")


BASE_DIR = Path(__file__).resolve().parent.parent
SERVICE_ACCOUNT_FILE = BASE_DIR / "secrets" / "qjoe-service-account.json"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]

def get_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )

    service = build("sheets", "v4", credentials=creds)
    return service


def get_new_jobs(spreadsheet_id, range_name="jobs!A2:D100"):
    service = get_service()
    sheet = service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    return result.get("values", [])


def get_jobs_to_process(spreadsheet_id, status="NEW"):
    service = get_service()
    sheet = service.spreadsheets()

    result = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range="2026!A7:S"
    ).execute()

    values = result.get("values", [])
    jobs = []

    for i, row in enumerate(values):
        row_number = 7 + i

        col_A = row[0] if len(row) > 0 else ""
        col_C = row[2] if len(row) > 2 else ""
        col_D = row[3] if len(row) > 3 else ""
        col_F = row[5] if len(row) > 5 else ""
        col_M = row[12] if len(row) > 12 else ""
        col_P = row[15] if len(row) > 15 else ""
        col_S = row[18] if len(row) > 18 else ""

        if col_A == "NON" and col_D and col_F and col_M in ["", status]:
            jobs.append({
                "row_index": row_number,
                "company": col_C,
                "url": col_F,
                "raw_domain": col_D,
                "language": col_P,
                "raw_text": col_S
            })
    print(f"Found {len(jobs)} jobs to process")

    return jobs


def update_engine_fields(spreadsheet_id, row, status, cv, ldm, draft=""):
    service = get_service()
    sheet = service.spreadsheets()

    updates = [
        {
            "range": f"2026!M{row}",  # Status
            "values": [[status]],
        },
        {
            "range": f"2026!N{row}",  # CV hyperlink
            "values": [[cv]],
        },
        {
            "range": f"2026!O{row}",  # LDM hyperlink
            "values": [[ldm]],
        },
        {
            "range": f"2026!P{row}",  # Gmail draft
            "values": [[draft]],
        },
    ]

    body = {
        "valueInputOption": "USER_ENTERED",
        "data": updates,
    }

    sheet.values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()

def get_contacts_rows():

    spreadsheet_id = GOOGLE_SHEET_ID
    service = get_service()
    sheet = service.spreadsheets()

    sheet_name = "CONTACTS"

    # Adapte le range: suppose header en ligne 1, data dès ligne 2
    resp = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A5:E"
    ).execute()

    values = resp.get("values", [])
    out = []
    row_index = 5
    for v in values:
        company = v[0] if len(v) > 0 else ""
        email = v[1] if len(v) > 1 else ""
        first_name = v[2] if len(v) > 2 else ""
        desk = v[3] if len(v) > 3 else ""
        language = v[4] if len(v) > 4 else "EN"
        status = v[5] if len(v) > 5 else ""
        out.append({
            "row": row_index,
            "company": company,
            "email": email,
            "first_name": first_name,
            "desk": desk,
            "status": status,
            "language": language,
        })
        row_index += 1
    return out

def update_contacts_fields(row, status, cv_cell, draft_cell, spreadsheet_id=None, sheet_name="CONTACTS"):
    service = get_service()
    sheet = service.spreadsheets()

    from dotenv import load_dotenv
    import os

    if spreadsheet_id is None:
        spreadsheet_id = GOOGLE_SHEET_ID

    updates = [
        {"range": f"{sheet_name}!F{row}", "values": [[status]]},        # status
        {"range": f"{sheet_name}!G{row}", "values": [[draft_cell]]},    # draft_link
        #{"range": f"{sheet_name}!I{row}", "values": [["SENT"]]},        # delivery_status
    ]

    body = {"valueInputOption": "USER_ENTERED", "data": updates}

    sheet.values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()


def update_bounce(row, spreadsheet_id=None, sheet_name="CONTACTS"):

    from dotenv import load_dotenv
    import os

    if spreadsheet_id is None:
        spreadsheet_id = GOOGLE_SHEET_ID

    service = get_service()
    sheet = service.spreadsheets()

    updates = [
        {"range": f"{sheet_name}!J{row}", "values": [["BOUNCED"]]},
    ]

    body = {"valueInputOption": "USER_ENTERED", "data": updates}

    sheet.values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()

def update_delivery_status(row, status, spreadsheet_id=None, sheet_name="CONTACTS"):

    from dotenv import load_dotenv
    import os

    if spreadsheet_id is None:
        spreadsheet_id = GOOGLE_SHEET_ID

    service = get_service()
    sheet = service.spreadsheets()

    updates = [
        {"range": f"{sheet_name}!I{row}", "values": [[status]]},
    ]

    body = {"valueInputOption": "USER_ENTERED", "data": updates}

    sheet.values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()