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

# Middleware
from middleware.rate_limit import limiter
from middleware.security_headers import apply_security_headers
from middleware.logging_middleware import before_request_logging, after_request_logging

# Database
from db import init_db_client, get_db

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # -------------------------------
    # Rate Limiting (global init)
    # -------------------------------
    limiter.init_app(app)

    # -------------------------------
    # CORS (restrictive)
    # -------------------------------
    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=False,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        max_age=3600,
    )

    # -------------------------------
    # Database init (one-time)
    # -------------------------------
    init_db_client(app)

    # -------------------------------
    # Register Blueprints
    # -------------------------------
    app.register_blueprint(user_routes, url_prefix="/api/users")
    app.register_blueprint(notes_routes, url_prefix="/api/notes")
    app.register_blueprint(ai_routes, url_prefix="/api/ai")

    # -------------------------------
    # Security Headers (global)
    # -------------------------------
    @app.after_request
    def set_security_headers(response):
        return apply_security_headers(response)

    # -------------------------------
    # Logging Middleware
    # -------------------------------
    @app.before_request
    def log_before():
        before_request_logging()

    @app.after_request
    def log_after(response):
        return after_request_logging(response)

    # -------------------------------
    # DB test route
    # -------------------------------
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
