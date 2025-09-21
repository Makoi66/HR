import json
from sqlalchemy import create_engine, Column, Integer, String, JSON, ForeignKey, Text, Table
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.pool import StaticPool
from typing import List, Dict, Any, Optional

# --- Конфигурация базы данных ---
DATABASE_URL = "sqlite:///./main.db"

# Используем StaticPool для совместимости с SQLite и Flask в одном потоке
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

# Создаем сессию для взаимодействия с БД
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для всех моделей SQLAlchemy
Base = declarative_base()

# --- Модели SQLAlchemy (структура таблиц) ---

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="Новый сотрудник")
    position = Column(String, default="Должность не указана")
    level = Column(String, default="Junior")
    experience_years = Column(Integer, default=0)
    hard_skills = Column(JSON, default=[]) # Список строк
    soft_skills = Column(JSON, default=[]) # Список строк
    # Связь с проектами
    projects = relationship("Project", back_populates="employee")

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    employee_id = Column(Integer, ForeignKey("employees.id"))
    # Обратная связь
    employee = relationship("Employee", back_populates="projects")

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, default="")
    level = Column(String, index=True) # например, "Beginner", "Advanced"
    keywords = Column(JSON, default=[]) # Список ключевых слов

class Technology(Base):
    __tablename__ = "technologies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    category = Column(String, index=True) # например, "Frontend", "Backend"

# --- Класс для взаимодействия с базой данных ---

class SQLiteDB:
    def __init__(self, session):
        self.db = session

    def get_employee_summary(self, employee_id: int) -> Dict[str, Any]:
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            return {}
        return {
            "name": employee.name,
            "position": employee.position,
            "level": employee.level,
            "experience_years": employee.experience_years
        }

    def get_employee_skills(self, employee_id: int) -> Dict[str, List[str]]:
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            return {"hard_skills": [], "soft_skills": []}
        return {
            "hard_skills": employee.hard_skills or [],
            "soft_skills": employee.soft_skills or []
        }

    def get_employee_projects(self, employee_id: int) -> List[Dict[str, str]]:
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            return []
        return [{ "name": p.name, "description": p.description } for p in employee.projects]

    def check_profile_completeness(self, employee_id: int) -> Dict[str, Any]:
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            return {"completeness_percent": 0, "missing_fields": []}
        
        required_fields = {
            "name": employee.name and employee.name != "Новый сотрудник",
            "position": employee.position and employee.position != "Должность не указана",
            "level": bool(employee.level),
            "experience_years": employee.experience_years > 0,
            "hard_skills": bool(employee.hard_skills),
            "soft_skills": bool(employee.soft_skills),
            "projects": bool(employee.projects)
        }
        
        filled_fields_count = sum(1 for filled in required_fields.values() if filled)
        total_fields = len(required_fields)
        completeness = (filled_fields_count / total_fields) * 100
        missing_fields = [field for field, filled in required_fields.items() if not filled]
        
        return {
            "completeness_percent": int(completeness),
            "missing_fields": missing_fields
        }

    def find_learning_courses(self, keywords: List[str], level: Optional[str] = None) -> List[Dict[str, Any]]:
        query = self.db.query(Course)
        # Фильтрация по уровню
        if level:
            query = query.filter(Course.level.ilike(f"%{level}%"))
        # Фильтрация по ключевым словам
        if keywords:
            # Ищем любое из ключевых слов в названии или в списке keywords курса
            or_conditions = []
            for keyword in keywords:
                or_conditions.append(Course.name.ilike(f"%{keyword}%"))
                or_conditions.append(Course.keywords.contains(keyword)) # Для JSON полей
            query = query.filter(or_(*or_conditions))

        found_courses = query.all()
        return [
            {"id": c.id, "name": c.name, "description": c.description, "level": c.level}
            for c in found_courses
        ]

    def get_available_technologies(self, category: Optional[str] = None) -> List[str]:
        query = self.db.query(Technology)
        if category:
            query = query.filter(Technology.category.ilike(f"%{category}%"))
        return [tech.name for tech in query.all()]

    def filter_employees_by_criteria(self, criteria: dict) -> List[int]:
        query = self.db.query(Employee.id)
        if 'hard_skills' in criteria and criteria['hard_skills']:
            for skill in criteria['hard_skills']:
                query = query.filter(Employee.hard_skills.contains(skill))
        if 'level' in criteria:
            query = query.filter(Employee.level == criteria['level'])
        if 'experience_min_years' in criteria:
            query = query.filter(Employee.experience_years >= criteria['experience_min_years'])
        
        return [emp_id for (emp_id,) in query.all()]

    def get_employee_profile(self, employee_id: int) -> Dict[str, Any]:
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            return {}
        
        return {
            "id": employee.id,
            "summary": self.get_employee_summary(employee_id),
            "skills": self.get_employee_skills(employee_id),
            "projects": self.get_employee_projects(employee_id)
        }

# --- Функция для создания и наполнения БД ---

def setup_database():
    """Создает таблицы и наполняет их тестовыми данными"""
    print("Инициализация базы данных...")
    # Удаляем старые таблицы (для простоты в разработке)
    Base.metadata.drop_all(bind=engine)
    # Создаем новые таблицы
    Base.metadata.create_all(bind=engine)

    # Используем новую сессию для добавления данных
    session = SessionLocal()

    try:
        # Проверяем, есть ли уже данные
        if session.query(Employee).count() > 0:
            print("База данных уже содержит данные. Пропускаем наполнение.")
            return
            
        print("Наполняем базу тестовыми данными...")

        # Сотрудники
        emp1 = Employee(
            id=123,
            name="Алиса",
            position="Python Developer",
            level="Middle",
            experience_years=3,
            hard_skills=["Python", "FastAPI", "SQLAlchemy", "Docker"],
            soft_skills=["Коммуникация", "Работа в команде"]
        )
        emp2 = Employee(
            name="Борис",
            position="Frontend Developer",
            level="Senior",
            experience_years=6,
            hard_skills=["JavaScript", "React", "Vue.js", "Webpack"],
            soft_skills=["Лидерство", "Менторство"]
        )
        emp3 = Employee(
            name="Виктор",
            position="Data Scientist",
            level="Middle",
            experience_years=4,
            hard_skills=["Python", "Pandas", "PyTorch", "Scikit-learn"],
            soft_skills=["Аналитическое мышление", "Решение проблем"]
        )
        session.add_all([emp1, emp2, emp3])

        # Проекты
        proj1 = Project(name="Система внутреннего трекинга задач", description="Разработка веб-приложения на FastAPI.", employee=emp1)
        proj2 = Project(name="Новый личный кабинет клиента", description="Миграция со старого стека на React.", employee=emp2)
        proj3 = Project(name="Модель кредитного скоринга", description="Построение ML-модели для оценки кредитоспособности.", employee=emp3)
        proj4 = Project(name="Оптимизация CI/CD", description="Внедрение Docker в процесс разработки.", employee=emp1)
        session.add_all([proj1, proj2, proj3, proj4])

        # Курсы
        courses_data = [
            {"name": "Advanced Python for Web", "level": "Advanced", "keywords": ["Python", "FastAPI", "AsyncIO"]},
            {"name": "React: The Complete Guide", "level": "Intermediate", "keywords": ["React", "Frontend", "JavaScript"]},
            {"name": "Introduction to Machine Learning", "level": "Beginner", "keywords": ["Python", "ML", "Data Science"]},
            {"name": "DevOps Essentials: Docker & Kubernetes", "level": "Intermediate", "keywords": ["DevOps", "Docker", "Kubernetes"]}
        ]
        for c in courses_data:
            session.add(Course(**c))

        # Технологии
        tech_data = ["Python", "JavaScript", "React", "FastAPI", "Docker", "Kubernetes", "Pandas", "PyTorch"]
        for t in tech_data:
            session.add(Technology(name=t, category="Backend" if t in ["Python", "FastAPI"] else "Frontend"))

        session.commit()
        print("✅ База данных успешно наполнена!")

    except Exception as e:
        print(f"❌ Ошибка при наполнении БД: {e}")
        session.rollback()
    finally:
        session.close()
