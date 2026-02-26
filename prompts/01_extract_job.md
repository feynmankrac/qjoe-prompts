EXTRACT_JOB — JSON STRICT (FACTUAL ONLY, v2)

Tu dois retourner UNIQUEMENT un JSON valide (aucun texte hors JSON, aucun markdown) respectant exactement le schéma ci-dessous (aucun champ en plus).

Objectif :
Extraire uniquement des informations factuelles explicitement présentes dans l’annonce.
Ne jamais interpréter stratégiquement.
Ne jamais scorer.
Ne jamais normaliser agressivement.

Schéma de sortie (strict)

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

RÈGLES GÉNÉRALES

Si information absente → null (ou [] pour listes).

Ne jamais inventer.

Ne jamais extrapoler.

Ne jamais interpréter implicitement.

Ne jamais ajouter de champ.

Retourner UNIQUEMENT le JSON final.

EXTRACTION FACTUELLE
1️⃣ Champs textuels

Remplir uniquement si explicitement mentionné :

company

role_title

location

remote_policy

contract_type (si explicitement indiqué : internship, permanent, etc.)

seniority (si explicitement mentionné : intern, junior, senior…)

Si non explicitement indiqué → null.

2️⃣ role_family et role_type

Remplir uniquement si explicitement identifiable dans le texte
(ex : “Market Risk Analyst”, “Model Validation”, “Trading Desk”, etc.)

Sinon → null.

Ne pas deviner.

3️⃣ business_domain

Inclure uniquement domaines explicitement cités, par exemple :

FX

Fixed Income

Equity Derivatives

Commodities

Crypto

Risk Management

Model Validation

Execution Algorithms

Machine Learning

Ne pas inférer.

4️⃣ asset_classes

Inclure uniquement si explicitement mentionné :

FX
RATES
CREDIT
EQUITIES
COMMODITIES
POWER
GAS
OIL
EMISSIONS
CRYPTO
MULTI_ASSET

Sinon [].

5️⃣ key_missions / key_requirements

Listes de phrases courtes.

Reformulation légère autorisée.

Ne jamais inventer.

Ne pas résumer excessivement.

Ne pas interpréter.

6️⃣ tools

Inclure uniquement outils/langages explicitement cités :

Exemples :
Python
SQL
VBA
C++
R
SAS
Bloomberg
Git

Ne pas ajouter si non mentionné.

BOOLÉENS (STRICTEMENT FACTUELS)

Mettre true uniquement si explicitement central dans l’annonce.

model_validation = true
→ si validation indépendante de modèles / benchmark / validation report explicitement mentionné.

market_risk = true
→ si VaR / stress testing / risk metrics / market risk explicitement mentionné.

counterparty_risk = true
→ si CVA / exposure / counterparty risk explicitement mentionné.

derivatives_pricing = true
→ si pricing / valuation de dérivés explicitement central.

energy_derivatives = true
→ si dérivés énergie / commodities trading explicitement mentionné.

quant_research_phd_mandatory = true
→ si PhD mandatory explicitement écrit.

cxx_hardcore = true
→ si développement C++ performance-critical est mission principale.

reporting_heavy = true
→ si reporting périodique, dashboards, regulatory reporting ou BAU reporting sont centraux.

Sinon → false.

IMPORTANT

quant_intensity doit rester 0 (sera calculé plus tard).

red_flags doit rester [].

signals_for_fit doit rester [].

Ne jamais appliquer de logique métier.

Ne jamais appliquer de scoring.

Ne jamais normaliser dans des catégories fermées.

Ne jamais interpréter stratégiquement.

Retourner UNIQUEMENT le JSON.
