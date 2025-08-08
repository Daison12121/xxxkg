# Telegram Bot с Web App

Этот бот демонстрирует интеграцию Telegram Bot API с Web App.

## Функциональность

- `/start` - Приветственное сообщение
- `/openweb` - Открывает Web App в Telegram
- Обработка данных, отправляемых из Web App

## Настройка для Railway

1. Установите переменные окружения в Railway:
   - `BOT_TOKEN` - токен вашего бота от @BotFather
   - `WEBHOOK_URL` - URL вашего приложения на Railway (например: https://xxxkg-production.up.railway.app)

2. Деплой происходит автоматически при пуше в репозиторий

## Локальная разработка

1. Создайте файл `.env` с переменными:
   ```
   BOT_TOKEN=ваш_токен_бота
   WEBHOOK_URL=https://ваш-домен.up.railway.app
   ```

2. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```

3. Запустите бота:
   ```
   python bot.py
   ```

## Структура проекта

- `bot.py` - основной файл бота
- `requirements.txt` - зависимости Python
- `Procfile` - конфигурация для Railway
- `runtime.txt` - версия Python
- `.env` - переменные окружения (только для локальной разработки)