import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "my-secret-path")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")

app = Flask(__name__)
telegram_app = Application.builder().token(BOT_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот работает на Render 🚀")


telegram_app.add_handler(CommandHandler("start", start))


@app.route("/")
def home():
    return "Bot is running!", 200


@app.route(f"/webhook/{WEBHOOK_SECRET}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)

    async def process():
        await telegram_app.initialize()
        await telegram_app.process_update(update)

    asyncio.run(process())
    return "ok", 200


@app.route("/set_webhook")
def set_webhook():
    if not RENDER_EXTERNAL_URL:
        return "RENDER_EXTERNAL_URL not found", 500

    webhook_url = f"{RENDER_EXTERNAL_URL}/webhook/{WEBHOOK_SECRET}"

    async def do_set():
        await telegram_app.initialize()
        result = await telegram_app.bot.set_webhook(url=webhook_url)
        return result

    result = asyncio.run(do_set())
    return f"Webhook set: {result} -> {webhook_url}", 200
