from flask import Blueprint, request, jsonify
from app.models.user import User
from app.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.auth import (
    get_tokens_for_user,
    decode_refresh_token,
    require_auth,
    revoke_all_user_tokens,
)
from app.utils.validator import validate_required

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    error = validate_required(data, ["name", "email", "password"])
    if error:
        return jsonify({"status": "error", "messages": error}), 400

    existing_user = User.query.filter_by(email=data["email"]).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 409

    user = User(
        name=data["name"],
        email=data["email"],
        password=generate_password_hash(data["password"]),
    )

    db.session.add(user)
    db.session.commit()

    tokens = get_tokens_for_user(user.id)

    return jsonify(
        {
            "message": "User registered successfully",
            "user": user.to_dict(),
            "tokens": tokens,
        }
    ), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    error = validate_required(data, ["email", "password"])
    if error:
        return jsonify({"status": "error", "messages": error}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    if not user.is_active:
        return jsonify({"error": "Account is inactive"}), 403

    user.token_version += 1

    tokens = get_tokens_for_user(user.id)

    user.refresh_token = tokens["refresh_token"]
    db.session.commit()

    return jsonify(
        {"message": "Login successful", "user": user.to_dict(), "tokens": tokens}
    ), 200


@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    data = request.get_json()
    error = validate_required(data, ["refresh_token"])
    if error:
        return jsonify({"status": "error", "messages": error}), 400

    payload = decode_refresh_token(data["refresh_token"])
    if not payload:
        return jsonify({"error": "Invalid or expired refresh token"}), 401

    user = User.query.get(payload["user_id"])
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not user.is_active:
        return jsonify({"error": "Account is inactive"}), 403

    tokens = get_tokens_for_user(user.id)

    user.refresh_token = tokens["refresh_token"]
    db.session.commit()

    return jsonify({"message": "Tokens refreshed successfully", "tokens": tokens}), 200


@auth_bp.route("/logout", methods=["POST"])
@require_auth
def logout():
    user_id = request.user_id
    revoke_all_user_tokens(user_id)
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/me", methods=["GET"])
@require_auth
def me():
    user_id = request.user_id
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"user": user.to_dict()}), 200
