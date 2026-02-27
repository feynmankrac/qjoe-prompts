from datetime import datetime
from pathlib import Path

from core.gate import evaluate_gate
from core.score import compute_score
from core.template_mapper import map_template
from core.language_strategy import determine_languages
from core.application_mode import detect_application_mode
from core.patch_latex_cv import patch_latex_cv
from core.latex_compiler import compile_latex

def build_cv_title(job_json: dict) -> str:
    role_title = job_json.get("role_title")
    if isinstance(role_title, str) and role_title.strip():
        return role_title.strip()

    role_family = job_json.get("role_family")
    signals = set(job_json.get("signals_for_fit") or [])
    asset_classes = set(job_json.get("asset_classes") or [])

    mapping = {
        "MARKET_RISK": "Market Risk Quant / Analyst",
        "MODEL_RISK": "Model Validation Quant",
        "PRICING": "Derivatives Pricing Quant",
        "STRUCTURING": "Structuring Analyst",
        "TRADING": "Trading Quant / Analyst",
        "FO_TOOLS": "Front Office Quant Developer",
        "P&L_VALUATION": "P&L / Valuation Analyst",
        "DATA_SCIENCE": "Quant Data Scientist",
        "XVA": "XVA Quant",
        "COUNTERPARTY_RISK": "Counterparty / XVA Quant",
    }

    base = mapping.get(role_family, "Quantitative Analyst")

    if "EXECUTION_ALGO_EXPOSURE" in signals:
        base = "Execution / Algo Quant"

    if "FX" in asset_classes and "EXECUTION_ALGO_EXPOSURE" in signals:
        base = "FX Execution / Algo Quant"

    return base

def run_analysis(job_json: dict) -> dict:
    """
    Pipeline décisionnel uniquement.
    Ne génère aucun fichier.
    """

    result = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "job_json": job_json,
    }

    # Gate
    gate_result = evaluate_gate(job_json)
    result["gate"] = gate_result

    if gate_result.get("is_blocked"):
        result["decision"] = "RED"
        result["status"] = "BLOCKED"
        return result

    # Score
    score_result = compute_score(job_json)
    result["score"] = score_result
    result["decision"] = score_result.get("decision")
    result["status"] = "DONE"

    return result


def run_generate_application(job_json: dict) -> dict:
    """
    Génère CV + compile PDF.
    Suppose que la décision a déjà été validée.
    """

    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # Template mapping
    template_result = map_template(job_json)
    template_path = Path("templates") / template_result["template_file"]

    # Language strategy
    language_config = determine_languages(job_json)

    # Application mode
    mode_result = detect_application_mode(job_json)

    # Patch CV
    generated_content = {
        "cv_title": build_cv_title(job_json)
    }

    output_tex_path = artifacts_dir / "generated_cv.tex"

    patch_latex_cv(
        template_path=str(template_path),
        output_path=str(output_tex_path),
        generated_content=generated_content
    )

    # Compile
    compile_result = compile_latex(str(output_tex_path))

    return {
        "template": template_result,
        "languages": language_config,
        "application_mode": mode_result,
        "artifacts": {
            "tex_path": str(output_tex_path),
            "pdf_path": compile_result.get("pdf_path"),
        },
        "compile": compile_result,
    }