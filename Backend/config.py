# config.py
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Environment and debug
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = ENV == "development"

    # Flask secret key (for sessions, signing, etc.)
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    if not SECRET_KEY and ENV != "development":
        raise RuntimeError("FLASK_SECRET_KEY must be set in production")

    # Mongo / database
    MONGO_URI = os.getenv("MONGO_URI")
    if not MONGO_URI:
        raise RuntimeError("MONGO_URI is required")

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET")
    if not JWT_SECRET_KEY and ENV != "development":
        raise RuntimeError("JWT_SECRET must be set in production")

    JWT_ALGORITHM = "HS256"
    # Access token lifetime in seconds (15 minutes)
    JWT_ACCESS_TTL = int(os.getenv("JWT_ACCESS_TTL", 900))
    # Refresh token lifetime in seconds (14 days)
    JWT_REFRESH_TTL = int(os.getenv("JWT_REFRESH_TTL", 1209600))

    # CORS
    # Restrict in real environments – adjust to your frontend domains
    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173"
    ).split(",")
