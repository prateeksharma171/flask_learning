import jwt
import os
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify, current_app
from app.models.user import User
from app.db import db


def get_tokens_for_user(user_id):

    user = User.query.get(user_id)
    if not user:
        return None

    access_token_expires = timedelta(
        minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 15))
    )
    refresh_token_expires = timedelta(
        days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 7))
    )

    access_token = jwt.encode(
        {
            "user_id": str(user_id),
            "exp": datetime.now(timezone.utc) + access_token_expires,
            "type": "access",
            "token_version": user.token_version,
        },
        os.getenv("JWT_SECRET_KEY"),
        algorithm="HS256",
    )

    refresh_token = jwt.encode(
        {
            "user_id": str(user_id),
            "exp": datetime.now(timezone.utc) + refresh_token_expires,
            "type": "refresh",
        },
        os.getenv("JWT_REFRESH_SECRET_KEY"),
        algorithm="HS256",
    )

    return {"access_token": access_token, "refresh_token": refresh_token}


def decode_access_token(token):
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=["HS256"])
        if payload.get("type") != "access":
            return None

        user_id = payload.get("user_id")
        token_version = payload.get("token_version")

        if token_version is None:
            return None

        user = User.query.get(user_id)
        if not user or not user.is_active:
            return None

        if user.token_version is None:
            return None

        if user.token_version != token_version:
            return None

        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def decode_refresh_token(token):
    try:
        payload = jwt.decode(
            token, os.getenv("JWT_REFRESH_SECRET_KEY"), algorithms=["HS256"]
        )
        if payload.get("type") != "refresh":
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def revoke_all_user_tokens(user_id):

    with current_app.app_context():
        user = User.query.get(user_id)
        if user:
            user.refresh_token = None
            db.session.commit()
        return user is not None


def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Authorization header missing"}), 401

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"error": "Invalid authorization header format"}), 401

        token = parts[1]
        payload = decode_access_token(token)

        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401

        request.user_id = payload.get("user_id")
        return f(*args, **kwargs)

    return wrapper
