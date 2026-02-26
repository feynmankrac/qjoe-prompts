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
    """
    Deterministic template selection.
    Returns:
      {
        "template_key": <one of TEMPLATE_MAPPING keys>,
        "template_file": <filename>
      }
    """

    role_family = job_json.get("role_family")

    def _ret(key: str) -> Dict:
        return {"template_key": key, "template_file": TEMPLATE_MAPPING[key]}

    # 1) Model Validation (highest priority)
    if job_json.get("model_validation") or role_family == "MODEL_RISK":
        return _ret("MODEL_VALIDATION")

    # 2) Energy (prioritize FO energy desk exposure whenever explicitly present)
    if job_json.get("energy_derivatives"):
        return _ret("ENERGY")

    # 3) Market Risk
    if job_json.get("market_risk") or role_family == "MARKET_RISK":
        return _ret("MARKET_RISK")

    # 4) Counterparty risk -> route to validation by default (more aligned with your templates)
    if job_json.get("counterparty_risk") or role_family == "COUNTERPARTY_RISK":
        return _ret("MODEL_VALIDATION")

    # 5) Trading desks
    if role_family == "TRADING":
        return _ret("TRADING")

    # 6) Structuring
    if role_family == "STRUCTURING":
        return _ret("STRUCTURING")

    # 7) PnL Valuation
    if role_family == "P&L_VALUATION":
        return _ret("PNL_VALUATION")

    # 8) Pricing / XVA (no dedicated template -> redirect deterministically)
    if role_family in ("PRICING", "XVA"):
        # Choose TRADING as a neutral FO-leaning template if pricing/xva template is removed
        return _ret("TRADING")

    # 9) FO tools / Data science -> data/execution template
    if role_family in ("FO_TOOLS", "DATA_SCIENCE"):
        return _ret("DATA_EXECUTION")

    # 10) Control/back-office-ish families (ideally gated out; still safe fallback)
    if role_family in ("PRODUCT_CONTROL", "ALM", "COMPLIANCE", "OPERATIONS", "UNKNOWN"):
        return _ret("DATA_EXECUTION")

    # 11) Final fallback
    return _ret("DATA_EXECUTION")
