import os

from fastapi import Request


def cookie_secure(request: Request | None = None) -> bool:
    """
    Resolve cookie `secure` flag.

    Priority:
    1) Explicit COOKIE_SECURE env var (true/false)
    2) Auto-detect from request scheme / proxy header
    3) Fallback: False (works for local http dev)
    """
    raw = os.getenv("COOKIE_SECURE")
    if raw is not None and raw.strip() != "":
        return raw.lower() == "true"

    if request is None:
        return False

    forwarded_proto = (
        request.headers.get("x-forwarded-proto", "").split(",")[0].strip().lower()
    )
    scheme = forwarded_proto or request.url.scheme
    return scheme == "https"
