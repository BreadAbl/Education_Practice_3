from database import db
from werkzeug.security import generate_password_hash


class UserService:

    @staticmethod
    def get_all_users():
        """Получить всех пользователей"""
        try:
            from models.user import User
            users = User.query.all()
            return [u.to_dict() for u in users]
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_user_by_id(user_id):
        """Получить пользователя по ID"""
        try:
            from models.user import User
            user = User.query.get(user_id)
            if not user:
                return None
            return user.to_dict()
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_masters():
        """Получить всех мастеров"""
        try:
            from models.user import User
            masters = User.query.filter_by(user_type="Мастер").all()
            return [u.to_dict() for u in masters]
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def list_assignable_users():
        """Пользователи, которых можно назначать ответственными (Мастера)"""
        try:
            from models.user import User
            users = User.query.filter_by(user_type="Мастер").order_by(User.full_name).all()
            return users
        except Exception as e:
            return []

    @staticmethod
    def create_user(full_name, phone, login, password, user_type="Заказчик"):
        """Создать нового пользователя"""
        try:
            from models.user import User

            existing_user = User.query.filter_by(login=login).first()
            if existing_user:
                return {"error": "Пользователь с таким логином уже существует"}

            if not full_name or not full_name.strip():
                return {"error": "ФИО не может быть пустым"}
            if not phone or not phone.strip():
                return {"error": "Телефон не может быть пустым"}
            if not login or not login.strip():
                return {"error": "Логин не может быть пустым"}
            if not password or not password.strip():
                return {"error": "Пароль не может быть пустым"}

            full_name = full_name.strip()
            phone = phone.strip()
            login = login.strip()
            password = password.strip()

            if len(login) < 3:
                return {"error": "Логин должен быть не менее 3 символов"}
            if len(password) < 3:
                return {"error": "Пароль должен быть не менее 3 символов"}

            allowed_types = ['Менеджер', 'Мастер', 'Оператор', 'Заказчик']
            if user_type not in allowed_types:
                return {"error": f"Тип пользователя должен быть одним из: {', '.join(allowed_types)}"}

            hashed_password = generate_password_hash(password)

            new_user = User(
                full_name=full_name,
                phone=phone,
                login=login,
                password=hashed_password,
                user_type=user_type
            )

            db.session.add(new_user)
            db.session.commit()

            return new_user.to_dict()

        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}

    @staticmethod
    def delete_user(user_id):
        """Удалить пользователя"""
        try:
            from models.user import User
            user = User.query.get(user_id)
            if not user:
                return {"error": "Пользователь не найден"}

            db.session.delete(user)
            db.session.commit()

            return {"message": "Пользователь успешно удален"}
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}
