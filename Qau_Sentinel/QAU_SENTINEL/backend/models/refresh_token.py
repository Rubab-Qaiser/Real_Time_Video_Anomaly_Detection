from datetime import datetime, timezone
from database.database import db


class RefreshToken(db.Model):
    __tablename__ = "refresh_tokens"

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    revoked = db.Column(db.Boolean, default=False, nullable=False)

    # Relationship
    user = db.relationship("User", backref="refresh_tokens")

    def is_expired(self):
        """Check if the refresh token has expired."""
        # ✅ Make expires_at timezone-aware for comparison
        if self.expires_at.tzinfo is None:
            # If naive, assume it's UTC
            expires_at = self.expires_at.replace(tzinfo=timezone.utc)
        else:
            expires_at = self.expires_at
        return datetime.now(timezone.utc) > expires_at

    def to_dict(self):
        return {
            "id": self.id,
            "token": self.token,
            "user_id": self.user_id,
            "expires_at": self.expires_at.isoformat(),
            "created_at": self.created_at.isoformat(),
            "revoked": self.revoked,
        }