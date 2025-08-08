import os
import sys
import logging
import asyncio
from aiohttp import web
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.error import TelegramError

# Загружаем переменные окружения, если файл .env существует.
# from dotenv import load_dotenv
# load_dotenv()

# Указываем переменные для токена и URL вебхука
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Порт для веб-сервера
WEB_SERVER_PORT = int(os.getenv("PORT", "8000"))
WEBHOOK_PATH = "/" # Используем корневой путь для вебхука

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
async def web_app_handler(request: web.Request) -> web.Response:
    """Обрабатывает запросы к корневому URL и отдаёт HTML."""
    return web.Response(text=WEB_APP_HTML, content_type='text/html')

# Функция для обработки вебхуков от Telegram
async def telegram_webhook_handler(request: web.Request) -> web.Response:
    """Обрабатывает вебхуки от Telegram."""
    try:
        data = await request.json()
        update = Update.de_json(data, app.bot)
        await app.process_update(update)
        return web.Response()
    except Exception as e:
        logging.error("Ошибка при обработке вебхука: %s", e)
        return web.Response(status=500)

# Команда для отправки кнопки Web App
async def start_webapp_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет кнопку для открытия Web App."""
    webapp_url = WEBHOOK_URL
    if not webapp_url:
        await update.message.reply_text("Ошибка: WEBHOOK_URL не установлен в переменных окружения. Пожалуйста, проверьте настройки Railway.")
        return

    keyboard = [
        [InlineKeyboardButton("Открыть Web App", web_app=WebAppInfo(url=webapp_url))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Нажмите кнопку, чтобы открыть Web App:", reply_markup=reply_markup)

# Функция для команды /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает команду /start."""
    await update.message.reply_text("Привет! Я готов к работе. Используйте /openweb, чтобы открыть Web App.")
    
async def setup_webhook():
    """Асинхронная функция для установки вебхука."""
    try:
        await app.bot.set_webhook(WEBHOOK_URL)
        logging.info("Вебхук успешно установлен.")
    except TelegramError as e:
        logging.error(f"Ошибка Telegram при установке вебхука: {e}")
        # Проверяем, если URL недействителен, завершаем работу приложения.
        if "invalid webhook" in str(e):
             logging.error("Недействительный URL вебхука. Пожалуйста, проверьте переменную окружения WEBHOOK_URL.")
             sys.exit(1)

def main():
    """Запускает бота."""
    global app
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    if not all([TOKEN, WEBHOOK_URL]):
        logging.error("Не установлены обязательные переменные окружения: BOT_TOKEN, WEBHOOK_URL.")
        sys.exit(1)
        
    logging.info(f"Используемый WEBHOOK_URL: {WEBHOOK_URL}")

    # Создаем объект Application
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("openweb", start_webapp_command))

    # Асинхронно устанавливаем вебхук перед запуском сервера
    try:
        asyncio.run(setup_webhook())
    except Exception as e:
        logging.error("Ошибка при установке вебхука: %s", e)
        sys.exit(1)

    # Создаем aiohttp приложение, которое будет обслуживать веб-приложение
    aiohttp_app = web.Application()
    aiohttp_app.add_routes([
        web.get('/', web_app_handler), # Обработчик для Web App
        web.post(WEBHOOK_PATH, telegram_webhook_handler) # Обработчик для вебхуков
    ])

    # Запускаем aiohttp сервер.
    web.run_app(aiohttp_app, host='0.0.0.0', port=WEB_SERVER_PORT)


if __name__ == "__main__":
    main()
