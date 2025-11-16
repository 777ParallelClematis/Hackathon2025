from flask import Blueprint
from controllers.user_controller import register_user, login_user
from middleware.rate_limit import limiter
from middleware.bruteforce import bruteforce_protect

user_routes = Blueprint("user_routes", __name__)

user_routes.route("/register", methods=["POST"])(
    limiter.limit("3 per minute")(register_user)
)

user_routes.route("/login", methods=["POST"])(
    limiter.limit("5 per minute")(bruteforce_protect(login_user))
)
