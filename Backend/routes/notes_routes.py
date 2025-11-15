from flask import Blueprint
from controllers.notes_controller import save_note, get_all_notes

notes_routes = Blueprint("notes_routes", __name__)

notes_routes.route("/save", methods=["POST"])(save_note)
notes_routes.route("/all", methods=["GET"])(get_all_notes)
