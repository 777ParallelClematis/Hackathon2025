from flask import Blueprint
from controllers.notes_controller import save_note, get_all_notes
from middleware.auth import require_auth
from middleware.rate_limit import limiter

notes_routes = Blueprint("notes_routes", __name__)

notes_routes.route("/save", methods=["POST"])(
    limiter.limit("30 per minute")(require_auth(save_note))
)

notes_routes.route("/all", methods=["GET"])(
    limiter.limit("60 per minute")(require_auth(get_all_notes))
)
