# tests/test_gate.py
from core.gate import evaluate_gate  # ajuste si ton import diffère


def base_job():
    # job "safe" qui ne doit PAS être bloqué
    return {
        "reporting_heavy": False,
        "quant_research_phd_mandatory": False,
        "cxx_hardcore": False,
        "role_family": "MARKET_RISK",
        "red_flags": [],
    }


def assert_block(job, expected_reason):
    out = evaluate_gate(job)
    assert out["is_blocked"] is True
    assert out["reason"] == expected_reason


def assert_allow(job):
    out = evaluate_gate(job)
    assert out["is_blocked"] is False
    assert out["reason"] is None


def test_gate_allows_safe_job():
    assert_allow(base_job())


def test_gate_blocks_reporting_heavy():
    job = base_job()
    job["reporting_heavy"] = True
    assert_block(job, "REPORTING_HEAVY")


def test_gate_blocks_phd_mandatory():
    job = base_job()
    job["quant_research_phd_mandatory"] = True
    assert_block(job, "PHD_MANDATORY")


def test_gate_blocks_cxx_hardcore():
    job = base_job()
    job["cxx_hardcore"] = True
    assert_block(job, "CXX_HARDCORE")


def test_gate_blocks_role_family_xva():
    job = base_job()
    job["role_family"] = "XVA"
    assert_block(job, "LOW_VALUE_ADD_ROLE")


def test_gate_blocks_role_family_counterparty_risk():
    job = base_job()
    job["role_family"] = "COUNTERPARTY_RISK"
    assert_block(job, "LOW_VALUE_ADD_ROLE")


def test_gate_blocks_low_fo_proximity_red_flag():
    job = base_job()
    job["red_flags"] = ["LOW_FO_PROXIMITY"]
    assert_block(job, "LOW_VALUE_ADD_ROLE")


def test_gate_precedence_reporting_over_others():
    # vérifie l'ordre (REPORTING_HEAVY doit gagner)
    job = base_job()
    job["reporting_heavy"] = True
    job["quant_research_phd_mandatory"] = True
    job["cxx_hardcore"] = True
    job["role_family"] = "XVA"
    job["red_flags"] = ["LOW_FO_PROXIMITY"]
    assert_block(job, "REPORTING_HEAVY")
