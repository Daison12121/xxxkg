#!/usr/bin/env python3
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        logging.info(f"=== ПОЛУЧЕН GET ЗАПРОС: {self.path} ===")
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        response = f"""
        <html>
        <head><title>Simple Test Server</title></head>
        <body>
            <h1>🎉 СЕРВЕР РАБОТАЕТ!</h1>
            <p><strong>Path:</strong> {self.path}</p>
            <p><strong>Port:</strong> {os.environ.get('PORT', 'НЕ УСТАНОВЛЕНА')}</p>
            <p><strong>Python:</strong> {sys.version}</p>
            <h2>Environment Variables:</h2>
            <ul>
        """
        
        # Показываем важные переменные окружения
        important_vars = ['PORT', 'RAILWAY_ENVIRONMENT', 'RAILWAY_PROJECT_ID']
        for var in important_vars:
            value = os.environ.get(var, 'НЕ УСТАНОВЛЕНА')
            response += f"<li><strong>{var}:</strong> {value}</li>"
        
        response += """
            </ul>
        </body>
        </html>
        """
        
        self.wfile.write(response.encode())
        logging.info(f"=== ОТВЕТ ОТПРАВЛЕН ДЛЯ: {self.path} ===")

    def do_POST(self):
        logging.info(f"=== ПОЛУЧЕН POST ЗАПРОС: {self.path} ===")
        self.do_GET()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    host = '0.0.0.0'
    
    logging.info(f"=== ЗАПУСК ПРОСТОГО HTTP СЕРВЕРА ===")
    logging.info(f"=== HOST: {host} ===")
    logging.info(f"=== PORT: {port} ===")
    logging.info(f"=== RAILWAY_ENVIRONMENT: {os.environ.get('RAILWAY_ENVIRONMENT', 'НЕ УСТАНОВЛЕНА')} ===")
    
    try:
        server = HTTPServer((host, port), SimpleHandler)
        logging.info(f"=== СЕРВЕР СОЗДАН УСПЕШНО ===")
        logging.info(f"=== АДРЕС СЕРВЕРА: {server.server_address} ===")
        logging.info(f"=== СЕРВЕР ГОТОВ К РАБОТЕ НА http://{host}:{port} ===")
        
        server.serve_forever()
    except Exception as e:
        logging.error(f"=== ОШИБКА ЗАПУСКА СЕРВЕРА: {e} ===")
        raise
    except KeyboardInterrupt:
        logging.info("=== СЕРВЕР ОСТАНОВЛЕН ===")
        server.server_close()