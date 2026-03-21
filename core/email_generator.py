from datetime import datetime
from zoneinfo import ZoneInfo

from core.cover_letter import select_template  # renvoie risk/pricing/fo_tools/energy


def _role_title(job_json: dict) -> str:
    return (job_json.get("role_title") or job_json.get("cv_title_override") or "Candidature").strip()


def _company(job_json: dict) -> str:
    return (job_json.get("company") or "").strip()


def _first_top_reason(score_result: dict) -> str:
    reasons = score_result.get("top_reasons") or []
    return reasons[0].strip() if reasons else ""


def build_email_subject(job_json: dict) -> str:
    lang = job_json.get("language", "EN")
    title = _role_title(job_json)
    if lang == "FR":
        return f"Candidature — {title}"
    return f"Application — {title}"


def generate_email_body(job_json: dict, score_result: dict) -> str:

    lang = job_json.get("language", "FR")

    role = job_json.get("role_title") or job_json.get("cv_title_override") or "ce poste"
    team = job_json.get("team") or "votre équipe"
    company = job_json.get("company", "")

    base_template = select_template(job_json)

    # phrase motivation selon type de rôle
    if base_template == "risk":
        motivation = "les problématiques d’analyse des risques de marché et de couverture"
    elif base_template == "pricing":
        motivation = "les problématiques de pricing et d’analyse des risques sur produits dérivés"
    elif base_template == "fo_tools":
        motivation = "les environnements proches du trading et le développement d’outils pour le Front Office"
    else:
        motivation = "les problématiques quantitatives appliquées aux marchés"

    if lang == "FR":

        body = f"""Bonjour,

Je vous adresse ma candidature pour un poste en {role} chez {company}, au sein du desk {team.replace(" desk","").title()}.

Je suis particulièrement motivé par l’environnement de marché et par {motivation}.

Je serais ravi de pouvoir contribuer au desk.

Bien cordialement,
Ely Henry
"""

        return body

    # version EN
    body = f"""Hello,

Please find my application for the {role} position at {company} within the {team}.

I am particularly motivated by trading environments and by {motivation}.

I would be glad to contribute to the desk.

Best regards,
Ely Henry
"""

    return body
