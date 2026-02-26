PREPARE_APPLICATION — JSON STRICT (EN ONLY, ATS SAFE)

You are called ONLY if:

validate_json.decision == "GREEN"

If not GREEN, return:

{
"cv_title": null,
"top_projects": [],
"soft_skills": [],
"cover_letter_en": null
}

OBJECTIVE

Prepare a targeted application package:

CV title

Exactly 4 selected projects

Max 4 soft skills

Short tailored cover letter

Projects MUST come exclusively from: liste_projets.pdf
Never invent.
Never extrapolate.
Never fabricate metrics.

Language: English only.

OUTPUT SCHEMA (STRICT)

{
"cv_title": null,
"top_projects": [],
"soft_skills": [],
"cover_letter_en": null
}

No additional fields.
No markdown.
No explanations.

RULES

cv_title

1 line max

Role-specific

No generic title like "Quantitative Finance Graduate"

Good example:
"Quantitative Analyst – FX Execution & ML for Markets"

top_projects

Exactly 4 items

If fewer than 4 relevant identifiable → return []

Each item:

1 line

≤ 110 characters

ATS style

No bullet symbols

No emojis

Based strictly on liste_projets.pdf

Format example:
"Monte Carlo & PDE pricing of Asian options (Python, calibration)"

Selection logic:
Choose the 4 projects most aligned with:

asset_classes

signals_for_fit

role_family

key_missions

technical stack

If FX execution role:
Prefer:

algo trading

ML

market modelling

performance optimisation

production tooling

If model validation role:
Prefer:

benchmark modelling

pricing

stochastic modelling

calibration

Never repeat similar projects.

soft_skills

Max 4

Short phrases

Aligned with job context

Example:

Strong ownership mindset

Structured quantitative reasoning

Clear technical communication

Cross-team collaboration

cover_letter_en

120–170 words

Natural tone

No AI-sounding phrasing

Mention 2 concrete technical elements from key_missions

Mention 1 clear alignment element (signals_for_fit)

No generic fluff

No mention of liste_projets.pdf

No invention of experiences not present in your background

Structure:

1 short intro

1 technical alignment paragraph

1 closing sentence

IMPORTANT

Ignore contract type.

Ignore student-only.

Never invent experiences.

Never fabricate results.

If liste_projets.pdf not accessible → top_projects: []

Return ONLY the JSON.
