from typing import Dict

def map_template(job_json: Dict) -> Dict:
    role_family = job_json.get("role_family")

    # 0️⃣ Hard ignore families (tu veux les sortir du scope)
    if role_family in ("XVA", "COUNTERPARTY_RISK"):
        return {
            "template_key": "DATA_EXECUTION",
            "template_file": TEMPLATE_MAPPING["DATA_EXECUTION"],
        }
        # (et surtout: ton GATE devrait déjà les rejeter, voir plus bas)

    # 1️⃣ Model Validation (inclut PRICING selon ta règle)
    if job_json.get("model_validation") or role_family == "MODEL_RISK" or role_family == "PRICING":
        return {
            "template_key": "MODEL_VALIDATION",
            "template_file": TEMPLATE_MAPPING["MODEL_VALIDATION"],
        }

    # 2️⃣ Energy (je laisserais ici, ok)
    if job_json.get("energy_derivatives"):
        return {
            "template_key": "ENERGY",
            "template_file": TEMPLATE_MAPPING["ENERGY"],
        }

    # 3️⃣ Market Risk
    if job_json.get("market_risk") or role_family == "MARKET_RISK":
        return {
            "template_key": "MARKET_RISK",
            "template_file": TEMPLATE_MAPPING["MARKET_RISK"],
        }

    # 4️⃣ Trading (inclut FO_TOOLS)
    if role_family in ("TRADING", "FO_TOOLS"):
        return {
            "template_key": "TRADING",
            "template_file": TEMPLATE_MAPPING["TRADING"],
        }

    # 5️⃣ Structuring
    if role_family == "STRUCTURING":
        return {
            "template_key": "STRUCTURING",
            "template_file": TEMPLATE_MAPPING["STRUCTURING"],
        }

    # 6️⃣ PnL Valuation
    if role_family == "P&L_VALUATION":
        return {
            "template_key": "PNL_VALUATION",
            "template_file": TEMPLATE_MAPPING["PNL_VALUATION"],
        }

    # 7️⃣ Data Science
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
