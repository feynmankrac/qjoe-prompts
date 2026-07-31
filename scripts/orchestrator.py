import sys
from pathlib import Path
import time
import traceback
from cleanup_artifacts import *
import re
import argparse

# add project root to python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.logger import get_logger

logger = get_logger("batch", "batch.log")

sys.path.append(str(Path(__file__).resolve().parent.parent))

import config
from filelock import FileLock, Timeout

import requests
from config import PROCESS_ONLY_STATUS, MAX_ROWS_PER_RUN, DRY_RUN
from infra.sheet_client import get_jobs_to_process, update_engine_fields
from scraping.scraper import scrape_url
from infra.drive_uploader import upload_to_drive
from pathlib import Path
from core.job_memory import load_memory, save_memory, hash_job
from config import PROCESS_ONLY_STATUS, MAX_ROWS_PER_RUN, DRY_RUN, SAVE_MODE, AUTO_DOWNLOAD, LOCAL_DOWNLOAD_PATH
import os

SPREADSHEET_ID = "10DSDAsJpXWmdpafk-MlG_FXA-5-idxnlzuWLY83G7Kk"
API_URL = "http://localhost:8000/analyze_text"

parser = argparse.ArgumentParser()
parser.add_argument("--row", type=int, default=None)
args = parser.parse_args()
force_row = args.row

def main():
    memory = load_memory()
    logger.info("Batch started")

    jobs = get_jobs_to_process(
        SPREADSHEET_ID,
        status=None if force_row else PROCESS_ONLY_STATUS,
        force_row=force_row
    )

    if force_row:
        jobs = [j for j in jobs if j["row_index"] == force_row]
    else:
        jobs = jobs[:MAX_ROWS_PER_RUN]

    if not jobs:
        print("No jobs to process")
        return

    print(f"Found {len(jobs)} jobs to process")

    for job in jobs:
        job_hash = None
        row = job["row_index"]
        gmail_draft_link = ""
        cv_name = ""
        ldm_name = ""

        logger.info(f"Processing row: {row}")
        print("RAW_DOMAIN:", job.get("raw_domain"))
        print("SCRAPING URL:", job["url"])

        try:
            if not DRY_RUN:
                update_engine_fields(SPREADSHEET_ID, row, "PROCESSING", "", "", "")

            if job.get("raw_text"):
                print("Using RAW_TEXT from sheet")
                scraped_text = job["raw_text"]
            else:
                scraped = scrape_url(job["url"])

                if not scraped["ok"]:
                    if not DRY_RUN:
                        update_engine_fields(SPREADSHEET_ID, row, "SCRAPE_FAILED", "", "", "")
                    continue

                scraped_text = scraped["text"]

            payload = {"job_text": scraped_text}
            headers = {"x-api-key": os.getenv("QJOE_API_TOKEN")}

            print("CALLING ANALYZE API")
            response = requests.post(API_URL, json=payload, headers=headers, timeout=20)
            response.raise_for_status()
            print("API RESPONSE RECEIVED")

            result = response.json()
            job_json = result.get("job_json") or {}
            score = result.get("score")
            decision = result.get("decision")

            print("DEBUG role_family:", job_json.get("role_family"))
            print("DEBUG derivatives_pricing:", job_json.get("derivatives_pricing"))
            print("DEBUG signals_for_fit:", job_json.get("signals_for_fit"))
            print("Score:", score)
            print(f"Row {row} | {decision} | score={score}")

            if "decision" not in result:
                print("Invalid API response")
                if not DRY_RUN:
                    update_engine_fields(SPREADSHEET_ID, row, "ERROR", "", "", "")
                continue

            if decision != "GREEN" and not force_row:
                status = "DONE_RED"

                if not DRY_RUN:
                    update_engine_fields(
                        SPREADSHEET_ID,
                        row,
                        status,
                        "",
                        "",
                        ""
                    )
                continue

            if not job_json:
                print("Missing job_json in API response")
                if not DRY_RUN:
                    update_engine_fields(SPREADSHEET_ID, row, "ERROR", "", "", "")
                continue

            job_json["row_index"] = row
            job_json["cv_title_override"] = job.get("raw_domain")
            job_json["language"] = job.get("language") or "EN"
            job_json["company"] = job.get("company") or job_json.get("company")

            contact_email = job_json.get("contact_email")
            valid_email = (
                contact_email
                and re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", contact_email)
            )

            if not valid_email:
                contact_email = None

            is_email_application = bool(contact_email)

            print("DEBUG JOB KEYS:", job.keys())
            cv_template = job.get("CV_template")
            print("DEBUG CV TEMPLATE:", cv_template)

            gen_response = retry_request(
                lambda: requests.post(
                    "http://localhost:8000/generate_application",
                    json={
                        "job_json": job_json,
                        "email_application": is_email_application,
                        "force_generate": True,
                        "cv_template": cv_template
                    },
                    headers=headers,
                    timeout=30
                )
            )

            gen_response.raise_for_status()
            gen_result = gen_response.json()
            #print("DEBUG GEN RESULT:", gen_result)

            generation = gen_result.get("generation", {})
            artifacts = generation.get("artifacts", {})
            email_data = generation.get("email", {})

            cv_local_path = artifacts.get("cv_pdf_path")
            ldm_local_path = None if is_email_application else artifacts.get("ldm_pdf_path")
            email_subject = email_data.get("subject", "")
            email_body = email_data.get("body", "")

            print("DEBUG CV PATH:", cv_local_path)
            print("DEBUG LDM PATH:", ldm_local_path)

            if not cv_local_path or not Path(cv_local_path).exists():
                print("CV file missing → generation failed")
                status = "GENERATION_FAILED"

                if not DRY_RUN:
                    update_engine_fields(SPREADSHEET_ID, row, status, "", "", "")
                continue

            if email_subject:
                print("EMAIL SUBJECT:", email_subject)
                print("EMAIL BODY:", email_body)

            if is_email_application and email_subject:
                gmail_response = retry_request(
                    lambda: requests.post(
                        "http://localhost:8000/create_gmail_draft",
                        json={
                            "to_email": contact_email,
                            "subject": email_subject,
                            "body": email_body,
                            "attachment_path": cv_local_path
                        },
                        headers=headers,
                        timeout=30
                    )
                )

                gmail_response.raise_for_status()

                if gmail_response.status_code == 200:
                    draft_id = gmail_response.json()["draft"]["id"]
                    gmail_draft_link = f'=HYPERLINK("https://mail.google.com/mail/#drafts?compose={draft_id}","OPEN")'

            drive_link_cv = ""
            drive_link_ldm = ""

            if not DRY_RUN:
                if SAVE_MODE == "drive":
                    drive_link_cv = upload_to_drive(cv_local_path)

                    if AUTO_DOWNLOAD and LOCAL_DOWNLOAD_PATH:
                        #os.system(f'scp "{cv_local_path}" "{LOCAL_DOWNLOAD_PATH}"')
                        os.system(f'scp root@178.104.64.115:"{cv_local_path}" "{LOCAL_DOWNLOAD_PATH}"')
                else:
                    drive_link_cv = f"file://{Path(cv_local_path).resolve()}"

                if (
                    not is_email_application
                    and ldm_local_path
                    and Path(ldm_local_path).exists()
                ):
                    if SAVE_MODE == "drive":
                        drive_link_ldm = upload_to_drive(ldm_local_path)

                        if AUTO_DOWNLOAD and LOCAL_DOWNLOAD_PATH:
                            #os.system(f'scp "{ldm_local_path}" "{LOCAL_DOWNLOAD_PATH}"')
                            os.system(f'scp root@178.104.64.115:"{ldm_local_path}" "{LOCAL_DOWNLOAD_PATH}"')
                    else:
                        drive_link_ldm = f"file://{Path(ldm_local_path).resolve()}"
            else:
                drive_link_cv = "DRY_RUN"
                if not is_email_application and ldm_local_path:
                    drive_link_ldm = "DRY_RUN"

            cv_file = Path(cv_local_path).name
            cv_name = f'=HYPERLINK("{drive_link_cv}";"{cv_file}")'

            if (
                not is_email_application
                and ldm_local_path
                and drive_link_ldm
                and Path(ldm_local_path).exists()
            ):
                ldm_file = Path(ldm_local_path).name
                ldm_name = f'=HYPERLINK("{drive_link_ldm}";"{ldm_file}")'
            else:
                ldm_name = ""

            status = "Exception" if force_row else "DONE_GREEN"

            if not DRY_RUN:
                update_engine_fields(
                    SPREADSHEET_ID,
                    row,
                    status,
                    cv_name,
                    ldm_name,
                    gmail_draft_link
                )
### nettoyage desactivé
           # if cv_local_path and os.path.exists(cv_local_path):
           #     os.remove(cv_local_path)

            #if ldm_local_path and os.path.exists(ldm_local_path):
             #   os.remove(ldm_local_path)

            if job_hash:
                logger.info(f"Saving job hash: {job_hash}")
                memory.add(job_hash)
                save_memory(memory)

        except Exception as e:
            print("ERROR:", str(e))
            traceback.print_exc()

            if not DRY_RUN:
                update_engine_fields(SPREADSHEET_ID, row, "ERROR", "", "", "")

            logger.error(f"Unexpected error: {str(e)}")

def retry_request(func, max_attempts=3, delay=2):

    for attempt in range(max_attempts):
        try:
            return func()

        except Exception as e:

            if attempt == max_attempts - 1:
                raise

            sleep_time = delay * (2 ** attempt)
            print(f"Retry in {sleep_time}s:", str(e))
            time.sleep(sleep_time)


if __name__ == "__main__":
    main()
