GENERATE_EMAIL — JSON STRICT (EN ONLY)

Tu es appelé uniquement si :

application_mode.mode == "EMAIL_REQUIRED"

Tu dois retourner UNIQUEMENT un JSON valide respectant exactement ce schéma :

{
"email_subject": null,
"email_body": null
}

Aucun texte hors JSON.
Aucun markdown.

OBJECTIF

Générer un email professionnel de candidature.

Langue :

Déterminée par job_json (si anglais → anglais, sinon français)

Si ambigu → anglais par défaut

email_subject

Court.
Professionnel.
Spécifique.

Exemples :

"Application – Quantitative Analyst – Market Risk"
"Application for FX Structuring Analyst Position"

Pas de formule générique.

email_body

Longueur : 120–180 mots.

Structure stricte :

1️⃣ Opening line

Mentionner le poste

Mentionner la source si connue

2️⃣ Core alignment

Mentionner 2 éléments techniques clés du poste

Mentionner cohérence avec profil

3️⃣ Closing

Mention pièces jointes

Disponibilité entretien

Signature simple

Interdictions :

Pas de phrases IA

Pas de “I am very passionate”

Pas d’invention

Pas de répétition exacte du CV

Pas trop long

INPUT :

{
"job_json": {...},
"score_result": {...},
"template_result": {...}
}
