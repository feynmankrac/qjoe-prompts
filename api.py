from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import List
import os

from core.pipeline import run_analysis, run_generate_application
from core.pipeline_text import run_analysis_from_text

app = FastAPI(title="QJOE Engine")

API_TOKEN = os.getenv("QJOE_API_TOKEN")


class JobJSONRequest(BaseModel):
    job_json: dict


class JobTextRequest(BaseModel):
    job_text: str


class BatchTextRequest(BaseModel):
    offers: List[str]


def verify_token(x_api_key: str = Header(None)):
    if API_TOKEN is None:
        raise HTTPException(status_code=500, detail="API token not configured on server")
    if x_api_key != API_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/health")
def health(x_api_key: str = Header(None)):
    verify_token(x_api_key)
    return {"status": "ok"}


# Analyse depuis texte brut
@app.post("/analyze_text")
def analyze_text(request: JobTextRequest, x_api_key: str = Header(None)):
    verify_token(x_api_key)
    return run_analysis_from_text(request.job_text)


# Analyse depuis JSON structuré
@app.post("/analyze")
def analyze(request: JobJSONRequest, x_api_key: str = Header(None)):
    verify_token(x_api_key)
    return run_analysis(request.job_json)


# Génération CV si GREEN
@app.post("/generate_application")
def generate_application(request: JobJSONRequest, x_api_key: str = Header(None)):
    verify_token(x_api_key)

    analysis = run_analysis(request.job_json)
    if analysis.get("decision") != "GREEN":
        raise HTTPException(status_code=400, detail="Cannot generate application: decision is not GREEN")

    generation = run_generate_application(request.job_json)
    return {"analysis": analysis, "generation": generation}


# 🔥 NOUVEAU : Batch processing
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
            entry["pdf_path"] = generation["artifacts"]["pdf_path"]

        results.append(entry)

    return {
        "count": len(results),
        "results": results
    }