from flask import Blueprint
from controllers.notes_controller import save_note, get_all_notes
from middleware.auth import require_auth

notes_routes = Blueprint("notes_routes", __name__)

# Protected endpoints
notes_routes.route("/save", methods=["POST"])(require_auth(save_note))
notes_routes.route("/all", methods=["GET"])(require_auth(get_all_notes))
