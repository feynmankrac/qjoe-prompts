# config.py — source unique de configuration

import os
from pathlib import Path
from dotenv import load_dotenv

# --- Load .env if present ---
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

# --- Feature flags ---
USE_LLM = os.getenv("USE_LLM", "0") == "1"
ENABLE_TELEGRAM = os.getenv("ENABLE_TELEGRAM", "0") == "1"
ENABLE_GMAIL_DRAFT = os.getenv("ENABLE_GMAIL_DRAFT", "1") == "1"

# --- Batch behavior ---
PROCESS_ONLY_STATUS = os.getenv("PROCESS_ONLY_STATUS", "")
MAX_ROWS_PER_RUN = int(os.getenv("MAX_ROWS_PER_RUN", "50"))
DRY_RUN = os.getenv("DRY_RUN", "0") == "1"

# --- Paths ---
SECRETS_DIR = Path(os.getenv("SECRETS_DIR", "secrets"))
ARTIFACTS_DIR = Path(os.getenv("ARTIFACTS_DIR", "artifacts"))

GOOGLE_CREDENTIALS_JSON_PATH = os.getenv(
    "GOOGLE_CREDENTIALS_JSON_PATH",
    str(SECRETS_DIR / "credentials.json")
)

GMAIL_TOKEN_JSON_PATH = os.getenv(
    "GMAIL_TOKEN_JSON_PATH",
    str(SECRETS_DIR / "gmail_token.json")
)

# --- Google Drive ---
GOOGLE_DRIVE_ENABLED = os.getenv("GOOGLE_DRIVE_ENABLED", "1") == "1"
DRIVE_FOLDER_CV = os.getenv("DRIVE_FOLDER_CV", "QJOE_CV")
DRIVE_FOLDER_COVER = os.getenv("DRIVE_FOLDER_COVER", "QJOE_COVER")

# --- Google Sheets ---
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

# --- Telegram ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- Output naming ---
ARTIFACT_NAME_FORMAT = os.getenv(
    "ARTIFACT_NAME_FORMAT",
    "{row}_{family}_{score}_{ts}"
)

# --- LLM ---
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "800"))
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))

# --- Lock ---
LOCK_PATH = os.getenv("LOCK_PATH", "/tmp/qjoe.lock")