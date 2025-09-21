import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import OpenAI

# Импорт компонентов для работы с БД
from database import SessionLocal, SQLiteDB

# --- Инициализация приложения ---
app = Flask(__name__)
CORS(app)

# --- Настройка AI клиента (используем мок) ---
try:
    class MockOpenAI:
        def __init__(self, *args, **kwargs): pass
        class MockChat:
            def __init__(self, *args, **kwargs): pass
            class MockCompletions:
                def create(self, *args, **kwargs):
                    class MockChoice:
                        def __init__(self, message): self.message = message
                    class MockMessage:
                        def __init__(self, content): self.content = content
                    # Возвращаем более релевантный мок-ответ
                    return MockChoice(MockMessage('{\n  "response_type": "learning_recommendation",\n  "data": [\n    {\n      "course_name": "Advanced Python for Web",\n      "reason": "Отличный выбор для углубления знаний в FastAPI, что соответствует вашим интересам в backend разработке.",\n      "relevance_score": 0.9\n    }\n  ]\n}'))
            @property
            def completions(self): return self.MockCompletions()
        @property
        def chat(self): return self.MockChat()
    client = MockOpenAI()
    print("🤖 Инициализирован мок-клиент OpenAI.")
except Exception as e:
    print(f"❌ Не удалось инициализировать OpenAI клиент: {e}")
    client = None

# --- Управление сессиями БД ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Endpoints ---

@app.route('/api/employee/<int:employee_id>', methods=['GET', 'POST'])
def handle_employee_data(employee_id):
    """Эндпоинт для получения и обновления данных сотрудника."""
    db_session = next(get_db())
    db = SQLiteDB(db_session)

    if request.method == 'GET':
        profile = db.get_employee_profile(employee_id)
        if not profile:
            return jsonify({"error": "Сотрудник не найден"}), 404
        return jsonify(profile)

    if request.method == 'POST': # В script.js используется POST, а не PUT
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
    """Обновленный эндпоинт для взаимодействия с AI-ассистентом."""
    if not client:
        return jsonify({"error": "AI клиент не инициализирован"}), 500

    data = request.get_json()
    user_query = data.get('query')
    employee_id = data.get('employee_id')

    if not user_query or not employee_id:
        return jsonify({"error": "Отсутствуют query или employee_id"}), 400

    db_session = next(get_db())
    db = SQLiteDB(db_session)

    # Получаем полный, актуальный профиль сотрудника
    profile = db.get_employee_profile(employee_id)
    if not profile:
        return jsonify({"error": "Сотрудник не найден"}), 404

    # Формируем более детальный промпт для AI
    prompt = f"""
    Ты — HR-ассистент 'Career on Autopilot'. 
    Твоя задача — помогать сотрудникам в карьерном развитии. 
    Отвечай на русском языке в формате JSON.

    АНАЛИЗ ПРОФИЛЯ СОТРУДНИКА:
    - Имя: {profile.get('name')}
    - Должность: {profile.get('role')}
    - Навыки: {json.dumps(profile.get('skills'), ensure_ascii=False)}
    - Карьерный путь: {json.dumps(profile.get('careerPath'), ensure_ascii=False)}
    - Профессиональные интересы (оценка от 0 до 10): {json.dumps(profile.get('interests'), ensure_ascii=False)}

    ЗАПРОС СОТРУДНИКА: "{user_query}"

    ТВОЯ ЗАДАЧА:
    Основываясь на профиле и запросе, сгенерируй JSON с рекомендациями. 
    Возможные типы ответов (`response_type`):
    1. `learning_recommendation`: Рекомендации по обучению (курсы, статьи).
    2. `project_recommendation`: Рекомендации по участию во внутренних проектах.
    3. `profile_improvement`: Советы по улучшению профиля (например, "добавить больше навыков в области DevOps").
    4. `general_advice`: Общий совет по карьере.

    СТРОГО придерживайся формата JSON. Пример:
    {{ "response_type": "learning_recommendation", "data": [{{ "course_name": "Название курса", "reason": "Почему это полезно для сотрудника", "relevance_score": 0.9 }}] }}
    """

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}]
        )
        response_content = completion.message.content
        # Убираем Markdown-обертки, если они есть
        if response_content.startswith("```json"): 
            response_content = response_content[7:-4]

        return jsonify(json.loads(response_content))

    except Exception as e:
        print(f"❌ Ошибка при обращении к OpenAI: {e}")
        return jsonify({
            "response_type": "general_advice",
            "data": {"message": "Извините, AI-ассистент временно недоступен."}
        })

# Удаляем старые, неиспользуемые эндпоинты
# /api/employees/search и /api/technologies
