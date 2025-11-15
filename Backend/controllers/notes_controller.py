from flask import request, jsonify
from datetime import datetime
from db import get_db
from dateutil import parser


def save_note():
    data = request.get_json()
    content = (data.get("content") or "").strip()

    if not content:
        return jsonify({"error": "Content is required"}), 400

    db = get_db()
    note = {
        "content": content,
        "created_at": datetime.utcnow(),
    }

    result = db.notes.insert_one(note)

    return jsonify({
        "message": "Note saved",
        "id": str(result.inserted_id),
    }), 201


def normalize_timestamp(value):
    """Ensure Mongo timestamp is returned as valid ISO-8601."""
    if not value:
        return None

    # If it's already a datetime object
    if hasattr(value, "isoformat"):
        return value.isoformat()

    # If it's a string, try parsing to datetime and re-serialising
    try:
        parsed = parser.parse(str(value))
        return parsed.isoformat()
    except Exception:
        # Fallback: return as string
        return str(value)


def get_all_notes():
    try:
        db = get_db()
        cursor = db.notes.find().sort("created_at", -1)

        notes = []
        for note in cursor:
            notes.append({
                "id": str(note["_id"]),
                "content": note.get("content", ""),
                "created_at": normalize_timestamp(note.get("created_at"))
            })

        return jsonify(notes), 200

    except Exception as e:
        print("Error fetching notes:", e)
        return jsonify({"error": "Failed to fetch notes"}), 500
