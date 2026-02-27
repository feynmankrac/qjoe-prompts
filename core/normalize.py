from typing import Dict


def clamp(value: int, min_val: int = 0, max_val: int = 10) -> int:
    return max(min_val, min(max_val, value))


def recompute_quant_intensity(job_json: Dict) -> int:
    score = 0

    text_blob = " ".join(
        (job_json.get("key_missions", []) or []) +
        (job_json.get("key_requirements", []) or [])
    ).lower()

    # +3 pricing / risk math keywords
    math_keywords = [
        "pricing", "stochastic", "pde",
        "monte carlo", "calibration",
        "greeks", "var", "stress", "xva"
    ]
    if any(k in text_blob for k in math_keywords):
        score += 3

    # tools
    tools = job_json.get("tools", []) or []
    if "Python" in tools:
        score += 2
    if "SQL" in tools:
        score += 1
    if "VBA" in tools:
        score += 1
    if "C++" in tools:
        score += 1

    # ML
    if "machine learning" in text_blob or "deep learning" in text_blob:
        score += 2

    # production code
    prod_keywords = ["git", "ci", "tests", "pipeline", "refactor", "performance"]
    if any(k in text_blob for k in prod_keywords):
        score += 2

    # reporting penalty
    if job_json.get("reporting_heavy"):
        score -= 3

    return clamp(score)


def compute_red_flags(job_json: Dict) -> list:
    flags = []

    if job_json.get("reporting_heavy"):
        flags.append("REPORTING")

    if job_json.get("quant_research_phd_mandatory"):
        flags.append("PHD_ONLY")

    if job_json.get("cxx_hardcore"):
        flags.append("CXX_HARDCORE")

    if job_json.get("role_type") in {"CONTROL", "BACK_OFFICE"}:
        flags.append("LOW_FO_PROXIMITY")

    return flags


def compute_signals(job_json: Dict) -> list:
    signals = []

    if job_json.get("role_type") in {"FRONT_OFFICE", "FRONT_SUPPORT"}:
        signals.append("FRONT_OFFICE_PROXIMITY")

    if job_json.get("derivatives_pricing"):
        signals.append("DERIVATIVES_PRICING_CORE")

    if job_json.get("model_validation"):
        signals.append("MODEL_VALIDATION_CORE")

    if job_json.get("market_risk"):
        signals.append("MARKET_RISK_ANALYTICS")

    if job_json.get("counterparty_risk"):
        signals.append("COUNTERPARTY_RISK_ANALYTICS")

    if job_json.get("energy_derivatives"):
        signals.append("ENERGY_COMMODITIES_EXPOSURE")

    # conserve ce signal si présent (ex: venant d'extract)
    if "EXECUTION_ALGO_EXPOSURE" in (job_json.get("signals_for_fit") or []):
        signals.append("EXECUTION_ALGO_EXPOSURE")

    # dédup
    return list(set(signals))


def normalize_job(job_json: Dict) -> Dict:
    """
    Normalisation conservatrice :
    - ne détruit pas les signaux/flags détectés à l'extract
    - ne baisse jamais quant_intensity
    """

    incoming_signals = set(job_json.get("signals_for_fit") or [])
    incoming_flags = set(job_json.get("red_flags") or [])
    incoming_qi = job_json.get("quant_intensity") or 0

    recomputed_qi = recompute_quant_intensity(job_json)
    job_json["quant_intensity"] = max(incoming_qi, recomputed_qi)

    computed_flags = set(compute_red_flags(job_json))
    job_json["red_flags"] = sorted(incoming_flags.union(computed_flags))

    computed_signals = set(compute_signals(job_json))
    job_json["signals_for_fit"] = sorted(incoming_signals.union(computed_signals))

    return job_json