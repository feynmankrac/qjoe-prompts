from __future__ import annotations

from typing import Optional

EMAIL_SIGNATURE = {
    "EN": (
        "Best regards,\n\n"
        "Ely Henry\n"
        "+33 6 16 70 29 16\n"
        "linkedin.com/in/ely-henry/\n"
        "github.com/feynmankrac"
    ),
    "FR": (
        "Bien cordialement,\n\n"
        "Ely Henry\n"
        "+33 6 16 70 29 16\n"
        "linkedin.com/in/ely-henry/\n"
        "github.com/feynmankrac"
    ),
}


def desk_to_human(desk: str) -> str:
    if not desk:
        return ""
    return desk.replace("_", " ").title()


def build_followup_subject(company: str, desk: str, language: str = "EN") -> str:
    is_fr = (language or "EN").upper().startswith("FR")
    desk_label = desk_to_human(desk)

    if is_fr:
        return f"Relance — {desk_label} — {company}"
    return f"Follow-up — {desk_label} — {company}"


def build_followup_body(company: str, desk: str, first_name: Optional[str], language: str = "EN") -> str:
    name = first_name.strip() if first_name else ""
    is_fr = (language or "EN").upper().startswith("FR")
    desk_label = desk_to_human(desk)

    if is_fr:
        hello = f"Bonjour {name}," if name else "Bonjour,"
        return (
            f"{hello}\n\n"
            f"Je me permets de revenir vers vous concernant mon précédent message au sujet d’opportunités au sein de vos activités de {desk_label.lower()} chez {company}.\n\n"
            f"Je reste très intéressé et serais ravi d’échanger si cela est pertinent.\n\n"
            f"{EMAIL_SIGNATURE['FR']}\n"
        )

    hello = f"Hello {name}," if name else "Hello,"
    return (
        f"{hello}\n\n"
        f"I’m following up on my previous email regarding opportunities within your {desk_label.lower()} activities at {company}.\n\n"
        f"I remain very interested and would be happy to discuss if relevant.\n\n"
        f"{EMAIL_SIGNATURE['EN']}\n"
    )