from typing import Dict


TEMPLATE_MAPPING = {
    "MODEL_VALIDATION": "cv_model_validation.tex",
    "MARKET_RISK": "cv_market_risk.tex",
    "ENERGY": "cv_energy_trading.tex",
    "TRADING": "cv_trading.tex",
    "STRUCTURING": "cv_structuring.tex",
    "PNL_VALUATION": "cv_pnl_valuation.tex",
    "DATA_EXECUTION": "cv_data_execution.tex",
}


def map_template(job_json: Dict) -> Dict:
    role_family = job_json.get("role_family")
    signals = job_json.get("signals_for_fit") or []

    # 1️⃣ Model validation prioritaire
    if "MODEL_VALIDATION_CORE" in signals:
        return {
            "template_key": "MODEL_VALIDATION",
            "template_file": TEMPLATE_MAPPING["MODEL_VALIDATION"],
        }

    # 2️⃣ Energy trading
    if job_json.get("energy_derivatives"):
        return {
            "template_key": "ENERGY",
            "template_file": TEMPLATE_MAPPING["ENERGY"],
        }

    # 3️⃣ Structuring
    if role_family == "STRUCTURING":
        return {
            "template_key": "STRUCTURING",
            "template_file": TEMPLATE_MAPPING["STRUCTURING"],
        }

    # 4️⃣ Derivatives pricing
    if job_json.get("derivatives_pricing"):
        return {
            "template_key": "MODEL_VALIDATION",
            "template_file": TEMPLATE_MAPPING["MODEL_VALIDATION"],
        }

    # 5️⃣ Market risk
    if job_json.get("market_risk"):
        return {
            "template_key": "MARKET_RISK",
            "template_file": TEMPLATE_MAPPING["MARKET_RISK"],
        }

    # 6️⃣ Trading / execution
    if (
        role_family in ("TRADING", "FO_TOOLS")
        or "EXECUTION_ALGO_EXPOSURE" in signals
    ):
        return {
            "template_key": "TRADING",
            "template_file": TEMPLATE_MAPPING["TRADING"],
        }

    # 7️⃣ Data science
    if role_family == "DATA_SCIENCE":
        return {
            "template_key": "DATA_EXECUTION",
            "template_file": TEMPLATE_MAPPING["DATA_EXECUTION"],
        }

    # Fallback
    return {
        "template_key": "DATA_EXECUTION",
        "template_file": TEMPLATE_MAPPING["DATA_EXECUTION"],
    }