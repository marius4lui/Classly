import secrets
import string

def generate_join_token(length=6):
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_public_share_code(length=12):
    """
    Non-guessable short code for public share links.
    Uses a reduced alphabet to avoid ambiguous characters.
    """
    alphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"  # no 0,O,1,I
    return ''.join(secrets.choice(alphabet) for _ in range(length))
