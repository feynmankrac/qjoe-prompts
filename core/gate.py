from typing import Dict


HARD_GATE_ORDER = [
    "REPORTING_HEAVY",
    "PHD_MANDATORY",
    "CXX_HARDCORE",
    "LOW_VALUE_ADD_ROLE"
]


def evaluate_gate(job_json: Dict) -> Dict:
    """
    Evaluate hard blocking conditions.

    Returns:
    {
        "is_blocked": bool,
        "reason": str | None
    }
    """

    # 1️⃣ Reporting heavy
    if job_json.get("reporting_heavy") is True:
        return {
            "is_blocked": True,
            "reason": "REPORTING_HEAVY"
        }

    # 2️⃣ PhD mandatory
    if job_json.get("quant_research_phd_mandatory") is True:
        return {
            "is_blocked": True,
            "reason": "PHD_MANDATORY"
        }

    # 3️⃣ Hardcore C++
    if job_json.get("cxx_hardcore") is True:
        return {
            "is_blocked": True,
            "reason": "CXX_HARDCORE"
        }

    # 4️⃣ Low value-add role (computed in NORMALIZE via red_flags)
    if "LOW_FO_PROXIMITY" in job_json.get("red_flags", []):
        return {
            "is_blocked": True,
            "reason": "LOW_VALUE_ADD_ROLE"
        }

    # ✅ No block
    return {
        "is_blocked": False,
        "reason": None
    }
