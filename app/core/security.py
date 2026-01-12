
import secrets
import string
from itsdangerous import URLSafeTimedSerializer
import os

# Default secret if not provided (only for dev)
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod")
signer = URLSafeTimedSerializer(SECRET_KEY, salt="auth-cookie-signer")

def generate_join_token():
    # 6 char uppercase alphanumeric
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(6))

def generate_token():
    return secrets.token_urlsafe(32)

def sign_data(data: dict) -> str:
    """Sign data for secure client-side storage (cookies)"""
    return signer.dumps(data)

def unsign_data(token: str, max_age: int = 3600) -> dict:
    """Unsign data. Returns None if invalid or expired."""
    try:
        return signer.loads(token, max_age=max_age)
    except Exception:
        return None
