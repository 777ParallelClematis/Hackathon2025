from flask import Blueprint
from controllers.user_controller import (
    register_user,
    login_user,
    refresh_session,
    logout_user,
)
from middleware.rate_limit import limiter
from middleware.bruteforce import bruteforce_protect

user_routes = Blueprint("user_routes", __name__)

# Register new user
user_routes.route("/register", methods=["POST"])(
    limiter.limit("3 per minute")(register_user)
)

# Login with brute-force protection
user_routes.route("/login", methods=["POST"])(
    limiter.limit("5 per minute")(bruteforce_protect(login_user))
)

# Refresh access token
user_routes.route("/refresh", methods=["POST"])(
    limiter.limit("20 per minute")(refresh_session)
)

# Logout
user_routes.route("/logout", methods=["POST"])(
    limiter.limit("30 per minute")(logout_user)
)
