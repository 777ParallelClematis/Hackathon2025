import uuid
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import request, jsonify, current_app, g
import os


def _get_jwt_config():
    """
    Load JWT configuration from app or environment.
    Must be consistent with user_controller._create_jwt.
    """
    secret = current_app.config.get("JWT_SECRET") or os.getenv("JWT_SECRET")
    alg = "HS256"

    if not secret:
        raise RuntimeError("JWT_SECRET must be set")

    return secret, alg


def create_access_token(user_id: str) -> str:
    secret, alg = _get_jwt_config()
    now = datetime.now(timezone.utc)
    ttl = int(current_app.config.get("JWT_ACCESS_TTL", 900))

    payload = {
        "sub": str(user_id),
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(seconds=ttl),
        "iss": "notebuddy-api",
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, secret, algorithm=alg)


def decode_token(token: str):
    secret, alg = _get_jwt_config()

    return jwt.decode(
        token,
        secret,
        algorithms=[alg],
        options={"require": ["exp", "iat", "sub"]},
    )


def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization") or ""
        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"message": "Unauthorized"}), 401

        token = parts[1]

        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Unauthorized"}), 401

        user_id = payload.get("sub")
        if not user_id:
            return jsonify({"message": "Unauthorized"}), 401

        g.user_id = user_id

        return f(*args, **kwargs)

    return wrapper
