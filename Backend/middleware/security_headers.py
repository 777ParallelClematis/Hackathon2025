# middleware/security_headers.py

def apply_security_headers(response):
    """
    Apply strong OWASP security headers to every outgoing response.
    Safe defaults for APIs + SPA frontends.
    """

    # Prevent MIME sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"

    # Basic referrer protection
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # HSTS (only effective over HTTPS)
    response.headers["Strict-Transport-Security"] = (
        "max-age=63072000; includeSubDomains; preload"
    )

    # Content Security Policy — safe for API-only!
    # Allows your frontend to call your backend without issues.
    response.headers["Content-Security-Policy"] = (
        "default-src 'none'; "
        "img-src 'self' data: https:; "
        "font-src 'self' https:; "
        "style-src 'self' 'unsafe-inline' https:; "
        "script-src 'self' 'unsafe-inline'; "
        "connect-src 'self' https:; "
        "base-uri 'self'; "
        "frame-ancestors 'none'"
    )

    return response
