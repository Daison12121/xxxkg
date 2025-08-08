import os
import logging
from flask import Flask

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

app = Flask(__name__)

@app.route('/')
def hello():
    logging.info("=== ПОЛУЧЕН ЗАПРОС НА ГЛАВНУЮ СТРАНИЦУ ===")
    return 'Hello from Railway! Server is working!'

@app.route('/health')
def health():
    logging.info("=== ПОЛУЧЕН ЗАПРОС НА /health ===")
    return 'OK'

@app.route('/test')
def test():
    logging.info("=== ПОЛУЧЕН ЗАПРОС НА /test ===")
    port = os.environ.get('PORT', 'НЕ УСТАНОВЛЕНА')
    return f'Test endpoint working! PORT={port}'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    logging.info(f"=== ЗАПУСК ТЕСТОВОГО СЕРВЕРА НА ПОРТУ: {port} ===")
    logging.info(f"=== ПЕРЕМЕННАЯ PORT: {os.environ.get('PORT', 'НЕ УСТАНОВЛЕНА')} ===")
    app.run(host='0.0.0.0', port=port, debug=True)