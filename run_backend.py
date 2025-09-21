#!/usr/bin/env python3
"""
Скрипт для запуска backend сервера
"""

import sys
import os

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from model_fixed import app
    print("🚀 Запуск Career on Autopilot Backend...")
    print("📡 API доступно по адресу: http://localhost:5000")
    print("🤖 AI чат: POST http://localhost:5000/chat")
    print("👤 Данные сотрудника: GET http://localhost:5000/api/employee/123")
    print("🔍 Поиск сотрудников: POST http://localhost:5000/api/employees/search")
    print("\nДля остановки нажмите Ctrl+C")
    print("-" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
    
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Убедитесь, что установлены все зависимости:")
    print("pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Ошибка запуска: {e}")
    sys.exit(1)
