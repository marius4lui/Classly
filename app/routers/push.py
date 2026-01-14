"""
Push Notification endpoints for Classly.

Endpoints:
- POST /api/push/register - Register/update FCM or APNs device token
- DELETE /api/push/unregister - Remove a device token
"""
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud

router = APIRouter(prefix="/api/push", tags=["push"])


def _extract_bearer_token(authorization: str) -> str:
    """Extract Bearer token from Authorization header"""
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) != 2:
        return None
    if parts[0].lower() != "bearer":
        return None
    return parts[1].strip()


class DeviceTokenRequest(BaseModel):
    """Request body for registering a device token"""
    device_token: str
    platform: str  # "fcm" or "apns"


class UnregisterRequest(BaseModel):
    """Request body for unregistering a device token"""
    device_token: str


@router.post("/register")
def register_device_token(
    request: DeviceTokenRequest,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Register or update a device token for push notifications.
    
    Requires a valid Bearer token (from OAuth flow or API token).
    
    Request Body (JSON):
        - device_token: The FCM or APNs device token
        - platform: "fcm" for Android/FCM or "apns" for iOS/APNs
    
    Response:
        - status: "registered" or "updated"
        - device_token: The registered device token
        - platform: The platform type
    """
    token_value = _extract_bearer_token(authorization)
    if not token_value:
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    
    token = crud.use_integration_token(db, token_value)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Validate platform
    if request.platform.lower() not in ["fcm", "apns"]:
        raise HTTPException(status_code=400, detail="Platform must be 'fcm' or 'apns'")
    
    # Validate device token length
    if not request.device_token or len(request.device_token) < 10:
        raise HTTPException(status_code=400, detail="Invalid device token")
    
    # Create or update device token
    device_token = crud.create_or_update_device_token(
        db,
        user_id=token.user_id,
        device_token=request.device_token,
        platform=request.platform.lower()
    )
    
    return {
        "status": "registered",
        "device_token": device_token.device_token,
        "platform": device_token.platform
    }


@router.delete("/unregister")
def unregister_device_token(
    request: UnregisterRequest,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Unregister a device token (e.g., on logout).
    
    Requires a valid Bearer token.
    
    Request Body (JSON):
        - device_token: The device token to remove
    
    Response:
        - status: "unregistered" or "not_found"
    """
    token_value = _extract_bearer_token(authorization)
    if not token_value:
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    
    token = crud.use_integration_token(db, token_value)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Delete device token (only if it belongs to this user)
    deleted = crud.delete_device_token(db, request.device_token, user_id=token.user_id)
    
    return {
        "status": "unregistered" if deleted else "not_found"
    }


@router.get("/tokens")
def list_device_tokens(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    List all registered device tokens for the authenticated user.
    
    Requires a valid Bearer token.
    
    Response:
        - tokens: List of device tokens with platform info
    """
    token_value = _extract_bearer_token(authorization)
    if not token_value:
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    
    token = crud.use_integration_token(db, token_value)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    device_tokens = crud.get_device_tokens_for_user(db, token.user_id)
    
    return {
        "tokens": [
            {
                "device_token": dt.device_token[:20] + "...",  # Truncate for security
                "platform": dt.platform,
                "created_at": dt.created_at.isoformat() if dt.created_at else None,
                "updated_at": dt.updated_at.isoformat() if dt.updated_at else None
            }
            for dt in device_tokens
        ]
    }
