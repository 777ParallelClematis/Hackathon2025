# middleware/refresh_tokens.py
import uuid
import time
import jwt
from flask import current_app
from middleware.redis_client import redis_client


REFRESH_TTL_SECONDS = 60 * 60 * 24 * 30  # 30 days


def create_refresh_token(user_id: str) -> str:
    """Generate a new refresh token and persist in Redis."""
    token_id = str(uuid.uuid4())

    payload = {
        "sub": user_id,
        "jti": token_id,
        "type": "refresh",
        "iat": int(time.time())
    }

    token = jwt.encode(
        payload,
        current_app.config["JWT_SECRET"],
        algorithm="HS256",
    )

    # store in Redis: token_id -> user_id
    redis_client.setex(
        f"refresh:{token_id}",
        REFRESH_TTL_SECONDS,
        user_id
    )

    return token


def verify_refresh_token(token: str):
    """Decode and verify the refresh token and check revocation."""
    try:
        payload = jwt.decode(
            token,
            current_app.config["JWT_SECRET"],
            algorithms=["HS256"],
            options={"require": ["sub", "jti"]}
        )
    except Exception:
        return None

    if payload.get("type") != "refresh":
        return None

    token_id = payload.get("jti")
    user_id = payload.get("sub")

    stored = redis_client.get(f"refresh:{token_id}")
    if not stored:
        return None  # expired or revoked

    if stored.decode() != user_id:
        return None

    return user_id


def revoke_refresh_token(token: str):
    """Delete refresh token from Redis."""
    try:
        payload = jwt.decode(
            token,
            current_app.config["JWT_SECRET"],
            algorithms=["HS256"],
        )
    except Exception:
        return

    token_id = payload.get("jti")
    redis_client.delete(f"refresh:{token_id}")
