from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def get_db():
    uri = os.getenv("MONGO_URI")
    if not uri:
        raise Exception("MONGO_URI not loaded from .env")

    client = MongoClient(uri)
    return client["notebuddy"]

print("DEBUG MONGO_URI:", os.getenv("MONGO_URI"))
