import hmac
import os
import secrets
from typing import Iterable

from fastapi import Request

CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "x-csrf-token"
CSRF_FORM_FIELD = "csrf_token"


def csrf_enabled() -> bool:
    return os.getenv("CSRF_PROTECTION_ENABLED", "true").lower() == "true"


def get_csrf_token(request: Request) -> str:
    return request.cookies.get(CSRF_COOKIE_NAME) or secrets.token_urlsafe(32)


def same_token(a: str | None, b: str | None) -> bool:
    if not a or not b:
        return False
    return hmac.compare_digest(a, b)


def is_state_changing(request: Request) -> bool:
    return request.method.upper() in {"POST", "PUT", "PATCH", "DELETE"}


def is_path_exempt(path: str, exempt_prefixes: Iterable[str]) -> bool:
    return any(path.startswith(prefix) for prefix in exempt_prefixes)

