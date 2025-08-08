import os
import sys
import logging
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

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
WEBHOOK_PATH = f'/{TOKEN}'

async def setup_webhook():
    """Setup webhook for the bot."""
    logging.info(f"BOT_TOKEN установлен: {'Да' if TOKEN else 'Нет'}")
    logging.info(f"WEBHOOK_URL установлен: {'Да' if WEBHOOK_URL else 'Нет'}")
    
    if not all([TOKEN, WEBHOOK_URL]):
        logging.error("Не установлены обязательные переменные окружения: BOT_TOKEN, WEBHOOK_URL.")
        sys.exit(1)

    logging.info(f"Используемый WEBHOOK_URL: {WEBHOOK_URL}")

    # Build the Application
    logging.info("Создание Telegram Application...")
    application = ApplicationBuilder().token(TOKEN).build()
    logging.info("Telegram Application создан успешно")

    # Set webhook
    webhook_full_url = WEBHOOK_URL + WEBHOOK_PATH
    await application.bot.set_webhook(url=webhook_full_url)
    logging.info(f"Вебхук успешно установлен на URL: {webhook_full_url}")

if __name__ == '__main__':
    asyncio.run(setup_webhook())