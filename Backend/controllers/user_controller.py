from flask import request, jsonify, current_app
from models.user_model import get_users_collection
import bcrypt
import jwt
import os
from datetime import datetime, timedelta

from validation.user_schemas import RegisterSchema, LoginSchema
from validation import validate_json

# Refresh token helpers
from middleware.refresh_tokens import (
    create_refresh_token,
    verify_refresh_token,
    revoke_refresh_token,
)


def _create_access_token(user_id: str) -> str:
    """
    Create a short-lived access JWT.
    """
    secret = current_app.config.get("JWT_SECRET") or os.getenv("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET must be set")

    expires_hours = int(os.getenv("JWT_EXPIRES_HOURS", "24"))

    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(hours=expires_hours),
        "iat": datetime.utcnow(),
        "type": "access",
    }

    return jwt.encode(payload, secret, algorithm="HS256")


# ---------------------------------------------------------
# REGISTER
# ---------------------------------------------------------
def register_user():
    users = get_users_collection()
    data = request.json or {}

    schema = RegisterSchema()
    error = validate_json(schema, data)
    if error:
        return error

    email = data["email"].strip().lower()
    password = data["password"]

    existing = users.find_one({"email": email})
    if existing:
        return jsonify({"message": "User already exists"}), 409

    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password_bytes, salt).decode("utf-8")

    user_doc = {
        "email": email,
        "password_hash": password_hash,
        "created_at": datetime.utcnow(),
    }

    result = users.insert_one(user_doc)
    user_id = str(result.inserted_id)

    # Issue tokens
    access = _create_access_token(user_id)
    refresh = create_refresh_token(user_id)

    return jsonify(
        {
            "message": "User registered",
            "userId": user_id,
            "accessToken": access,
            "refreshToken": refresh,
        }
    ), 201


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------
def login_user():
    users = get_users_collection()
    data = request.json or {}

    schema = LoginSchema()
    error = validate_json(schema, data)
    if error:
        return error

    email = data["email"].strip().lower()
    password = data["password"]

    user = users.find_one({"email": email})
    if not user:
        return jsonify({"message": "Invalid credentials"}), 401

    stored_hash = user.get("password_hash")
    if not stored_hash:
        return jsonify({"message": "Invalid credentials"}), 401

    if not bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
        return jsonify({"message": "Invalid credentials"}), 401

    user_id = str(user["_id"])

    # Issue tokens
    access = _create_access_token(user_id)
    refresh = create_refresh_token(user_id)

    return jsonify(
        {
            "message": "Login successful",
            "userId": user_id,
            "accessToken": access,
            "refreshToken": refresh,
        }
    ), 200


# ---------------------------------------------------------
# REFRESH SESSION
# ---------------------------------------------------------
def refresh_session():
    data = request.get_json() or {}
    token = data.get("refreshToken")

    if not token:
        return jsonify({"message": "Refresh token required"}), 400

    user_id = verify_refresh_token(token)
    if not user_id:
        return jsonify({"message": "Invalid or expired refresh token"}), 401

    # Rotate old refresh token
    revoke_refresh_token(token)

    # Issue new pair
    new_refresh = create_refresh_token(user_id)
    new_access = _create_access_token(user_id)

    return jsonify(
        {
            "accessToken": new_access,
            "refreshToken": new_refresh,
        }
    ), 200


# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------
def logout_user():
    data = request.get_json() or {}
    token = data.get("refreshToken")

    if token:
        revoke_refresh_token(token)

    return jsonify({"message": "Logged out"}), 200
