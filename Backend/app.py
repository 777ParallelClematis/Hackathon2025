from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Blueprints
from routes.user_routes import user_routes
from routes.notes_routes import notes_routes
from routes.ai_routes import ai_routes

# Database
from db import get_db

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(user_routes, url_prefix="/api/users")
app.register_blueprint(notes_routes, url_prefix="/api/notes")
app.register_blueprint(ai_routes, url_prefix="/api/ai")

# DB test route
@app.route("/api/test-db", methods=["GET"])
def test_db():
    try:
        db = get_db()
        collections = db.list_collection_names()
        return {"status": "ok", "collections": collections}, 200
    except Exception as e:
        print("TEST-DB ERROR:", e)
        return {"status": "error", "message": str(e)}, 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(port=port, debug=True)
