from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core.pipeline import run_analysis, run_generate_application

app = FastAPI(title="QJOE Engine")


class JobRequest(BaseModel):
    job_json: dict


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
def analyze(request: JobRequest):
    return run_analysis(request.job_json)


@app.post("/generate_application")
def generate_application(request: JobRequest):

    analysis = run_analysis(request.job_json)

    if analysis.get("decision") != "GREEN":
        raise HTTPException(
            status_code=400,
            detail="Cannot generate application: decision is not GREEN"
        )

    generation = run_generate_application(request.job_json)

    return {
        "analysis": analysis,
        "generation": generation
    }