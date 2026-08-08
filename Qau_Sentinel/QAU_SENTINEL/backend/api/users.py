from flask import Blueprint, request, jsonify
from middleware.auth import token_required, admin_required, viewer_required
from services.user_service import user_service

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("/", methods=["GET"])  # ✅ Always with trailing slash
@admin_required
def get_users():
    search = request.args.get("search", "").strip()
    users = user_service.get_all(search=search)
    return jsonify({
        "items": users,
        "total": len(users)
    })


@users_bp.route("/<int:id>", methods=["GET"])
@admin_required
def get_user(id):
    user = user_service.get_by_id(id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)


@users_bp.route("/", methods=["POST"])
@admin_required
def create_user():
    data = request.get_json()
    required_fields = ["username", "email", "password"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    try:
        user = user_service.create(data)
        return jsonify(user), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@users_bp.route("/<int:id>", methods=["PUT"])
@admin_required
def update_user(id):
    data = request.get_json()
    try:
        user = user_service.update(id, data)
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify(user)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@users_bp.route("/<int:id>", methods=["DELETE"])
@admin_required
def delete_user(id):
    try:
        success = user_service.delete(id)
        if not success:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"message": "User deleted successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400