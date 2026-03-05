from pathlib import Path
from datetime import datetime
import subprocess

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
        if language == "FR":
            return "l’analyse quantitative et le développement d’outils appliqués aux marchés financiers"
        else:
            return "quantitative analysis and development of tools applied to financial markets"

    mission = key_missions[0].strip()

    if mission:
        mission = mission[0].lower() + mission[1:]

    # enlever ponctuation finale parasite (.,;:—- etc.)
    mission = mission.rstrip().rstrip(" .,:;–—-")

    return mission

def map_top_reason(top_reasons):
    if not top_reasons:
        return ""

    reason = top_reasons[0]

    if "Market risk" in reason:
        return "L’exposition aux problématiques de VaR et de stress testing fait écho à mon parcours quantitatif."

    return ""


def generate_cover_letter_tex(job, score):
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
    )

    if result.returncode != 0:
        raise RuntimeError(f"LaTeX compilation failed:\n{result.stderr.decode()}")

    pdf_path = tex_path.with_suffix(".pdf")

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
    """
    Returns 'FR' or 'EN' based on manual Sheet input.
    Default = EN
    """
    lang = job.get("language", "EN")

    if lang not in ["FR", "EN"]:
        return "EN"

    return lang