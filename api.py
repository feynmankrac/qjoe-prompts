from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, UTC

from core.normalize import normalize_job
from core.gate import evaluate_gate
from core.score import compute_score

app = FastAPI(title="QJOE Engine")

class JobRequest(BaseModel):
    job_text: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze")
def analyze(request: JobRequest):

    # ⚠️ Pour l’instant on bypass extract (si ton extract est LLM-based)
    # On simule un "normalized" minimal si nécessaire.
    # Si tu as un extract déterministe, branche-le ici.

    normalized = normalize_job({
        "raw_text": request.job_text
    })

    gate = evaluate_gate(normalized)

    if gate["is_blocked"]:
        return {
            "decision": "RED",
            "reason": gate["reason"],
            "normalized_job": normalized,
            "ts": datetime.now(UTC).isoformat()
        }

    score = compute_score(normalized)

    return {
        "score": score["score_0_100"],
        "decision": score["decision"],
        "top_reasons": score["top_reasons"],
        "main_risk": score["main_risk"],
        "normalized_job": normalized,
        "ts": datetime.now(UTC).isoformat()
    }