from flask import request, jsonify, current_app
from models.user_model import get_users_collection
import bcrypt
import jwt
import os
from datetime import datetime, timedelta

from validation.user_schemas import RegisterSchema, LoginSchema
from validation import validate_json


def _create_jwt(user_id: str) -> str:
    """
    Create a JWT for the given user id.
    Uses JWT_SECRET from environment or app config.
    """
    secret = current_app.config.get("JWT_SECRET") or os.getenv("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET must be set")

    expires_hours = int(os.getenv("JWT_EXPIRES_HOURS", "24"))

    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(hours=expires_hours),
        "iat": datetime.utcnow(),
    }

    return jwt.encode(payload, secret, algorithm="HS256")


def register_user():
    users = get_users_collection()
    data = request.json or {}

    # -------------------------
    # Server-side validation
    # -------------------------
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

    token = _create_jwt(user_id)

    return jsonify(
        {
            "message": "User registered",
            "userId": user_id,
            "token": token,
        }
    ), 201


def login_user():
    users = get_users_collection()
    data = request.json or {}

    # -------------------------
    # Server-side validation
    # -------------------------
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
    token = _create_jwt(user_id)

    return jsonify(
        {
            "message": "Login successful",
            "userId": user_id,
            "token": token,
        }
    ), 200
