from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, UTC

from core.pipeline import run_pipeline

app = FastAPI(title="QJOE Engine")

class JobRequest(BaseModel):
    job_text: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
def analyze(request: JobRequest):

    # ⚠️ Pour l’instant on envoie un job_json minimal.
    # On branchera extract + normalize après.
    job_json = {
        "raw_text": request.job_text
    }

    result = run_pipeline(job_json)

    return result