import sys
import os

# Add backend to path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# Import the app WITHOUT creating tables
from app import app
from database.database import db
from models.user import User


def seed_users():
    """Seed users without trying to create tables."""
    with app.app_context():
        # Check if users already exist
        existing_count = User.query.count()
        if existing_count > 0:
            print(f"⚠️  {existing_count} users already exist. Skipping seed.")
            return

        # Sample users
        users = [
            {
                "username": "admin",
                "email": "admin@qau.edu.pk",
                "password": "admin123",
                "role": "Admin",
            },
            {
                "username": "operator1",
                "email": "operator1@qau.edu.pk",
                "password": "operator123",
                "role": "Operator",
            },
            {
                "username": "viewer1",
                "email": "viewer1@qau.edu.pk",
                "password": "viewer123",
                "role": "Viewer",
            },
        ]

        for user_data in users:
            user = User()
            user.username = user_data["username"]
            user.email = user_data["email"]
            user.role = user_data["role"]
            user.active = True  # Use 'active' not 'is_active'
            user.set_password(user_data["password"])
            db.session.add(user)

        db.session.commit()
        print(f"✅ {len(users)} sample users added successfully!")


if __name__ == "__main__":
    seed_users()