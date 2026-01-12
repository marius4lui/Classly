from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import json

from app.database import get_db
from app.models import User, UserPreferences, ApiKey
from app.core.auth import get_current_user
from app.core.auth_config import get_auth_settings
import pyotp
import qrcode
import io
import base64
import secrets
from datetime import datetime, timedelta
from fastapi import Form

router = APIRouter(
    prefix="/preferences",
    tags=["preferences"],
    responses={404: {"description": "Not found"}},
)
settings = get_auth_settings()

class PreferencesUpdate(BaseModel):
    filter_subjects: List[str]
    filter_event_types: List[str]
    filter_priority: List[str] = []

@router.get("")
def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    prefs = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()
    
    if not prefs:
        # Return defaults
        return {
            "filter_subjects": [],
            "filter_event_types": [],
            "filter_priority": []
        }
        
    return {
        "filter_subjects": json.loads(prefs.filter_subjects or "[]"),
        "filter_event_types": json.loads(prefs.filter_event_types or "[]"),
        "filter_priority": json.loads(prefs.filter_priority or "[]"),
    }

@router.put("")
def update_preferences(
    data: PreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    prefs = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()
    
    if not prefs:
        prefs = UserPreferences(user_id=current_user.id)
        db.add(prefs)
    
    prefs.filter_subjects = json.dumps(data.filter_subjects)
    prefs.filter_event_types = json.dumps(data.filter_event_types)
    prefs.filter_priority = json.dumps(data.filter_priority)
    
    db.commit()
    return {"status": "ok"}

# --- 2FA Setup Routes ---

@router.get("/2fa/setup")
def setup_2fa(
    current_user: User = Depends(get_current_user)
):
    if not settings.enable_2fa:
        raise HTTPException(status_code=400, detail="2FA is not enabled on this server")

    if current_user.totp_enabled:
        return {"status": "already_enabled"}

    # Generate Secret
    secret = pyotp.random_base32()

    # Generate QR Code
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=current_user.email or current_user.name, issuer_name="Classly")

    img = qrcode.make(uri)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    return {
        "secret": secret,
        "qr_code": f"data:image/png;base64,{img_str}"
    }

@router.post("/2fa/enable")
def enable_2fa(
    secret: str = Form(...),
    code: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not settings.enable_2fa:
         raise HTTPException(status_code=400, detail="2FA not enabled")

    # Verify code with secret
    totp = pyotp.TOTP(secret)
    if not totp.verify(code):
        raise HTTPException(status_code=400, detail="Invalid code")

    # Save to user
    current_user.totp_secret = secret
    current_user.totp_enabled = True
    db.commit()

    return {"status": "success"}

@router.post("/2fa/disable")
def disable_2fa(
    code: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.totp_enabled:
        return {"status": "already_disabled"}

    # Verify code before disabling
    totp = pyotp.TOTP(current_user.totp_secret)
    if not totp.verify(code):
        raise HTTPException(status_code=400, detail="Invalid code")

    current_user.totp_enabled = False
    current_user.totp_secret = None
    db.commit()

    return {"status": "success"}

# --- API Keys Routes ---

@router.get("/api-keys")
def list_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not settings.enable_api_keys:
        return []

    keys = db.query(ApiKey).filter(ApiKey.user_id == current_user.id).all()
    return [
        {"id": k.id, "name": k.name, "created_at": k.created_at, "expires_at": k.expires_at}
        for k in keys
    ]

@router.post("/api-keys")
def create_api_key(
    name: str = Form(...),
    expires_in_days: int = Form(365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not settings.enable_api_keys:
        raise HTTPException(status_code=400, detail="API Keys not enabled")

    # Generate Key
    raw_key = "cls_" + secrets.token_urlsafe(32)
    # Hash it for storage (simplified, ideally use slow hash like argon2 but for API keys SHA256 is common if high entropy)
    # Actually we should use a fast hash because it's checked on every request.
    # But wait, `passlib` is available. Let's use SHA256 or similar.
    # Or just store the hash.
    import hashlib
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    new_key = ApiKey(
        user_id=current_user.id,
        name=name,
        key_hash=key_hash,
        expires_at=datetime.utcnow() + timedelta(days=expires_in_days)
    )
    db.add(new_key)
    db.commit()

    return {"name": name, "key": raw_key, "expires_at": new_key.expires_at}

@router.delete("/api-keys/{key_id}")
def delete_api_key(
    key_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    key = db.query(ApiKey).filter(ApiKey.id == key_id, ApiKey.user_id == current_user.id).first()
    if key:
        db.delete(key)
        db.commit()
    return {"status": "deleted"}
