from typing import Dict


def compute_score(job_json: Dict) -> Dict:
    score = 0
    contributions = []

    signals = job_json.get("signals_for_fit") or []
    red_flags = job_json.get("red_flags") or []
    role_family = job_json.get("role_family")
    role_type = job_json.get("role_type")
    quant_intensity = job_json.get("quant_intensity") or 0

    # ======================
    # 1️⃣ CORE STRATEGIC FIT
    # ======================

    if job_json.get("model_validation"):
        score += 20
        contributions.append(("Model validation core", 20))

    if job_json.get("market_risk"):
        score += 18
        contributions.append(("Market risk quant", 18))

    if job_json.get("derivatives_pricing"):
        score += 22
        contributions.append(("Derivatives pricing core", 22))

    if job_json.get("energy_derivatives"):
        score += 22
        contributions.append(("Energy trading quant", 22))

    if role_family == "STRUCTURING":
        score += 20
        contributions.append(("Structuring derivatives", 20))

    # ======================
    # 2️⃣ FO / DESK PROXIMITY
    # ======================

    if role_type == "FRONT_OFFICE":
        score += 15
        contributions.append(("Front office", 15))

    if role_type == "FRONT_SUPPORT":
        score += 12
        contributions.append(("Front support technical", 12))

    if "INTERACTION_WITH_TRADERS" in signals:
        score += 8
        contributions.append(("Interaction with traders", 8))

    if "BUILDING_INTERNAL_TOOLS" in signals:
        score += 8
        contributions.append(("Building internal tools", 8))

    if "PRODUCTION_CODE_EXPECTED" in signals:
        score += 10
        contributions.append(("Production code expected", 10))

    # ======================
    # 3️⃣ DATA / EXECUTION INTENSITY
    # ======================

    if "EXECUTION_ALGO_EXPOSURE" in signals:
        score += 15
        contributions.append(("Execution algo exposure", 15))

    if "FX_DATA_SCIENCE_CORE" in signals:
        score += 12
        contributions.append(("FX data science core", 12))

    if "ML_APPLIED_TO_MARKETS" in signals:
        score += 10
        contributions.append(("ML applied to markets", 10))

    if "TOOLING_PYTHON_CORE" in signals:
        score += 6
        contributions.append(("Python tooling core", 6))

    # ======================
    # 4️⃣ RISK ANALYTICS GRANULARITY
    # ======================

    if "MARKET_RISK_ANALYTICS" in signals:
        score += 10
        contributions.append(("Market risk analytics", 10))

    # ======================
    # 5️⃣ QUANT INTENSITY
    # ======================

    if quant_intensity >= 8:
        score += 8
        contributions.append(("Very high quant intensity", 8))
    elif quant_intensity in {6, 7}:
        score += 5
        contributions.append(("High quant intensity", 5))
    elif quant_intensity in {4, 5}:
        score += 2
        contributions.append(("Moderate quant intensity", 2))

    # ======================
    # 6️⃣ CONVEXITY BONUS
    # ======================

    if job_json.get("market_risk") and job_json.get("derivatives_pricing"):
        score += 10
        contributions.append(("Opens trading & risk", 10))

    if role_family in {"STRUCTURING", "PRICING"}:
        score += 10
        contributions.append(("Opens structuring & pricing", 10))

    if job_json.get("energy_derivatives") and "EXECUTION_ALGO_EXPOSURE" in signals:
        score += 12
        contributions.append(("Opens energy & algo", 12))

    # ======================
    # 🔻 PENALTIES
    # ======================

    if job_json.get("reporting_heavy"):
        score -= 30

    if "COMPLIANCE_HEAVY" in red_flags:
        score -= 20

    if "OPS_HEAVY" in red_flags:
        score -= 20

    if "MIDDLE_OFFICE_DISGUISED" in red_flags:
        score -= 25

    if "LOW_FO_PROXIMITY" in red_flags:
        score -= 15

    if "ELIGIBILITY_BLOCKER" in red_flags:
        score -= 20

    if "PURE_STAGE_NON_STRATEGIC" in red_flags:
        score -= 10

    # ======================
    # FINAL DECISION
    # ======================

    score = max(0, min(100, score))

    if score >= 75:
        decision = "GREEN"
        main_risk = None
    elif 55 <= score < 75:
        decision = "BORDERLINE"
        main_risk = "NEEDS_LLM_VALIDATE"
    else:
        decision = "RED"
        main_risk = "LOW_SCORE"

    contributions.sort(key=lambda x: x[1], reverse=True)
    top_reasons = [c[0] for c in contributions[:3]]

    return {
        "score_0_100": score,
        "decision": decision,
        "top_reasons": top_reasons,
        "main_risk": main_risk,
    }