from core.cover_letter import (
    generate_cover_letter_tex,
    save_cover_letter_tex,
    compile_tex_to_pdf,
    build_cover_letter_filename,
    select_template, get_language
)

job = {
    "role_family": "MARKET_RISK",
    "role_title": "Analyste risque de marché",
    "company": "Example Bank",
    "key_missions": ["Develop and maintain VaR models"],
    "signals_for_fit": ["MARKET_RISK_ANALYTICS"],
    "energy_derivatives": False,
    "language": "EN"
}

score = {
    "top_reasons": ["Market risk analytics (VaR/stress)"],
    "score_0_100": 58
}

# 1️⃣ Sélection du template
base_template = select_template(job)
language = get_language(job)
template_filename = f"{base_template}_{language.lower()}.tex"

# 2️⃣ Génération du TEX
print("JOB KEYS:", job.keys())
tex_output = generate_cover_letter_tex(job, score)

# 3️⃣ Construction du nom intelligent
language = get_language(job)
filename = build_cover_letter_filename(base_template, score, language)

# 4️⃣ Sauvegarde TEX avec nom cohérent
tex_path = save_cover_letter_tex(tex_output, filename.replace(".pdf", ".tex"))
print("TEX saved at:", tex_path)

# 5️⃣ Compilation PDF
pdf_path = compile_tex_to_pdf(tex_path)
print("PDF generated at:", pdf_path)