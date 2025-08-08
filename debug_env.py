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
def debug_info():
    logging.info("=== ПОЛУЧЕН ЗАПРОС НА DEBUG INFO ===")
    
    # Собираем информацию об окружении
    env_info = []
    env_info.append("=== ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ ===")
    
    important_vars = ['PORT', 'HOST', 'RAILWAY_ENVIRONMENT', 'RAILWAY_PROJECT_ID', 'RAILWAY_SERVICE_ID']
    for var in important_vars:
        value = os.environ.get(var, 'НЕ УСТАНОВЛЕНА')
        env_info.append(f"{var}: {value}")
        logging.info(f"{var}: {value}")
    
    env_info.append("\n=== ВСЕ ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ ===")
    for key, value in sorted(os.environ.items()):
        if 'TOKEN' not in key.upper() and 'SECRET' not in key.upper():  # Не показываем секреты
            env_info.append(f"{key}: {value}")
    
    return '<br>'.join(env_info)

@app.route('/health')
def health():
    logging.info("=== ПОЛУЧЕН ЗАПРОС НА /health ===")
    return 'OK'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    logging.info(f"=== ЗАПУСК DEBUG СЕРВЕРА НА ПОРТУ: {port} ===")
    app.run(host='0.0.0.0', port=port, debug=False)