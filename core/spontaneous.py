from __future__ import annotations

from pathlib import Path
from typing import Optional

from core.pipeline import patch_latex_cv, build_cv_title # si ton projet a ces fonctions ailleurs, adapte l'import
#from core.template_selector import map_template, select_template  # idem
from core.pipeline import compile_latex

EMAIL_SIGNATURE = {
    "EN": "Best regards,\n\nEly Henry\n+33 6 16 70 29 16\nlinkedin.com/in/ely-henry/\ngithub.com/feynmankrac",
    "FR": "Bien cordialement,\n\nEly Henry\n+33 6 16 70 29 16\nlinkedin.com/in/ely-henry/\ngithub.com/feynmankrac"
}

DESK_TEMPLATE_MAP = {
    "DATA_EXECUTION": "cv_data_execution.tex",
    "ENERGY_TRADING": "cv_energy_trading.tex",
    "MARKET_RISK": "cv_market_risk.tex",
    "MODEL_VALIDATION": "cv_model_validation.tex",
    "PNL_VALUATION": "cv_pnl_valuation.tex",
    "STRUCTURING": "cv_structuring.tex",
    "TRADING": "cv_trading.tex",
    "ENERGY_MODELING": "cv_energy_modeling.tex",
}

def desk_to_cv_title(desk: str) -> str:

    mapping = {
        "ENERGY_TRADING": "Quantitative Finance – Energy Markets",
        "TRADING": "Quantitative Trading",
        "MARKET_RISK": "Market Risk – Quantitative Finance",
        "MODEL_VALIDATION": "Model Validation – Quantitative Finance",
        "STRUCTURING": "Derivatives Structuring",
        "PNL_VALUATION": "Derivatives Valuation",
        "DATA_EXECUTION": "Quantitative Data Analysis",
        "ENERGY_MODELING": "Quantitative Finance – Energy Markets",
    }

    return mapping.get(desk, desk.replace("_", " ").title())

#def desk_to_human(desk: str) -> str:
 #   return desk.replace("_", " ").title()

def desk_to_human(desk: str) -> str:

    mapping = {
        "ENERGY_MODELING": "Energy Forecasting",
    }

    return mapping.get(desk, desk.replace("_", " ").title())


def build_spontaneous_email_subject(company: str, desk: str, language: str) -> str:
    if (language or "EN").upper().startswith("FR"):
        return f"Candidature spontanée — {desk} — {company}"
    return f"Spontaneous application — {desk} — {company}"


def build_spontaneous_email_body(company: str, desk: str, first_name: Optional[str], language: str) -> str:
    name = first_name.strip() if first_name else ""
    is_fr = (language or "EN").upper().startswith("FR")

    hello = (
        f"Bonjour {name}," if is_fr and name else
        ("Bonjour," if is_fr else (f"Hello {name}," if name else "Hello,"))
    )

    signature = EMAIL_SIGNATURE["FR"] if is_fr else EMAIL_SIGNATURE["EN"]

    if is_fr:
        return (
            f"{hello}\n\n"
            f"Je me permets de vous contacter pour une candidature spontanée "
            f"au sein de vos activités de {desk.lower()}.\n\n"
            f"Je suis diplômé d’un Master 2 en finance quantitative et je souhaite évoluer dans un environnement rigoureux "
            f"où la modélisation et les produits dérivés sont centraux.\n\n"
            f"Vous trouverez mon CV en pièce jointe. Je serais ravi d’échanger si mon profil correspond à vos besoins.\n\n"
            f"{EMAIL_SIGNATURE['FR']}\n"
        )

    return (
        f"{hello}\n\n"
        f"I’m reaching out with a spontaneous application to {company}, regarding opportunities within your {desk.lower()} activities.\n\n"
        f"I hold a Master’s degree (M2) in Quantitative Finance and I’m looking to join a rigorous environment "
        f"where modelling and derivatives are central.\n\n"
        f"Please find my CV attached. I would be happy to discuss if my profile matches your needs.\n\n"
        f"{EMAIL_SIGNATURE['FR']}\n"
    )


def desk_to_template(desk: str) -> str:
    if not desk:
        return "cv_trading.tex"
    return DESK_TEMPLATE_MAP.get(desk.upper(), "cv_trading.tex")

def run_generate_spontaneous_application(
    *,
    company: str,
    to_email: str,
    first_name: Optional[str],
    desk: str,
    language: str = "EN",
) -> dict:

    # Normalise le desk venant du Sheet
    desk = (desk or "").upper().strip()
    desk_label = desk_to_human(desk)

    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # minimal job_json for CV templating (deterministic)
    job_json = {
        "company": company,
        "contact_email": to_email,
        "language": language,
        "cv_title_override": desk_to_cv_title(desk),
        "role_title": desk,     # helps title fallback
        "role_family": None,    # template selection can fallback
        "role_type": None,
        "tools": [],
        "asset_classes": [],
        "key_missions": [],
        "key_requirements": [],
    }

    template_file = desk_to_template(desk)
    template_path = Path("templates") / template_file
    base_template = template_file.replace(".tex", "")

    template_result = {
    "template_file": template_file
}

    cv_title = job_json.get("cv_title_override") or build_cv_title(job_json)

    generated_content = {"cv_title": cv_title}

    # stable name
    safe_company = "".join([c for c in company if c.isalnum()])[:24] or "COMPANY"
    safe_desk = "".join([c for c in desk if c.isalnum()])[:24] or "DESK"
    row_key = f"Ely_Henry_CV_{safe_company}"

    cv_tex_path = artifacts_dir / f"{row_key}_cv_{base_template}.tex"

    patch_latex_cv(
        template_path=str(template_path),
        output_path=str(cv_tex_path),
        generated_content=generated_content
    )

    compile_result_cv = compile_latex(str(cv_tex_path))

    cv_pdf_path = None
    if not compile_result_cv.get("success"):
        print("COMPILE ERROR:", compile_result_cv)

    elif compile_result_cv.get("pdf_path"):
        tmp_pdf = Path(compile_result_cv["pdf_path"])
        safe_company = "".join([c for c in company if c.isalnum()])
        final_cv_pdf = artifacts_dir / f"Ely_Henry_cv_{safe_company}.pdf"

        if tmp_pdf.exists():
            tmp_pdf.rename(final_cv_pdf)
            cv_pdf_path = str(final_cv_pdf)
    
    #email_subject = build_spontaneous_email_subject(company, desk, language)
    email_subject = build_spontaneous_email_subject(company, desk_label, language)
    #email_body = build_spontaneous_email_body(company, desk, first_name, language)
    email_body = build_spontaneous_email_body(company, desk_label, first_name, language)

    return {
        "template": template_result,
        "artifacts": {"cv_pdf_path": cv_pdf_path},
        "email": {"subject": email_subject, "body": email_body},
        "meta": {"company": company, "desk": desk, "to_email": to_email}
    }
