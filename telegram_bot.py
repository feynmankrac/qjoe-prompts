import os

import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import json
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_KEY = os.getenv("QJOE_API_TOKEN")

#TOKEN = "8752014640:AAH2ifMXh--vfY1MzkKzjMuVk-uMbMVMxkU"
API_URL = "http://127.0.0.1:8000/run_batch"
SPONT_URL = "http://localhost:8000/run_spontaneous"
HEALTH_URL = "http://127.0.0.1:8000/health"
#API_KEY = "c5eafd20e696c1640d03793ff870b91aac922a905090ee81907bca513d8a967b"

ALLOWED_USER = 5428800302  # remplace par ton Telegram ID


def allowed(update):
    return update.effective_user.id == ALLOWED_USER


async def run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return

    r = requests.post(API_URL, headers={"x-api-key": API_KEY})
    await update.message.reply_text("Batch started")


async def health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return

    r = requests.get(HEALTH_URL, headers={"x-api-key": API_KEY})
    await update.message.reply_text(r.text)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return

    try:
        with open("artifacts/last_run.json") as f:
            data = json.load(f)

        ts = data.get("run_meta", {}).get("ts")
        decision = data.get("final_decision")
        score = data.get("score", {}).get("score_0_100")
        company = data.get("job_json", {}).get("company")
        role = data.get("job_json", {}).get("role_title")

        msg = (
            f"{company} — {role}\n"
            f"score: {score}\n"
            f"decision: {decision}\n"
            f"time: {ts}"
        )

        await update.message.reply_text(msg)

    except Exception as e:
        await update.message.reply_text(str(e))

async def spont(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return

    r = requests.post(SPONT_URL, headers={"x-api-key": API_KEY})

    await update.message.reply_text(f"{r.status_code} {r.text}")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("run", run))
app.add_handler(CommandHandler("spont", spont))
app.add_handler(CommandHandler("health", health))
app.add_handler(CommandHandler("status", status))

app.run_polling()
