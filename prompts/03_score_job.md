SCORE_JOB — JSON STRICT (DETERMINISTIC)

Tu reçois en entrée un objet INPUT_JSON conforme au schéma EXTRACT_JOB (déjà normalisé).

Tu dois retourner UNIQUEMENT un JSON valide respectant EXACTEMENT le schéma ci-dessous.

Interdictions :

aucun champ supplémentaire

aucun markdown

aucun texte hors JSON

Schéma de sortie :

{
"decision": "RED",
"score_0_100": 0,
"top_reasons": [],
"main_risk": null,
"override_possible": false
}

RÈGLE PRIORITAIRE — HARD GATES

Si l’un des cas suivants est vrai :

reporting_heavy == true

quant_research_phd_mandatory == true

cxx_hardcore == true

role_type ∈ {"CONTROL","BACK_OFFICE"}
ET signals_for_fit ne contient aucun de :
{"BUILDING_INTERNAL_TOOLS","DERIVATIVES_PRICING_CORE","MODEL_VALIDATION_CORE","MARKET_RISK_ANALYTICS","XVA_EXPOSURE"}

Alors :

decision = "RED"

override_possible = true

score_0_100 = 0

top_reasons = []

main_risk = correspondant :
REPORTING_HEAVY
PHD_MANDATORY
CXX_HARDCORE
LOW_VALUE_ADD_ROLE

Et NE PAS appliquer la section Score pondéré.

SCORE PONDÉRÉ (si aucun hard gate)

Initialiser score = 0.

Positif :

+25 si model_validation == true
+20 si market_risk == true
+15 si counterparty_risk == true
+20 si derivatives_pricing == true
+15 si energy_derivatives == true
+10 si role_type ∈ {"FRONT_OFFICE","FRONT_SUPPORT"}
+10 si signals_for_fit contient "BUILDING_INTERNAL_TOOLS"
+10 si signals_for_fit contient "PRODUCTION_CODE_EXPECTED"
+5 si quant_intensity >= 7
+3 si quant_intensity ∈ {5,6}

Bonus stratégique FX Execution :

+30 si
(role_family == "DATA_SCIENCE")
ET ("FX" ∈ asset_classes)
ET (signals_for_fit contient "EXECUTION_ALGO_EXPOSURE")

Négatif :

-25 si reporting_heavy == true
-15 si red_flags contient "COMPLIANCE_HEAVY"
-10 si red_flags contient "OPS_HEAVY"
-10 si red_flags contient "LOW_FO_PROXIMITY"

Borner score entre 0 et 100.

DÉCISION

Si score >= 70 :
decision = "GREEN"
override_possible = false
main_risk = null

Si 50 <= score <= 69 :
decision = "RED"
override_possible = true
main_risk = "BORDERLINE"

Si score < 50 :
decision = "RED"
override_possible = false
main_risk = "LOW_SCORE"

Interdiction : decision="GREEN" si score < 70.

TOP_REASONS

Maximum 2 éléments.

Doivent refléter les plus gros contributeurs positifs.

Si bonus FX appliqué :
Inclure explicitement :
"DATA_SCIENCE+FX+EXECUTION_ALGO_EXPOSURE bonus"

La seconde raison doit correspondre au second plus fort poids positif.

Ne jamais inventer d’arguments non présents dans INPUT_JSON.

IMPORTANT

Ignorer totalement le type de contrat et les mentions “student-only”.

Toujours retourner UNIQUEMENT le JSON final.
