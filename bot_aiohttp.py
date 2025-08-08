#!/usr/bin/env python3
import os
import sys
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# --- Логирование ---
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- Flask ---
app = Flask(__name__)

# --- Переменные окружения ---
PORT = int(os.environ.get("PORT", 8080))
TOKEN = os.environ.get("BOT_TOKEN")  # Railway Variables
WEBHOOK_URL = f"https://{os.environ.get('RAILWAY_STATIC_URL', 'xxxkg-production.up.railway.app')}/{TOKEN}"

# --- Telegram bot ---
application = Application.builder().token(TOKEN).build()

# --- Хэндлеры ---
async def start(update: Update, context):
    await update.message.reply_text("Привет! Бот работает на Railway 🚀")

async def echo_text(update: Update, context):
    await update.message.reply_text(f"Ты написал: {update.message.text}")

async def handle_photo(update: Update, context):
    await update.message.reply_text("Фото получил! 📸")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_text))
application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

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
    return "OK", 200

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    """Получение апдейтов от Telegram"""
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200

# --- Установка вебхука при запуске ---
try:
    logging.info("=== УСТАНАВЛИВАЕМ ВЕБХУК ===")
    asyncio.get_event_loop().run_until_complete(
        application.bot.set_webhook(url=WEBHOOK_URL)
    )
except Exception as e:
    logging.error(f"Ошибка при установке вебхука: {e}")

# Gunicorn будет использовать app
logging.info("=== Flask приложение загружено и готово к работе ===")
