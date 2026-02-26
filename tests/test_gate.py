# tests/test_gate.py
import copy
import pytest

from core.gate import gate  # ajuste si ton import diffère

def base_job():
    # job "safe" qui ne doit PAS être bloqué
    return {
        "company": "X",
        "role_title": "Quant Analyst",
        "role_family": "MARKET_RISK",
        "role_type": "FRONT_SUPPORT",
        "seniority": "JUNIOR",
        "location": "Paris",
        "remote_policy": None,
        "contract_type": "PERMANENT",
        "business_domain": [],
        "asset_classes": [],
        "key_missions": [],
        "key_requirements": [],
        "model_validation": False,
        "market_risk": True,
        "counterparty_risk": False,
        "derivatives_pricing": False,
        "energy_derivatives": False,
        "quant_research_phd_mandatory": False,
        "cxx_hardcore": False,
        "reporting_heavy": False,
        "quant_intensity": 0,
        "tools": [],
        "red_flags": [],
        "signals_for_fit": [],
    }

def run_gate(job):
    # On s'adapte aux 2 styles fréquents:
    # - gate(job) -> dict
    # - gate(job) -> (allowed:bool, tags:list, reason:str, ...)
    out = gate(job)
    if isinstance(out, tuple):
        # (allowed, tags, reason, ...) ou similaire
        return out
    if isinstance(out, dict):
        # ex: {"allowed": bool, "tags": [...], "reason": "..."}
        return (out.get("allowed"), out.get("tags", []), out.get("reason"))
    raise TypeError(f"Unexpected gate() output type: {type(out)}")

def assert_block(job, expected_tag):
    allowed, tags, _ = run_gate(job)
    assert allowed is False
    assert expected_tag in (tags or [])

def assert_allow(job):
    allowed, tags, _ = run_gate(job)
    assert allowed is True
    assert (tags or []) == [] or all(t is None for t in (tags or []))

def test_gate_allows_safe_job():
    assert_allow(base_job())

@pytest.mark.parametrize(
    "mutator,expected_tag",
    [
        (lambda j: j.__setitem__("reporting_heavy", True), "REPORTING"),
        (lambda j: j.__setitem__("quant_research_phd_mandatory", True), "PHD_ONLY"),
        (lambda j: j.__setitem__("cxx_hardcore", True), "CXX_HARDCORE"),

        # si ton gate bloque XVA / counterparty / low fo
        (lambda j: j.__setitem__("role_family", "XVA"), "LOW_FO_PROXIMITY"),  # adapte tag si différent
        (lambda j: j.__setitem__("counterparty_risk", True), "LOW_FO_PROXIMITY"),  # idem
        (lambda j: j.__setitem__("role_type", "CONTROL"), "LOW_FO_PROXIMITY"),
    ],
)
def test_gate_blocks_expected(mutator, expected_tag):
    job = base_job()
    mutator(job)
    assert_block(job, expected_tag)

def test_gate_does_not_block_when_cxx_is_just_a_plus():
    # sécurité: si cxx_hardcore False, gate ne doit pas bloquer
    job = base_job()
    job["tools"] = ["Python", "C++"]  # mention faible
    job["cxx_hardcore"] = False
    assert_allow(job)

def test_gate_does_not_block_when_phd_is_preferred_not_mandatory():
    job = base_job()
    job["quant_research_phd_mandatory"] = False
    job["key_requirements"] = ["PhD preferred"]  # texte, mais booléen off
    assert_allow(job)
