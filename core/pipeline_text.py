from core.pipeline import run_analysis
from core.extract import extract_job
from core.normalize import normalize_job


def run_analysis_from_text(job_text: str) -> dict:
    """
    job_text (str) -> extract -> normalize -> run_analysis(job_json)
    """
    extracted = extract_job(job_text)
    normalized = normalize_job(extracted)
    return run_analysis(normalized)