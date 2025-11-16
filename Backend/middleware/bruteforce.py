# middleware/bruteforce.py
import time
from functools import wraps
from flask import request, jsonify

# In-memory tracking (per-process)
# In production, you would replace this with Redis.
_failed_attempts = {}
_locked_accounts = {}

# Configuration
MAX_ATTEMPTS = 5           # before lockout
LOCKOUT_SECONDS = 600      # 10 minutes


def bruteforce_protect(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        data = request.get_json() or {}

        email = (data.get("email") or "").lower().strip()
        ip = request.remote_addr or "unknown"

        # Keyed by BOTH email and ip
        key = f"{email}:{ip}"

        # ----------------------------------------
        # Check if account is currently locked
        # ----------------------------------------
        if email in _locked_accounts:
            locked_until = _locked_accounts[email]
            now = time.time()

            if now < locked_until:
                # Still locked
                return jsonify({
                    "message": "Invalid credentials"  # don't reveal lockout
                }), 401
            else:
                # Lock expired
                _locked_accounts.pop(email, None)
                _failed_attempts.pop(key, None)

        # ----------------------------------------
        # Call the wrapped function (login_user)
        # ----------------------------------------
        response = f(*args, **kwargs)

        # If login successful, reset counters
        if response[1] == 200:
            _failed_attempts.pop(key, None)
            return response

        # ----------------------------------------
        # Handle failed login (status not 200)
        # ----------------------------------------
        count = _failed_attempts.get(key, 0) + 1
        _failed_attempts[key] = count

        if count >= MAX_ATTEMPTS:
            # Lock the account
            _locked_accounts[email] = time.time() + LOCKOUT_SECONDS
            _failed_attempts.pop(key, None)

        # Always return the same message
        return jsonify({"message": "Invalid credentials"}), 401

    return wrapper
