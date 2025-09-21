#!/usr/bin/env python3
"""
Скрипт для запуска backend сервера
"""

import sys
import os

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем и вызываем функцию настройки БД
from database import setup_database


if __name__ == "__main__":
    # Инициализируем базу данных при старте
    setup_database()

    try:
        # Импортируем Flask app ПОСЛЕ настройки БД
        from model import app 
        print("\n🚀 Запуск Career on Autopilot Backend...")
        print("📡 API доступно по адресу: http://localhost:5000")
        print("🤖 AI чат: POST http://localhost:5000/chat")
        print("👤 Данные сотрудника: GET http://localhost:5000/api/employee/123")
        print("🔍 Поиск сотрудников: POST http://localhost:5000/api/employees/search")
        print("\nДля остановки нажмите Ctrl+C")
        print("-" * 50)
        
        # Запускаем Flask приложение
        # debug=False, так как автоперезагрузка может вызывать повторную инициализацию БД
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Убедитесь, что установлены все зависимости:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        sys.exit(1)
