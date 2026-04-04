import requests

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import subprocess
import json
from datetime import datetime

print("START SCRIPT")

def parse_linkedin_results(snapshot_json, max_profiles):
    
    results = []
    refs = snapshot_json.get("data", {}).get("refs", {})

    for _, v in refs.items():
        text = (v.get("name") or "").strip()

        if "Poste actuel :" not in text:
            continue

        first_part = text.split("•")[0].strip()
        name_tokens = first_part.split()
        if len(name_tokens) == 0:
            continue

        first_name = name_tokens[0]
        last_name = " ".join(name_tokens[1:]) if len(name_tokens) > 1 else ""

        job_title = None
        if "Poste actuel :" in text:
            after = text.split("Poste actuel :", 1)[1].strip()
            job_title = after.split(" chez ", 1)[0].strip()

            job_title = job_title.split("|")[0].strip()

        location = None
        if "Paris" in text:
            location = "Paris"
        elif "France" in text:
            location = "France"

        profile_url = None
        if "ref" in v:
            ref_id = v.get("ref")
            ref_data = snapshot_json.get("data", {}).get("refs", {}).get(ref_id, {})
            possible = ref_data.get("name", "")
            if "linkedin.com/in/" in possible:
                start = possible.find("linkedin.com/in/")
                profile_url = "https://" + possible[start:].split()[0]
        
        if job_title is None:
            continue

        if len(first_name) < 2:
            continue

        results.append({
            "first_name": first_name,
            "last_name": last_name,
            "job_title": job_title,
            "location": location,
            "profile_url": profile_url
        })

        if len(results) >= int(max_profiles):
            break

    return results


def openclaw_search(query, location, max_profiles):
    ids = row["company_ids"].split(",")

    company_filter = "%2C".join([f"%22{id.strip()}%22" for id in ids])

    url = f"https://www.linkedin.com/search/results/people/?keywords={query}&geoUrn=%5B%2290009659%22%5D&currentCompany=%5B{company_filter}%5D"

    subprocess.run([
        "agent-browser",
        "--auto-connect",
        "open",
        url
    ])

    subprocess.run(["agent-browser", "wait", "2000"])
    subprocess.run(["agent-browser", "click", "Suivant"])
    subprocess.run(["agent-browser", "wait", "2000"])

    output = subprocess.check_output([
        "agent-browser",
        "--auto-connect",
        "snapshot",
        "-i",
        "--json"
    ])

    data = json.loads(output)

    output2 = subprocess.check_output([
    "agent-browser",
    "--auto-connect",
    "snapshot",
    "-i",
    "--json"
    ])

    data2 = json.loads(output2)
    results += parse_linkedin_results(data2, max_profiles)

    return parse_linkedin_results(data, max_profiles)



scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "secrets/qjoe-service-account.json",
    scope
)

client = gspread.authorize(creds)

sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID"))

input_sheet = sheet.worksheet("INPUT")
output_sheet = sheet.worksheet("OUTPUT_1")


# --- 1. Lire INPUT
rows = input_sheet.get_all_records()

row = None
row_index = None

for i, r in enumerate(rows, start=2):  # start=2 (header)
    #if r["status"] == "TO_DO":
    if r["status"] == "TO_DO" and r["search_id"]:
        row = r
        row_index = i
        break
print("ROW SELECTED:", row)

if not row:
    exit()

# --- 2. Lock
input_sheet.update_cell(row_index, 8, "IN_PROGRESS")  # col status

import time
time.sleep(2)

# --- 3. FAKE results (à remplacer par OpenClaw)


#results = openclaw_search(
 #   query=row["query"],
  #  location=row["location"],
  #  max_profiles=row["max_profiles"]
#)
with open("data.json") as f:
    data = json.load(f)
results = parse_linkedin_results(data, row["max_profiles"])

print("RESULTS:", results)

if results is None or len(results) == 0:
    input_sheet.update_cell(row_index, 8, "STOPPED")
    exit()



existing_rows = output_sheet.get_all_records()

existing_keys = set()

for e in existing_rows:
    key = (
        (e.get("first_name") or "").lower().strip(),
        (e.get("last_name") or "").lower().strip(),
        (e.get("company") or "").lower().strip(),
        #(e.get("desk") or "").lower().strip()
        (e.get("job_title") or "").lower().strip()
    )
    existing_keys.add(key)

headers = output_sheet.row_values(1)
#print(headers)
print("HEADERS OUTPUT_1:", headers)

# --- 4. Insert
for r in results:
    key = (
        (r.get("first_name") or "").lower().strip(),
        (r.get("last_name") or "").lower().strip(),
        (row.get("company") or "").lower().strip(),
        (r.get("job_title") or "").lower().strip()
        #(row.get("desk") or "").lower().strip()
        #(row.get("target_desk") or "").lower().strip()
    )

    if key in existing_keys:
        continue

    if r.get("first_name") is None:
        continue

    contact = [
    "",  # contact_id
    r.get("first_name"),
    r.get("last_name"),
    r.get("job_title"),
    row.get("company"),
    r.get("location"),
    row.get("target_desk"),
    row.get("query"),
    row.get("search_id"),
    #r.get("profile_url"),   # linkedin_url
    #r.get("profile_url"),   # clean_url (temp)
    None,
    None,
    datetime.today().strftime("%Y-%m-%d"),
    "NEW"
]

    output_sheet.append_row(contact)


    existing_keys.add(key)

# --- 5. Finish
input_sheet.update_cell(row_index, 8, "DONE")
input_sheet.update_cell(row_index, 9, datetime.today().strftime("%Y-%m-%d"))
