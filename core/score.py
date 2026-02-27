from typing import Dict


def compute_score(job_json: Dict) -> Dict:
    score = 0
    contributions = []

    signals = job_json.get("signals_for_fit") or []
    red_flags = job_json.get("red_flags") or []
    asset_classes = job_json.get("asset_classes") or []

    role_family = job_json.get("role_family")
    role_type = job_json.get("role_type")

    # ======================
    # CORE TARGETS
    # ======================

    if job_json.get("model_validation"):
        score += 25
        contributions.append(("Model validation core", 25))

    if job_json.get("market_risk"):
        score += 20
        contributions.append(("Market risk analytics (VaR/stress)", 20))

    if job_json.get("derivatives_pricing") or role_family in {"PRICING", "XVA", "FO_TOOLS"}:
        score += 20
        contributions.append(("Derivatives pricing / FO tools exposure", 20))

    if job_json.get("energy_derivatives") or "ENERGY_COMMODITIES_EXPOSURE" in signals:
        score += 15
        contributions.append(("Energy/commodities exposure", 15))

    # ======================
    # FO PROXIMITY (SPEC)
    # ======================

    if job_json.get("role_type") in {"FRONT_OFFICE", "FRONT_SUPPORT"}:
        score += 10
        contributions.append(("Front office proximity", 10))

    # Production code bonus (signal-based)
    if "PRODUCTION_CODE_EXPECTED" in signals:
        score += 10
        contributions.append(("Production-quality code expected", 10))

    # ======================
    # QUANT INTENSITY BONUS
    # ======================

    quant_intensity = job_json.get("quant_intensity") or 0
    if quant_intensity >= 7:
        score += 5
        contributions.append(("High quant intensity", 5))
    elif quant_intensity in {5, 6}:
        score += 3
        contributions.append(("Moderate quant intensity", 3))

    # ======================
    # FX DATA SCIENCE TRADING BONUS (STRUCTURED ONLY)
    # ======================

    if (
        role_family == "DATA_SCIENCE"
        and "FX" in asset_classes
        and "FRONT_OFFICE_PROXIMITY" in signals
    ):
        score += 15
        contributions.append(("FX data science in trading environment", 15))

    if (
        role_family == "DATA_SCIENCE"
        and "FX" in asset_classes
        and "EXECUTION_ALGO_EXPOSURE" in signals
    ):
        score += 10
        contributions.append(("Execution algorithm exposure", 10))

    if (
        role_family == "DATA_SCIENCE"
        and "FX" in asset_classes
        and "FRONT_OFFICE_PROXIMITY" in signals
        and "EXECUTION_ALGO_EXPOSURE" in signals
        and "BUILDING_INTERNAL_TOOLS" in signals
    ):
        score += 20
        contributions.append(("Target profile: FX execution + FO + tooling", 20))

    # ======================
    # PENALTIES (SPEC)
    # ======================

    if job_json.get("reporting_heavy") is True or "REPORTING" in red_flags:
        score -= 25

    if "COMPLIANCE_HEAVY" in red_flags:
        score -= 15

    if "OPS_HEAVY" in red_flags:
        score -= 10

    if "LOW_FO_PROXIMITY" in red_flags:
        score -= 10

    if "ELIGIBILITY_BLOCKER" in red_flags:
        score -= 15

    # ======================
    # FINAL DECISION
    # ======================

    score = max(0, min(100, score))

    if score >= 70:
        decision = "GREEN"
        main_risk = None
    elif 50 <= score <= 69:
        decision = "BORDERLINE"
        main_risk = "BORDERLINE_SCORE"
    else:
        decision = "RED"
        main_risk = "LOW_SCORE"

    contributions.sort(key=lambda x: x[1], reverse=True)
    top_reasons = [c[0] for c in contributions[:2]]

    return {
        "score_0_100": score,
        "decision": decision,
        "top_reasons": top_reasons,
        "main_risk": main_risk,
    }