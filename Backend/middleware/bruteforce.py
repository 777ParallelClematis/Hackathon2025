# middleware/bruteforce.py
import time
from functools import wraps
from flask import request, jsonify

# from middleware.redis_client import redis_client # <--- KEEP THIS COMMENTED OUT

MAX_ATTEMPTS = 5         # before lockout
LOCKOUT_SECONDS = 600    # 10 minutes (temporary lockout)


def brute_force_key(email, ip):
    return f"bf:{email}:{ip}"


def lockout_key(email):
    return f"bf_lock:{email}"


def bruteforce_protect(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        data = request.get_json() or {}

        email = (data.get("email") or "").lower().strip()
        ip = request.remote_addr or "unknown"

        attempt_key = brute_force_key(email, ip)
        lock_key = lockout_key(email)

        # -------------------------------------
        # Check lockout (TEMPORARILY DISABLED)
        # -------------------------------------
        # locked_until = redis_client.get(lock_key) 
        locked_until = None # <--- Mock the result to skip lockout check
        
        if locked_until:
            if float(locked_until) > time.time():
                # Locked; return generic error (OWASP requirement)
                return jsonify({"message": "Invalid credentials"}), 401
            else:
                     # Lock expired → remove
                    # redis_client.delete(lock_key) # <--- Commented out
                    # redis_client.delete(attempt_key) # <--- Commented out
                    pass # <--- ADD THIS LINE with the correct indentation

        # -------------------------------------
        # Execute actual login logic
        # -------------------------------------
        try:
            response = f(*args, **kwargs)
        except Exception:
            # If the login handler throws an exception (e.g., error in controller/model),
            # we need to return the generic failure response instead of falling through
            # to the failure logic below.
            return jsonify({"message": "Invalid credentials"}), 401


        # Successful login resets counters
        if response[1] == 200:
            # redis_client.delete(attempt_key) # <--- Commented out
            return response

        # -------------------------------------
        # On failure: increment attempts (TEMPORARILY DISABLED)
        # -------------------------------------
        # attempts = redis_client.incr(attempt_key) # <--- Commented out
        
        # Set TTL on attempts so old failures expire
        # redis_client.expire(attempt_key, LOCKOUT_SECONDS) # <--- Commented out

        # if attempts >= MAX_ATTEMPTS:
            # Place lockout
            # redis_client.set(
            #     lock_key,
            #     time.time() + LOCKOUT_SECONDS,
            #     ex=LOCKOUT_SECONDS
            # )
            # Reset attempts
            # redis_client.delete(attempt_key) # <--- Commented out

        # Always return the login function's original response on failure (not always 401)
        # To strictly bypass the bruteforce mechanism's custom return:
        return response # <--- Return the original failure response from the view function (e.g., 401 or 400)

    return wrapper