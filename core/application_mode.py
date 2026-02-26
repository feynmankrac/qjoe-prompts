from typing import Dict


def detect_application_mode(job_json: Dict) -> Dict:
    """
    Detect whether the job requires email application,
    platform upload, or is unclear.
    """

    text_blob = " ".join(
        job_json.get("key_missions", [])
        + job_json.get("key_requirements", [])
    ).lower()

    if "send your cv to" in text_blob or "email your application" in text_blob:
        return {
            "mode": "EMAIL_REQUIRED",
            "confidence": "HIGH"
        }

    if "apply via" in text_blob or "apply online" in text_blob:
        return {
            "mode": "PLATFORM_UPLOAD",
            "confidence": "HIGH"
        }

    return {
        "mode": "UNKNOWN",
        "confidence": "LOW"
    }
