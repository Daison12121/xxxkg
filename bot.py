import os
import sys
import logging
import asyncio
from aiohttp import web
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.error import TelegramError
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

# Define web server settings
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

# Handler for the Web App HTML page (GET request to '/')
async def web_app_handler(request: web.Request) -> web.Response:
    """Handles requests for the Web App and returns the HTML page."""
    return web.Response(text=WEB_APP_HTML, content_type='text/html')

# Handler for incoming Telegram webhooks (POST request to '/{TOKEN}')
async def telegram_webhook_handler(request: web.Request) -> web.Response:
    """
    Handles incoming webhooks from Telegram.
    This function will be called for all POST requests to the WEBHOOK_PATH.
    """
    try:
        # Get the bot from the app context
        app = request.app['bot_application']
        
        # Read the JSON body from the request
        data = await request.json()
        logging.info(f"Получен вебхук от Telegram: {data.get('update_id', 'unknown')}")
        
        # Create an Update object from the JSON data
        update = Update.de_json(data, app.bot)
        
        if not update:
            logging.warning("Не удалось создать объект Update из данных вебхука")
            return web.Response(status=400, text='Invalid update data')
        
        # Process the update with the bot application
        await app.process_update(update)
        logging.info("Вебхук обработан успешно")
        
        # Return a success response
        return web.Response(text='OK')
    except Exception as e:
        logging.error("Ошибка при обработке вебхука: %s", e, exc_info=True)
        return web.Response(status=500, text=f'Error: {e}')

# Command to send the Web App button
async def start_webapp_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a button to open the Web App."""
    try:
        logging.info(f"Получена команда /openweb от пользователя {update.effective_user.id}")
        
        if not WEBHOOK_URL:
            await update.message.reply_text("Ошибка: WEBHOOK_URL не установлен. Проверьте переменные окружения на Railway.")
            return
        
        # The URL for the web app is the base URL (remove the webhook path if present)
        # WEBHOOK_URL should be something like: https://xxxkg-production.up.railway.app
        # We want just the base URL for the web app
        webapp_url = WEBHOOK_URL.rstrip('/')  # Remove trailing slash if present
        
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

# Command to handle /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command."""
    try:
        logging.info(f"Получена команда /start от пользователя {update.effective_user.id}")
        await update.message.reply_text("Привет! Я готов к работе. Используйте /openweb, чтобы открыть Web App.")
        logging.info("Ответ на команду /start отправлен успешно")
    except Exception as e:
        logging.error(f"Ошибка при обработке команды /start: {e}")
        await update.message.reply_text("Произошла ошибка при обработке команды.")

# Handler for Web App data
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

async def main():
    """Main function to run the bot."""
    
    if not all([TOKEN, WEBHOOK_URL]):
        logging.error("Не установлены обязательные переменные окружения: BOT_TOKEN, WEBHOOK_URL.")
        sys.exit(1)

    logging.info(f"Используемый WEBHOOK_URL: {WEBHOOK_URL}")
    logging.info(f"Веб-сервер будет запущен на порту {PORT}")

    # Build the Application
    app = ApplicationBuilder().token(TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("openweb", start_webapp_command))
    
    # Add handler for Web App data
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data_handler))

    # --- Новая реализация начинается здесь ---
    # Создаём Aiohttp-приложение, чтобы контролировать маршруты
    server_app = web.Application()

    # Добавляем маршрут для Web App (GET-запросы на корневой URL)
    server_app.router.add_get('/', web_app_handler)
    
    # Добавляем маршрут для вебхука (POST-запросы на WEBHOOK_PATH)
    server_app.router.add_post(WEBHOOK_PATH, telegram_webhook_handler)

    # Сохраняем экземпляр Application в приложении Aiohttp
    server_app['bot_application'] = app

    # Устанавливаем вебхук в Telegram асинхронно
    # Полный URL для вебхука включает путь с токеном
    webhook_full_url = WEBHOOK_URL + WEBHOOK_PATH
    await app.bot.set_webhook(url=webhook_full_url)
    logging.info(f"Вебхук успешно установлен на URL: {webhook_full_url}")

    # Запускаем наш Aiohttp-сервер
    runner = web.AppRunner(server_app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
    await site.start()
    logging.info("Веб-сервер запущен.")

    # Эта часть кода нужна, чтобы сервер продолжал работать
    # и не завершал процесс
    try:
        while True:
            await asyncio.sleep(3600)  # Спим час
    finally:
        await runner.cleanup()

    # --- Новая реализация заканчивается здесь ---

asyncio.run(main())
