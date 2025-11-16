from flask import request, jsonify, g
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
from dateutil import parser

from db import get_db
from validation.note_schemas import SaveNoteSchema, UpdateNoteSchema
from validation import validate_json


def normalize_timestamp(value):
    """Ensure Mongo timestamp is returned as ISO-8601."""
    if not value:
        return None

    if hasattr(value, "isoformat"):
        return value.isoformat()

    try:
        parsed = parser.parse(str(value))
        return parsed.isoformat()
    except Exception:
        return str(value)


# -------------------------------------------------------------
# SAVE NOTE
# -------------------------------------------------------------
def save_note():
    data = request.get_json() or {}

    # Validation
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
        "created_by": ObjectId(g.user_id),  # BOLA protection
    }

    result = db.notes.insert_one(note)

    return jsonify({
        "message": "Note saved",
        "id": str(result.inserted_id),
    }), 201


# -------------------------------------------------------------
# GET NOTES FOR USER
# -------------------------------------------------------------
def get_all_notes():
    try:
        db = get_db()

        cursor = db.notes.find(
            {"created_by": ObjectId(g.user_id)}
        ).sort("created_at", -1)

        notes = []
        for note in cursor:
            notes.append({
                "id": str(note["_id"]),
                "title": note.get("title", ""),
                "note_text": note.get("note_text", ""),
                "created_at": normalize_timestamp(note.get("created_at")),
                "updated_at": normalize_timestamp(note.get("updated_at")),
            })

        return jsonify(notes), 200

    except Exception as e:
        print("Error fetching notes:", e)
        return jsonify({"error": "Failed to fetch notes"}), 500


# -------------------------------------------------------------
# UPDATE NOTE
# -------------------------------------------------------------
def update_note(note_id):
    """
    Securely update a user's note.
    PATCH /api/notes/update/<note_id>
    """

    # Validate ID
    try:
        oid = ObjectId(note_id)
    except InvalidId:
        return jsonify({"error": "Invalid note ID"}), 400

    data = request.get_json() or {}

    # Validation
    schema = UpdateNoteSchema()
    error = validate_json(schema, data)
    if error:
        return error

    if not data:
        return jsonify({"error": "No valid fields provided"}), 400

    # Build update fields
    update_fields = {}
    if "note_text" in data:
        update_fields["note_text"] = data["note_text"].strip()

    if "title" in data:
        update_fields["title"] = data["title"].strip()

    update_fields["updated_at"] = datetime.utcnow()

    db = get_db()

    # BOLA: Only update if note belongs to user
    result = db.notes.update_one(
        {"_id": oid, "created_by": ObjectId(g.user_id)},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Note not found or not yours"}), 404

    updated = db.notes.find_one({"_id": oid})

    return jsonify({
        "message": "Note updated",
        "id": str(updated["_id"]),
        "title": updated.get("title", ""),
        "note_text": updated.get("note_text", ""),
        "created_at": normalize_timestamp(updated.get("created_at")),
        "updated_at": normalize_timestamp(updated.get("updated_at")),
    }), 200
