from google.oauth2 import service_account
from googleapiclient.discovery import build
from pathlib import Path
from dotenv import load_dotenv
import os
from config import GOOGLE_SHEET_ID

load_dotenv()


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

def get_new_jobs(spreadsheet_id, sheet_name="2026"):
    service = get_service()
    sheet = service.spreadsheets()

    result = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A6:Z"
    ).execute()

    values = result.get("values", [])

    if not values:
        return []

    headers = values[0]
    #header_index = {h: i for i, h in enumerate(headers)}
    header_index = {h.strip().lower(): i for i, h in enumerate(headers)}

    def get(row, name):
#        i = header_index.get(name)
        i = header_index.get(name.lower())
        return row[i] if i is not None and len(row) > i else ""

    jobs = []

    for i, row in enumerate(values[1:]):
        jobs.append({
            "company": get(row, "ENTREPRISE"),
            "poste": get(row, "POSTE"),
            "contrat": get(row, "CONTRAT"),
            "lieu": get(row, "LIEU"),
            "lien": get(row, "LIEN"),
            "raw_text": get(row, "RAW_TEXT"),
            "langue": get(row, "LANGUE"),
            "status": get(row, "STATUS")
        })

    return jobs

def get_jobs_to_process(spreadsheet_id, status="NEW", force_row=None):
#def get_jobs_to_process(spreadsheet_id, status="NEW"):
    service = get_service()
    sheet = service.spreadsheets()

    result = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range="2026!A6:Z"
    ).execute()

    values = result.get("values", [])
    jobs = []

    if not values:
        return []
    headers = values[0]
    header_index = {h: i for i, h in enumerate(headers)}

    def get(row, name):
        i = header_index.get(name)
        return row[i] if i is not None and len(row) > i else ""

    for i, row in enumerate(values[1:]):
        row_number = 7 + i

        company = get(row, "ENTREPRISE")
        poste = get(row, "POSTE")
        url = get(row, "LIEN")
       # engine_status = get(row, "STATUS")
        language = get(row, "LANGUE")
        raw_text = get(row, "RAW_TEXT")
        postule = get(row, "Apply").strip().upper()
        engine_status = get(row, "STATUS")
        cv_template = get(row, "CV_template")

        if force_row:
            if row_number != force_row:
                continue

            jobs.append({
                "row_index": row_number,
                "company": company,
                "url": url,
                "raw_domain": poste,
                "language": language,
                "raw_text": raw_text,
                "CV_template": cv_template
            })
            continue

        if postule == "NON" and poste and not engine_status:
            jobs.append({
                "row_index": row_number,
                "company": company,
                "url": url,
                "raw_domain": poste,
                "language": language,
                "raw_text": raw_text,
                "CV_template": cv_template
            })

#        print("DEBUG:", row_number, postule, poste, engine_status)

#        if postule == "NON" and poste and not engine_status:
#

 #           jobs.append({
 #               "row_index": row_number,
 #               "company": company,
 #               "url": url,
 #               "raw_domain": poste,
 #               "language": language,
 #               "raw_text": raw_text
 #           })
    print(f"Found {len(jobs)} jobs to process")

    return jobs

def update_engine_fields(spreadsheet_id, row, status, cv, ldm, draft=""):
    service = get_service()
    sheet = service.spreadsheets()

    # récupérer headers
    resp = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range="2026!A6:Z6"
    ).execute()

    headers = resp.get("values", [[]])[0]
    header_index = {h: i for i, h in enumerate(headers)}

    def col_letter(name):
        i = header_index.get(name)
        if i is None:
            return None
        return chr(ord('A') + i)

    status_col = col_letter("STATUS")
    cv_col = col_letter("CV_File")
    ldm_col = col_letter("LDM_file")
    #draft_col = col_letter("Email_body")

    updates = []

    if status_col:
        updates.append({
            "range": f"2026!{status_col}{row}",
            "values": [[status]],
        })

    if cv_col:
        updates.append({
            "range": f"2026!{cv_col}{row}",
            "values": [[cv]],
        })

    if ldm_col:
        updates.append({
            "range": f"2026!{ldm_col}{row}",
            "values": [[ldm]],
        })

    #if draft_col:
     #   updates.append({
      #      "range": f"2026!{draft_col}{row}",
       #     "values": [[draft]],
       # })

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

    resp = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A4:Z"
    ).execute()

    values = resp.get("values", [])
    out = []

    headers = values[0]
    header_index = {h: i for i, h in enumerate(headers)}

    def get(row, name):
        i = header_index.get(name)
        return row[i] if i is not None and len(row) > i else ""

    row_index = 5

    for v in values[1:]:

        company = get(v, "company")
        email = get(v, "email")
        first_name = get(v, "first_name")
        desk = get(v, "desk")
        language = get(v, "language") or "EN"
        status = get(v, "status")
        group_id = get(v, "group_id")
        draft_link = get(v, "draft_link")
        date_prévue = get(v, "date_prévue")
        out.append({
            "row": row_index,
            "company": company,
            "email": email,
            "first_name": first_name,
            "desk": desk,
            "language": language,
            "status": status,
            "group_id": group_id,
            "draft_link": draft_link,
            "date_prévue": date_prévue,
        })

        row_index += 1

    return out


def update_contacts_fields(row, status, cv_cell, draft_cell, spreadsheet_id=None, sheet_name="CONTACTS"):
    service = get_service()
    sheet = service.spreadsheets()

    if spreadsheet_id is None:
        spreadsheet_id = GOOGLE_SHEET_ID

    # récupérer les headers
    resp = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A4:Z4"
    ).execute()

    headers = resp.get("values", [[]])[0]
    header_index = {h: i for i, h in enumerate(headers)}

    def col_letter(name):
        i = header_index.get(name)
        if i is None:
            return None
        return chr(ord('A') + i)

    status_col = col_letter("status")
    draft_col = col_letter("draft_link")

    updates = []

    if status_col:
        updates.append({
            "range": f"{sheet_name}!{status_col}{row}",
            "values": [[status]]
        })

    if draft_col:
        updates.append({
            "range": f"{sheet_name}!{draft_col}{row}",
            "values": [[draft_cell]]
        })

    body = {
        "valueInputOption": "USER_ENTERED",
        "data": updates
    }

    sheet.values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()

def update_bounce(row, spreadsheet_id=None, sheet_name="CONTACTS"):

    if spreadsheet_id is None:
        spreadsheet_id = GOOGLE_SHEET_ID

    service = get_service()
    sheet = service.spreadsheets()

    resp = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A4:Z4"
    ).execute()

    headers = resp.get("values", [[]])[0]
    header_index = {h: i for i, h in enumerate(headers)}

    def col_letter(name):
        i = header_index.get(name)
        if i is None:
            return None
        return chr(ord('A') + i)

    delivery_col = col_letter("delivery_status")

    updates = []

    if delivery_col:
        updates.append({
            "range": f"{sheet_name}!{delivery_col}{row}",
            "values": [["BOUNCED"]],
        })

    body = {"valueInputOption": "USER_ENTERED", "data": updates}

    sheet.values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()


def update_delivery_status(row, status, spreadsheet_id=None, sheet_name="CONTACTS"):

    if spreadsheet_id is None:
        spreadsheet_id = GOOGLE_SHEET_ID

    service = get_service()
    sheet = service.spreadsheets()

    resp = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A4:Z4"
    ).execute()

    headers = resp.get("values", [[]])[0]
    header_index = {h: i for i, h in enumerate(headers)}

    def col_letter(name):
        i = header_index.get(name)
        if i is None:
            return None
        return chr(ord('A') + i)

    delivery_col = col_letter("delivery_status")

    updates = []

    if delivery_col:
        updates.append({
            "range": f"{sheet_name}!{delivery_col}{row}",
            "values": [[status]],
        })

    body = {"valueInputOption": "USER_ENTERED", "data": updates}

    sheet.values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()

def update_date_envoi(row, date_str, spreadsheet_id=None, sheet_name="CONTACTS"):

    if spreadsheet_id is None:
        spreadsheet_id = GOOGLE_SHEET_ID

    service = get_service()
    sheet = service.spreadsheets()

    resp = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A4:Z4"
    ).execute()

    headers = resp.get("values", [[]])[0]
    header_index = {h: i for i, h in enumerate(headers)}

    def col_letter(name):
        i = header_index.get(name)
        if i is None:
            return None
        return chr(ord('A') + i)

    date_col = col_letter("date_envoi")

    if not date_col:
        return

    body = {
        "valueInputOption": "USER_ENTERED",
        "data": [{
            "range": f"{sheet_name}!{date_col}{row}",
            "values": [[date_str]],
        }]
    }

    sheet.values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()


def update_contact_extra_fields(row, fields: dict, spreadsheet_id=None, sheet_name="CONTACTS"):
    service = get_service()
    sheet = service.spreadsheets()

    if spreadsheet_id is None:
        spreadsheet_id = GOOGLE_SHEET_ID

    resp = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A4:Z4"
    ).execute()

    headers = resp.get("values", [[]])[0]
    header_index = {h: i for i, h in enumerate(headers)}

    def col_letter(name):
        i = header_index.get(name)
        if i is None:
            return None
        return chr(ord('A') + i)

    updates = []

    for field_name, value in fields.items():
        col = col_letter(field_name)
        if col:
            updates.append({
                "range": f"{sheet_name}!{col}{row}",
                "values": [[value]]
            })

    if not updates:
        return

    body = {
        "valueInputOption": "USER_ENTERED",
        "data": updates
    }

    sheet.values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()
