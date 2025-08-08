#!/usr/bin/env python3
import os
import sys
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application

# --- Логирование ---
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- Flask ---
app = Flask(__name__)

# --- Переменные окружения ---
PORT = int(os.environ.get("PORT", 8080))
TOKEN = os.environ.get("BOT_TOKEN")  # Установи в Railway Variables
WEBHOOK_URL = f"https://{os.environ.get('RAILWAY_STATIC_URL', 'xxxkg-production.up.railway.app')}/{TOKEN}"

# --- Telegram bot ---
application = Application.builder().token(TOKEN).build()

# Пример хэндлера
from telegram.ext import CommandHandler
async def start(update: Update, context):
    await update.message.reply_text("Привет! Бот работает на Railway 🚀")

application.add_handler(CommandHandler("start", start))


# --- Flask маршруты ---
@app.route("/")
def home():
    logging.info("=== ПОЛУЧЕН ЗАПРОС НА ГЛАВНУЮ СТРАНИЦУ ===")
    return f"""
    <h1>🎉 FLASK СЕРВЕР РАБОТАЕТ!</h1>
    <p>Port: {PORT}</p>
    <p>Python: {sys.version}</p>
    """

@app.route("/health")
def health():
    logging.info("=== ПОЛУЧЕН ЗАПРОС НА HEALTH CHECK ===")
    return "OK", 200

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    """Получение апдейтов от Telegram"""
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200


# --- Запуск вебхука при старте ---
@app.before_first_request
def init_webhook():
    logging.info("=== УСТАНАВЛИВАЕМ ВЕБХУК ===")
    application.bot.set_webhook(url=WEBHOOK_URL)


# Gunicorn будет использовать app
logging.info("=== Flask приложение загружено и готово к работе ===")
