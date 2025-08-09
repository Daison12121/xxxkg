#!/usr/bin/env python3
import os
import sys
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import asyncio
import json

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

# Создаем Application
application = Application.builder().token(TOKEN).build()

# Обработчики бота
async def start(update: Update, context):
    await update.message.reply_text("Привет! Бот работает 🚀")

async def echo_text(update: Update, context):
    await update.message.reply_text(f"Ты написал: {update.message.text}")

async def handle_photo(update: Update, context):
    await update.message.reply_text("Фото получил! 📸")

# Добавляем обработчики
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_text))
application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

# Инициализация приложения
async def init_app():
    await application.initialize()
    await application.start()

# Обработка update
async def process_telegram_update(update_data):
    try:
        update = Update.de_json(update_data, application.bot)
        await application.process_update(update)
        return True
    except Exception as e:
        logging.error(f"❌ Ошибка обработки update: {e}")
        return False

# Инициализируем приложение при запуске
try:
    asyncio.run(init_app())
    logging.info("✅ Application инициализировано")
except Exception as e:
    logging.error(f"❌ Ошибка инициализации: {e}")

@app.route("/")
def home():
    logging.info("=== ПОЛУЧЕН ЗАПРОС НА ГЛАВНУЮ СТРАНИЦУ ===")
    return f"""
    <h1>🎉 FLASK СЕРВЕР РАБОТАЕТ!</h1>
    <p><strong>Port:</strong> {PORT}</p>
    <p><strong>Token:</strong> {TOKEN[:10]}...</p>
    <p><strong>Webhook URL:</strong> {WEBHOOK_URL}</p>
    <p><strong>Python:</strong> {sys.version}</p>
    <hr>
    <p><a href="/set_webhook">🔗 Установить вебхук</a></p>
    <p><a href="/health">❤️ Health Check</a></p>
    """, 200

@app.route("/health")
def health():
    return "OK", 200

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    """Получение апдейтов от Telegram"""
    try:
        # Получаем JSON данные
        json_data = request.get_json(force=True)
        if not json_data:
            logging.error("❌ Пустые данные в webhook")
            return "ERROR", 400
        
        logging.info(f"📨 Получен webhook: {json.dumps(json_data, ensure_ascii=False)[:200]}...")
        
        # Обрабатываем в новом event loop
        success = asyncio.run(process_telegram_update(json_data))
        
        if success:
            logging.info("✅ Update успешно обработан")
            return "OK", 200
        else:
            logging.error("❌ Ошибка обработки update")
            return "ERROR", 500
            
    except Exception as e:
        logging.error(f"❌ Критическая ошибка в webhook: {e}")
        import traceback
        logging.error(f"❌ Traceback: {traceback.format_exc()}")
        return "ERROR", 500

@app.route("/set_webhook")
def set_webhook_route():
    """Маршрут для установки вебхука"""
    try:
        import requests
        url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
        data = {"url": WEBHOOK_URL}
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            result = response.json()
            logging.info(f"✅ Вебхук установлен: {WEBHOOK_URL}")
            logging.info(f"📋 Ответ Telegram: {result}")
            return f"✅ Вебхук установлен: {WEBHOOK_URL}<br>Ответ: {result}", 200
        else:
            logging.error(f"❌ Ошибка установки вебхука: {response.text}")
            return f"❌ Ошибка: {response.text}", 500
    except Exception as e:
        logging.error(f"❌ Исключение при установке вебхука: {e}")
        return f"❌ Исключение: {e}", 500

@app.route("/webhook_info")
def webhook_info():
    """Получить информацию о текущем webhook"""
    try:
        import requests
        url = f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo"
        response = requests.get(url)
        
        if response.status_code == 200:
            result = response.json()
            return f"<pre>{json.dumps(result, indent=2, ensure_ascii=False)}</pre>", 200
        else:
            return f"❌ Ошибка: {response.text}", 500
    except Exception as e:
        return f"❌ Исключение: {e}", 500

logging.info("=== Flask приложение загружено и готово к работе ===")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False)