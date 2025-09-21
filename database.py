import json
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool
from werkzeug.security import generate_password_hash, check_password_hash
from typing import List, Dict, Any, Optional

# --- Конфигурация базы данных ---
DATABASE_URL = "sqlite:///./main.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Модели SQLAlchemy ---

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    
    name = Column(String, default="Новый сотрудник")
    position = Column(String, default="Должность не указана") # 'role' в frontend
    avatar = Column(String, default="https://images.unsplash.com/photo-1580489944761-15a19d654956?q=80&w=1961&auto-format=fit=crop")
    
    interests = Column(JSON, default=lambda: {"backend": 0, "frontend": 0, "dataScience": 0, "devops": 0, "mobileDev": 0, "qa": 0})
    skills = Column(JSON, default=lambda: [])
    achievements = Column(JSON, default=lambda: {"xp": 0, "badges": 0, "rating": 999})
    career_path = Column(JSON, default=lambda: [])
    chat_history = Column(JSON, default=lambda: [])

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# --- Класс для взаимодействия с базой данных ---

class SQLiteDB:
    def __init__(self, session):
        self.db = session

    def get_employee_by_email(self, email: str) -> Optional[Employee]:
        return self.db.query(Employee).filter(Employee.email == email).first()

    def create_employee(self, email: str, password: str) -> Employee:
        existing_user = self.get_employee_by_email(email)
        if existing_user:
            raise ValueError(f"Пользователь с email {email} уже существует.")

        new_employee = Employee(email=email)
        new_employee.set_password(password)
        self.db.add(new_employee)
        self.db.commit()
        self.db.refresh(new_employee)
        return new_employee

    def authenticate_employee(self, email: str, password: str) -> Optional[Employee]:
        employee = self.get_employee_by_email(email)
        if employee and employee.check_password(password):
            return employee
        return None

    def get_employee_profile(self, employee_id: int) -> Optional[Dict[str, Any]]:
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            return None
        
        return {
            "id": employee.id,
            "email": employee.email,
            "name": employee.name,
            "role": employee.position,
            "avatar": employee.avatar,
            "interests": employee.interests,
            "skills": employee.skills,
            "achievements": employee.achievements,
            "careerPath": employee.career_path,
            "chatHistory": employee.chat_history,
            "applications": [], # Заглушка
        }

    def update_employee_profile(self, employee_id: int, data: Dict[str, Any]) -> bool:
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            return False

        for key, value in data.items():
            # Адаптируем имена полей frontend -> backend
            if key == "role": key = "position"
            if key == "careerPath": key = "career_path"
            if key == "chatHistory": key = "chat_history"
            
            # Обновляем только те поля, которые есть в модели
            if hasattr(employee, key) and key not in ["id", "email", "password_hash"]:
                setattr(employee, key, value)
        
        try:
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Ошибка при обновлении профиля: {e}")
            return False

# --- Функция для создания и наполнения БД ---

def setup_database():
    print("Инициализация базы данных...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        if session.query(Employee).count() > 0:
            print("База данных уже содержит данные.")
            return
            
        print("Наполняем базу тестовыми данными...")

        # Создаем сотрудника "Алиса" с email и паролем
        alice = Employee(
            email="alice@example.com",
            name="Алиса",
            position="Python Developer",
            # ... остальные данные из предыдущей версии
        )
        alice.set_password("password123") # Пароль для входа
        session.add(alice)
        session.commit()
        print("✅ База данных успешно наполнена тестовым пользователем (alice@example.com / password123)!")

    except Exception as e:
        print(f"❌ Ошибка при наполнении БД: {e}")
        session.rollback()
    finally:
        session.close()
