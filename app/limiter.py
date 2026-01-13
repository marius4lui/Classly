import os
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

# Helper to get IP (Secure: relies on get_remote_address which handles X-Forwarded-For if configured)
def get_key_func(request: Request):
    return get_remote_address(request)

def is_whitelisted(request: Request):
    whitelist = os.getenv("RATE_LIMIT_WHITELIST_IPS", "")
    if not whitelist:
        return False

    client_ip = get_remote_address(request)
    return client_ip in [ip.strip() for ip in whitelist.split(",")]

def get_key_func_with_whitelist(request: Request):
    if is_whitelisted(request):
        return None # Skip rate limit
    return get_key_func(request)

def get_default_limit_string():
    # Prefer IP based limit config if enabled, else generic
    if os.getenv("IP_RATE_LIMIT_ENABLED", "true").lower() == "true":
         requests = os.getenv('IP_RATE_LIMIT_REQUESTS', '200')
         window = os.getenv('IP_RATE_LIMIT_WINDOW', '60')
         return f"{requests}/{window} second"

    if os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true":
         requests = os.getenv('RATE_LIMIT_REQUESTS', '100')
         window = os.getenv('RATE_LIMIT_WINDOW', '60')
         return f"{requests}/{window} second"

    return "100/minute" # Fallback

# Configure Limiter
limiter = Limiter(
    key_func=get_key_func_with_whitelist,
    default_limits=[get_default_limit_string],
    enabled=True # Always enabled in limiter, but limits might be loose if env var off.
    # Wait, if RATE_LIMIT_ENABLED is false, we should disable.
    # But we have two flags.
    # We'll set enabled=True and control via the limit string or a custom enabled check?
    # SlowAPI `enabled` is global.
    # If IP limit is enabled OR Rate limit is enabled, we should be enabled.
)

# We can also add a custom toggle if needed, but the limit string function
# returning a permissive limit or the enabled flag handles it.
# Actually, let's respect the flags properly.
# If neither is enabled, we can disable.
is_enabled = (os.getenv("IP_RATE_LIMIT_ENABLED", "true").lower() == "true") or \
             (os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true")

limiter.enabled = is_enabled
