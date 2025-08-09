#!/usr/bin/env python3
"""
Скрипт для установки и проверки webhook на Railway
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
RAILWAY_URL = "https://xxxkg-production.up.railway.app"  # Замените на ваш URL

def get_webhook_info():
    """Получить информацию о текущем webhook"""
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo"
        response = requests.get(url)
        
        if response.status_code == 200:
            result = response.json()
            print("📋 Информация о webhook:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result
        else:
            print(f"❌ Ошибка получения информации: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Исключение: {e}")
        return None

def set_webhook():
    """Установить webhook"""
    webhook_url = f"{RAILWAY_URL}/{TOKEN}"
    
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
        data = {"url": webhook_url}
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook установлен: {webhook_url}")
            print(f"📋 Ответ Telegram: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ Ошибка установки webhook: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Исключение при установке webhook: {e}")
        return False

def delete_webhook():
    """Удалить webhook"""
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/deleteWebhook"
        response = requests.post(url)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook удален")
            print(f"📋 Ответ Telegram: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ Ошибка удаления webhook: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Исключение при удалении webhook: {e}")
        return False

def test_server():
    """Проверить доступность сервера"""
    try:
        response = requests.get(f"{RAILWAY_URL}/health", timeout=10)
        if response.status_code == 200:
            print(f"✅ Сервер доступен: {response.text}")
            return True
        else:
            print(f"❌ Сервер недоступен: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения к серверу: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Настройка webhook для Telegram бота...")
    print(f"🤖 Token: {TOKEN[:10]}...")
    print(f"🌐 Railway URL: {RAILWAY_URL}")
    
    print("\n1. Проверяем доступность сервера...")
    if not test_server():
        print("❌ Сервер недоступен. Проверьте деплой на Railway.")
        exit(1)
    
    print("\n2. Получаем текущую информацию о webhook...")
    current_info = get_webhook_info()
    
    print("\n3. Устанавливаем новый webhook...")
    if set_webhook():
        print("\n4. Проверяем установленный webhook...")
        get_webhook_info()
        print("\n✅ Webhook успешно настроен!")
    else:
        print("\n❌ Не удалось установить webhook")