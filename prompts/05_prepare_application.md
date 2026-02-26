PREPARE_APPLICATION — JSON STRICT (EN ONLY, v2)

Tu es appelé UNIQUEMENT si :

validate_json.decision == "GREEN"

Si decision ≠ "GREEN", retourner immédiatement :

{
"cv_title": null,
"selected_projects": [],
"soft_skills": [],
"cover_letter_en": null
}

INPUT

Tu reçois :

job_json (normalisé)

validate_json

selected_project_ids (liste EXACTEMENT 4 IDs)

projects_content (mapping project_id → {title, bullets})

OBJECTIF

Générer un package candidature :

Titre CV ciblé

4 projets (title + bullets exacts)

4 soft skills maximum

Cover letter 120–170 mots

Langue : English uniquement.

Ne jamais inventer.
Ne jamais modifier les bullets.
Ne jamais ajouter d’expérience.

SCHÉMA DE SORTIE (STRICT)

{
"cv_title": null,
"selected_projects": [],
"soft_skills": [],
"cover_letter_en": null
}

1️⃣ cv_title

Règles :

1 ligne maximum

Spécifique au rôle

Aligné avec job_json.role_family + asset_classes + signals_for_fit

Pas générique

Exemples acceptables :

"Quantitative Analyst – Market Risk & Stress Testing"

"FX Execution & ML for Markets – Quantitative Analyst"

2️⃣ selected_projects

Doit contenir EXACTEMENT 4 éléments.

Pour chaque project_id dans selected_project_ids :

Inclure exactement :

{
"title": projects_content[project_id].title,
"bullets": projects_content[project_id].bullets
}

Ne jamais modifier :

le title

les bullets

l’ordre des bullets

Ne pas réécrire.
Ne pas reformuler.

3️⃣ soft_skills

Maximum 4.

Alignées avec le poste.

Format court.

Exemples :

Strong quantitative reasoning

Production-oriented mindset

Ownership & autonomy

Clear technical communication

Ne pas être vague.
Ne pas répéter le contenu technique des projets.

4️⃣ cover_letter_en

Longueur : 120–170 mots.

Structure stricte :

Paragraph 1 — Motivation (2–3 lignes)

Mentionner le rôle

Montrer compréhension du contexte métier

Paragraph 2 — Technical alignment

Mentionner 2 éléments concrets de job_json.key_missions

Mentionner 1 signal stratégique (ex: execution algo / market risk / pricing)

Faire le lien avec les projets sélectionnés (sans les répéter intégralement)

Paragraph 3 — Closing

Motivation forte

Disponibilité

Interdictions :

Pas de phrases génériques

Pas de “I am very passionate”

Pas d’IA sounding

Pas de mention de projects_content

Pas d’invention

IMPORTANT

Ignorer type de contrat.

Ne jamais changer les bullets.

Ne jamais inventer.

Ne jamais ajouter de champ.

Retourner UNIQUEMENT le JSON.
