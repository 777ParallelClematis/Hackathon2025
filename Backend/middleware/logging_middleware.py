# middleware/logging_middleware.py
import time
import uuid
import json
from flask import request, g

# Fields we never log for security reasons
SENSITIVE_FIELDS = {"password", "new_password", "token"}


def sanitize_payload(data):
    """Remove sensitive information before logging."""
    if not isinstance(data, dict):
        return data

    return {
        k: ("[REDACTED]" if k in SENSITIVE_FIELDS else v)
        for k, v in data.items()
    }


def before_request_logging():
    """Executed before each request."""
    g.request_id = str(uuid.uuid4())
    g.start_time = time.time()

    try:
        payload = request.get_json(silent=True) or {}
    except Exception:
        payload = {}

    payload = sanitize_payload(payload)

    log = {
        "event": "request_received",
        "request_id": g.request_id,
        "method": request.method,
        "path": request.path,
        "client_ip": request.remote_addr,
        "payload": payload,
    }

    print(json.dumps(log))


def after_request_logging(response):
    """Executed after each request."""
    duration = round((time.time() - g.start_time) * 1000, 2)

    # Attach Request ID to response headers so frontend can report errors with it
    response.headers["X-Request-ID"] = g.request_id

    user_id = getattr(g, "user_id", None)

    log = {
        "event": "request_completed",
        "request_id": g.request_id,
        "method": request.method,
        "path": request.path,
        "status": response.status_code,
        "duration_ms": duration,
        "client_ip": request.remote_addr,
        "user_id": user_id,
    }

    # Print structured JSON log
    print(json.dumps(log))

    return response
