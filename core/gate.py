from typing import Dict


HARD_GATE_ORDER = [
    "REPORTING_HEAVY",
    "PHD_MANDATORY",
    "CXX_HARDCORE",
    "LOW_VALUE_ADD_ROLE"
]


def evaluate_gate(job_json: Dict) -> Dict:

    if job_json.get("reporting_heavy") is True:
        return {
            "is_blocked": True,
            "reason": "REPORTING_HEAVY"
        }

    if job_json.get("quant_research_phd_mandatory") is True:
        return {
            "is_blocked": True,
            "reason": "PHD_MANDATORY"
        }

    if job_json.get("cxx_hardcore") is True:
        return {
            "is_blocked": True,
            "reason": "CXX_HARDCORE"
        }

    if job_json.get("role_family") in ("XVA", "COUNTERPARTY_RISK"):
        return {
            "is_blocked": True,
            "reason": "LOW_VALUE_ADD_ROLE"
        }

    if "LOW_FO_PROXIMITY" in job_json.get("red_flags", []):
        return {
            "is_blocked": True,
            "reason": "LOW_VALUE_ADD_ROLE"
        }

    return {
        "is_blocked": False,
        "reason": None
    }
