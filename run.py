import threading
import time
import uvicorn
import webview
from app.main import app

def start_server():
    # Запускаем сервер с отключенными системными сигналами (чтобы не было конфликтов в потоках)
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="info")
    server = uvicorn.Server(config)
    server.install_signal_handlers = lambda: None
    server.run()

if __name__ == '__main__':
    # 1. Запускаем сервер в фоновом потоке
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # 2. Ждем 4 секунды, чтобы сервер точно успел загрузить все таблицы
    print("Запуск сервера... Пожалуйста, подождите.")
    time.sleep(4)

    # 3. Создаем и открываем окно приложения
    print("Открываем окно...")
    webview.create_window(
        title="AI ERP - Моя система", 
        url="http://127.0.0.1:8000", 
        width=1280, 
        height=800,
        min_size=(800, 600)
    )
    
    # Запускаем окно (программа будет работать, пока вы его не закроете)
    webview.start()