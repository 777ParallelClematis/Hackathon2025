from flask import request, jsonify
from datetime import datetime
from bson import ObjectId
from flask import g

from db import get_db
from dateutil import parser

from validation.note_schemas import SaveNoteSchema
from validation import validate_json


def save_note():
    data = request.get_json() or {}

    # -------------------------
    # Server-side validation
    # -------------------------
    schema = SaveNoteSchema()
    error = validate_json(schema, data)
    if error:
        return error

    note_text = data["note_text"]
    title = data.get("title", "")

    db = get_db()
    note = {
        "note_text": note_text,
        "title": title,
        "created_at": datetime.utcnow(),
        "created_by": ObjectId(g.user_id),   # OWASP: BOLA prevention
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

    if hasattr(value, "isoformat"):
        return value.isoformat()

    try:
        parsed = parser.parse(str(value))
        return parsed.isoformat()
    except Exception:
        return str(value)


def get_all_notes():
    try:
        db = get_db()

        # -------------------------
        # Restrict to logged-in user
        # -------------------------
        cursor = db.notes.find({"created_by": ObjectId(g.user_id)}).sort("created_at", -1)

        notes = []
        for note in cursor:
            notes.append({
                "id": str(note["_id"]),
                "title": note.get("title", ""),
                "note_text": note.get("note_text", ""),
                "created_at": normalize_timestamp(note.get("created_at")),
            })

        return jsonify(notes), 200

    except Exception as e:
        print("Error fetching notes:", e)
        return jsonify({"error": "Failed to fetch notes"}), 500
