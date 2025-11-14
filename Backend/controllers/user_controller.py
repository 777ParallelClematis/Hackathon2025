from flask import request, jsonify
from models.user_model import users
import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from bson import ObjectId


def _create_jwt(user_id: str) -> str:
    """
    Create a JWT for the given user id.
    """
    secret = os.getenv("JWT_SECRET", "dev-secret-change-me")
    expires_hours = int(os.getenv("JWT_EXPIRES_HOURS", "24"))

    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(hours=expires_hours),
        "iat": datetime.utcnow(),
    }

    # PyJWT returns a string in v2+
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token


def register_user():
    data = request.json or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    # normalize email
    email = email.strip().lower()

    # check if user already exists
    existing = users.find_one({"email": email})
    if existing:
        return jsonify({"message": "User already exists"}), 409

    # hash password
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

    # optional: issue JWT immediately on register
    token = _create_jwt(user_id)

    return jsonify(
        {
            "message": "User registered",
            "userId": user_id,
            "token": token,
        }
    ), 201


def login_user():
    data = request.json or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    email = email.strip().lower()

    user = users.find_one({"email": email})
    if not user:
        # don’t leak whether email exists
        return jsonify({"message": "Invalid credentials"}), 401

    stored_hash = user.get("password_hash")
    if not stored_hash:
        return jsonify({"message": "Invalid credentials"}), 401

    password_bytes = password.encode("utf-8")
    stored_hash_bytes = stored_hash.encode("utf-8")

    if not bcrypt.checkpw(password_bytes, stored_hash_bytes):
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
