# middleware/bruteforce.py
import time
from functools import wraps
from flask import request, jsonify

from middleware.redis_client import redis_client

MAX_ATTEMPTS = 5          # before lockout
LOCKOUT_SECONDS = 600     # 10 minutes (temporary lockout)


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
        # Check lockout
        # -------------------------------------
        locked_until = redis_client.get(lock_key)
        if locked_until:
            if float(locked_until) > time.time():
                # Locked; return generic error (OWASP requirement)
                return jsonify({"message": "Invalid credentials"}), 401
            else:
                # Lock expired → remove
                redis_client.delete(lock_key)
                redis_client.delete(attempt_key)

        # -------------------------------------
        # Execute actual login logic
        # -------------------------------------
        response = f(*args, **kwargs)

        # Successful login resets counters
        if response[1] == 200:
            redis_client.delete(attempt_key)
            return response

        # -------------------------------------
        # On failure: increment attempts
        # -------------------------------------
        attempts = redis_client.incr(attempt_key)

        # Set TTL on attempts so old failures expire
        redis_client.expire(attempt_key, LOCKOUT_SECONDS)

        if attempts >= MAX_ATTEMPTS:
            # Place lockout
            redis_client.set(
                lock_key,
                time.time() + LOCKOUT_SECONDS,
                ex=LOCKOUT_SECONDS
            )
            # Reset attempts
            redis_client.delete(attempt_key)

        # Always return the same message
        return jsonify({"message": "Invalid credentials"}), 401

    return wrapper
