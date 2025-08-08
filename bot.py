import os
import sys
import logging
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from aiohttp import web

# Загружаем переменные окружения, если файл .env существует.
# from dotenv import load_dotenv
# load_dotenv()

# Указываем переменные для токена и URL вебхука
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Порт для веб-сервера
WEB_SERVER_PORT = int(os.getenv("PORT", "8000"))

# Веб-приложение
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

# Функция, которая будет отдавать HTML-страницу
async def web_app_handler(request):
    return web.Response(text=WEB_APP_HTML, content_type='text/html')

# Команда для отправки кнопки Web App
async def start_webapp_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    webapp_url = WEBHOOK_URL
    keyboard = [
        [InlineKeyboardButton("Открыть Web App", web_app=WebAppInfo(url=webapp_url))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Нажмите кнопку, чтобы открыть Web App:", reply_markup=reply_markup)

# Функция для команды /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Я готов к работе. Используйте /openweb, чтобы открыть Web App.")

def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    if not all([TOKEN, WEBHOOK_URL]):
        logging.error("Не установлены обязательные переменные окружения: BOT_TOKEN, WEBHOOK_URL.")
        sys.exit(1)

    # Создаем объект Application
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("openweb", start_webapp_command))

    # Добавляем маршрут для нашего веб-приложения во встроенный веб-сервер
    # Исправлено: теперь мы используем app.web_app вместо app.updater.web_app
    app.web_app.router.add_get("/", web_app_handler)

    # Запускаем бота в режиме вебхука без аргумента web_server
    app.run_webhook(
        listen="0.0.0.0",
        port=WEB_SERVER_PORT,
        url_path="",
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    main()
