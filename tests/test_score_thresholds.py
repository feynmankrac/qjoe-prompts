from core.score import compute_score  # ajuste si ton import diffère


def base_job():
    return {
        "model_validation": False,
        "market_risk": False,
        "counterparty_risk": False,
        "derivatives_pricing": False,
        "energy_derivatives": False,
        "role_family": "UNKNOWN",
        "role_type": "UNKNOWN",
        "reporting_heavy": False,
        "quant_research_phd_mandatory": False,
        "cxx_hardcore": False,
        "business_domain": [],
        "asset_classes": [],
        "key_missions": [],
        "key_requirements": [],
        "tools": [],
        "signals_for_fit": [],
        "red_flags": [],
        "quant_intensity": 0,
    }


def get_score_and_decision(job):
    out = compute_score(job)
    print("DEBUG OUTPUT:", out)
    return out.get("score_0_100"), out.get("decision"), out


def test_score_bounds_and_decision_keys_exist():
    s, d, out = get_score_and_decision(base_job())
    assert isinstance(s, (int, float))
    assert 0 <= s <= 100
    assert d in ("GREEN", "BORDERLINE", "RED")


def test_threshold_green_at_70_or_more():
    job = base_job()
    job["model_validation"] = True        # +25
    job["derivatives_pricing"] = True     # +20 (ou via role_family)
    job["role_type"] = "FRONT_OFFICE"     # +10
    job["signals_for_fit"] = ["PRODUCTION_CODE_EXPECTED"]  # +10
    # total attendu >= 65, on complète avec market_risk pour viser >=70
    job["market_risk"] = True             # +20
    s, d, _ = get_score_and_decision(job)
    assert s >= 70
    assert d == "GREEN"


def test_threshold_borderline_between_50_and_69():
    job = base_job()
    job["model_validation"] = True        # +25
    job["role_type"] = "FRONT_SUPPORT"    # +10
    job["signals_for_fit"] = ["PRODUCTION_CODE_EXPECTED"]  # +10
    # total ~45; on ajoute derivatives_pricing pour passer >=50
    job["derivatives_pricing"] = True     # +20  => ~65
    s, d, _ = get_score_and_decision(job)
    assert 50 <= s <= 69
    assert d == "BORDERLINE"


def test_threshold_red_below_50():
    job = base_job()
    job["role_type"] = "FRONT_SUPPORT"    # +10
    job["signals_for_fit"] = []           # 0
    job["market_risk"] = True             # +20 => 30
    s, d, _ = get_score_and_decision(job)
    assert s < 50
    assert d == "RED"


def test_penalty_reporting_heavy_drags_down():
    job = base_job()
    job["model_validation"] = True        # +25
    job["market_risk"] = True             # +20 => 45
    job["role_type"] = "FRONT_SUPPORT"    # +10 => 55
    job["reporting_heavy"] = True         # -25 => 30
    s, d, _ = get_score_and_decision(job)
    assert s < 50
    assert d == "RED"
