import os
import json
import numpy as np
from openai import OpenAI
from typing import List, Dict, Any, Optional

from flask import Flask, request, jsonify
from flask_cors import CORS

API_KEY = "sk-Sou5qWmNeBPhIf6LYSnfsw" 
BASE_URL = "https://llm.t1v.scibox.tech/v1"  
CHAT_MODEL = "Qwen2.5-72B-Instruct-AWQ"
EMBEDDING_MODEL = "bge-m3"


# Инициализация OpenAI клиента с правильными параметрами
try:
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
except Exception as e:
    print(f"Ошибка инициализации OpenAI клиента: {e}")
    # Fallback для старых версий
    client = OpenAI(api_key=API_KEY)
class MockDB:
    """
    Класс-заглушка для имитации работы с реальной базой данных.
    В будущем здесь будет подключение к реальной БД.
    """
    def __init__(self):
        # Моковые данные, которые будут заменены на реальные из БД
        self.employees = {
            123: {
                "name": "Alexey Ivanov",
                "position": "Middle Backend Developer", 
                "level": "Middle", 
                "experience_years": 3,
                "hard_skills": ["Python", "Django", "Docker", "SQL"],
                "soft_skills": ["communication", "teamwork"],
                "projects": [
                    {
                        "name": "Проект 'Альфа'",
                        "role": "Разработчик ML-моделей", 
                        "description": "Разрабатывал модели кредитного скоринга."
                    }
                ],
                "profile_completeness": 80,
                "missing_fields": ["certifications", "publications"]
            }
        }
    
    def get_employee_summary(self, employee_id: int):
        print(f"[DB] Запрос сводки по сотруднику ID: {employee_id}")
        employee = self.employees.get(employee_id, self.employees[123])
        return {
            "name": employee["name"], 
            "position": employee["position"], 
            "level": employee["level"], 
            "experience_years": employee["experience_years"]
        }
    
    def get_employee_skills(self, employee_id: int):
        print(f"[DB] Запрос навыков сотрудника ID: {employee_id}")
        employee = self.employees.get(employee_id, self.employees[123])
        return {
            "hard_skills": employee["hard_skills"], 
            "soft_skills": employee["soft_skills"]
        }

    def get_employee_projects(self, employee_id: int):
        print(f"[DB] Запрос проектов сотрудника ID: {employee_id}")
        employee = self.employees.get(employee_id, self.employees[123])
        return employee["projects"]

    def check_profile_completeness(self, employee_id: int):
        print(f"[DB] Проверка полноты профиля ID: {employee_id}")
        employee = self.employees.get(employee_id, self.employees[123])
        return {
            "completeness_percent": employee["profile_completeness"], 
            "missing_fields": employee["missing_fields"]
        }

    def find_learning_courses(self, keywords: List[str], level: Optional[str] = None):
        print(f"[DB] Поиск курсов по ключевым словам: {keywords}, уровень: {level}")
        courses = []
        if "kubernetes" in [k.lower() for k in keywords]:
            courses.append({"name": "Kubernetes для продвинутых", "duration_hours": 40, "level": "advanced"})
        if "devops" in [k.lower() for k in keywords]:
            courses.append({"name": "Основы DevOps для инженеров", "duration_hours": 60, "level": "middle"})
        if "python" in [k.lower() for k in keywords]:
            courses.append({"name": "Advanced Python Programming", "duration_hours": 30, "level": "intermediate"})
        if "django" in [k.lower() for k in keywords]:
            courses.append({"name": "Django Web Development", "duration_hours": 25, "level": "intermediate"})
        return courses
    
    def get_available_technologies(self, category: Optional[str] = None):
        return ["Python", "Go", "Kubernetes", "Docker", "Terraform", "PyTorch", "TensorFlow", "PostgreSQL", "Django", "FastAPI"]

    def filter_employees_by_criteria(self, criteria: dict):
        # Моковая фильтрация - в реальном приложении здесь будет SQL запрос
        print(f"[DB] Фильтрация сотрудников по критериям: {criteria}")
        # Возвращаем ID всех сотрудников для демонстрации
        return list(self.employees.keys())

    def get_employee_profile(self, employee_id: int):
        """
        Вспомогательная функция для потока менеджера, собирает полный профиль.
        """
        print(f"[DB] Сбор полного профиля для ID: {employee_id}")
        return {
            "id": employee_id,
            "summary": self.get_employee_summary(employee_id),
            "skills": self.get_employee_skills(employee_id),
            "projects": self.get_employee_projects(employee_id)
        }
    

class MockVectorDB:
    def find_similar(self, query: str, ids: List[int], top_k: int):
        # Просто возвращаем первые K ID для примера
        return ids[:top_k]

EMPLOYEE_SYSTEM_PROMPT = """
Ты — 'Career Architect AI', эмпатичный и опытный HR-консультант. Твоя миссия — построить для сотрудника персонализированный и достижимый план карьерного развития.

Твой рабочий процесс:
1. Анализ Запроса: Внимательно изучи запрос сотрудника.
2. Сбор Данных: Используй инструменты, чтобы получить полную картину о сотруднике.
3. Формирование Ответа: Когда вся информация собрана, сформируй развернутый ответ.

ПРАВИЛА ВЫЗОВА ИНСТРУМЕНТОВ:
1. Если для ответа на запрос пользователя тебе нужна информация, твой следующий ответ должен быть ТОЛЬКО JSON-объектом.
2. Никогда не предваряй JSON-объект никаким текстом, пояснениями или приветствиями.
3. Твой ответ должен начинаться с символа `{` и заканчиваться символом `}`. Ничего другого в ответе быть не должно.

ПЛОХОЙ ПРИМЕР (ТАК ДЕЛАТЬ НЕЛЬЗЯ):
Конечно, я помогу! Вот JSON для получения данных:
{
  "tool_name": "get_employee_summary",
  "parameters": {}
}

ХОРОШИЙ ПРИМЕР (ТАК НУЖНО ДЕЛАТЬ):
{
  "tool_name": "get_employee_summary",
  "parameters": {}
}

Если тебе больше не нужно вызывать инструменты и у тебя достаточно информации, дай развернутый ответ пользователю в свободной форме.

Доступные инструменты:
1. get_employee_summary(employee_id: int)
   Описание: Получить краткую сводку по сотруднику: должность, уровень, опыт.
   Пример вызова: {"tool_name": "get_employee_summary", "parameters": {"employee_id": 123}}

2. check_profile_completeness(employee_id: int)
   Описание: Проверить анкету сотрудника на полноту и найти незаполненные разделы.
   Пример вызова: {"tool_name": "check_profile_completeness", "parameters": {"employee_id": 123}}

3. get_employee_skills(employee_id: int)
   Описание: Получить полный стек технологий (hard skills) и мягких навыков (soft skills) сотрудника.
   Пример вызова: {"tool_name": "get_employee_skills", "parameters": {"employee_id": 123}}

4. get_employee_projects(employee_id: int)
   Описание: Получить информацию о проектах, в которых участвовал сотрудник.
   Пример вызова: {"tool_name": "get_employee_projects", "parameters": {"employee_id": 123}}

5. find_learning_courses(keywords: list[str], level: str = None)
   Описание: Найти обучающие курсы по ключевым словам и, опционально, по уровню сложности.
   Пример вызова: {"tool_name": "find_learning_courses", "parameters": {"keywords": ["Kubernetes", "DevOps"]}}

Правила общения:
- Никогда не выдумывай информацию.
- Общайся с сотрудником на "ты", будь дружелюбным, но профессиональным.
- Не отвечай на запрос пользователя по существу, пока не соберешь необходимые данные.
"""


class LLMProcessor:
    def __init__(self, client, db_instance, vector_db_instance):
        self.client = client
        self.db = db_instance
        self.vector_db = vector_db_instance
        self.available_tools = {
        "get_employee_summary": self.db.get_employee_summary,
        "get_employee_skills": self.db.get_employee_skills,
        "get_employee_projects": self.db.get_employee_projects,
        "check_profile_completeness": self.db.check_profile_completeness,
        "find_learning_courses": self.db.find_learning_courses,
        }

    
    def handle_employee_query(self, user_query: str, employee_id: int, max_steps: int = 5):
        """
        Обрабатывает запрос от сотрудника (Поток 1: HR-консультант).
        Эмулирует ReAct/Tool Calling через промпты.
        """
        print("\n=== НАЧАЛО ОБРАБОТКИ ЗАПРОСА СОТРУДНИКА ===")
        messages = [
            {"role": "system", "content": EMPLOYEE_SYSTEM_PROMPT},
            {"role": "user", "content": user_query}
        ]
        
        for i in range(max_steps):
            print(f"\n--- Итерация #{i + 1} ---")
            
            response = self.client.chat.completions.create(
                model=CHAT_MODEL,
                messages=messages,
                temperature=0.1 # Низкая температура для предсказуемости вызова функций
            )

            response_content = response.choices[0].message.content
            #print(f"Ответ LLM: {response_content}")

            try:
                # Пытаемся распарсить ответ как JSON - это сигнал к вызову функции
                tool_call_request = json.loads(response_content)
                function_name = tool_call_request.get("tool_name")
                function_args = tool_call_request.get("parameters", {})

                if function_name in self.available_tools:
                    function_to_call = self.available_tools[function_name]
                    
                    # Всегда передаем ID текущего пользователя, если функция его требует
                    if "employee_id" in function_to_call.__code__.co_varnames:
                        function_args["employee_id"] = employee_id

                    print(f"Вызов функции: {function_name}({function_args})")
                    function_response = function_to_call(**function_args)
                    
                    # Добавляем в историю и запрос на вызов, и результат вызова
                    messages.append({"role": "assistant", "content": response_content})
                    messages.append({
                        "role": "user", # Используем роль user, чтобы передать результат обратно LLM
                        "content": f"Результат вызова инструмента '{function_name}':\n{json.dumps(function_response, ensure_ascii=False)}"
                    })
                else:
                    # Модель сгенерировала JSON, но с неизвестной функцией
                    print(f"Ошибка: LLM запросила неизвестную функцию '{function_name}'")
                    messages.append({"role": "assistant", "content": response_content})
                    messages.append({
                        "role": "user",
                        "content": f"Ошибка: инструмент с именем '{function_name}' не найден."
                    })

            except (json.JSONDecodeError, AttributeError):
                # Если парсинг не удался, значит это финальный текстовый ответ для пользователя
                print(">>> LLM сгенерировала финальный ответ. Завершение цикла.")
                return response_content
        
        print(">>> Достигнут лимит итераций. Генерируем финальный ответ на основе собранных данных.")
        final_response_generation = self.client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages + [{"role": "user", "content": "Пожалуйста, предоставь финальный ответ на основе уже собранной информации."}]
        )
        return final_response_generation.choices[0].message.content
    
    def handle_manager_query(self, manager_query: str):
        """
        Обрабатывает запрос от менеджера (Поток 2: Поиск кандидатов).
        """
        print("\n=== НАЧАЛО ОБРАБОТКИ ЗАПРОСА МЕНЕДЖЕРА ===")
        
        # Шаг 1: Структурируем запрос
        print("1. Вызов LLM для структурирования запроса менеджера...")
        prompt_struct = f"""
        Извлеки из запроса менеджера структурированные критерии поиска. 
        Доступные поля: hard_skills (list[str]), level (str), experience_min_years (int), domain (str).
        Верни только JSON. Не добавляй поля, которых нет в запросе.

        Запрос: "{manager_query}"
        """
        response_struct = self.client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role": "user", "content": prompt_struct}],
            temperature=0.0
        )
        try:
            criteria = json.loads(response_struct.choices[0].message.content)
            print(f"   - Структурированные критерии: {criteria}")
        except (json.JSONDecodeError, IndexError):
            print("   - Не удалось извлечь структурированные критерии, пропускаем фильтрацию.")
            criteria = {}

        # Шаг 2: Жесткая фильтрация
        print("2. Фильтрация кандидатов по жестким критериям...")
        filtered_ids = self.db.filter_employees_by_criteria(criteria)
        if not filtered_ids:
            return "По заданным жестким критериям не найдено ни одного сотрудника."
        print(f"   - Найдено кандидатов после фильтрации: {len(filtered_ids)}")

        # Шаг 3: Семантическое ранжирование
        print("3. Ранжирование с помощью векторной БД...")
        top_ids = self.vector_db.find_similar(manager_query, filtered_ids, top_k=5)
        print(f"   - Топ-{len(top_ids)} кандидатов после ранжирования: {top_ids}")
        
        # Шаг 4: Сбор данных для отчета
        print("4. Сбор полных профилей для отчета...")
        top_profiles = [self.db.get_employee_profile(emp_id) for emp_id in top_ids]

        # Шаг 5: Финальный вызов LLM для саммари
        print("5. Финальный вызов LLM для подготовки отчета менеджеру...")
        MANAGER_SUMMARY_PROMPT = f"""
        Ты — ассистент руководителя, специализирующийся на подборе внутренних кадров. Твоя задача — предоставить четкий и аргументированный отчет.

        **Изначальный запрос менеджера:**
        <query>
        {manager_query}
        </query>

        **Найденные кандидаты:**
        <candidates>
        {json.dumps(top_profiles, indent=2, ensure_ascii=False)}
        </candidates>

        **Твоя задача:**
        Подготовь краткое саммари по каждому кандидату в формате маркированного списка. Для каждого кандидата:
        1.  **Имя и должность:** Укажи ФИО, текущую должность и уровень.
        2.  **Ключевое соответствие:** Одним предложением опиши, почему этот кандидат — отличный выбор. Ссылайся на ключевые требования из запроса (например, "Идеально подходит благодаря опыту в кредитном скоринге и знанию PyTorch").
        3.  **Потенциальные риски или вопросы:** Если есть что-то, на что менеджеру стоит обратить внимание (например, "Стек совпадает на 80%, но нет опыта с Kubernetes"), кратко укажи это. Если рисков нет, напиши "Полное соответствие".
        4.  **Рекомендация:** Напиши четкую рекомендацию ("Рекомендуется к собеседованию" или "Первоочередной кандидат").

        Отчет должен быть структурированным и легко читаемым.
        """
        final_response = self.client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role": "user", "content": MANAGER_SUMMARY_PROMPT}]
        )
        return final_response.choices[0].message.content

  


# if __name__ == '__main__':
#     # Инициализация OpenAI клиента с правильными параметрами
try:
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
except Exception as e:
    print(f"Ошибка инициализации OpenAI клиента: {e}")
    # Fallback для старых версий
    client = OpenAI(api_key=API_KEY)
#     db = MockDB()
#     vector_db = MockVectorDB()
    
#     processor = LLMProcessor(client, db, vector_db)
    
#     employee_query = "Привет, я стремлюсь стать senior mlops через 3 года. Сейчас я middle ml. Подскажи, что мне нужно изучить?"
#     employee_response = processor.handle_employee_query(employee_query, employee_id=123)
#     print("\n\n*** ОТВЕТ ДЛЯ СОТРУДНИКА ***")
#     print(employee_response)
    
#     manager_query = "Ищу Python-разработчика уровня Middle+ с опытом в финтехе для работы над проектом кредитного скоринга."
#     # manager_response = processor.handle_manager_query(manager_query)
#     # print("\n\n*** ОТВЕТ ДЛЯ МЕНЕДЖЕРА ***")
#     # print(manager_response)



app = Flask(__name__)
CORS(app)  # Включаем CORS для всех маршрутов


print("Инициализация API...")
# Инициализация OpenAI клиента с правильными параметрами
try:
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
except Exception as e:
    print(f"Ошибка инициализации OpenAI клиента: {e}")
    # Fallback для старых версий
    client = OpenAI(api_key=API_KEY)
db = MockDB()
vector_db = MockVectorDB()
processor = LLMProcessor(client, db, vector_db)
print("API готово к работе.")

@app.route('/api/employee/<int:employee_id>', methods=['GET'])
def get_employee_data(employee_id):
    """Получить данные сотрудника по ID"""
    try:
        # В реальном приложении здесь будет запрос к базе данных
        # Пока возвращаем моковые данные
        employee_data = {
            "id": employee_id,
            "name": "Alexey Ivanov",
            "role": "Middle Backend Developer",
            "level": "Middle",
            "experience_years": 3,
            "skills": {
                "hard_skills": ["Python", "Django", "Docker", "SQL"],
                "soft_skills": ["communication", "teamwork"]
            },
            "projects": [
                {
                    "name": "Проект 'Альфа'",
                    "role": "Разработчик ML-моделей",
                    "description": "Разрабатывал модели кредитного скоринга."
                }
            ]
        }
        return jsonify(employee_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/employees/search', methods=['POST'])
def search_employees():
    """Поиск сотрудников по критериям"""
    try:
        data = request.get_json()
        criteria = data.get('criteria', {})
        
        # В реальном приложении здесь будет поиск в базе данных
        # Пока возвращаем моковые результаты
        employees = [
            {
                "id": 1,
                "name": "Alexey Ivanov",
                "role": "Middle Backend Developer",
                "skills": ["Python", "Django", "Docker"],
                "match_score": 0.95
            }
        ]
        return jsonify({"employees": employees})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def handle_chat():
    """
    Эта функция будет вызываться каждый раз, когда фронтенд отправляет
    запрос на адрес http://<адрес_сервера>/chat
    """
    # Получаем JSON данные, которые отправил фронтенд
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    user_query = data.get('query')
    user_role = data.get('role') # 'employee' или 'manager'
    user_id = data.get('userId', 123) # Получаем ID, если нет - ставим заглушку

    if not user_query or not user_role:
        return jsonify({"error": "Missing 'query' or 'role' in request"}), 400
        
    print(f"\n[API] Получен запрос от {user_role} (ID: {user_id}): '{user_query}'")

    try:
        if user_role == 'employee':
            response_text = processor.handle_employee_query(user_query, employee_id=user_id)
        elif user_role == 'manager':
            response_text = processor.handle_manager_query(user_query)
        else:
            return jsonify({"error": "Invalid role specified"}), 400
            
        # Возвращаем ответ в формате JSON
        return jsonify({"response": response_text})

    except Exception as e:
        print(f"[API] Произошла ошибка: {e}")
        return jsonify({"error": "An internal error occurred"}), 500


# ===============================================================
# ШАГ 2.3: Запуск сервера
# ===============================================================

if __name__ == '__main__':
    # Запускаем веб-сервер. 
    # debug=True позволяет автоматически перезагружать сервер при изменениях в коде.
    # host='0.0.0.0' делает сервер доступным в локальной сети (полезно для хакатона).
    app.run(host='0.0.0.0', port=5000, debug=True)