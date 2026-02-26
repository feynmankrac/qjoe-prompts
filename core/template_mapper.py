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

    if role_family in ("XVA", "COUNTERPARTY_RISK"):
        return {
            "template_key": "DATA_EXECUTION",
            "template_file": TEMPLATE_MAPPING["DATA_EXECUTION"],
        }

    if job_json.get("model_validation") or role_family in ("MODEL_RISK", "PRICING"):
        return {
            "template_key": "MODEL_VALIDATION",
            "template_file": TEMPLATE_MAPPING["MODEL_VALIDATION"],
        }

    if job_json.get("energy_derivatives"):
        return {
            "template_key": "ENERGY",
            "template_file": TEMPLATE_MAPPING["ENERGY"],
        }

    if job_json.get("market_risk") or role_family == "MARKET_RISK":
        return {
            "template_key": "MARKET_RISK",
            "template_file": TEMPLATE_MAPPING["MARKET_RISK"],
        }

    if role_family in ("TRADING", "FO_TOOLS"):
        return {
            "template_key": "TRADING",
            "template_file": TEMPLATE_MAPPING["TRADING"],
        }

    if role_family == "STRUCTURING":
        return {
            "template_key": "STRUCTURING",
            "template_file": TEMPLATE_MAPPING["STRUCTURING"],
        }

    if role_family == "P&L_VALUATION":
        return {
            "template_key": "PNL_VALUATION",
            "template_file": TEMPLATE_MAPPING["PNL_VALUATION"],
        }

    if role_family == "DATA_SCIENCE":
        return {
            "template_key": "DATA_EXECUTION",
            "template_file": TEMPLATE_MAPPING["DATA_EXECUTION"],
        }

    return {
        "template_key": "DATA_EXECUTION",
        "template_file": TEMPLATE_MAPPING["DATA_EXECUTION"],
    }
