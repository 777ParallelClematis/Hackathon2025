# config.py
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ---------------------------------------------------------
    # Environment mode
    # ---------------------------------------------------------
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = ENV == "development"

    # ---------------------------------------------------------
    # Flask internal signing key (not JWT)
    # ---------------------------------------------------------
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret")
    if not SECRET_KEY and ENV != "development":
        raise RuntimeError("FLASK_SECRET_KEY must be set in production")

    # ---------------------------------------------------------
    # MongoDB configuration
    # ---------------------------------------------------------
    MONGO_URI = os.getenv("MONGO_URI")
    if not MONGO_URI:
        raise RuntimeError("MONGO_URI is required")

    # ---------------------------------------------------------
    # JWT (Access + Refresh)
    # ---------------------------------------------------------
    # This MUST match the key used by your refresh_token middleware.
    JWT_SECRET = os.getenv("JWT_SECRET")
    if not JWT_SECRET and ENV != "development":
        raise RuntimeError("JWT_SECRET must be set in production")

    JWT_ALGORITHM = "HS256"

    # Access token lifetime (default: 15 minutes)
    JWT_ACCESS_TTL = int(os.getenv("JWT_ACCESS_TTL", 900))

    # Refresh token lifetime (default: 14 days)
    JWT_REFRESH_TTL = int(os.getenv("JWT_REFRESH_TTL", 1209600))

    # ---------------------------------------------------------
    # CORS (limit this in real deployments)
    # ---------------------------------------------------------
    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173"
    ).split(",")
