SCORE_JOB — JSON STRICT (DETERMINISTIC, v3)

Tu reçois en entrée un objet INPUT_JSON conforme au schéma NORMALIZE_JOB (déjà normalisé).

Tu dois retourner UNIQUEMENT un JSON valide respectant EXACTEMENT le schéma ci-dessous.
Interdictions : aucun champ supplémentaire, aucun markdown, aucun texte hors JSON.

Schéma de sortie (strict)

{
"decision": "RED",
"score_0_100": 0,
"top_reasons": [],
"main_risk": null,
"override_possible": false
}

RÈGLE PRIORITAIRE — HARD GATES (bloquants)

Si l’un des cas suivants est vrai :

INPUT_JSON.reporting_heavy == true

INPUT_JSON.quant_research_phd_mandatory == true

INPUT_JSON.cxx_hardcore == true

INPUT_JSON.red_flags contient "LOW_FO_PROXIMITY"

Alors retourner immédiatement (sans calculer le score pondéré) :

decision = "RED"

override_possible = true

score_0_100 = 0

top_reasons = []

main_risk = selon le premier match dans cet ordre strict :

"REPORTING_HEAVY"

"PHD_MANDATORY"

"CXX_HARDCORE"

"LOW_VALUE_ADD_ROLE"

SCORE PONDÉRÉ (si aucun hard gate)

Initialiser score = 0.

Positif (ajouter)

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

Bonus stratégique FX Execution

+30 si :
(role_family == "DATA_SCIENCE")
ET ("FX" ∈ asset_classes)
ET (signals_for_fit contient "EXECUTION_ALGO_EXPOSURE")

Négatif (soustraire)

-15 si red_flags contient "COMPLIANCE_HEAVY"
-10 si red_flags contient "OPS_HEAVY"
-10 si red_flags contient "LOW_FO_PROXIMITY"

Borner score entre 0 et 100.

DÉCISION (seuils stricts)

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

TOP_REASONS (2 max, déterministe)

Règles :

Construire la liste des contributions POSITIVES effectivement appliquées.

Pour chaque contribution appliquée, associer une raison texte standard.

Trier ces contributions par poids décroissant (poids numérique).

Retourner les 2 premières (maximum).

Si bonus FX appliqué, une des reasons DOIT être exactement :
"DATA_SCIENCE+FX+EXECUTION_ALGO_EXPOSURE bonus"

Raisons texte standards (à utiliser uniquement si la règle correspondante est appliquée) :

+30 bonus FX → "DATA_SCIENCE+FX+EXECUTION_ALGO_EXPOSURE bonus"

+25 model_validation → "Model validation core"

+20 market_risk → "Market risk analytics (VaR/stress)"

+20 derivatives_pricing → "Derivatives pricing exposure"

+15 counterparty_risk → "Counterparty risk analytics"

+15 energy_derivatives → "Energy/commodities derivatives exposure"

+10 role_type FO/FS → "Front office proximity (role_type)"

+10 BUILDING_INTERNAL_TOOLS → "Building internal tools"

+10 PRODUCTION_CODE_EXPECTED → "Production code expected (git/tests/CI)"

+5 quant_intensity>=7 → "High quant intensity"

+3 quant_intensity 5-6 → "Moderate quant intensity"

Ne jamais inventer de raisons non listées.

IMPORTANT

Ignorer totalement le type de contrat et les mentions “student-only”.

Retourner UNIQUEMENT le JSON final.
