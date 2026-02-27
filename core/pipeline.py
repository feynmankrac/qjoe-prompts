from datetime import datetime
from typing import Optional

from core.gate import evaluate_gate
from core.score import compute_score


def run_pipeline(job_json: dict) -> dict:
    """
    Pipeline déterministe minimal :
    Gate → Score → (LLM si borderline)

    Ne génère PAS de PDF.
    Ne touche PAS aux templates.
    Pure logique décisionnelle.
    """

    result = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "job_json": job_json,
    }

    # 1️⃣ Gate
    gate_result = evaluate_gate(job_json)
    result["gate"] = gate_result

    if gate_result.get("is_blocked"):
        result["decision"] = "RED"
        result["status"] = "BLOCKED"
        return result

    # 2️⃣ Score
    score_result = compute_score(job_json)
    result["score"] = score_result

    final_decision = score_result.get("decision")

    result["decision"] = final_decision
    result["status"] = "DONE"

    return result