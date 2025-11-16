from flask import Blueprint
from controllers.notes_controller import save_note, get_all_notes, update_note
from middleware.auth import require_auth
from middleware.rate_limit import limiter

notes_routes = Blueprint("notes_routes", __name__)

# Save new note
notes_routes.route("/save", methods=["POST"])(
    limiter.limit("30 per minute")(require_auth(save_note))
)

# Fetch notes for the logged-in user
notes_routes.route("/all", methods=["GET"])(
    limiter.limit("60 per minute")(require_auth(get_all_notes))
)

# Update an existing note
notes_routes.route("/update/<note_id>", methods=["PATCH"])(
    limiter.limit("30 per minute")(require_auth(update_note))
)
