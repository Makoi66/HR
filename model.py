import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import OpenAI

# Импорт компонентов для работы с БД
from database import SessionLocal, SQLiteDB

# --- Инициализация приложения ---
app = Flask(__name__)
CORS(app) # Включаем CORS для всех маршрутов

# --- Настройка AI клиента ---
try:
    # Для локального запуска, используйте ваш API ключ
    # open_api_key = os.environ.get("OPENAI_API_KEY")
    # client = OpenAI(api_key=open_api_key)
    
    # Используем мок-клиент для демонстрации
    class MockOpenAI:
        def __init__(self, *args, **kwargs):
            pass
        class MockChat:
            def __init__(self, *args, **kwargs):
                pass
            class MockCompletions:
                def create(self, *args, **kwargs):
                    class MockChoice:
                        def __init__(self, message):
                            self.message = message
                    class MockMessage:
                        def __init__(self, content):
                            self.content = content
                    return MockChoice(MockMessage('{\n  "response_type": "learning_recommendation",\n  "data": [\n    {\n      "course_name": "Advanced Python for Web",\n      "reason": "Для углубления знаний в FastAPI и асинхронной разработке.",\n      "relevance_score": 0.9\n    },\n    {\n      "course_name": "DevOps Essentials: Docker & Kubernetes",\n      "reason": "Навыки контейнеризации и CI/CD значительно повысят вашу ценность как backend-разработчика.",\n      "relevance_score": 0.8\n    }\n  ]\n}'))
            @property
            def completions(self):
                return self.MockCompletions()
        @property
        def chat(self):
            return self.MockChat()
    client = MockOpenAI()
    print("🤖 Инициализирован мок-клиент OpenAI.")

except Exception as e:
    print(f"❌ Не удалось инициализировать OpenAI клиент: {e}")
    client = None

# --- Управление сессиями БД ---

def get_db():
    """Создает и возвращает новую сессию БД для каждого запроса."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Endpoints ---

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    """Эндпоинт для взаимодействия с AI-ассистентом."""
    if not client:
        return jsonify({"error": "AI клиент не инициализирован"}), 500

    data = request.get_json()
    user_query = data.get('query')
    employee_id = data.get('employee_id')

    if not user_query or not employee_id:
        return jsonify({"error": "Отсутствуют query или employee_id"}), 400

    # Получаем сессию БД
    db_session = next(get_db())
    db = SQLiteDB(db_session)

    # Собираем контекст о сотруднике для AI
    summary = db.get_employee_summary(employee_id)
    skills = db.get_employee_skills(employee_id)
    projects = db.get_employee_projects(employee_id)

    prompt = f"""
    Ты — HR-ассистент, встроенный в корпоративную систему 'Career on Autopilot'. 
    Твоя задача — помогать сотрудникам в их карьерном развитии. 
    Отвечай на русском языке.
    
    Вот информация о сотруднике, который к тебе обратился:
    - Имя: {summary.get('name')}
    - Должность: {summary.get('position')}, Уровень: {summary.get('level')}
    - Опыт: {summary.get('experience_years')} лет
    - Ключевые навыки (hard skills): {skills.get('hard_skills')}
    - Soft skills: {skills.get('soft_skills')}
    - Участвовал в проектах: {[p['name'] for p in projects]}

    Запрос сотрудника: "{user_query}"

    Твоя задача — сгенерировать JSON с рекомендациями. 
    Возможные типы ответов (response_type):
    1. `learning_recommendation`: Рекомендации по обучению (курсы, статьи, книги).
    2. `project_recommendation`: Рекомендации по участию во внутренних проектах.
    3. `profile_improvement`: Советы по улучшению профиля сотрудника.
    4. `general_advice`: Общий совет по карьере.

    Пример JSON ответа:
    {{ "response_type": "learning_recommendation", "data": [{{ "course_name": "Название курса", "reason": "Почему этот курс полезен", "relevance_score": 0.9 }}] }}

    Сгенерируй наиболее подходящий ответ в формате JSON.
    """

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt}
            ]
        )
        response_content = completion.message.content
        # Убираем возможные Markdown-обертки
        if response_content.startswith("```json"): 
            response_content = response_content[7:-4]

        return jsonify(json.loads(response_content))

    except Exception as e:
        print(f"❌ Ошибка при обращении к OpenAI: {e}")
        # Возвращаем запасной ответ в случае ошибки
        return jsonify({
            "response_type": "general_advice",
            "data": {
                "message": "Извините, в данный момент AI-ассистент недоступен. Попробуйте уточнить ваш запрос позже."
            }
        })


@app.route('/api/employee/<int:employee_id>', methods=['GET'])
def get_employee_data(employee_id):
    """Эндпоинт для получения полной информации о сотруднике."""
    db_session = next(get_db())
    db = SQLiteDB(db_session)
    
    profile = db.get_employee_profile(employee_id)
    if not profile:
        return jsonify({"error": "Сотрудник не найден"}), 404

    # Добавляем информацию о заполненности профиля
    completeness = db.check_profile_completeness(employee_id)
    profile["profile_completeness"] = completeness
    
    return jsonify(profile)


@app.route('/api/employees/search', methods=['POST'])
def search_employees():
    """Эндпоинт для поиска сотрудников по критериям."""
    criteria = request.get_json()
    if not criteria:
        return jsonify({"error": "Не указаны критерии поиска"}), 400

    db_session = next(get_db())
    db = SQLiteDB(db_session)

    employee_ids = db.filter_employees_by_criteria(criteria)
    
    # Получаем полные профили найденных сотрудников
    results = [db.get_employee_profile(emp_id) for emp_id in employee_ids]
    
    return jsonify(results)


# Пример эндпоинта для получения доступных технологий (для UI)
@app.route('/api/technologies', methods=['GET'])
def get_technologies():
    db_session = next(get_db())
    db = SQLiteDB(db_session)
    category = request.args.get('category')
    techs = db.get_available_technologies(category)
    return jsonify(techs)
