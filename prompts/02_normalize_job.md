🔧 PROMPT — NORMALIZE_JOB (JSON STRICT)

Tu reçois en entrée un JSON valide issu de l’étape EXTRACT_JOB.

Ta mission :

Normaliser strictement les champs catégoriels

Recalculer quant_intensity de manière déterministe

Remplir red_flags et signals_for_fit selon les règles

Ne jamais inventer d'information

Retourner UNIQUEMENT un JSON valide respectant exactement le même schéma

Ne jamais ajouter de champ

Ne jamais écrire de texte hors JSON

Schéma de sortie (strictement identique) :

{
"company": null,
"role_title": null,
"role_family": null,
"role_type": null,
"seniority": null,
"location": null,
"remote_policy": null,
"contract_type": null,
"business_domain": [],
"asset_classes": [],
"key_missions": [],
"key_requirements": [],
"model_validation": false,
"market_risk": false,
"counterparty_risk": false,
"derivatives_pricing": false,
"energy_derivatives": false,
"quant_research_phd_mandatory": false,
"cxx_hardcore": false,
"reporting_heavy": false,
"quant_intensity": 0,
"tools": [],
"red_flags": [],
"signals_for_fit": []
}

RÈGLES DE NORMALISATION

contract_type ∈ {INTERNSHIP, APPRENTICESHIP, VIE, PERMANENT, TEMP, GRADUATE_PROGRAM, CDD}
Sinon → null

seniority ∈ {INTERN, JUNIOR, ASSOCIATE, SENIOR, UNKNOWN}
Sinon → UNKNOWN

role_family ∈ {
TRADING,
STRUCTURING,
PRICING,
XVA,
MODEL_RISK,
MARKET_RISK,
COUNTERPARTY_RISK,
P&L_VALUATION,
FO_TOOLS,
DATA_SCIENCE,
PRODUCT_CONTROL,
ALM,
COMPLIANCE,
OPERATIONS,
UNKNOWN
}

Si ambigu → UNKNOWN

role_type ∈ {
FRONT_OFFICE,
FRONT_SUPPORT,
MIDDLE_OFFICE,
CONTROL,
BACK_OFFICE,
RESEARCH,
UNKNOWN
}

Si ambigu → UNKNOWN

Ne pas déduire agressivement. Rester conservateur.

QUANT_INTENSITY (RECALCUL OBLIGATOIRE)

Recalculer entièrement. Ne jamais garder la valeur d’entrée.

base = 0

+3 si mention explicite de :
pricing / stochastic / PDE / Monte Carlo / calibration / Greeks / VaR / stress testing / XVA

+2 si Python
+1 si SQL
+1 si VBA
+1 si C++

+2 si ML / AI / deep learning

+2 si production-quality code explicite :
git / CI / tests / pipelines / performance optimization / refactoring

-3 si reporting_heavy = true

Clamp final entre 0 et 10.

RED_FLAGS (remplir automatiquement)

Ajouter uniquement parmi :

REPORTING → si reporting_heavy=true
COMPLIANCE_HEAVY → si rôle centré conformité/réglementaire
OPS_HEAVY → si rôle principalement opérationnel / process
PHD_ONLY → si quant_research_phd_mandatory=true
CXX_HARDCORE → si cxx_hardcore=true
ELIGIBILITY_BLOCKER → si restriction explicite (nationality/final-year/etc.)
LOW_FO_PROXIMITY → si role_type ∈ {CONTROL,BACK_OFFICE,OPERATIONS}
ET absence de signaux FO/modelling forts

SIGNALS_FOR_FIT (remplir automatiquement)

Ajouter uniquement parmi :

FRONT_OFFICE_PROXIMITY → si role_type ∈ {FRONT_OFFICE, FRONT_SUPPORT}
BUILDING_INTERNAL_TOOLS → si outils internes / automation / dev desk tools
PRODUCTION_CODE_EXPECTED → si prod code mentionné (git/tests/CI/pipelines)
DERIVATIVES_PRICING_CORE → si derivatives_pricing=true
MODEL_VALIDATION_CORE → si model_validation=true
MARKET_RISK_ANALYTICS → si market_risk=true
COUNTERPARTY_RISK_ANALYTICS → si counterparty_risk=true
ENERGY_COMMODITIES_EXPOSURE → si energy_derivatives=true
CRYPTO_EXPOSURE → si crypto explicitement mentionné
EXECUTION_ALGO_EXPOSURE → si algo execution / trading algo mentionné
XVA_EXPOSURE → si XVA explicite

Ne rien ajouter si non justifié.

RÈGLES FINALES

Ne jamais inventer

Ne jamais modifier company / role_title / missions / requirements

Ne jamais ajouter de champ

Toujours recalculer quant_intensity

Retourner UNIQUEMENT le JSON final

Aucun commentaire

Aucun markdown

Aucun texte hors JSON
