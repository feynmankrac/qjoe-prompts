from core.gate import evaluate_gate
from core.score import compute_score
from core.template_mapper import map_template


def test_e2e_fx_data_science_borderline():
    job_json = {
        "company": "Test Bank",
        "role_title": "FX Data Scientist",
        "role_family": "DATA_SCIENCE",
        "role_type": "FRONT_SUPPORT",
        "seniority": "JUNIOR",
        "location": "Paris",
        "remote_policy": None,
        "contract_type": "PERMANENT",
        "business_domain": ["FX", "Execution Algorithms"],
        "asset_classes": ["FX"],
        "key_missions": [
            "Develop execution algorithms for FX desk",
            "Build decision-support tools for traders",
        ],
        "key_requirements": [
            "Strong Python skills",
            "Machine learning knowledge",
            "English required",
        ],
        "model_validation": False,
        "market_risk": False,
        "counterparty_risk": False,
        "derivatives_pricing": False,
        "energy_derivatives": False,
        "quant_research_phd_mandatory": False,
        "cxx_hardcore": False,
        "reporting_heavy": False,
        "quant_intensity": 7,
        "tools": ["Python"],
        "red_flags": [],
        "signals_for_fit": [
            "FRONT_OFFICE_PROXIMITY",
            "BUILDING_INTERNAL_TOOLS",
            "EXECUTION_ALGO_EXPOSURE",
        ],
    }

    # 1️⃣ Gate
    gate_result = evaluate_gate(job_json)
    assert gate_result["is_blocked"] is False

    # 2️⃣ Score
    score_result = compute_score(job_json)

    assert score_result["score_0_100"] == 55
    assert score_result["decision"] == "BORDERLINE"
    assert score_result["main_risk"] == "BORDERLINE_SCORE"

    assert "Front office proximity" in score_result.get("top_reasons", [])
    assert any("EXECUTION_ALGO_EXPOSURE" in r for r in score_result.get("top_reasons", []))

    # 3️⃣ Template mapping
    template_result = map_template(job_json)
    assert template_result["template_file"] == "cv_data_execution.tex"


def test_e2e_green_model_validation():
    job_json = {
        "company": "Test Bank",
        "role_title": "Traded Risk Model Validation (Pricing & Risk)",
        "role_family": "MODEL_RISK",
        "role_type": "FRONT_SUPPORT",
        "seniority": "ASSOCIATE",
        "location": "Paris",
        "remote_policy": None,
        "contract_type": "PERMANENT",
        "business_domain": ["Model Risk", "Validation"],
        "asset_classes": ["FX"],
        "key_missions": [
            "Independently validate pricing and risk models",
            "Build benchmark models and perform independent testing",
        ],
        "key_requirements": [
            "Strong Python skills",
            "Quantitative background",
            "English required",
        ],
        "model_validation": True,
        "market_risk": True,
        "counterparty_risk": False,
        "derivatives_pricing": True,
        "energy_derivatives": False,
        "quant_research_phd_mandatory": False,
        "cxx_hardcore": False,
        "reporting_heavy": False,
        "quant_intensity": 9,
        "tools": ["Python"],
        "red_flags": [],
        "signals_for_fit": [
            "MODEL_VALIDATION_CORE",
            "MARKET_RISK_ANALYTICS",
            "DERIVATIVES_PRICING_CORE",
            "FRONT_OFFICE_PROXIMITY",
            "PRODUCTION_CODE_EXPECTED",
        ],
    }

    gate_result = evaluate_gate(job_json)
    assert gate_result["is_blocked"] is False

    score_result = compute_score(job_json)
    assert score_result["decision"] == "GREEN"
    assert score_result["score_0_100"] >= 70

    template_result = map_template(job_json)
    assert "template_file" in template_result
    assert template_result["template_file"] is not None


def test_e2e_red_blocked_reporting_heavy():
    job_json = {
        "company": "Test Bank",
        "role_title": "Risk Reporting Analyst",
        "role_family": "MARKET_RISK",
        "role_type": "MIDDLE_OFFICE",
        "seniority": "JUNIOR",
        "location": "Paris",
        "remote_policy": None,
        "contract_type": "PERMANENT",
        "business_domain": ["Risk", "Reporting"],
        "asset_classes": [],
        "key_missions": [
            "Produce daily/weekly risk reports and KPIs",
            "Maintain dashboards for management committees",
        ],
        "key_requirements": [
            "Excel and PowerPoint",
            "Attention to detail",
        ],
        "model_validation": False,
        "market_risk": True,
        "counterparty_risk": False,
        "derivatives_pricing": False,
        "energy_derivatives": False,
        "quant_research_phd_mandatory": False,
        "cxx_hardcore": False,
        "reporting_heavy": True,
        "quant_intensity": 2,
        "tools": ["Excel"],
        "red_flags": ["REPORTING"],
        "signals_for_fit": [],
    }

    gate_result = evaluate_gate(job_json)
    assert gate_result["is_blocked"] is True
    assert "REPORT" in gate_result.get("reason", "").upper() or "REPORTING" in gate_result.get("reason", "").upper()