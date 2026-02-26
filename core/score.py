from typing import Dict


def compute_score(job_json: Dict) -> Dict:
    """
    Compute weighted score for a normalized job_json.

    Assumes gate.py has already been executed.
    """

    score = 0
    contributions = []

    # ==========================
    # Positive contributions
    # ==========================

    if job_json.get("model_validation"):
        score += 25
        contributions.append(("Model validation core", 25))

    if job_json.get("market_risk"):
        score += 20
        contributions.append(("Market risk analytics (VaR/stress)", 20))

    if job_json.get("counterparty_risk"):
        score += 15
        contributions.append(("Counterparty risk analytics", 15))

    if job_json.get("derivatives_pricing"):
        score += 20
        contributions.append(("Derivatives pricing exposure", 20))

    if job_json.get("energy_derivatives"):
        score += 15
        contributions.append(("Energy/commodities derivatives exposure", 15))

    if job_json.get("role_type") in {"FRONT_OFFICE", "FRONT_SUPPORT"}:
        score += 10
        contributions.append(("Front office proximity", 10))

    if "BUILDING_INTERNAL_TOOLS" in job_json.get("signals_for_fit", []):
        score += 10
        contributions.append(("Building internal tools", 10))

    if "PRODUCTION_CODE_EXPECTED" in job_json.get("signals_for_fit", []):
        score += 10
        contributions.append(("Production code expected", 10))

    quant_intensity = job_json.get("quant_intensity", 0)

    if quant_intensity >= 7:
        score += 5
        contributions.append(("High quant intensity", 5))
    elif quant_intensity in {5, 6}:
        score += 3
        contributions.append(("Moderate quant intensity", 3))

    # FX Execution strategic bonus
    if (
        job_json.get("role_family") == "DATA_SCIENCE"
        and "FX" in job_json.get("asset_classes", [])
        and "EXECUTION_ALGO_EXPOSURE" in job_json.get("signals_for_fit", [])
    ):
        score += 30
        contributions.append(
            ("DATA_SCIENCE+FX+EXECUTION_ALGO_EXPOSURE bonus", 30)
        )

    # ==========================
    # Negative contributions
    # ==========================

    if "COMPLIANCE_HEAVY" in job_json.get("red_flags", []):
        score -= 15

    if "OPS_HEAVY" in job_json.get("red_flags", []):
        score -= 10

    if "LOW_FO_PROXIMITY" in job_json.get("red_flags", []):
        score -= 10

    # Clamp score
    score = max(0, min(100, score))

    # ==========================
    # Decision logic
    # ==========================

    if score >= 70:
        decision = "GREEN"
        main_risk = None
    elif 50 <= score <= 69:
        decision = "BORDERLINE"
        main_risk = "BORDERLINE_SCORE"
    else:
        decision = "RED"
        main_risk = "LOW_SCORE"

    # Sort contributions by weight descending
    contributions.sort(key=lambda x: x[1], reverse=True)
    top_reasons = [c[0] for c in contributions[:2]]

    return {
        "score_0_100": score,
        "decision": decision,
        "top_reasons": top_reasons,
        "main_risk": main_risk,
    }
