# database.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Инициализация БД с приложением Flask"""
    db.init_app(app)

    with app.app_context():
        # ВАЖНО: Импортируем модели ДО создания таблиц
        # Иначе SQLAlchemy не увидит модели и не создаст таблицы
        from models.user import User
        from models.repair_request import RepairRequest
        from models.comment import Comment

        # Создаем таблицы если их нет
        db.create_all()
        print("✓ База данных инициализирована")


def get_db():
    """Получить объект БД"""
    return db
