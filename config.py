# config.py — source unique de configuration

# --- Feature flags ---
USE_LLM = False              # LLM purement optionnel (style), jamais décisionnel
ENABLE_TELEGRAM = False
ENABLE_GMAIL_DRAFT = False

# --- Batch behavior ---
PROCESS_ONLY_STATUS = ""  # ne traite que les lignes NEW
MAX_ROWS_PER_RUN = 50        # sécurité (évite de tout cramer si bug)
DRY_RUN =  False           # True = calcule tout mais n’écrit rien dans le Sheet

# --- Google ---
GOOGLE_DRIVE_ENABLED = True
DRIVE_FOLDER_CV = "QJOE_CV"
DRIVE_FOLDER_COVER = "QJOE_COVER"

# --- Output naming ---
ARTIFACT_NAME_FORMAT = "{row}_{family}_{score}_{ts}"  # ex: 077_MARKET_RISK_65_2026-03-04_07-30

# --- LLM (si activé un jour) ---
LLM_PROVIDER = "openai"
OPENAI_MODEL = "gpt-4o-mini"
OPENAI_MAX_TOKENS = 800
OPENAI_TEMPERATURE = 0.2