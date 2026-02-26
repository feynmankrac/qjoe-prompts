from core.normalize import normalize_job
from core.gate import evaluate_gate
from core.score import compute_score
from core.template_mapper import map_template
from core.patch_latex_cv import patch_latex_cv
from core.latex_compiler import compile_latex


job_json = {
    "role_family": "MARKET_RISK",
    "role_type": "FRONT_SUPPORT",
    "model_validation": False,
    "market_risk": True,
    "counterparty_risk": False,
    "derivatives_pricing": False,
    "energy_derivatives": False,
    "quant_research_phd_mandatory": False,
    "cxx_hardcore": False,
    "reporting_heavy": False,
    "quant_intensity": 7,
    "signals_for_fit": ["BUILDING_INTERNAL_TOOLS"],
    "red_flags": [],
    "asset_classes": []
}

gate_result = evaluate_gate(job_json)
print("Gate:", gate_result)

if not gate_result["is_blocked"]:
    score_result = compute_score(job_json)
    print("Score:", score_result)

    template_result = map_template(job_json)
    print("Template:", template_result)

    patch_latex_cv(
        template_path=f"templates/{template_result['template_file']}",
        output_path="generated_cv.tex",
        generated_content={
            "cv_title": "Quantitative Market Risk Analyst"
        }
    )

    compile_result = compile_latex("generated_cv.tex")
    print("Compile:", compile_result)
