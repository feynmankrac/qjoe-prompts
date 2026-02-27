from typing import Dict, Any, List
import re


def load_prompt(prompt_path: str) -> str:
    # Conservé pour compat, même si non utilisé en mode déterministe
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def call_llm(prompt_text: str) -> Dict:
    # Stub : à câbler plus tard
    raise NotImplementedError("LLM call not implemented yet.")


def _empty_extraction(raw_text: str) -> Dict[str, Any]:
    return {
        "company": None,
        "role_title": None,
        "role_family": None,
        "role_type": None,
        "seniority": None,
        "location": None,
        "remote_policy": None,
        "contract_type": None,
        "business_domain": [],
        "asset_classes": [],
        "key_missions": [],
        "key_requirements": [],
        "model_validation": False,
        "market_risk": False,
        "counterparty_risk": False,
        "derivatives_pricing": False,
        "energy_derivatives": False,
        "quant_research_phd_mandatory": False,
        "cxx_hardcore": False,
        "reporting_heavy": False,
        "quant_intensity": 0,
        "tools": [],
        "red_flags": [],
        "signals_for_fit": [],
        "raw_text": raw_text,
    }


def _has_any(text: str, patterns: List[str]) -> bool:
    return any(re.search(p, text) for p in patterns)


def _deterministic_extract(raw_text: str) -> Dict[str, Any]:
    """
    Extract déterministe par mots-clés (MVP).
    Zéro hallucination: on ne remplit que ce qu'on peut inférer directement.
    """
    base = _empty_extraction(raw_text)

    t = raw_text.lower()

    # ---- Tools (uniquement si explicitement mentionnés)
    tools = []
    tool_patterns = [
        ("Python", r"\bpython\b"),
        ("SQL", r"\bsql\b"),
        ("VBA", r"\bvba\b"),
        ("C++", r"\bc\+\+\b"),
        ("C#", r"\bc#\b"),
        ("Java", r"\bjava\b"),
        ("R", r"\br\b"),
        ("SAS", r"\bsas\b"),
        ("Excel", r"\bexcel\b"),
        ("Power BI", r"\bpower\s*bi\b"),
        ("Tableau", r"\btableau\b"),
        ("Bloomberg", r"\bbloomberg\b"),
        ("Git", r"\bgit\b"),
        ("Linux", r"\blinux\b"),
    ]
    for name, pat in tool_patterns:
        if re.search(pat, t):
            tools.append(name)
    base["tools"] = tools

    # ---- Core booleans
    base["market_risk"] = _has_any(t, [
        r"\bmarket risk\b", r"\bvar\b", r"\bstress test", r"\bstress testing\b",
        r"\bsensitivity\b", r"\bbacktesting\b"
    ])

    base["counterparty_risk"] = _has_any(t, [
        r"\bcounterparty\b", r"\bcredit risk\b", r"\bcva\b", r"\bdva\b", r"\bfva\b",
        r"\bxva\b", r"\bexposure\b", r"\bepe\b", r"\benea\b"
    ])

    base["model_validation"] = _has_any(t, [
        r"\bmodel validation\b", r"\bvalidate models?\b", r"\bmodel risk\b",
        r"\bvalidation report\b", r"\bindependent validation\b", r"\bbenchmark model\b"
    ])

    base["derivatives_pricing"] = _has_any(t, [
        r"\bpricing\b", r"\bvaluation\b", r"\bderivatives?\b", r"\bgreeks?\b",
        r"\bcalibration\b", r"\bmonte carlo\b", r"\bpde\b", r"\bstochastic\b"
    ])

    # Énergie / commodities dérivés
    base["energy_derivatives"] = _has_any(t, [
        r"\bpower\b", r"\belectricity\b", r"\bgas\b", r"\bnatural gas\b", r"\boil\b",
        r"\bcrude\b", r"\bemissions?\b", r"\bcarbon\b", r"\bcommodit"
    ])

    # PhD mandatory
    base["quant_research_phd_mandatory"] = _has_any(t, [
        r"\bphd\b.*\b(mandatory|required)\b", r"\bdoctoral\b.*\b(mandatory|required)\b"
    ])

    # C++ hardcore (perf/low-latency)
    base["cxx_hardcore"] = _has_any(t, [
        r"\blow latency\b", r"\bultra low latency\b", r"\bhft\b", r"\bperformance[-\s]?critical\b",
        r"\bhigh performance c\+\+\b", r"\boptimis(e|ing) c\+\+\b"
    ]) and re.search(r"\bc\+\+\b", t) is not None

    # Reporting heavy (dashboards/KPI/reg reporting)
    base["reporting_heavy"] = _has_any(t, [
        r"\bkpi\b", r"\bdashboard\b", r"\breporting\b", r"\bmis\b", r"\bregulatory reporting\b",
        r"\bmonthly report\b", r"\bweekly report\b", r"\bcommittee packs?\b"
    ])

    # ---- Asset classes (uniquement si explicitement repérées)
    asset_classes = set()

    if _has_any(t, [r"\bfx\b", r"\bforeign exchange\b", r"\bcurrency\b"]):
        asset_classes.add("FX")
    if _has_any(t, [r"\brates\b", r"\binterest rate", r"\bir swaps?\b", r"\bswaption"]):
        asset_classes.add("RATES")
    if _has_any(t, [r"\bcredit\b", r"\bcds\b", r"\bspread\b", r"\bbonds?\b"]):
        asset_classes.add("CREDIT")
    if _has_any(t, [r"\bequity\b", r"\bequities\b", r"\bstock\b", r"\bstocks\b"]):
        asset_classes.add("EQUITIES")
    if _has_any(t, [r"\bcommodit", r"\bpower\b", r"\bgas\b", r"\boil\b", r"\bemissions?\b"]):
        asset_classes.add("COMMODITIES")
    if _has_any(t, [r"\bcrypto\b", r"\bbitcoin\b", r"\bethereum\b"]):
        asset_classes.add("CRYPTO")

    base["asset_classes"] = sorted(asset_classes)

    # ---- Signals for fit (tags standardisés)
    signals = set()

    if base["model_validation"]:
        signals.add("MODEL_VALIDATION_CORE")
    if base["market_risk"]:
        signals.add("MARKET_RISK_ANALYTICS")
    if base["counterparty_risk"]:
        signals.add("COUNTERPARTY_RISK_ANALYTICS")
        # XVA exposure (si CVA/DVA/FVA/XVA)
        if _has_any(t, [r"\bcva\b", r"\bdva\b", r"\bfva\b", r"\bxva\b"]):
            signals.add("XVA_EXPOSURE")
    if base["derivatives_pricing"]:
        signals.add("DERIVATIVES_PRICING_CORE")
    if base["energy_derivatives"]:
        signals.add("ENERGY_COMMODITIES_EXPOSURE")

    # Proximity FO (mots-clés simples)
    if _has_any(t, [r"\btrading desk\b", r"\bfront office\b", r"\btrader", r"\bdesk\b"]):
        signals.add("FRONT_OFFICE_PROXIMITY")
    if _has_any(t, [r"\binternal tools?\b", r"\bbuild tools?\b", r"\btooling\b", r"\bplatform\b"]):
        signals.add("BUILDING_INTERNAL_TOOLS")

    # Production code expected
    if _has_any(t, [r"\bci\b", r"\bcd\b", r"\bunit tests?\b", r"\bintegration tests?\b", r"\bgit\b"]):
        signals.add("PRODUCTION_CODE_EXPECTED")

    base["signals_for_fit"] = sorted(signals)

    # ---- Red flags (tags standardisés)
    red_flags = set()
    if base["reporting_heavy"]:
        red_flags.add("REPORTING")
    if base["quant_research_phd_mandatory"]:
        red_flags.add("PHD_ONLY")
    if base["cxx_hardcore"]:
        red_flags.add("CXX_HARDCORE")

    # LOW_FO_PROXIMITY : si role_type/control/back-office (non dispo via texte brut MVP) -> on ne le met pas ici.
    base["red_flags"] = sorted(red_flags)

    return base


def extract_job(raw_text: str) -> Dict:
    """
    Extraction factuelle.
    MVP: heuristique déterministe d'abord.
    LLM optionnel en fallback (si un jour câblé).
    """
    # 1) extract déterministe (toujours)
    deterministic = _deterministic_extract(raw_text)

    # 2) Si tu veux plus tard activer LLM extract conditionnel, tu peux le faire ici.
    # Pour l’instant on évite de bloquer le système.
    try:
        prompt_text = load_prompt("prompts/01_extract_job.md")
        full_prompt = prompt_text + "\n\nJOB_TEXT:\n" + raw_text
        llm_res = call_llm(full_prompt)
        if isinstance(llm_res, dict) and llm_res:
            # Merge conservateur: ne remplace que les champs vides
            for k, v in llm_res.items():
                if k not in deterministic:
                    continue
                if deterministic[k] in (None, [], False, 0) and v not in (None, [], ""):
                    deterministic[k] = v
    except NotImplementedError:
        pass
    except Exception:
        pass

    return deterministic