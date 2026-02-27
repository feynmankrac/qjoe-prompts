import json
from typing import Dict, Any


def load_prompt(prompt_path: str) -> str:
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def _empty_extraction(raw_text: str) -> Dict[str, Any]:
    """
    Fallback déterministe ultra-safe (zéro hallucination).
    Remplit strictement le schéma d'extraction QJOE.
    """
    return {
        "company": None,
        "role_title": None,
        "role_family": None,
        "role_type": None,
        "seniority": None,
        "location": None,
        "remote_policy": None,
        "contract_type": None,
        "business_domain": [],
        "asset_classes": [],
        "key_missions": [],
        "key_requirements": [],
        "model_validation": False,
        "market_risk": False,
        "counterparty_risk": False,
        "derivatives_pricing": False,
        "energy_derivatives": False,
        "quant_research_phd_mandatory": False,
        "cxx_hardcore": False,
        "reporting_heavy": False,
        "quant_intensity": 0,
        "tools": [],
        "red_flags": [],
        "signals_for_fit": [],
        # utile pour debug / audit / tracking
        "raw_text": raw_text,
    }


def call_llm(prompt_text: str) -> Dict:
    """
    Stub : à câbler plus tard.
    """
    raise NotImplementedError("LLM call not implemented yet.")


def extract_job(raw_text: str) -> Dict:
    """
    Extraction factuelle.
    MVP : si LLM non câblé, fallback déterministe (ne bloque jamais l'API).
    """
    prompt_text = load_prompt("prompts/01_extract_job.md")
    full_prompt = prompt_text + "\n\nJOB_TEXT:\n" + raw_text

    try:
        response = call_llm(full_prompt)
    except NotImplementedError:
        return _empty_extraction(raw_text)
    except Exception:
        # fallback safe sur toute erreur inattendue
        return _empty_extraction(raw_text)

    # Validation minimale : si le LLM renvoie un truc bizarre, on fallback
    if not isinstance(response, dict) or not response:
        return _empty_extraction(raw_text)

    # Optionnel: garantir que raw_text est présent pour traçabilité
    response.setdefault("raw_text", raw_text)

    return response