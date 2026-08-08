from datetime import datetime, timezone
from models.user import User
from database.database import db


class UserService:
    def get_all(self, search=None):
        query = User.query
        if search:
            query = query.filter(
                (User.username.ilike(f"%{search}%")) |
                (User.email.ilike(f"%{search}%"))
            )
        users = query.all()
        return [user.to_dict() for user in users]

    def get_by_id(self, user_id):
        user = User.query.get(user_id)
        return user.to_dict() if user else None

    def get_by_email(self, email):
        user = User.query.filter_by(email=email).first()
        return user.to_dict() if user else None

    def create(self, data):
        if User.query.filter_by(email=data.get("email")).first():
            raise ValueError("Email already exists")
        
        if User.query.filter_by(username=data.get("username")).first():
            raise ValueError("Username already exists")

        user = User()
        user.username = data.get("username")
        user.email = data.get("email")
        user.role = data.get("role", "Viewer")
        user.active = data.get("is_active", True)  # ✅ Use active
        user.set_password(data.get("password"))

        db.session.add(user)
        db.session.commit()
        return user.to_dict()

    def update(self, user_id, data):
        user = User.query.get(user_id)
        if not user:
            return None

        if "username" in data:
            existing = User.query.filter(User.username == data["username"], User.id != user_id).first()
            if existing:
                raise ValueError("Username already taken")
            user.username = data["username"]

        if "email" in data:
            existing = User.query.filter(User.email == data["email"], User.id != user_id).first()
            if existing:
                raise ValueError("Email already exists")
            user.email = data["email"]

        if "role" in data:
            user.role = data["role"]

        if "is_active" in data:
            user.active = data["is_active"]  # ✅ Use active

        if "password" in data and data["password"]:
            user.set_password(data["password"])

        db.session.commit()
        return user.to_dict()

    def delete(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return False

        if user.role == "Admin":
            admin_count = User.query.filter_by(role="Admin").count()
            if admin_count <= 1:
                raise ValueError("Cannot delete the last admin user")

        db.session.delete(user)
        db.session.commit()
        return True

    def update_last_login(self, user_id):
        user = User.query.get(user_id)
        if user:
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            return True
        return False


user_service = UserService()