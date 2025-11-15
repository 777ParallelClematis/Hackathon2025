from flask import Blueprint
from controllers.user_controller import register_user, login_user

user_routes = Blueprint("user_routes", __name__)

user_routes.route("/register", methods=["POST"])(register_user)
user_routes.route("/login", methods=["POST"])(login_user)
