import os
import jwt
from functools import wraps
from flask import request, jsonify


def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"message": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ", 1)[1].strip()
        secret = os.getenv("JWT_SECRET", "dev-secret-change-me")

        try:
            payload = jwt.decode(token, secret, algorithms=["HS256"])
            # attach user id to request for downstream use
            request.user_id = payload.get("sub")
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401

        return f(*args, **kwargs)

    return wrapper
