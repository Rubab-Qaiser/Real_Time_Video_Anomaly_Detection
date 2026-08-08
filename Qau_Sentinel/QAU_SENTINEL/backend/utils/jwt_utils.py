import jwt
from datetime import datetime, timezone, timedelta
from flask import current_app
from models.user import User
from models.refresh_token import RefreshToken
from database.database import db
import secrets


def generate_access_token(user_id):
    """Generate a JWT access token for a user."""
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + current_app.config["JWT_ACCESS_TOKEN_EXPIRES"],
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm=current_app.config["JWT_ALGORITHM"])


def generate_refresh_token(user_id):
    """Generate a refresh token for a user and store it in the database."""
    token = secrets.token_urlsafe(64)
    expires_at = datetime.now(timezone.utc) + current_app.config["JWT_REFRESH_TOKEN_EXPIRES"]
    
    refresh_token = RefreshToken()
    refresh_token.token = token
    refresh_token.user_id = user_id
    refresh_token.expires_at = expires_at
    
    db.session.add(refresh_token)
    db.session.commit()
    
    return token, expires_at


def verify_access_token(token):
    """Verify a JWT access token and return the user_id if valid."""
    try:
        payload = jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=[current_app.config["JWT_ALGORITHM"]])
        
        # Check token type
        if payload.get("type") != "access":
            return None, "Invalid token type"
        
        user_id = payload.get("user_id")
        if not user_id:
            return None, "Invalid token payload"
        
        # Check if user exists and is active
        user = User.query.get(user_id)
        if not user or not user.active:
            return None, "User not found or inactive"
        
        return user_id, None
    except jwt.ExpiredSignatureError:
        return None, "Token has expired"
    except jwt.InvalidTokenError:
        return None, "Invalid token"


def verify_refresh_token(token):
    """Verify a refresh token and return the user_id if valid."""
    refresh_token = RefreshToken.query.filter_by(token=token, revoked=False).first()
    
    if not refresh_token:
        return None, "Invalid refresh token"
    
    if refresh_token.is_expired():
        return None, "Refresh token has expired"
    
    return refresh_token.user_id, None


def revoke_refresh_token(token):
    """Revoke a refresh token."""
    refresh_token = RefreshToken.query.filter_by(token=token).first()
    if refresh_token:
        refresh_token.revoked = True
        db.session.commit()
        return True
    return False


def revoke_all_user_refresh_tokens(user_id):
    """Revoke all refresh tokens for a user."""
    RefreshToken.query.filter_by(user_id=user_id, revoked=False).update({"revoked": True})
    db.session.commit()