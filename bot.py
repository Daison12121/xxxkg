import os
import sys
import logging
from aiohttp import web
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.error import TelegramError

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
# Use a specific path for the webhook for security. Telegram will send updates to this path.
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

# Handler for the Web App HTML page
async def web_app_handler(request: web.Request) -> web.Response:
    """Handles requests for the Web App and returns the HTML page."""
    return web.Response(text=WEB_APP_HTML, content_type='text/html')

# Handler for incoming Telegram webhooks
async def telegram_webhook_handler(request: web.Request) -> web.Response:
    """
    Handles incoming webhooks from Telegram.
    This function will be called for all POST requests to the WEBHOOK_PATH.
    """
    try:
        data = await request.json()
        update = Update.de_json(data, app.bot)
        await app.process_update(update)
        return web.Response()
    except Exception as e:
        logging.error("Error processing webhook: %s", e)
        return web.Response(status=500)

# Command to send the Web App button
async def start_webapp_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a button to open the Web App."""
    if not WEBHOOK_URL:
        await update.message.reply_text("Ошибка: WEBHOOK_URL не установлен. Проверьте переменные окружения на Railway.")
        return
    
    # The URL for the web app is the base URL without the webhook path
    webapp_url = WEBHOOK_URL.split(WEBHOOK_PATH)[0]
    keyboard = [
        [InlineKeyboardButton("Открыть Web App", web_app=WebAppInfo(url=webapp_url))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Нажмите кнопку, чтобы открыть Web App:", reply_markup=reply_markup)

# Command to handle /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command."""
    await update.message.reply_text("Привет! Я готов к работе. Используйте /openweb, чтобы открыть Web App.")

def main():
    """Main function to run the bot."""
    global app
    
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
    
    # --- Изменения начинаются здесь ---
    # Создаём Aiohttp-приложение, чтобы контролировать маршруты
    server_app = web.Application()
    
    # Добавляем маршрут для Web App (GET-запросы на корневой URL)
    server_app.router.add_get('/', web_app_handler)
    
    # Запускаем Application в режиме вебхука, используя созданный нами сервер
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=WEBHOOK_PATH.strip("/"),
        webhook_url=WEBHOOK_URL,
        webhook_server=server_app # Передаем наш настроенный сервер
    )
    # --- Изменения заканчиваются здесь ---

if __name__ == '__main__':
    main()
