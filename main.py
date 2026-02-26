from core.gate import evaluate_gate
from core.score import compute_score
from core.template_mapper import map_template
from core.language_strategy import determine_languages
from core.application_mode import detect_application_mode
from core.patch_latex_cv import patch_latex_cv
from core.latex_compiler import compile_latex

from pathlib import Path


# ==============================
# MOCK JOB (pour test local)
# ==============================

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
        "Build decision-support tools for traders"
    ],
    "key_requirements": [
        "Strong Python skills",
        "Machine learning knowledge",
        "English required"
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
        "EXECUTION_ALGO_EXPOSURE"
    ]
}


def main():

    print("=== QJOE PIPELINE START ===")

    # 1️⃣ Gate
    gate_result = evaluate_gate(job_json)

    if gate_result["is_blocked"]:
        print(f"❌ Blocked by gate: {gate_result['reason']}")
        return

    print("✅ Gate passed")

    # 2️⃣ Score
    score_result = compute_score(job_json)
    print(f"Score: {score_result['score_0_100']}")
    print(f"Decision: {score_result['decision']}")

    if score_result["decision"] == "RED":
        print("❌ Not proceeding (score too low)")
        return

    # 3️⃣ Template mapping
    template_result = map_template(job_json)
    template_path = Path("templates") / template_result["template_file"]

    print(f"Using template: {template_result['template_file']}")

    # 4️⃣ Language strategy
    language_config = determine_languages(job_json)
    print(f"CV language: {language_config['cv_language']}")
    print(f"Written language: {language_config['written_language']}")

    # 5️⃣ Application mode
    mode_result = detect_application_mode(job_json)
    print(f"Application mode: {mode_result['mode']}")

    # 6️⃣ Patch CV title (mock content for now)
    generated_content = {
        "cv_title": f"{job_json['role_title']} – {job_json['company']}"
    }

    output_tex_path = Path("generated_cv.tex")

    patch_latex_cv(
        template_path=str(template_path),
        output_path=str(output_tex_path),
        generated_content=generated_content
    )

    print("CV .tex generated")

    # 7️⃣ Compile
    compile_result = compile_latex(str(output_tex_path))

    if compile_result["success"]:
        print(f"✅ PDF generated: {compile_result['pdf_path']}")
    else:
        print("❌ Compilation failed")
        print(compile_result["error"])


if __name__ == "__main__":
    main()
