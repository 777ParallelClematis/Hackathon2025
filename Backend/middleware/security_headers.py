# middleware/security_headers.py

def apply_security_headers(response):
    """
    Apply strong OWASP security headers to every outgoing response.
    Safe defaults for API + React SPA frontends.
    """

    # Prevent MIME sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"

    # Basic referrer protection
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # HSTS (enforced only when HTTPS is used)
    response.headers["Strict-Transport-Security"] = (
        "max-age=63072000; includeSubDomains; preload"
    )

    # -------------------------------------------------------------
    # Content Security Policy — hardened & adjusted for your stack
    #
    # - NO inline scripts allowed (React doesn't need them)
    # - Inline styles allowed ('unsafe-inline') because React sometimes uses them
    # - Only specific external connections allowed:
    #      - HF API
    #      - Dev server (5173)
    #      - Your own backend
    # -------------------------------------------------------------
    response.headers["Content-Security-Policy"] = (
        "default-src 'none'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self' http://localhost:5173 https://router.huggingface.co; "
        "base-uri 'self'; "
        "frame-ancestors 'none'"
    )

    return response
