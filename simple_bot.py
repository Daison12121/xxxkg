import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
import threading

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load environment variables
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = f'/{TOKEN}'

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
    
    # Set webhook in background
    def setup_webhook_background():
        async def setup_webhook():
            webhook_full_url = WEBHOOK_URL + WEBHOOK_PATH
            await bot_application.bot.set_webhook(url=webhook_full_url)
            logging.info(f"Вебхук успешно установлен на URL: {webhook_full_url}")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(setup_webhook())
        loop.close()
    
    setup_thread = threading.Thread(target=setup_webhook_background)
    setup_thread.daemon = True
    setup_thread.start()
    
    logging.info("Bot application инициализирован")
    return bot_application

@app.route('/health')
def health_check():
    """Health check endpoint."""
    logging.info("=== ПОЛУЧЕН ЗАПРОС НА /health ===")
    return 'OK', 200

@app.route('/')
def home():
    """Home page."""
    logging.info("=== ПОЛУЧЕН ЗАПРОС НА ГЛАВНУЮ СТРАНИЦУ ===")
    return 'Telegram Bot is running!'

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
        
        # Process the update
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

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command."""
    try:
        logging.info(f"Получена команда /start от пользователя {update.effective_user.id}")
        await update.message.reply_text("Привет! Я работаю на Railway! 🚀")
        logging.info("Ответ на команду /start отправлен успешно")
    except Exception as e:
        logging.error(f"Ошибка при обработке команды /start: {e}")
        await update.message.reply_text("Произошла ошибка при обработке команды.")

# Initialize bot when module is imported
init_bot()
logging.info("Простой бот готов к работе!")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    logging.info(f"Запуск Flask сервера на порту: {port}")
    logging.info(f"Переменная PORT из окружения: {os.environ.get('PORT', 'НЕ УСТАНОВЛЕНА')}")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)