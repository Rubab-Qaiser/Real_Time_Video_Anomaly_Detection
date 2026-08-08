from functools import wraps
from flask import request, jsonify
from utils.jwt_utils import verify_access_token
from models.user import User


def token_required(f):
    """Decorator to protect routes that require authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        token = None

        # 1. Try Authorization: Bearer <token> header
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        # 2. Fallback: ?token=<jwt> query param (for window.open downloads)
        elif request.args.get("token"):
            token = request.args.get("token")

        if not token:
            return jsonify({"error": "Authorization header required"}), 401
        
        user_id, error = verify_access_token(token)
        if error:
            return jsonify({"error": error}), 401
        
        # Attach user to request context
        request.user_id = user_id  # type: ignore
        request.user = User.query.get(user_id)  # type: ignore
        
        return f(*args, **kwargs)
    
    return decorated


def role_required(required_roles):
    """Decorator to protect routes that require specific roles."""
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            user = getattr(request, 'user', None)
            
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            if user.role not in required_roles:
                return jsonify({
                    "error": f"Role '{user.role}' does not have access. Required: {', '.join(required_roles)}"
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated
    
    return decorator


# ============= CONVENIENCE DECORATORS =============
# These are the functions that cameras.py and users.py import

def admin_required(f):
    """Decorator to protect routes that require Admin role."""
    @wraps(f)
    @role_required(["Admin"])
    def decorated(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated


def operator_required(f):
    """Decorator to protect routes that require Admin or Operator role."""
    @wraps(f)
    @role_required(["Admin", "Operator"])
    def decorated(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated


def viewer_required(f):
    """Decorator to protect routes that require any authenticated user."""
    @wraps(f)
    @role_required(["Admin", "Operator", "Viewer"])
    def decorated(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated