# app.py
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

from config import Config

# Blueprints
from routes.user_routes import user_routes
from routes.notes_routes import notes_routes
from routes.ai_routes import ai_routes

# Rate limiter
from middleware.rate_limit import limiter

# Database
from db import init_db_client, get_db

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # --- Initialise rate limiting for this app ---
    limiter.init_app(app)

    # --- Restrictive CORS ---
    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=False,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        max_age=3600,
    )

    # --- Initialise DB client once ---
    init_db_client(app)

    # --- Register blueprints ---
    app.register_blueprint(user_routes, url_prefix="/api/users")
    app.register_blueprint(notes_routes, url_prefix="/api/notes")
    app.register_blueprint(ai_routes, url_prefix="/api/ai")

    # --- DB test route ---
    @app.route("/api/test-db", methods=["GET"])
    def test_db():
        try:
            db = get_db()
            collections = db.list_collection_names()
            return {"status": "ok", "collections": collections}, 200
        except Exception as e:
            app.logger.error("TEST-DB ERROR: %s", e)
            return {"status": "error", "message": "Internal server error"}, 500

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", 5000))
    app.run(port=port, debug=app.config["DEBUG"])
