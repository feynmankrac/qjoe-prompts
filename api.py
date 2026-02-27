from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import os

from core.pipeline import run_analysis, run_generate_application

app = FastAPI(title="QJOE Engine")

# Token attendu (défini en variable d'environnement)
API_TOKEN = os.getenv("QJOE_API_TOKEN")
print("SERVER TOKEN:", API_TOKEN)


class JobRequest(BaseModel):
    job_json: dict


def verify_token(x_api_key: str = Header(None)):
    print("EXPECTED TOKEN:", API_TOKEN)
    print("RECEIVED TOKEN:", x_api_key)
    if API_TOKEN is None:
        raise HTTPException(status_code=500, detail="API token not configured on server")

    if x_api_key != API_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/health")
def health(x_api_key: str = Header(None)):
    verify_token(x_api_key)
    return {"status": "ok"}


@app.post("/analyze")
def analyze(request: JobRequest, x_api_key: str = Header(None)):
    verify_token(x_api_key)
    return run_analysis(request.job_json)


@app.post("/generate_application")
def generate_application(request: JobRequest, x_api_key: str = Header(None)):

    verify_token(x_api_key)

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