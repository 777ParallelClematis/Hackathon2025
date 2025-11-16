# db.py
import os
from pymongo import MongoClient
from flask import current_app

_client = None


def init_db_client(app=None):
    """
    Initialise a single MongoClient for the app lifetime.
    Call this once in app.py (create_app).
    """
    global _client

    if _client is None:
        if app is None:
            raise RuntimeError("App context required to initialise DB client")

        uri = app.config.get("MONGO_URI")
        if not uri:
            raise RuntimeError("MONGO_URI not configured")

        _client = MongoClient(
            uri,
            serverSelectionTimeoutMS=5000,  # fail fast
        )

        # Optional: force a ping on startup to fail early
        try:
            _client.admin.command("ping")
        except Exception as exc:
            app.logger.error("Mongo connection failed: %s", exc)
            raise


def get_db():
    """
    Get the 'notebuddy' database from the existing client.
    Assumes init_db_client() has been called at startup.
    """
    global _client
    if _client is None:
        # For safety; in practice you should always call init_db_client in app startup
        uri = current_app.config.get("MONGO_URI")
        if not uri:
            raise RuntimeError("MONGO_URI not configured")
        _client = MongoClient(uri, serverSelectionTimeoutMS=5000)

    return _client["notebuddy"]
