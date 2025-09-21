import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import OpenAI

# Импорт компонентов для работы с БД
from database import SessionLocal, SQLiteDB

# --- Инициализация приложения ---
app = Flask(__name__)
CORS(app) # Разрешаем CORS для всех маршрутов и источников

# --- Мок-клиент OpenAI (без изменений) ---
try:
    class MockOpenAI: # ... (содержимое мока без изменений)
        def __init__(self, *args, **kwargs): pass
        class MockChat:
            def __init__(self, *args, **kwargs): pass
            class MockCompletions:
                def create(self, *args, **kwargs):
                    class MockChoice: def __init__(self, message): self.message = message
                    class MockMessage: def __init__(self, content): self.content = content
                    return MockChoice(MockMessage('{"response_type": "general_advice", "data": {"message": "Я — мок-ответ от AI. Я здесь, чтобы помочь вам с карьерой!"}}'))
            @property
            def completions(self): return self.MockCompletions()
        @property
        def chat(self): return self.MockChat()
    client = MockOpenAI()
except Exception as e:
    client = None

# --- Управление сессиями БД ---
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# --- НОВЫЕ Эндпоинты для Аутентификации ---

@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Требуется Email и пароль"}), 400

    db_session = next(get_db())
    db = SQLiteDB(db_session)
    
    try:
        new_employee = db.create_employee(email, password)
        return jsonify({"message": "Регистрация прошла успешно", "employee_id": new_employee.id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 409 # 409 Conflict
    except Exception as e:
        return jsonify({"error": f"Внутренняя ошибка сервера: {e}"}), 500

@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Требуется Email и пароль"}), 400

    db_session = next(get_db())
    db = SQLiteDB(db_session)

    employee = db.authenticate_employee(email, password)
    if employee:
        return jsonify({"message": "Вход выполнен успешно", "employee_id": employee.id})
    else:
        return jsonify({"error": "Неверный email или пароль"}), 401 # 401 Unauthorized

# --- ОБНОВЛЕННЫЕ Эндпоинты для данных ---

@app.route('/api/employee/<int:employee_id>', methods=['GET', 'POST'])
def handle_employee_data(employee_id):
    db_session = next(get_db())
    db = SQLiteDB(db_session)

    # Проверка, существует ли такой сотрудник (для безопасности)
    profile = db.get_employee_profile(employee_id)
    if not profile:
        return jsonify({"error": "Сотрудник не найден"}), 404

    if request.method == 'GET':
        return jsonify(profile)

    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({"error": "Нет данных для обновления"}), 400
        
        success = db.update_employee_profile(employee_id, data)
        if success:
            return jsonify({"message": "Профиль успешно обновлен"})
        else:
            return jsonify({"error": "Не удалось обновить профиль"}), 500

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.get_json()
    user_query = data.get('query')
    employee_id = data.get('employee_id') # ID теперь приходит от клиента

    if not user_query or not employee_id:
        return jsonify({"error": "Отсутствуют query или employee_id"}), 400

    db_session = next(get_db())
    db = SQLiteDB(db_session)

    profile = db.get_employee_profile(employee_id)
    if not profile:
        return jsonify({"error": "Сотрудник не найден"}), 404
    
    # Логика промпта и вызова AI остается без изменений
    prompt = f"Ты — HR-ассистент... (Запрос сотрудника: {user_query})"
    try:
        # ... (вызов мок-клиента OpenAI)
        completion = client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "system", "content": prompt}])
        response_content = completion.message.content
        return jsonify(json.loads(response_content))
    except Exception as e:
        return jsonify({"response_type": "general_advice", "data": {"message": "AI временно недоступен."}})
