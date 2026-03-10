import sys
from pathlib import Path
import time
import traceback
from cleanup_artifacts import *

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
import os

SPREADSHEET_ID = "10DSDAsJpXWmdpafk-MlG_FXA-5-idxnlzuWLY83G7Kk"
API_URL = "http://localhost:8000/analyze_text"

def main():
    memory = load_memory()
    logger.info("Batch started")

    jobs = get_jobs_to_process(
        SPREADSHEET_ID,
        status=PROCESS_ONLY_STATUS
    )
    jobs = jobs[:MAX_ROWS_PER_RUN]

    if not jobs:
        print("No jobs to process")
        return

    for job in jobs:
        job_hash = None
        row = job["row_index"]

        gmail_draft_link = ""

        logger.info(f"Processing row: {row}")
        #print("Processing row:", row)
        print("RAW_DOMAIN:", job.get("raw_domain"))
        print("SCRAPING URL:", job["url"])

        try:

            # 1️⃣ Mark as PROCESSING
            if not DRY_RUN:
                update_engine_fields(SPREADSHEET_ID, row, "PROCESSING", "", "")

            # 2️⃣ Scrape
            # ===============================
            # SCRAPING / RAW TEXT STRATEGY
            # ===============================

            if job.get("raw_text"):
                print("Using RAW_TEXT from sheet")
                scraped_text = job["raw_text"]
                #scraped_text = scraped_text.replace("\n", " ").replace("\r", " ")

            else:
                scraped = scrape_url(job["url"])

                if not scraped["ok"]:
                    if not DRY_RUN:
                        update_engine_fields(SPREADSHEET_ID, row, "SCRAPE_FAILED", "", "")
                    continue

                scraped_text = scraped["text"]

            # ANTI DUPLICATE
            job_hash = hash_job(scraped_text)

            if job_hash in memory:
                logger.info("Duplicate job skipped")
                if not DRY_RUN:
                    update_engine_fields(
                    SPREADSHEET_ID,
                    row,
                    "DEJA_VU",
                    "",
                    "",
                    ""
                    )
                continue

            # Payload API
            payload = {"job_text": scraped_text}
            headers = {"x-api-key": os.getenv("QJOE_API_TOKEN")}

            #response = requests.post(API_URL, json=payload, headers=headers, timeout=20)
            print("CALLING ANALYZE API")

            response = requests.post(API_URL, json=payload, headers=headers, timeout=20)
            response.raise_for_status()

            print("API RESPONSE RECEIVED")
           # print(response.json())

            if response.status_code != 200:
                if not DRY_RUN:
                    update_engine_fields(SPREADSHEET_ID, row, "ERROR", "", "")
                continue

            result = response.json()
            job_json = result.get("job_json")

            score = result.get("score")
            decision = result.get("decision")

            logger.info(f"Decision: {decision}")
            #print("Decision:", decision)
            print("Score:", score)
            print(f"Row {row} | {decision} | score={score}")

            if "decision" not in result:
                print("Invalid API response")
                continue

            # 4️⃣ Handle decision
            if decision == "GREEN":

                #job_json = result.get("job_json")
                #print(f"Row {row} | {decision} | score={score}")

                if not job_json:
                    print("Missing job_json in API response")
                    continue
                job_json["row_index"] = row
                job_json["cv_title_override"] = job["raw_domain"]
                job_json["language"] = job.get("language", "EN")
                job_json["company"] = job.get("company") or job_json.get("company")
                contact_email = job_json.get("contact_email")
                is_email_application = bool(contact_email)

                gen_response = retry_request(
                    lambda: requests.post(            
                        "http://localhost:8000/generate_application",
                        json={
                            "job_json": job_json,
                            "email_application": is_email_application
                        },
                        headers=headers,
                        timeout=30
                    )
                )

                gen_response.raise_for_status()

                if gen_response.status_code == 200:
                    gen_result = gen_response.json()

                    cv_local_path = gen_result["generation"]["artifacts"]["cv_pdf_path"]
                    email_subject = gen_result["generation"]["email"]["subject"]
                    email_body = gen_result["generation"]["email"]["body"]

                    ldm_local_path = None
                    if not is_email_application:
                        ldm_local_path = gen_result["generation"]["artifacts"]["ldm_pdf_path"]

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
                    if not DRY_RUN:
                        drive_link_cv = upload_to_drive(cv_local_path)

                        drive_link_ldm = ""
                        if not is_email_application and ldm_local_path:
                            drive_link_ldm = upload_to_drive(ldm_local_path)
                    else:
                        drive_link_cv = "DRY_RUN"
                        drive_link_ldm = "DRY_RUN"

                    cv_file = Path(cv_local_path).name
                    cv_name = f'=HYPERLINK("{drive_link_cv}";"{cv_file}")'

                    ldm_name = ""
                    if not is_email_application and ldm_local_path:
                        ldm_file = Path(ldm_local_path).name
                        ldm_name = f'=HYPERLINK("{drive_link_ldm}";"{ldm_file}")'

                    #cv_name = f'=HYPERLINK("{drive_link_cv}";"{cv_file}")'
                    #ldm_name = f'=HYPERLINK("{drive_link_ldm}";"{ldm_file}")'

                    status = "DONE_GREEN"

                    # Clean local files
                    if os.path.exists(cv_local_path):
                        os.remove(cv_local_path)

                    if ldm_local_path and os.path.exists(ldm_local_path):
                        os.remove(ldm_local_path)

                else:
                    status = "GENERATION_FAILED"
                    cv_name = ""
                    ldm_name = ""

            else:
                status = "DONE_RED"
                cv_name = ""
                ldm_name = ""
                gmail_draft_link = ""
                print(f"Row {row} | {decision} | score={score}")
                #print(result["job_json"])

            if not DRY_RUN:
                update_engine_fields(
                    SPREADSHEET_ID,
                    row,
                    status,
                    cv_name,
                    ldm_name,
                    gmail_draft_link
                )
            if job_hash:
                logger.info(f"Saving job hash: {job_hash}")
                memory.add(job_hash)
                save_memory(memory)

        except Exception as e:
            print("ERROR:", str(e))
            traceback.print_exc()
            if not DRY_RUN:
                update_engine_fields(SPREADSHEET_ID, row, "ERROR", "", "")
            logger.error(f"Unexpected error: {str(e)}")
            #print("Unexpected error:", str(e))

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
