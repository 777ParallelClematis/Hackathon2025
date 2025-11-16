# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------
# Model & AI Settings
# ---------------------------------------------------------
MINILM_MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'
SIMILARITY_THRESHOLD = 0.75
CLASSIFICATION_THRESHOLD = 0.60

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = 'gemini-2.5-flash'

# ---------------------------------------------------------
# MongoDB Collection Constants
# ---------------------------------------------------------
MONGO_REF_COLLECTION = 'notes' 
MONGO_GRADES_COLLECTION = 'assessment'


# ---------------------------------------------------------
# Flask Config Class
# ---------------------------------------------------------
class Config:
    # Environment
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = ENV == "development"

    # Flask internal signing key (not JWT)
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret")
    if not SECRET_KEY and ENV != "development":
        raise RuntimeError("FLASK_SECRET_KEY must be set in production")

    # MongoDB
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "notebuddy")
    if not MONGO_URI:
        raise RuntimeError("MONGO_URI is required")

    # JWT config
    JWT_SECRET = os.getenv("JWT_SECRET")
    if not JWT_SECRET and ENV != "development":
        raise RuntimeError("JWT_SECRET must be set in production")

    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TTL = int(os.getenv("JWT_ACCESS_TTL", 900))
    JWT_REFRESH_TTL = int(os.getenv("JWT_REFRESH_TTL", 1209600))

    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
