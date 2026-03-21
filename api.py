from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional
import os
from core.gmail_draft import create_gmail_draft
import subprocess
from fastapi import BackgroundTasks
from filelock import FileLock, Timeout
import config

from core.pipeline import run_analysis, run_generate_application
from core.pipeline_text import run_analysis_from_text

from pydantic import BaseModel
from core.logger import get_logger

logger = get_logger("api", "api.log")

class GmailDraftRequest(BaseModel):
    to_email: str
    subject: str
    body: str
    attachment_path: Optional[str] = None
    bcc_emails: list[str] = []

class SpontaneousRequest(BaseModel):
    company: str
    to_email: str
    first_name: Optional[str] = None
    desk: str
    language: str = "EN"

app = FastAPI(title="QJOE Engine")

API_TOKEN = os.getenv("QJOE_API_TOKEN")


class JobJSONRequest(BaseModel):
    job_json: dict
    email_application: bool = False
    force_generate: bool = False
    cv_template: Optional[str] = None

class JobTextRequest(BaseModel):
    job_text: str


class BatchTextRequest(BaseModel):
    offers: List[str]


def verify_token(x_api_key: str = Header(None)):
    # 🔥 MODE DEV : si pas de token configuré → on laisse passer
    if API_TOKEN is None:
        return
    if x_api_key != API_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/health")
def health(x_api_key: str = Header(None)):
    verify_token(x_api_key)
    return {"status": "ok"}


@app.post("/analyze_text")
def analyze_text(request: JobTextRequest, x_api_key: str = Header(None)):
    verify_token(x_api_key)

    analysis = run_analysis_from_text(request.job_text)

    return {
        "decision": analysis.get("decision"),
        "score": analysis.get("score"),
        "job_json": analysis.get("job_json")
    }


@app.post("/analyze")
def analyze(request: JobJSONRequest, x_api_key: str = Header(None)):
    verify_token(x_api_key)
    return run_analysis(request.job_json)


@app.post("/generate_application")
def generate_application(request: JobJSONRequest, x_api_key: str = Header(None)):
    verify_token(x_api_key)

    analysis = run_analysis(request.job_json)
    if analysis.get("decision") != "GREEN" and not request.force_generate:
        raise HTTPException(status_code=400, detail="Cannot generate application: decision is not GREEN")

    job_json = request.job_json
    email_application = request.email_application
    cv_template = request.cv_template

    generation = run_generate_application(
        job_json,
        email_application=email_application,
        cv_template=cv_template
    )
#    generation = run_generate_application(job_json, email_application=email_application)
    return {"analysis": analysis, "generation": generation}


@app.post("/analyze_batch")
def analyze_batch(request: BatchTextRequest, x_api_key: str = Header(None)):
    verify_token(x_api_key)

    results = []

    for job_text in request.offers:
        analysis = run_analysis_from_text(job_text)

        entry = {
            "decision": analysis.get("decision"),
            "score": analysis.get("score", {}).get("score_0_100"),
        }

        if analysis.get("decision") == "GREEN":
            generation = run_generate_application(analysis["job_json"])
            entry["pdf_path"] = generation["artifacts"]["cv_pdf_path"]

        results.append(entry)

    return {
        "count": len(results),
        "results": results
    }

@app.post("/create_gmail_draft")
def create_gmail_draft_endpoint(req: GmailDraftRequest):
    credentials_path = os.getenv("GMAIL_OAUTH_CREDENTIALS", "secrets/gmail_oauth_client.json")
    token_path = os.getenv("GMAIL_OAUTH_TOKEN", "secrets/gmail_token.json")
    from_email = os.getenv("GMAIL_FROM_EMAIL")  # optionnel

    draft = create_gmail_draft(
        to_email=req.to_email,
        bcc_emails=req.bcc_emails,
        subject=req.subject,
        body=req.body,
        attachment_path=req.attachment_path,
        from_email=from_email,
        credentials_path=credentials_path,
        token_path=token_path,
    )
    return {"ok": True, "draft": draft}

from core.spontaneous import run_generate_spontaneous_application

@app.post("/generate_spontaneous")
def generate_spontaneous(req: SpontaneousRequest, x_api_key: str = Header(None)):
    verify_token(x_api_key)

    generation = run_generate_spontaneous_application(
        company=req.company,
        to_email=req.to_email,
        first_name=req.first_name,
        desk=req.desk,
        language=req.language
    )
    return {"generation": generation}


@app.post("/run_batch")
def run_batch(background_tasks: BackgroundTasks, x_api_key: str = Header(None)):
    if API_TOKEN and x_api_key != API_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")

    def run():

        lock = FileLock(config.LOCK_PATH, timeout=1)

        try:
            with lock:
                subprocess.run(
                    ["python", "scripts/orchestrator.py"],
                    cwd="/root/qjoe-prompts"
                )

        except Timeout:
            print("Batch already running")

    background_tasks.add_task(run)

    return {"status": "batch started"}

@app.post("/run_spontaneous")
def run_spontaneous(background_tasks: BackgroundTasks, x_api_key: str = Header(None)):

    if API_TOKEN and x_api_key != API_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")

    def run():

        subprocess.run(
            ["/root/qjoe-prompts/venv/bin/python", "scripts/orchestrator_spontaneous.py"],
            cwd="/root/qjoe-prompts",
            env={**os.environ}
        )

    background_tasks.add_task(run)

    return {"status": "spontaneous batch started"}

from fastapi import Request

@app.post("/run_override")
async def run_override(request: Request):
    data = await request.json()
    row = data.get("row")

    import subprocess

    subprocess.Popen(
        ["python3", "scripts/orchestrator.py", "--row", str(row)],
        cwd="/root/qjoe-prompts"
    )

    return {"status": "override_started", "row": row}
