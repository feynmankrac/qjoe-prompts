import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


#HEADERS = {
    #"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
#}
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
}




def scrape_url(url: str) -> dict:
    try:
        #response = requests.get(url, headers=HEADERS, timeout=10)
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code != 200:
            return {"ok": False, "error": f"HTTP_{response.status_code}"}

        soup = BeautifulSoup(response.text, "lxml")

        for tag in soup(["script", "style", "noscript"]):
            tag.extract()

        text = soup.get_text(separator="\n")
        text = "\n".join(line.strip() for line in text.splitlines() if line.strip())

        # 🔥 On envoie le texte complet (troncation sécurité)
        full_text = text[:20000] if len(text) > 20000 else text
        return {"ok": True, "text": full_text, "note": "RAW_FULL"}

        # fallback brut
        fallback = text[:20000] if len(text) > 20000 else text

        # 🔥 JS-only probable → fallback Playwright
        if len(text) < 1000:
            try:
                browser_html = scrape_with_browser(url)
                soup_browser = BeautifulSoup(browser_html, "lxml")

                for tag in soup_browser(["script", "style", "noscript"]):
                    tag.extract()

                text_browser = soup_browser.get_text(separator="\n")
                text_browser = "\n".join(
                    line.strip()
                    for line in text_browser.splitlines()
                    if line.strip()
                )

                return {
                    "ok": True,
                    "text": text_browser[:20000],
                    "note": "PLAYWRIGHT"
                }

            except Exception as e:
                return {"ok": False, "error": f"PLAYWRIGHT_FAIL_{str(e)}"}

        return {"ok": True, "text": fallback, "note": "FALLBACK_RAW"}

    except Exception as e:
        return {"ok": False, "error": str(e)}
def filter_relevant_sections(text: str) -> str:
    keep_keywords = [
        "pricing", "valuation", "model", "risk", "var", "stress",
        "monte", "pde", "calibration", "derivative", "xva",
        "hedging", "volatility", "stochastic",
        "python", "c++", "sql", "pipeline", "backtesting",
        "requirements", "responsibilities", "mission"
    ]

    drop_keywords = [
        "why join", "diversity", "values", "benefits",
        "culture", "inclusion", "about us",
        "equal opportunity", "who we are"
    ]

    paragraphs = text.split("\n\n")
    kept = []

    for p in paragraphs:
        lower = p.lower()

        if any(dk in lower for dk in drop_keywords):
            continue

        if any(kk in lower for kk in keep_keywords):
            kept.append(p.strip())

    return "\n\n".join(kept)


def scrape_with_browser(url: str, timeout: int = 15000) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto(url, timeout=timeout, wait_until="networkidle")

        # 🔥 accepter tous boutons possibles
        try:
            page.locator("button").filter(has_text="Accept").first.click(timeout=2000)
        except:
            pass
        try:
            page.locator("button").filter(has_text="Tout accepter").first.click(timeout=2000)
        except:
            pass

        page.wait_for_timeout(3000)

        content = page.content()
        browser.close()
        return content

# def filter_relevant_sections(text: str) -> str:
#     keep_keywords = [
#         "pricing", "valuation", "model", "risk", "var", "stress",
#         "monte", "pde", "calibration", "derivative", "xva",
#         "hedging", "volatility", "stochastic",
#         "python", "c++", "sql", "pipeline", "backtesting",
#         "requirements", "responsibilities", "mission"
#     ]
#
#     drop_keywords = [
#         "why join", "diversity", "values", "benefits",
#         "culture", "inclusion", "about us",
#         "equal opportunity", "who we are"
#     ]
#
#     filtered_lines = []
#
#     for line in text.split("\n"):
#         lower = line.lower()
#
#         if any(dk in lower for dk in drop_keywords):
#             continue
#
#         if any(kk in lower for kk in keep_keywords):
#             filtered_lines.append(line.strip())
#
#     return "\n".join(filtered_lines)