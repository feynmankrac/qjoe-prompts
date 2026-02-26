from typing import Dict


FRENCH_MARKERS = [
    "le", "la", "les", "des", "une", "poste", "candidature",
    "expérience", "compétences", "profil", "anglais requis"
]


def detect_offer_language(job_json: Dict) -> str:
    """
    Rough heuristic detection of offer language.
    Returns: "FR" or "EN"
    """

    text_blob = " ".join(
        job_json.get("key_missions", [])
        + job_json.get("key_requirements", [])
    ).lower()

    french_hits = sum(marker in text_blob for marker in FRENCH_MARKERS)

    if french_hits >= 2:
        return "FR"

    return "EN"


def determine_languages(job_json: Dict) -> Dict:
    """
    Decide language for CV and letter/email.
    """

    offer_lang = detect_offer_language(job_json)

    return {
        "cv_language": "EN",  # Always English
        "written_language": offer_lang  # FR or EN
    }
