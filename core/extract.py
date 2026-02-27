from typing import Dict, Any, List
import re


def load_prompt(prompt_path: str) -> str:
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def call_llm(prompt_text: str) -> Dict:
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
    base = _empty_extraction(raw_text)
    t = raw_text.lower()

    # -----------------------------
    # TOOLS
    # -----------------------------
    tools = []
    tool_patterns = [
        ("Python", r"\bpython\b"),
        ("SQL", r"\bsql\b"),
        ("VBA", r"\bvba\b"),
        ("C++", r"\bc\+\+\b"),
        ("C#", r"\bc#\b"),
        ("Java", r"\bjava\b"),
        ("R", r"(?<![a-z0-9_])r(?![a-z0-9_])"),  # évite de matcher "risk"
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

    # -----------------------------
    # BOOLEANS CORE
    # -----------------------------
    base["market_risk"] = _has_any(t, [
        r"\bmarket risk\b", r"\bvar\b", r"\bstress test", r"\bstress testing\b",
        r"\bsensitivity\b", r"\bbacktesting\b"
    ])

    base["counterparty_risk"] = _has_any(t, [
        r"\bcounterparty\b", r"\bcredit risk\b", r"\bcva\b", r"\bdva\b", r"\bfva\b",
        r"\bxva\b", r"\bexposure\b", r"\bepe\b", r"\benee\b"
    ])

    base["model_validation"] = _has_any(t, [
        r"\bmodel validation\b", r"\bvalidate models?\b", r"\bmodel risk\b",
        r"\bvalidation report\b", r"\bindependent validation\b", r"\bbenchmark model\b"
    ])

    base["derivatives_pricing"] = _has_any(t, [
        r"\bpricing\b", r"\bvaluation\b", r"\bderivatives?\b", r"\bgreeks?\b",
        r"\bcalibration\b", r"\bmonte carlo\b", r"\bpde\b", r"\bstochastic\b",
        r"\bvolatility\b", r"\bsmile\b"
    ])

    base["energy_derivatives"] = _has_any(t, [
        r"\bpower\b", r"\belectricity\b", r"\bgas\b", r"\bnatural gas\b", r"\boil\b",
        r"\bcrude\b", r"\bemissions?\b", r"\bcarbon\b", r"\bcommodit"
    ])

    base["quant_research_phd_mandatory"] = _has_any(t, [
        r"\bphd\b.*\b(mandatory|required)\b", r"\bdoctoral\b.*\b(mandatory|required)\b"
    ])

    base["cxx_hardcore"] = (_has_any(t, [
        r"\blow latency\b", r"\bultra low latency\b", r"\bhft\b", r"\bperformance[-\s]?critical\b",
        r"\blatency[-\s]?sensitive\b", r"\bhigh performance\b"
    ]) and re.search(r"\bc\+\+\b", t) is not None)

    base["reporting_heavy"] = _has_any(t, [
        r"\bkpi\b", r"\bdashboard\b", r"\breporting\b", r"\bmis\b", r"\bregulatory reporting\b",
        r"\bmonthly report\b", r"\bweekly report\b", r"\bcommittee packs?\b"
    ])

    # -----------------------------
    # ASSET CLASSES
    # -----------------------------
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

    # -----------------------------
    # SIGNALS
    # -----------------------------
    signals = set()

    if base["model_validation"]:
        signals.add("MODEL_VALIDATION_CORE")

    if base["market_risk"]:
        signals.add("MARKET_RISK_ANALYTICS")

    if base["counterparty_risk"]:
        signals.add("COUNTERPARTY_RISK_ANALYTICS")
        if _has_any(t, [r"\bcva\b", r"\bdva\b", r"\bfva\b", r"\bxva\b"]):
            signals.add("XVA_EXPOSURE")

    if base["derivatives_pricing"]:
        signals.add("DERIVATIVES_PRICING_CORE")

    if base["energy_derivatives"]:
        signals.add("ENERGY_COMMODITIES_EXPOSURE")

    # -----------------------------
    # FO proximity (EN + FR)
    # -----------------------------
    if _has_any(t, [
        r"\btrading desk\b",
        r"\bfront office\b",
        r"\btrader\b",
        r"\bdesk\b",
        r"\bsalle des marchés\b",
        r"\btrading\b"
    ]):
        signals.add("FRONT_OFFICE_PROXIMITY")

    # -----------------------------
    # Internal tools (EN + FR)
    # -----------------------------
    if _has_any(t, [
        r"\binternal tools?\b",
        r"\bbuild tools?\b",
        r"\btooling\b",
        r"\bplatform\b",
        r"\bcréation d['’]outils\b",
        r"\bconception d['’]outils\b",
        r"\boutils d['’]aide à la décision\b"
    ]):
        signals.add("BUILDING_INTERNAL_TOOLS")

    # -----------------------------
    # Execution algorithm exposure (EN + FR)
    # -----------------------------
    if _has_any(t, [
        r"\bexecution algorithm\b",
        r"\balgorithmes? d['’]exécution\b",
        r"\balgo execution\b",
        r"\bexecution algo\b"
    ]):
        signals.add("EXECUTION_ALGO_EXPOSURE")

    # -----------------------------
    # Production code expected
    # -----------------------------
    if _has_any(t, [
        r"\bgit\b",
        r"\bci\b",
        r"\bcd\b",
        r"\bunit tests?\b",
        r"\bintegration tests?\b",
        r"\bpipeline(s)?\b",
        r"\bcode review\b"
    ]):
        signals.add("PRODUCTION_CODE_EXPECTED")

    base["signals_for_fit"] = sorted(signals)

    # -----------------------------
    # ROLE FAMILY / ROLE TYPE (heuristique, seulement si évident)
    # -----------------------------
    # role_family ∈ {TRADING, STRUCTURING, PRICING, XVA, MODEL_RISK, MARKET_RISK, COUNTERPARTY_RISK, P&L_VALUATION, FO_TOOLS, DATA_SCIENCE, PRODUCT_CONTROL, ALM, COMPLIANCE, OPERATIONS, UNKNOWN}
    role_family = None

    if base["model_validation"]:
        role_family = "MODEL_RISK"
    elif base["counterparty_risk"]:
        role_family = "COUNTERPARTY_RISK"
    elif base["market_risk"]:
        role_family = "MARKET_RISK"
    elif base["derivatives_pricing"] and _has_any(t, [r"\bxva\b", r"\bcva\b", r"\bdva\b", r"\bfva\b"]):
        role_family = "XVA"
    elif base["derivatives_pricing"]:
        role_family = "PRICING"
    elif _has_any(t, [r"\bstructuring\b", r"\bstructurer\b"]):
        role_family = "STRUCTURING"
    elif _has_any(t, [r"\btrading\b", r"\btrader\b"]):
        role_family = "TRADING"
    elif _has_any(t, [r"\bvaluation\b", r"\bp&l\b", r"\bpnl\b", r"\bindependent price verification\b", r"\bipv\b"]):
        role_family = "P&L_VALUATION"
    elif _has_any(t, [r"\btooling\b", r"\bfront office tools\b", r"\btrade capture\b", r"\bpricing library\b"]):
        role_family = "FO_TOOLS"
    elif _has_any(t, [r"\bdata scientist\b", r"\bmachine learning\b", r"\bml\b", r"\bdata science\b"]):
        role_family = "DATA_SCIENCE"
    elif _has_any(t, [r"\bproduct control\b"]):
        role_family = "PRODUCT_CONTROL"
    elif _has_any(t, [r"\bal m\b", r"\bal\-m\b", r"\basset liability\b"]):
        role_family = "ALM"
    elif _has_any(t, [r"\bcompliance\b", r"\bam l\b", r"\bkyt\b", r"\bkyc\b"]):
        role_family = "COMPLIANCE"
    elif _has_any(t, [r"\boperations?\b", r"\bsettlement\b", r"\breconciliation\b"]):
        role_family = "OPERATIONS"

    base["role_family"] = role_family

    # role_type ∈ {FRONT_OFFICE, FRONT_SUPPORT, MIDDLE_OFFICE, CONTROL, BACK_OFFICE, RESEARCH, UNKNOWN}
    role_type = None
    if _has_any(t, [r"\bfront office\b", r"\btrading desk\b"]):
        role_type = "FRONT_OFFICE"
    elif _has_any(t, [r"\bmiddle office\b"]):
        role_type = "MIDDLE_OFFICE"
    elif _has_any(t, [r"\bback office\b", r"\bsettlement\b", r"\breconciliation\b"]):
        role_type = "BACK_OFFICE"
    elif _has_any(t, [r"\bmodel validation\b", r"\bresearch\b", r"\bquant research\b"]):
        # prudence: model validation est souvent CONTROL/FRONT_SUPPORT, research -> RESEARCH
        if _has_any(t, [r"\bquant research\b", r"\bresearch\b"]):
            role_type = "RESEARCH"
        else:
            role_type = "CONTROL"
    elif _has_any(t, [r"\brisk\b", r"\bmarket risk\b", r"\bcounterparty\b"]):
        # risque peut être MO/Control; prudence -> MIDDLE_OFFICE si "risk management", sinon UNKNOWN
        if _has_any(t, [r"\brisk management\b", r"\brisk department\b"]):
            role_type = "MIDDLE_OFFICE"
        else:
            role_type = None

    base["role_type"] = role_type

    # -----------------------------
    # QUANT INTENSITY (déterministe selon tes règles)
    # base = 0
    # +3 si mention explicite de (pricing/stochastic/PDE/Monte Carlo/calibration/Greeks/VaR/stress testing/XVA)
    # +2 si Python requis, +1 si SQL requis, +1 si VBA, +1 si C++
    # +2 si ML/AI/deep learning requis
    # +2 si production-quality code (git, CI, tests, pipelines, refactor performance)
    # -3 si reporting_heavy=true
    # borne 0..10
    qi = 0

    if _has_any(t, [
        r"\bpricing\b", r"\bstochastic\b", r"\bpde\b", r"\bmonte carlo\b",
        r"\bcalibration\b", r"\bgreeks?\b", r"\bvar\b", r"\bstress testing\b",
        r"\bxva\b", r"\bcva\b", r"\bdva\b", r"\bfva\b"
    ]):
        qi += 3

    if "Python" in tools:
        qi += 2
    if "SQL" in tools:
        qi += 1
    if "VBA" in tools:
        qi += 1
    if "C++" in tools:
        qi += 1

    if _has_any(t, [
        r"\bmachine learning\b",
        r"\bdeep learning\b",
        r"\bai\b",
        r"\bml\b",
        r"\bia\b",
        r"\bintelligence artificielle\b"
    ]):
        qi += 2

    if _has_any(t, [
        r"\bgit\b", r"\bci\b", r"\bcd\b", r"\bunit tests?\b", r"\bpipeline(s)?\b",
        r"\brefactor\b", r"\bperformance\b", r"\bcode review\b"
    ]):
        qi += 2

    if base["reporting_heavy"]:
        qi -= 3

    qi = max(0, min(10, qi))
    base["quant_intensity"] = qi

    # -----------------------------
    # RED FLAGS (standard tags)
    # -----------------------------
    red_flags = set()
    if base["reporting_heavy"]:
        red_flags.add("REPORTING")
    if base["quant_research_phd_mandatory"]:
        red_flags.add("PHD_ONLY")
    if base["cxx_hardcore"]:
        red_flags.add("CXX_HARDCORE")
    base["red_flags"] = sorted(red_flags)

    return base


def extract_job(raw_text: str) -> Dict:
    deterministic = _deterministic_extract(raw_text)

    # LLM merge optionnel plus tard (ne bloque jamais)
    try:
        prompt_text = load_prompt("prompts/01_extract_job.md")
        full_prompt = prompt_text + "\n\nJOB_TEXT:\n" + raw_text
        llm_res = call_llm(full_prompt)
        if isinstance(llm_res, dict) and llm_res:
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