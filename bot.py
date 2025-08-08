import os
import sys
import logging
import asyncio
from flask import Flask, request, jsonify
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.error import TelegramError
from dotenv import load_dotenv
import threading

# Load environment variables from .env file
load_dotenv()

# Set up logging for better visibility
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load environment variables
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", "8000"))
WEBHOOK_PATH = f'/{TOKEN}'

# Web App HTML content
WEB_APP_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Моё первое Web App</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            text-align: center;
            background-color: #f0f2f5;
            padding: 20px;
        }
        .container {
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            padding: 30px;
            max-width: 400px;
            margin: 0 auto;
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
        }
        p {
            color: #666;
            line-height: 1.6;
        }
        button {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
            margin-top: 20px;
        }
        button:hover {
            background-color: #0056b3;
        }
    </style>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <script>
        function sendMessage() {
            // Отправляем данные боту
            Telegram.WebApp.sendData("Привет, бот! Я из Web App!");
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>Добро пожаловать в Web App!</h1>
        <p>Это простое веб-приложение, запущенное прямо в Telegram.</p>
        <button onclick="sendMessage()">Отправить сообщение боту</button>
    </div>
</body>
</html>
"""

# Create Flask app
app = Flask(__name__)

# Global variable to store the bot application
bot_application = None

def init_bot():
    """Initialize bot application."""
    global bot_application
    
    if not all([TOKEN, WEBHOOK_URL]):
        logging.error("Не установлены обязательные переменные окружения")
        return None
    
    # Build the Application
    bot_application = ApplicationBuilder().token(TOKEN).build()
    
    # Add command handlers
    bot_application.add_handler(CommandHandler("start", start_command))
    bot_application.add_handler(CommandHandler("openweb", start_webapp_command))
    bot_application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data_handler))
    
    # Set webhook
    async def setup_webhook():
        webhook_full_url = WEBHOOK_URL + WEBHOOK_PATH
        await bot_application.bot.set_webhook(url=webhook_full_url)
        logging.info(f"Вебхук успешно установлен на URL: {webhook_full_url}")
    
    # Run webhook setup in a separate thread
    def run_webhook_setup():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(setup_webhook())
        loop.close()
    
    setup_thread = threading.Thread(target=run_webhook_setup)
    setup_thread.start()
    setup_thread.join()
    
    logging.info("Bot application инициализирован")
    return bot_application

@app.route('/health')
def health_check():
    """Health check endpoint."""
    logging.info("Получен запрос на /health")
    return 'OK', 200

@app.route('/')
def web_app_handler():
    """Handles requests for the Web App and returns the HTML page."""
    logging.info("Получен GET-запрос на главную страницу Web App")
    return WEB_APP_HTML

@app.route(WEBHOOK_PATH, methods=['POST'])
def telegram_webhook_handler():
    """Handles incoming webhooks from Telegram."""
    try:
        data = request.get_json()
        logging.info(f"Получен вебхук от Telegram: {data.get('update_id', 'unknown')}")
        
        if not bot_application:
            logging.error("Bot application не инициализирован")
            return 'Bot not initialized', 500
        
        update = Update.de_json(data, bot_application.bot)
        
        if not update:
            logging.warning("Не удалось создать объект Update из данных вебхука")
            return 'Invalid update data', 400
        
        # Process the update with the bot application in a separate thread
        def process_update():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(bot_application.process_update(update))
            loop.close()
        
        thread = threading.Thread(target=process_update)
        thread.start()
        
        logging.info("Вебхук обработан успешно")
        return 'OK'
        
    except Exception as e:
        logging.error("Ошибка при обработке вебхука: %s", e, exc_info=True)
        return f'Error: {e}', 500

# Command handlers
async def start_webapp_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a button to open the Web App."""
    try:
        logging.info(f"Получена команда /openweb от пользователя {update.effective_user.id}")
        
        webapp_url = WEBHOOK_URL.rstrip('/')
        logging.info(f"Используется URL для Web App: {webapp_url}")
        
        keyboard = [
            [InlineKeyboardButton("Открыть Web App", web_app=WebAppInfo(url=webapp_url))]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Нажмите кнопку, чтобы открыть Web App:", reply_markup=reply_markup)
        logging.info("Кнопка Web App отправлена успешно")
        
    except Exception as e:
        logging.error(f"Ошибка при обработке команды /openweb: {e}")
        await update.message.reply_text("Произошла ошибка при создании Web App.")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command."""
    try:
        logging.info(f"Получена команда /start от пользователя {update.effective_user.id}")
        await update.message.reply_text("Привет! Я готов к работе. Используйте /openweb, чтобы открыть Web App.")
        logging.info("Ответ на команду /start отправлен успешно")
    except Exception as e:
        logging.error(f"Ошибка при обработке команды /start: {e}")
        await update.message.reply_text("Произошла ошибка при обработке команды.")

async def web_app_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles data sent from the Web App."""
    try:
        if update.message.web_app_data:
            data = update.message.web_app_data.data
            logging.info(f"Получены данные от Web App: {data}")
            await update.message.reply_text(f"Получено сообщение от Web App: {data}")
        else:
            logging.warning("Получено сообщение без данных Web App")
    except Exception as e:
        logging.error(f"Ошибка при обработке данных Web App: {e}")
        await update.message.reply_text("Ошибка при обработке данных от Web App.")

# Initialize bot when module is imported
init_bot()

if __name__ == '__main__':
    logging.info("Запуск Flask веб-сервера...")
    app.run(host='0.0.0.0', port=PORT, debug=False)