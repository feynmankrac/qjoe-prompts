from core.pipeline import run_analysis
from core.extract import extract_job
from core.normalize import normalize_job


def run_analysis_from_text(job_text: str) -> dict:
    extracted = extract_job(job_text)
    normalized = normalize_job(extracted)

    analysis = run_analysis(normalized)

    return {
        "job_json": normalized,
        "decision": analysis["decision"],
        "score": analysis["score"]
    }