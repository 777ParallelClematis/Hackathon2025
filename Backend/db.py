from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB_NAME
import certifi

_client = None

def get_db():
    global _client
    if _client is None:
        extra = {}
        # If using Atlas, enable TLS with certifi CA bundle
        if MONGO_URI.startswith("mongodb+srv://") or "mongodb.net" in MONGO_URI:
            extra["tlsCAFile"] = certifi.where()

        _client = MongoClient(MONGO_URI, **extra)

    return _client[MONGO_DB_NAME]
