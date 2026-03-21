from typing import Optional
from core.gate import evaluate_gate
from core.score import compute_score
from core.template_mapper import map_template
from core.language_strategy import determine_languages
from core.application_mode import detect_application_mode
from core.patch_latex_cv import patch_latex_cv
from core.latex_compiler import compile_latex

from pathlib import Path
import json
from datetime import datetime


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


def _save_run_output(payload: dict, artifacts_dir: Path) -> Path:
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    out_path = artifacts_dir / "last_run.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return out_path



def _maybe_llm_validate(job_json: dict, score_result: dict) -> Optional[dict]:
    """
    Appelé uniquement si decision == BORDERLINE.
    Retour attendu:
      {
        "override_decision": "GREEN"|"RED",
        "reasons": [..],
        "main_risk": "..."
      }
    Si pas câblé, renvoie None et on garde la decision déterministe.
    """
    try:
        from core.llm_validate import llm_validate  # à créer (stub ok)
    except Exception as e:
        print(f"⚠️ LLM_VALIDATE not available (import error): {e}")
        return None

    try:
        res = llm_validate(job_json, score_result)
    except NotImplementedError as e:
        print(f"⚠️ LLM_VALIDATE not wired yet: {e}")
        return None
    except Exception as e:
        print(f"⚠️ LLM_VALIDATE failed, keeping deterministic decision: {e}")
        return None

    if not isinstance(res, dict):
        print("⚠️ LLM_VALIDATE returned non-dict, keeping deterministic decision")
        return None

    override = res.get("override_decision")
    if override not in {"GREEN", "RED"}:
        print("⚠️ LLM_VALIDATE missing/invalid override_decision, keeping deterministic decision")
        return None

    return res


def main():
    print("=== QJOE PIPELINE START ===")

    artifacts_dir = Path("artifacts")

    # 1️⃣ Gate
    gate_result = evaluate_gate(job_json)

    if gate_result.get("is_blocked"):
        print(f"❌ Blocked by gate: {gate_result.get('reason')}")
        run_output = {
            "run_meta": {"ts": datetime.utcnow().isoformat() + "Z"},
            "job_json": job_json,
            "gate": gate_result,
            "status": "BLOCKED",
        }
        out_path = _save_run_output(run_output, artifacts_dir)
        print(f"📁 Run output saved: {out_path}")
        return

    print("✅ Gate passed")

    # 2️⃣ Score
    score_result = compute_score(job_json)
    print(f"Score: {score_result.get('score_0_100')}")
    print(f"Decision: {score_result.get('decision')}")

    if "top_reasons" in score_result:
        print("Top reasons:")
        for r in score_result["top_reasons"]:
            print(f" - {r}")
    if "main_risk" in score_result:
        print(f"Main risk: {score_result['main_risk']}")

    # 2 Final decision (deterministic + optional LLM override on BORDERLINE)
    final_decision = score_result.get("decision")
    llm_validate_result = None

    if final_decision == "BORDERLINE":
        llm_validate_result = _maybe_llm_validate(job_json, score_result)
        if llm_validate_result is not None:
            final_decision = llm_validate_result["override_decision"]
            print(f"LLM override decision: {final_decision}")

    if final_decision == "RED":
        print("❌ Not proceeding (final decision RED)")
        run_output = {
            "run_meta": {"ts": datetime.utcnow().isoformat() + "Z"},
            "job_json": job_json,
            "gate": gate_result,
            "score": score_result,
            "llm_validate": llm_validate_result,
            "final_decision": final_decision,
            "status": "STOP_RED",
        }
        out_path = _save_run_output(run_output, artifacts_dir)
        print(f"📁 Run output saved: {out_path}")
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

    # 8️⃣ Persist run output (JSON)
    run_output = {
        "run_meta": {"ts": datetime.utcnow().isoformat() + "Z"},
        "job_json": job_json,
        "gate": gate_result,
        "score": score_result,
        "llm_validate": llm_validate_result,
        "final_decision": final_decision,
        "template": {
            "template_file": template_result.get("template_file"),
            "template_path": str(template_path),
        },
        "languages": language_config,
        "application_mode": mode_result,
        "artifacts": {
            "tex_path": str(output_tex_path),
            "pdf_path": compile_result.get("pdf_path"),
        },
        "compile": compile_result,
        "status": "DONE" if compile_result.get("success") else "COMPILE_FAILED",
    }

    out_path = _save_run_output(run_output, artifacts_dir)
    print(f"📁 Run output saved: {out_path}")

    if compile_result.get("success"):
        print(f"✅ PDF generated: {compile_result['pdf_path']}")
    else:
        print("❌ Compilation failed")
        print(compile_result.get("error"))


if __name__ == "__main__":
    main()

   

@app.post("/run_batch")
def run_batch():

    import subprocess

    subprocess.Popen(
        ["python3", "scripts/orchestrator.py"],
        cwd="/root/qjoe-prompts"
    )

    return {"status": "batch_started"}


from fastapi import Request

@app.post("/run_override")
async def run_override(request: Request):
    data = await request.json()
    row = data.get("row")

    import subprocess

    subprocess.Popen(
        ["python3", "scripts/orchestrator.py", "--row", str(row)],
        cwd="/root/qjoe-prompts"
    )

    return {"status": "override_started", "row": row}
