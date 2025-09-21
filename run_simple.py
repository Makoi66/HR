#!/usr/bin/env python3
"""
Простой запуск backend без base_url для тестирования
"""

import sys
import os

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    
    print("🚀 Запуск простого backend для тестирования...")
    
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/')
    def home():
        return jsonify({
            "message": "Career on Autopilot API работает!",
            "status": "ok",
            "endpoints": {
                "chat": "POST /chat",
                "employee": "GET /api/employee/<id>",
                "search": "POST /api/employees/search"
            }
        })
    
    @app.route('/chat', methods=['POST'])
    def handle_chat():
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        user_query = data.get('query', '')
        user_role = data.get('role', 'employee')
        
        # Простой ответ без AI для тестирования
        if user_role == 'employee':
            response = f"Привет! Я получил ваш запрос: '{user_query}'. Это тестовый ответ от backend."
        else:
            response = f"HR запрос получен: '{user_query}'. Это тестовый ответ для поиска кандидатов."
        
        return jsonify({"response": response})
    
    @app.route('/api/employee/<int:employee_id>', methods=['GET'])
    def get_employee_data(employee_id):
        return jsonify({
            "id": employee_id,
            "name": "Test Employee",
            "role": "Test Role",
            "status": "test_data"
        })
    
    @app.route('/api/employees/search', methods=['POST'])
    def search_employees():
        data = request.get_json()
        return jsonify({
            "employees": [
                {
                    "id": 1,
                    "name": "Test Candidate",
                    "role": "Test Role",
                    "match_score": 0.95
                }
            ]
        })
    
    print("📡 API доступно по адресу: http://localhost:5000")
    print("🧪 Это тестовая версия без AI - для проверки подключения")
    print("Для остановки нажмите Ctrl+C")
    print("-" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
    
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Убедитесь, что установлены Flask и flask-cors:")
    print("pip install flask flask-cors")
    sys.exit(1)
except Exception as e:
    print(f"❌ Ошибка запуска: {e}")
    sys.exit(1)
