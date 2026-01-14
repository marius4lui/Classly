"""
OAuth 2.0 Authorization Code Flow endpoints for Classly.

Endpoints:
- POST /api/oauth/authorize - Create authorization code (requires session cookie)
- POST /api/oauth/token - Exchange authorization code for access token
- GET /api/oauth/userinfo - Get current user info (requires Bearer token)
"""
import datetime
from fastapi import APIRouter, Depends, Form, Header, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, models
from app.core.auth import get_current_user

router = APIRouter(prefix="/api/oauth", tags=["oauth"])


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


@router.post("/authorize")
def oauth_authorize(
    request: Request,
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    scope: str = Form("read:events"),
    response_type: str = Form("code"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    OAuth 2.0 Authorization Endpoint.
    
    Creates an authorization code for the authenticated user.
    Requires a valid session cookie (user must be logged in).
    
    Request:
        - client_id: The OAuth client ID
        - redirect_uri: The redirect URI registered with the client
        - scope: Requested scope (default: read:events)
        - response_type: Must be "code" for authorization code flow
    
    Response:
        - code: The authorization code to exchange for an access token
        - redirect_uri: The redirect URI to use
        - expires_in: Seconds until the code expires
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required. Please login first.")
    
    if response_type != "code":
        raise HTTPException(status_code=400, detail="Only response_type=code is supported")
    
    # For now, we accept any client_id (simplified flow for mobile apps)
    # In production, you should validate the client_id and redirect_uri
    # against registered OAuth clients using:
    # client = crud.get_oauth_client_by_client_id(db, client_id)
    
    # Create authorization code
    auth_code = crud.create_authorization_code(
        db,
        client_id=client_id,
        user_id=current_user.id,
        redirect_uri=redirect_uri,
        scope=scope,
        expires_in_seconds=600  # 10 minutes
    )
    
    return {
        "code": auth_code.code,
        "redirect_uri": redirect_uri,
        "expires_in": 600
    }


@router.post("/token")
def oauth_token(
    grant_type: str = Form(...),
    code: str = Form(None),
    client_id: str = Form(...),
    client_secret: str = Form(None),
    redirect_uri: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    OAuth 2.0 Token Endpoint.
    
    Exchanges an authorization code for an access token.
    
    Request:
        - grant_type: Must be "authorization_code"
        - code: The authorization code from /authorize
        - client_id: The OAuth client ID
        - client_secret: The OAuth client secret (optional for public clients)
        - redirect_uri: Must match the redirect_uri from /authorize
    
    Response:
        - access_token: The Bearer token to use for API requests
        - token_type: "bearer"
        - expires_at: ISO timestamp when the token expires (or null for no expiry)
        - scope: The granted scope
    """
    if grant_type != "authorization_code":
        raise HTTPException(status_code=400, detail="Only grant_type=authorization_code is supported")
    
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code is required")
    
    # Use the authorization code
    auth_code = crud.use_authorization_code(db, code, client_id, redirect_uri)
    if not auth_code:
        raise HTTPException(status_code=400, detail="Invalid, expired, or already used authorization code")
    
    # Get the user
    user = crud.get_user(db, auth_code.user_id)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    
    # Create an integration token (access token)
    integration_token = crud.create_integration_token(
        db,
        user_id=user.id,
        class_id=user.class_id,
        scopes=auth_code.scope,
        expires_at=None  # No expiration for OAuth tokens (revocable via API)
    )
    
    return {
        "access_token": integration_token.token,
        "token_type": "bearer",
        "expires_at": integration_token.expires_at.isoformat() if integration_token.expires_at else None,
        "scope": integration_token.scopes,
        "class_id": integration_token.class_id
    }


@router.get("/userinfo")
def oauth_userinfo(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    OAuth 2.0 UserInfo Endpoint.
    
    Returns information about the authenticated user.
    Requires a valid Bearer token in the Authorization header.
    
    Request:
        - Authorization: Bearer <access_token>
    
    Response:
        - sub: User ID (subject)
        - name: User's display name
        - role: User's role in the class
        - class_id: The class ID the user belongs to
        - class_name: The name of the class
    """
    token_value = _extract_bearer_token(authorization)
    if not token_value:
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    
    token = crud.use_integration_token(db, token_value)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = crud.get_user(db, token.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    clazz = crud.get_class(db, user.class_id)
    
    return {
        "sub": user.id,
        "name": user.name,
        "role": user.role.value if hasattr(user.role, "value") else user.role,
        "class_id": user.class_id,
        "class_name": clazz.name if clazz else None,
        "email": user.email,  # May be null for unregistered users
        "is_registered": user.is_registered
    }
