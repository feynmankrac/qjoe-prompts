EXTRACT_JOB — JSON STRICT (stable)

Tu dois retourner UNIQUEMENT un JSON valide (aucun texte hors JSON, aucun markdown) respectant exactement ce schéma (aucun champ en plus) :

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
Règles (obligatoires)

Si info absente : null ou [].

Normalisation :

contract_type ∈ {INTERNSHIP,APPRENTICESHIP,VIE,PERMANENT,TEMP,GRADUATE_PROGRAM,CDD} sinon null

seniority ∈ {INTERN,JUNIOR,ASSOCIATE,SENIOR,UNKNOWN} sinon null

role_family ∈ {TRADING,STRUCTURING,PRICING,XVA,MODEL_RISK,MARKET_RISK,COUNTERPARTY_RISK,P&L_VALUATION,FO_TOOLS,DATA_SCIENCE,PRODUCT_CONTROL,ALM,COMPLIANCE,OPERATIONS,UNKNOWN}

role_type ∈ {FRONT_OFFICE,FRONT_SUPPORT,MIDDLE_OFFICE,CONTROL,BACK_OFFICE,RESEARCH,UNKNOWN}

tools: uniquement outils/langages explicitement cités.

asset_classes: uniquement ce qui est explicitement cité (FX/RATES/CREDIT/EQUITIES/COMMODITIES/POWER/GAS/OIL/EMISSIONS/CRYPTO/MULTI_ASSET).

Flags :

reporting_heavy=true si reporting périodique / regulatory reporting / dashboards / BAU est central.

model_validation=true si validation indépendante/benchmark/validation report/model risk est central.

derivatives_pricing=true si pricing/valuation dérivés est central.

energy_derivatives=true si dérivés énergie/commodities explicitement.

cxx_hardcore=true seulement si dev C++ perf-critical est mission principale.

quant_research_phd_mandatory=true si PhD mandatory.

quant_intensity (déterministe) :

base 0

+3 si pricing/stochastic/PDE/MC/calibration/Greeks/VaR/stress/XVA

+2 Python, +1 SQL, +1 VBA, +1 C++

+2 ML/AI

+2 prod code (git/CI/tests/pipelines)

-3 si reporting_heavy

clamp 0..10

Tags :

red_flags ∈ {REPORTING,COMPLIANCE_HEAVY,OPS_HEAVY,PHD_ONLY,CXX_HARDCORE,ELIGIBILITY_BLOCKER,LOW_FO_PROXIMITY}

signals_for_fit ∈ {FRONT_OFFICE_PROXIMITY,BUILDING_INTERNAL_TOOLS,PRODUCTION_CODE_EXPECTED,DERIVATIVES_PRICING_CORE,MODEL_VALIDATION_CORE,MARKET_RISK_ANALYTICS,COUNTERPARTY_RISK_ANALYTICS,ENERGY_COMMODITIES_EXPOSURE,CRYPTO_EXPOSURE,EXECUTION_ALGO_EXPOSURE,XVA_EXPOSURE}
