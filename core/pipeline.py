from datetime import datetime
from pathlib import Path
import re
from datetime import datetime
from zoneinfo import ZoneInfo

from core.gate import evaluate_gate
from core.score import compute_score
from core.template_mapper import map_template
from core.language_strategy import determine_languages
from core.application_mode import detect_application_mode
from core.patch_latex_cv import patch_latex_cv
from core.latex_compiler import compile_latex
from core.cover_letter import (
    generate_cover_letter_tex,
    save_cover_letter_tex,
    compile_tex_to_pdf,
    select_template,
    get_language,
    build_cover_letter_filename
)
from core.email_generator import build_email_subject, generate_email_body
from typing import Optional

# ======================
# TITLE BUILDER
# ======================

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


# ======================
# ARTIFACT NAMING (FORMAT A)
# ======================

def _slug(s: str) -> str:
    s = (s or "").strip().upper()
    s = re.sub(r"[^A-Z0-9]+", "_", s)
    return s.strip("_") or "UNKNOWN"



def build_artifact_basename(job_json: dict, score_result: dict) -> str:
    score = int(score_result.get("score_0_100") or 0)
    score_str = f"{score:02d}"  # garde 2 digits si tu veux 58 au lieu de 058

    role_family = _slug(job_json.get("role_family") or "UNKNOWN")

    ts = datetime.now(ZoneInfo("Europe/Paris")).strftime("%d-%m-%y-%H-%M")

    print("DEBUG BASENAME TZ PARIS:", ts)

    return f"{score_str}_{role_family}_{ts}"

# ======================
# ANALYSIS ONLY
# ======================

def run_analysis(job_json: dict) -> dict:
    result = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "job_json": job_json,
    }

    gate_result = evaluate_gate(job_json)
    result["gate"] = gate_result

    if gate_result.get("is_blocked"):
        result["decision"] = "RED"
        result["status"] = "BLOCKED"
        return result

    score_result = compute_score(job_json)
    result["score"] = score_result["score_0_100"]
    result["decision"] = score_result["decision"]
    result["status"] = "DONE"

    return result


# ======================
# GENERATE CV + PDF
# ======================

def run_generate_application(job_json: dict, email_application: bool = False, cv_template: Optional[str] = None) -> dict:
#def run_generate_application(job_json: dict, email_application: bool = False) -> dict:

   # print("DEBUG email_application flag:", email_application)

    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # ===== Recompute score (utile pour la lettre dynamique) =====
    score_result = compute_score(job_json)
    contact_email = job_json.get("contact_email")

    if contact_email:
        email_subject = build_email_subject(job_json)
        email_body = generate_email_body(job_json, score_result)
    else:
        email_subject = ""
        email_body = ""
    score_value = int(score_result.get("score_0_100") or 0)

    # ===== Identifiants stables =====
    row_index = job_json.get("row_index", "X")
    base_template = select_template(job_json)

    #print("ROLE TITLE IN JOB_JSON:", job_json.get("role_title"))
    #print("CV TITLE OVERRIDE:", job_json.get("cv_title_override"))
    #print("LANGUAGE IN JOB_JSON:", job_json.get("language"))

    # ============================================================
    # ======================= CV GENERATION ======================
    # ============================================================

   # template_result = map_template(job_json)
   # template_path = Path("templates") / template_result["template_file"]
    if cv_template:
        template_file = f"cv_{cv_template}.tex"
        template_result = {"template_file": template_file}
    else:
        template_result = map_template(job_json)

    template_path = Path("templates") / template_result["template_file"] 
    print("TEMPLATE SELECTED:", template_result)

    cv_title = job_json.get("cv_title_override") or build_cv_title(job_json)

    generated_content = {
        "cv_title": cv_title
    }

    cv_tex_path = artifacts_dir / f"{row_index}_cv_{score_value}_{base_template}.tex"

    patch_latex_cv(
        template_path=str(template_path),
        output_path=str(cv_tex_path),
        generated_content=generated_content
    )

    compile_result_cv = compile_latex(str(cv_tex_path))

    cv_pdf_path = None

    if compile_result_cv.get("pdf_path"):
        tmp_pdf = Path(compile_result_cv["pdf_path"])
        if email_application:
            final_cv_pdf = artifacts_dir / "Ely_Henry_CV.pdf"
        else:
            final_cv_pdf = artifacts_dir / f"{row_index}_cv_{score_value}_{base_template}.pdf"      
 #final_cv_pdf = artifacts_dir / f"{row_index}_cv_{score_value}_{base_template}.pdf"

        if tmp_pdf.exists():
            tmp_pdf.replace(final_cv_pdf)
            cv_pdf_path = str(final_cv_pdf)

    if email_application:
        return {
            "template": template_result,
            "artifacts": {
                "cv_pdf_path": cv_pdf_path,
            },
            "email": {
                "subject": email_subject,
                "body": email_body
            }
        }
    # ============================================================
    # ====================== LDM GENERATION ======================
    # ============================================================

    language = job_json.get("language", "EN")
   # print("LANGUAGE DETECTED:", language)

    score_dict = {
        "score_0_100": score_result.get("score_0_100", 0),
        "top_reasons": score_result.get("top_reasons", [])
    }

    ldm_tex_content = generate_cover_letter_tex(job_json, score_dict)
   # print("DEBUG LDM TEX:", ldm_tex_content[:200] if ldm_tex_content else None)

    prefix = "ldm" if language == "FR" else "cover"

    ldm_tex_path = artifacts_dir / f"{row_index}_{prefix}_{score_value}_{base_template}.tex"
    #ldm_tex_path = artifacts_dir / f"{row_index}_ldm_{score_value}_{base_template}.tex"
    ldm_tex_path.write_text(ldm_tex_content, encoding="utf-8")

    ldm_pdf_path = None

    try:
        compiled_ldm_pdf = compile_tex_to_pdf(ldm_tex_path)
        final_ldm_pdf = artifacts_dir / f"{row_index}_{prefix}_{score_value}_{base_template}.pdf"   
 # final_ldm_pdf = artifacts_dir / f"{row_index}_ldm_{score_value}_{base_template}.pdf"
    #    print("DEBUG compiled_ldm_pdf:", compiled_ldm_pdf)
     #   print("DEBUG compiled_ldm_pdf exists:", compiled_ldm_pdf.exists())
      #  print("DEBUG final_ldm_pdf:", final_ldm_pdf)
       # print("DEBUG same path:", compiled_ldm_pdf == final_ldm_pdf)

        if compiled_ldm_pdf.exists():
            compiled_ldm_pdf.replace(final_ldm_pdf)
            print("DEBUG replace done")
            ldm_pdf_path = str(compiled_ldm_pdf)
            print("DEBUG ldm_pdf_path set to:", ldm_pdf_path)
        else:
            print("DEBUG compiled_ldm_pdf does not exist inside try")
    
    except Exception as e:
        print("LDM compilation error:", str(e))

    # ============================================================

    return {
        "template": template_result,
        "artifacts": {
            "cv_pdf_path": cv_pdf_path,
            "ldm_pdf_path": ldm_pdf_path,
        },
        "email": {
            "subject": email_subject,
            "body": email_body
        }
    }
