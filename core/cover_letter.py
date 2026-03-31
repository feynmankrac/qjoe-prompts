from pathlib import Path
from datetime import datetime
import subprocess
import time

ARTIFACTS_DIR = Path(__file__).resolve().parent.parent / "artifacts" / "cover_letters"
# ===== CONSTANTES GLOBALES =====
TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates" / "cover_letters"
ROLE_FAMILY_SIGNAL = {
    "MARKET_RISK": "Les enjeux d’analyse et de mesure des risques de marché correspondent directement à mon parcours.",
}

def select_template(job):

    signals = set(job.get("signals_for_fit", []))
    role_family = job.get("role_family")

    # 1️⃣ ENERGY priorité absolue
    if job.get("energy_derivatives") or "ENERGY_COMMODITIES_EXPOSURE" in signals:
        return "energy"

    # 2️⃣ PRICING
    if "DERIVATIVES_PRICING_CORE" in signals:
        return "pricing"

    # 3️⃣ RISK
    if "MARKET_RISK_ANALYTICS" in signals or "MODEL_VALIDATION_CORE" in signals:
        return "risk"

    # 4️⃣ FO Tools
    if "FRONT_OFFICE_PROXIMITY" in signals or "BUILDING_INTERNAL_TOOLS" in signals:
        return "fo_tools"

    # fallback
    return "risk"

def load_template(template_filename: str) -> str:
    template_path = TEMPLATE_DIR / template_filename

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    return template_path.read_text(encoding="utf-8")

def escape_latex(text: str) -> str:
    if not text:
        return ""

    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }

    for key, value in replacements.items():
        text = text.replace(key, value)

    return text

def build_core_mission(key_missions, language):
    if not key_missions:
        return (
            "la modélisation et la valorisation de produits dérivés"
            if language == "FR"
            else "the modelling and pricing of derivative products"
        )

    blacklist_starts = [
        "vous recherchez",
        "nous recherchons",
        "rejoindre",
        "crédit agricole cib",
        "cacib",
        "localisation du poste",
        "ce stage de",
        "cette offre",
        "vous êtes",
    ]

    priority_keywords = [
        "recherche",
        "conception",
        "implémentation",
        "calibration",
        "diagnostic",
        "application",
        "évaluation",
        "développer",
        "calibrer",
        "appliquer",
        "modèle",
        "pricing",
        "dérivés",
        "monte carlo",
        "pde",
    ]

    cleaned = []
    for mission in key_missions:
        raw = " ".join(mission.strip().split())
        low = raw.lower()

        if len(raw) < 20:
            continue
        if any(low.startswith(x) for x in blacklist_starts):
            continue
        if "banque de financement" in low:
            continue
        if "acteur européen majeur" in low:
            continue
        if "opportunités en alternance" in low:
            continue

        cleaned.append(raw)

    for mission in cleaned:
        low = mission.lower()
        if any(k in low for k in priority_keywords):
            mission = mission[0].lower() + mission[1:]
            return mission.rstrip(" .,:;–—-")

    if cleaned:
        mission = cleaned[0]
        mission = mission[0].lower() + mission[1:]
        return mission.rstrip(" .,:;–—-")

    return (
        "la modélisation et la valorisation de produits dérivés"
        if language == "FR"
        else "the modelling and pricing of derivative products"
    )

def map_top_reason(top_reasons):
    if not top_reasons:
        return ""

    reason = top_reasons[0]

    if "Market risk" in reason:
        return "L’exposition aux problématiques de VaR et de stress testing fait écho à mon parcours quantitatif."

    return ""


def generate_cover_letter_tex(job, score):
    #base_template = select_template(job)
    if cv_template:
        base_template = cv_template.lower()
    else:
        base_template = select_template(job)
    language = get_language(job)

    template_filename = f"{base_template}_{language.lower()}.tex"
    template_str = load_template(template_filename)

    now = datetime.now()
    if language == "FR":
        months_fr = ["", "janvier", "février", "mars", "avril", "mai", "juin",
                    "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
        date_str = f"{now.day} {months_fr[now.month]} {now.year}"
    else:
        date_str = now.strftime("%d %B %Y")

    role_title = escape_latex(
        job.get("role_title")
        or job.get("cv_title_override")
        or "Candidature"
    )
    company = escape_latex(job.get("company", ""))
    core_mission = escape_latex(
    build_core_mission(job.get("key_missions", []), language))
    why_fit = escape_latex(ROLE_FAMILY_SIGNAL.get(job.get("role_family"), ""))
    dynamic_sentence = escape_latex(map_top_reason(score.get("top_reasons", [])))

    tex = (
        template_str
        .replace("{{DATE}}", date_str)
        .replace("{{ROLE_TITLE}}", role_title)
        .replace("{{COMPANY}}", company)
        .replace("{{CORE_MISSIONS}}", core_mission)
        .replace("{{WHY_FIT_SIGNAL}}", why_fit)
        .replace("{{DYNAMIC_SIGNAL_SENTENCE}}", dynamic_sentence)
    )
    #print(">>> LANGUAGE USED:", language)
    #print(">>> TEMPLATE USED:", template_filename)
    return tex

def save_cover_letter_tex(tex_content: str, filename: str) -> Path:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    file_path = ARTIFACTS_DIR / filename
    file_path.write_text(tex_content, encoding="utf-8")

    return file_path

def compile_tex_to_pdf(tex_path: Path) -> Path:
    output_dir = tex_path.parent

    command = [
        "pdflatex",
        "-interaction=nonstopmode",
        "-output-directory",
        str(output_dir),
        str(tex_path),
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False
    )
    time.sleep(0.2)
    pdf_path = tex_path.with_suffix(".pdf")

   # print("DEBUG EXPECTED PDF:", pdf_path)
   # print("DEBUG PDF EXISTS:", pdf_path.exists())
    if not pdf_path.exists():
        raise RuntimeError(f"LaTeX compilation failed:\n{result.stderr.decode()}")

    # Nettoyage des fichiers auxiliaires
    for ext in [".aux", ".log", ".out"]:
        aux_file = tex_path.with_suffix(ext)
        if aux_file.exists():
            aux_file.unlink()

    return pdf_path

def build_cover_letter_filename(base_template: str, score: dict, language: str) -> str:
    score_value = score.get("score_0_100", 0)

    prefix = "ldm" if language == "FR" else "cover"

    return f"{prefix}_{score_value}_{base_template}.pdf"

def get_language(job) -> str:
    lang = job.get("language", "EN")

    if lang not in ["FR", "EN"]:
        return "EN"

    return lang
