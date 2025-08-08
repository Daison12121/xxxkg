#!/usr/bin/env python3
import os
import sys
import logging
from flask import Flask

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

app = Flask(__name__)

@app.route('/')
def home():
    logging.info("=== ПОЛУЧЕН ЗАПРОС НА ГЛАВНУЮ СТРАНИЦУ ===")
    
    port = os.environ.get('PORT', 'НЕ УСТАНОВЛЕНА')
    railway_env = os.environ.get('RAILWAY_ENVIRONMENT', 'НЕ УСТАНОВЛЕНА')
    
    return f"""
    <html>
    <head><title>Flask Simple Test</title></head>
    <body>
        <h1>🎉 FLASK СЕРВЕР РАБОТАЕТ!</h1>
        <p><strong>Port:</strong> {port}</p>
        <p><strong>Railway Environment:</strong> {railway_env}</p>
        <p><strong>Python:</strong> {sys.version}</p>
        <h2>Environment Variables:</h2>
        <ul>
            <li><strong>PORT:</strong> {port}</li>
            <li><strong>RAILWAY_ENVIRONMENT:</strong> {railway_env}</li>
            <li><strong>RAILWAY_PROJECT_ID:</strong> {os.environ.get('RAILWAY_PROJECT_ID', 'НЕ УСТАНОВЛЕНА')}</li>
        </ul>
    </body>
    </html>
    """

@app.route('/health')
def health():
    logging.info("=== ПОЛУЧЕН ЗАПРОС НА HEALTH CHECK ===")
    return 'OK', 200

# Gunicorn будет использовать этот app
logging.info("=== Flask приложение загружено и готово к работе ===")
