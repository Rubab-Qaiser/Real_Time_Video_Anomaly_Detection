from flask import Blueprint, request, jsonify, current_app
from services.user_service import user_service
from utils.jwt_utils import (
    generate_access_token,
    generate_refresh_token,
    verify_access_token,
    verify_refresh_token,
    revoke_refresh_token,
    revoke_all_user_refresh_tokens,
)
from models.user import User
from database.database import db
import re

auth_bp = Blueprint("auth", __name__)


# ====================== LOGIN ======================
@auth_bp.post("/login")
def login():
    """Authenticate user and return access + refresh tokens."""
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400
    
    email = data.get("email").strip()
    password = data.get("password")
    
    # Find user by email
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    
    # Check if user is active
    if not user.active:
        return jsonify({"error": "Account is deactivated. Please contact administrator."}), 401
    
    # Verify password
    if not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401
    
    # Generate tokens
    access_token = generate_access_token(user.id)
    refresh_token, refresh_expires = generate_refresh_token(user.id)
    
    # Update last login
    user_service.update_last_login(user.id)
    
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "refresh_expires": refresh_expires.isoformat(),
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.active,
        }
    }), 200


# ====================== REFRESH ======================
@auth_bp.post("/refresh")
def refresh():
    """Get a new access token using a refresh token."""
    data = request.get_json()
    
    if not data or not data.get("refresh_token"):
        return jsonify({"error": "Refresh token is required"}), 400
    
    refresh_token = data.get("refresh_token")
    
    # Verify refresh token
    user_id, error = verify_refresh_token(refresh_token)
    if error:
        return jsonify({"error": error}), 401
    
    # Generate new access token
    new_access_token = generate_access_token(user_id)
    
    return jsonify({
        "access_token": new_access_token,
    }), 200


# ====================== LOGOUT ======================
@auth_bp.post("/logout")
def logout():
    """Logout user by revoking refresh token."""
    data = request.get_json()
    
    if not data or not data.get("refresh_token"):
        return jsonify({"error": "Refresh token is required"}), 400
    
    refresh_token = data.get("refresh_token")
    
    # Revoke the refresh token
    success = revoke_refresh_token(refresh_token)
    
    return jsonify({
        "message": "Logged out successfully" if success else "Invalid token"
    }), 200 if success else 400


# ====================== ME (Get Current User) ======================
@auth_bp.get("/me")
def get_current_user():
    """Get the current authenticated user from the access token."""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Authorization header required"}), 401
    
    token = auth_header.split(" ")[1]
    
    user_id, error = verify_access_token(token)
    if error:
        return jsonify({"error": error}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_active": user.active,
    }), 200