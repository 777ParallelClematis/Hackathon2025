# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Model Settings (Remain the same)
MINILM_MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'
SIMILARITY_THRESHOLD = 0.75
CLASSIFICATION_THRESHOLD = 0.60

# Gemini API Settings (Remain the same)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = 'gemini-2.5-flash'

# NEW: MongoDB Settings
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "notebuddy")
MONGO_REF_COLLECTION = 'notes' 
MONGO_GRADES_COLLECTION = 'assessment'