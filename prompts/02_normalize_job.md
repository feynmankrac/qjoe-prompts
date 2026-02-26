NORMALIZE_JOB — JSON STRICT (LOGIC LAYER, v2)

Tu reçois en entrée un JSON valide issu de EXTRACT_JOB v2.

Tu dois retourner UNIQUEMENT un JSON valide respectant EXACTEMENT le même schéma.
Aucun champ supplémentaire.
Aucun texte hors JSON.
Aucun markdown.

Schéma de sortie (strictement identique)

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

RÈGLES STRUCTURELLES

Ne jamais modifier :
company
role_title
location
remote_policy
key_missions
key_requirements

Ne jamais inventer.

Ne jamais ajouter de champ.

Nettoyer doublons dans tools / business_domain / asset_classes si nécessaire.

Tous les enums doivent être forcés dans l’espace fermé ci-dessous.

1️⃣ NORMALISATION DES ENUMS
contract_type

Doit appartenir à :
{INTERNSHIP, APPRENTICESHIP, VIE, PERMANENT, TEMP, GRADUATE_PROGRAM, CDD}

Sinon → null

seniority

Si null → UNKNOWN

Doit appartenir à :
{INTERN, JUNIOR, ASSOCIATE, SENIOR, UNKNOWN}

Sinon → UNKNOWN

role_family

Doit appartenir à :

TRADING
STRUCTURING
PRICING
XVA
MODEL_RISK
MARKET_RISK
COUNTERPARTY_RISK
P&L_VALUATION
FO_TOOLS
DATA_SCIENCE
PRODUCT_CONTROL
ALM
COMPLIANCE
OPERATIONS
UNKNOWN

Si null ou ambigu → UNKNOWN

Ne pas déduire agressivement.

role_type

Doit appartenir à :

FRONT_OFFICE
FRONT_SUPPORT
MIDDLE_OFFICE
CONTROL
BACK_OFFICE
RESEARCH
UNKNOWN

Si null → UNKNOWN

2️⃣ QUANT_INTENSITY (RECALCUL OBLIGATOIRE)

Ignorer la valeur d’entrée.
Recalculer entièrement.

Base = 0

+3 si mention explicite dans key_missions ou key_requirements de :
pricing / stochastic / PDE / Monte Carlo / calibration / Greeks / VaR / stress testing / XVA

+2 si Python dans tools
+1 si SQL
+1 si VBA
+1 si C++

+2 si ML / AI / deep learning mentionné

+2 si mention explicite de :
git / CI / tests / pipelines / performance optimization / refactoring

-3 si reporting_heavy == true

Clamp final entre 0 et 10.

3️⃣ RED_FLAGS (remplissage automatique)

Réinitialiser red_flags à [] avant calcul.

Ajouter uniquement parmi :

REPORTING → si reporting_heavy == true
COMPLIANCE_HEAVY → si role_family == COMPLIANCE
OPS_HEAVY → si role_family == OPERATIONS
PHD_ONLY → si quant_research_phd_mandatory == true
CXX_HARDCORE → si cxx_hardcore == true

LOW_FO_PROXIMITY → si
role_type ∈ {CONTROL, BACK_OFFICE}
ET signals_for_fit ne contient aucun signal modelling fort
(après calcul des signals_for_fit)

4️⃣ SIGNALS_FOR_FIT (remplissage automatique)

Réinitialiser signals_for_fit à [] avant calcul.

Ajouter uniquement parmi :

FRONT_OFFICE_PROXIMITY → si role_type ∈ {FRONT_OFFICE, FRONT_SUPPORT}

BUILDING_INTERNAL_TOOLS → si missions mentionnent outils internes / automation / tooling

PRODUCTION_CODE_EXPECTED → si git/tests/CI/pipelines mentionnés

DERIVATIVES_PRICING_CORE → si derivatives_pricing == true

MODEL_VALIDATION_CORE → si model_validation == true

MARKET_RISK_ANALYTICS → si market_risk == true

COUNTERPARTY_RISK_ANALYTICS → si counterparty_risk == true

ENERGY_COMMODITIES_EXPOSURE → si energy_derivatives == true

CRYPTO_EXPOSURE → si CRYPTO ∈ asset_classes

EXECUTION_ALGO_EXPOSURE → si execution algorithm / algo trading mentionné

XVA_EXPOSURE → si XVA mentionné

Ne rien ajouter si non justifié explicitement.

5️⃣ COHÉRENCE INTERNE

red_flags dépend de signals_for_fit.

signals_for_fit dépend des booléens et missions.

quant_intensity dépend uniquement des règles ci-dessus.

Aucune autre logique autorisée.

6️⃣ INTERDICTIONS

Ne jamais modifier tools sauf suppression doublons.

Ne jamais modifier asset_classes sauf nettoyage doublons.

Ne jamais ajouter de nouveaux tags non listés.

Ne jamais inventer.

Ne jamais appliquer logique de scoring global.

Ne jamais décider GREEN/RED ici.

Retourner UNIQUEMENT le JSON final.
