import json
from sqlalchemy import create_engine, Column, Integer, String, JSON, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.pool import StaticPool
from typing import List, Dict, Any, Optional

# --- Конфигурация базы данных ---
DATABASE_URL = "sqlite:///./main.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Модели SQLAlchemy (структура таблиц) ---

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="Новый сотрудник")
    position = Column(String, default="Должность не указана") # 'role' в frontend
    avatar = Column(String, default="https://images.unsplash.com/photo-1580489944761-15a19d654956?q=80&w=1961&auto-format=fit=crop")
    
    # JSON поля для хранения сложных структур, как в frontend
    interests = Column(JSON, default=lambda: {"backend": 0, "frontend": 0, "dataScience": 0, "devops": 0, "mobileDev": 0, "qa": 0})
    skills = Column(JSON, default=lambda: []) # Теперь это список объектов: {"name": "Python", "level": "Advanced"}
    achievements = Column(JSON, default=lambda: {"xp": 0, "badges": 0, "rating": 999, "hasUploadedAvatar": False, "hasAddedFirstSkill": False, "hasAddedFirstCareerPath": False})
    career_path = Column(JSON, default=lambda: []) # careerPath в frontend
    chat_history = Column(JSON, default=lambda: [])


# --- Класс для взаимодействия с базой данных ---

class SQLiteDB:
    def __init__(self, session):
        self.db = session

    def get_employee_profile(self, employee_id: int) -> Optional[Dict[str, Any]]:
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            return None
        
        # Адаптируем имена полей под те, что используются в `script.js`
        return {
            "id": employee.id,
            "name": employee.name,
            "role": employee.position, # frontend использует 'role'
            "avatar": employee.avatar,
            "interests": employee.interests,
            "skills": employee.skills,
            "achievements": employee.achievements,
            "careerPath": employee.career_path, # frontend использует 'careerPath'
            "chatHistory": employee.chat_history,
            # Добавляем поля, которые были в старой структуре, для совместимости
            "applications": [], # Заглушка, т.к. этой логики еще нет в новой БД
        }

    def update_employee_profile(self, employee_id: int, data: Dict[str, Any]) -> bool:
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            return False

        # Обновляем поля, адаптируя имена из frontend
        employee.name = data.get("name", employee.name)
        employee.position = data.get("role", employee.position)
        employee.avatar = data.get("avatar", employee.avatar)
        employee.interests = data.get("interests", employee.interests)
        employee.skills = data.get("skills", employee.skills)
        employee.achievements = data.get("achievements", employee.achievements)
        employee.career_path = data.get("careerPath", employee.career_path)
        employee.chat_history = data.get("chatHistory", employee.chat_history)
        
        try:
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Ошибка при обновлении профиля: {e}")
            return False

    # Методы-заглушки для функций, которые мы пока не перенесли в новую БД
    def get_employee_summary(self, employee_id: int) -> Dict[str, Any]:
        profile = self.get_employee_profile(employee_id)
        if not profile: return {}
        return {"name": profile["name"], "position": profile["role"], "level": "N/A", "experience_years": 0}

    def get_employee_skills(self, employee_id: int) -> Dict[str, List[str]]:
        profile = self.get_employee_profile(employee_id)
        if not profile: return {"hard_skills": [], "soft_skills": []}
        return {"hard_skills": [s['name'] for s in profile["skills"]], "soft_skills": []}

    def get_employee_projects(self, employee_id: int) -> List[Dict[str, str]]:
        profile = self.get_employee_profile(employee_id)
        if not profile: return []
        return [{ "name": p['project'], "description": p['role'] } for p in profile["careerPath"]]


# --- Функция для создания и наполнения БД ---

def setup_database():
    """Создает таблицы и наполняет их тестовыми данными"""
    print("Инициализация базы данных...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        if session.query(Employee).count() > 0:
            print("База данных уже содержит данные. Пропускаем наполнение.")
            return
            
        print("Наполняем базу тестовыми данными...")

        # Создаем сотрудника с данными, соответствующими `script.js`
        emp1 = Employee(
            id=123,
            name="Алиса",
            position="Python Developer",
            avatar="https://images.unsplash.com/photo-1580489944761-15a19d654956?q=80&w=1961&auto-format=fit=crop",
            interests={"backend": 8, "frontend": 3, "dataScience": 5, "devops": 6, "mobileDev": 1, "qa": 2},
            skills=[
                {"name": "Python", "level": "Advanced"},
                {"name": "FastAPI", "level": "Intermediate"},
                {"name": "SQLAlchemy", "level": "Intermediate"},
                {"name": "Docker", "level": "Beginner"}
            ],
            achievements={"xp": 150, "badges": 2, "rating": 134, "hasUploadedAvatar": True, "hasAddedFirstSkill": True, "hasAddedFirstCareerPath": False},
            career_path=[
                {"year": "2022", "role": "Junior Python Developer", "project": "Legacy System Support"},
                {"year": "2023", "role": "Python Developer", "project": "Internal CRM"}
            ],
            chat_history=[
                {"sender": "ai", "text": "Здравствуйте! Готова ответить на Ваши вопросы."}
            ]
        )
        session.add(emp1)
        session.commit()
        print("✅ База данных успешно наполнена!")

    except Exception as e:
        print(f"❌ Ошибка при наполнении БД: {e}")
        session.rollback()
    finally:
        session.close()
