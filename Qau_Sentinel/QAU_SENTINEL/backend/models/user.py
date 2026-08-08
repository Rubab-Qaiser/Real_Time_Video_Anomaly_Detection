from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from database.database import db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False,
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False,
    )

    password_hash = db.Column(
        db.String(256),
        nullable=False,
    )

    role = db.Column(
        db.String(20),
        default="Viewer",
        nullable=False,
    )

    # ✅ Rename the database column to avoid conflict
    active = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
        name="is_active",  # Keep the same column name in the database
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    last_login = db.Column(
        db.DateTime,
        nullable=True,
    )

    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password."""
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        """Override get_id to return the user id as string."""
        return str(self.id)

    # ✅ Flask-Login expects is_active property
    @property
    def is_active(self):
        """Return True if user is active, False otherwise."""
        return self.active

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "is_active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }