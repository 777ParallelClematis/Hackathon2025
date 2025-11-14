from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

from routes.user_routes import user_routes
from db import get_db

load_dotenv()

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(user_routes, url_prefix="/api/users")


# ----------------------------
# TEST DB ROUTE
# ----------------------------
@app.route("/api/test-db", methods=["GET"])
def test_db():
    try:
        db = get_db()
        collections = db.list_collection_names()
        return {"status": "ok", "collections": collections}, 200
    except Exception as e:
        print("TEST-DB ERROR:", e)
        return {"status": "error", "message": str(e)}, 500


# ----------------------------
# START SERVER (this was missing!)
# ----------------------------
if __name__ == "__main__":
    app.run(port=int(os.getenv("PORT", 5000)), debug=True)
