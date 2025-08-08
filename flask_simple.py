#!/usr/bin/env python3
import os
import sys
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

app = Flask(__name__)

PORT = int(os.environ.get("PORT", 8000))
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    logging.error("❌ BOT_TOKEN не найден в переменных окружения!")
    sys.exit(1)

WEBHOOK_URL = f"https://{os.environ.get('RAILWAY_STATIC_URL', 'xxxkg-production.up.railway.app')}/{TOKEN}"

application = Application.builder().token(TOKEN).build()

async def start(update: Update, context):
    await update.message.reply_text("Привет! Бот работает 🚀")

async def echo_text(update: Update, context):
    await update.message.reply_text(f"Ты написал: {update.message.text}")

async def handle_photo(update: Update, context):
    await update.message.reply_text("Фото получил! 📸")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_text))
application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

@app.route("/")
def home():
    return "<h1>Flask сервер работает ✅</h1>", 200

@app.route("/health")
def health():
    return "OK", 200

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200

@app.route("/set_webhook")
def set_webhook_route():
    """Маршрут для установки вебхука"""
    try:
        import requests
        url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
        data = {"url": WEBHOOK_URL}
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            logging.info(f"✅ Вебхук установлен: {WEBHOOK_URL}")
            return f"✅ Вебхук установлен: {WEBHOOK_URL}", 200
        else:
            logging.error(f"❌ Ошибка установки вебхука: {response.text}")
            return f"❌ Ошибка: {response.text}", 500
    except Exception as e:
        logging.error(f"❌ Исключение при установке вебхука: {e}")
        return f"❌ Исключение: {e}", 500

logging.info("=== Flask приложение загружено и готово к работе ===")
