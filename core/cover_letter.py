from pathlib import Path
from datetime import datetime
import subprocess
import time

ARTIFACTS_DIR = Path(__file__).resolve().parent.parent / "artifacts" / "cover_letters"
# ===== CONSTANTES GLOBALES =====
TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates" / "cover_letters"
#ROLE_FAMILY_SIGNAL = {
 #   "MARKET_RISK": {
  #      "FR": "Les enjeux d’analyse et de mesure des risques de marché correspondent directement à mon parcours.",
   #     "EN": "Market risk measurement and analysis directly align with my background."
    #},
    #"PRICING": {
    #    "FR": "Les problématiques de pricing de dérivés correspondent directement à mon parcours.",
    #    "EN": "Derivative pricing challenges directly align with my background."
    #},
    #"ENERGY": {
     #   "FR": "Les marchés de l’énergie et leurs dynamiques quantitatives correspondent directement à mon parcours.",
     #   "EN": "Energy markets and their quantitative dynamics align with my background."
    #},
    #"FO_TOOLS": {
    #    "FR": "Le développement d’outils quantitatifs pour le Front Office correspond directement à mon parcours.",
     #   "EN": "Building quantitative tools for front-office environments aligns with my background."
    #},
#}

NORMALIZE_TEMPLATE = {
    "ENERGY_TRADING": "energy",
    "MARKET_RISK": "risk",
    "MODEL_VALIDATION": "risk",
    "TRADING": "fo_tools",
    "STRUCTURING": "pricing",
    "PNL_VALUATION": "pricing",
    "DATA_EXECUTION": "fo_tools",
    "ENERGY_MODELING": "energy",
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

#def map_top_reason(top_reasons, language, base_template):
#    if not top_reasons:
 #       return ""
#
 #   role_key = resolve_role_key(base_template)

  #  mapping = {
   #     "MARKET_RISK": {
    #        "FR": "L’exposition aux problématiques de VaR et de stress testing fait écho à mon parcours quantitatif.",
     #       "EN": "My exposure to VaR and stress testing aligns with my quantitative background.",
      #  },
       # "PRICING": {
        #    "FR": "Les modèles de pricing et leur implémentation font partie intégrante de mon parcours.",
        #    "EN": "Pricing models and their implementation are a core part of my background.",
        #},
        #"ENERGY": {
        #    "FR": "La modélisation des marchés de l’énergie correspond directement à mon expérience.",
        #    "EN": "Energy market modeling directly aligns with my experience.",
        #},
        #"FO_TOOLS": {
        #    "FR": "Le développement d’outils pour les équipes de trading correspond à mon expérience.",
        #    "EN": "Developing tools for trading desks aligns with my experience.",
        #},
   # }

    #return mapping.get(role_key, {}).get(language, "")

   # if "Market risk" in reason:
    #    return "L’exposition aux problématiques de VaR et de stress testing fait écho à mon parcours quantitatif."

    #return ""

def generate_cover_letter_tex(job, score, cv_template=None):

    #if cv_template:
     #   base_template = cv_template.lower()
      #  template_filename = f"{base_template}_{get_language(job).lower()}.tex"
       # if not (TEMPLATE_DIR / template_filename).exists():
        #    base_template = select_template(job)
    #else:
     #   base_template = select_template(job)

    if cv_template:
        base_template = NORMALIZE_TEMPLATE.get(cv_template.upper(), "risk").lower()
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
        job.get("role_title") or job.get("cv_title_override") or "Candidature"
    )

    company = escape_latex(job.get("company", ""))

    core_mission = escape_latex(
        build_core_mission(job.get("key_missions", []), language)
    )

    role_key = resolve_role_key(base_template)

    def build_fit_sentence(role_key, language):
        mapping = {
            "MARKET_RISK": {
                "FR": "Les enjeux de mesure des risques de marché, notamment via la VaR et les stress tests, correspondent directement à mon parcours.",
                "EN": "Market risk measurement, particularly through VaR and stress testing, directly aligns with my background.",
            },
            "PRICING": {
                "FR": "Les problématiques de pricing et de modélisation de dérivés correspondent directement à mon parcours.",
                "EN": "Derivative pricing and modelling challenges directly align with my background.",
            },
            "ENERGY": {
                "FR": "La modélisation des marchés de l’énergie correspond directement à mon expérience.",
                "EN": "Energy market modelling directly aligns with my experience.",
            },
            "FO_TOOLS": {
                "FR": "Le développement d’outils quantitatifs pour le Front Office correspond à mon expérience.",
                "EN": "Developing quantitative tools for front-office environments aligns with my experience.",
            },
        }
        return mapping.get(role_key, {}).get(language, "")

    fit_sentence = escape_latex(build_fit_sentence(role_key, language))

    tex = (
        template_str
        .replace("{{DATE}}", date_str)
        .replace("{{ROLE_TITLE}}", role_title)
        .replace("{{COMPANY}}", company)
        .replace("{{CORE_MISSIONS}}", core_mission)
        .replace("{{WHY_FIT_SIGNAL}}", fit_sentence)
        .replace("{{DYNAMIC_SIGNAL_SENTENCE}}", "")
    )

    #enforce_language_consistency(tex, language)
    try:
        enforce_language_consistency(tex, language)
    except Exception:
        pass

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

def resolve_role_key(base_template: str) -> str:
    mapping = {
        "risk": "MARKET_RISK",
        "pricing": "PRICING",
        "energy": "ENERGY",
        "energy_modeling": "ENERGY",
        "fo_tools": "FO_TOOLS",
    }
    return mapping.get(base_template, "MARKET_RISK")

def enforce_language_consistency(text: str, language: str):
    if language == "EN":
        forbidden = ["Les ", "L’", "Je ", "mon parcours", "enjeux", "marché"]
    else:
        forbidden = ["I am", "market", "risk", "would", "position"]

    for token in forbidden:
        if token in text:
            raise ValueError(f"Language violation detected: {token}")