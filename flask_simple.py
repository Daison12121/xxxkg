#!/usr/bin/env python3
import os
import sys
import logging
from flask import Flask

# Set up logging
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
            <li><strong>PORT:</strong> {os.environ.get('PORT', 'НЕ УСТАНОВЛЕНА')}</li>
            <li><strong>RAILWAY_ENVIRONMENT:</strong> {os.environ.get('RAILWAY_ENVIRONMENT', 'НЕ УСТАНОВЛЕНА')}</li>
            <li><strong>RAILWAY_PROJECT_ID:</strong> {os.environ.get('RAILWAY_PROJECT_ID', 'НЕ УСТАНОВЛЕНА')}</li>
        </ul>
    </body>
    </html>
    """

@app.route('/health')
def health():
    logging.info("=== ПОЛУЧЕН ЗАПРОС НА HEALTH CHECK ===")
    return 'OK', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    
    logging.info(f"=== ЗАПУСК FLASK СЕРВЕРА ===")
    logging.info(f"=== PORT: {port} ===")
    logging.info(f"=== RAILWAY_ENVIRONMENT: {os.environ.get('RAILWAY_ENVIRONMENT', 'НЕ УСТАНОВЛЕНА')} ===")
    
    # Запускаем Flask development server
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )