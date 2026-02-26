from typing import Dict


TEMPLATE_MAPPING = {
    "MODEL_VALIDATION": "cv_model_validation.tex",
    "MARKET_RISK": "cv_market_risk.tex",
    "PRICING_XVA": "cv_pricing_xva.tex",
    "ENERGY": "cv_energy_trading.tex",
    "TRADING": "cv_trading.tex",
    "STRUCTURING": "cv_structuring.tex",
    "PNL_VALUATION": "cv_pnl_valuation.tex",
    "FO_SUPPORT": "cv_fo_support.tex",
    "DATA_EXECUTION": "cv_data_execution.tex",
}


def map_template(job_json: Dict) -> Dict:

    role_family = job_json.get("role_family")

    # 1️⃣ Model Validation
    if job_json.get("model_validation") or role_family == "MODEL_RISK":
        return {
            "template_key": "MODEL_VALIDATION",
            "template_file": TEMPLATE_MAPPING["MODEL_VALIDATION"],
        }

    # 2️⃣ Market Risk
    if job_json.get("market_risk") or role_family == "MARKET_RISK":
        return {
            "template_key": "MARKET_RISK",
            "template_file": TEMPLATE_MAPPING["MARKET_RISK"],
        }

    # 3️⃣ Pricing / XVA
    if (
        job_json.get("derivatives_pricing")
        or role_family in {"PRICING", "XVA"}
    ):
        return {
            "template_key": "PRICING_XVA",
            "template_file": TEMPLATE_MAPPING["PRICING_XVA"],
        }

    # 4️⃣ Energy
    if job_json.get("energy_derivatives"):
        return {
            "template_key": "ENERGY",
            "template_file": TEMPLATE_MAPPING["ENERGY"],
        }

    # 5️⃣ Trading desks
    if role_family == "TRADING":
        return {
            "template_key": "TRADING",
            "template_file": TEMPLATE_MAPPING["TRADING"],
        }

    # 6️⃣ Structuring
    if role_family == "STRUCTURING":
        return {
            "template_key": "STRUCTURING",
            "template_file": TEMPLATE_MAPPING["STRUCTURING"],
        }

    # 7️⃣ PnL Valuation
    if role_family == "P&L_VALUATION":
        return {
            "template_key": "PNL_VALUATION",
            "template_file": TEMPLATE_MAPPING["PNL_VALUATION"],
        }

    # 8️⃣ Trader Assistant / FO tools
    if role_family == "FO_TOOLS":
        return {
            "template_key": "FO_SUPPORT",
            "template_file": TEMPLATE_MAPPING["FO_SUPPORT"],
        }

    # 9️⃣ Data Science / Execution
    if role_family == "DATA_SCIENCE":
        return {
            "template_key": "DATA_EXECUTION",
            "template_file": TEMPLATE_MAPPING["DATA_EXECUTION"],
        }

    # 🔟 Final fallback
    return {
        "template_key": "DATA_EXECUTION",
        "template_file": TEMPLATE_MAPPING["DATA_EXECUTION"],
    }
