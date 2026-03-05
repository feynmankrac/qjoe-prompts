from google.oauth2 import service_account
from googleapiclient.discovery import build
from pathlib import Path

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