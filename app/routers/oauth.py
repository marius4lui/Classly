"""
OAuth 2.0 Authorization Code Flow endpoints for Classly.

Endpoints:
- POST /api/oauth/authorize - Create authorization code (requires session cookie)
- POST /api/oauth/token - Exchange authorization code for access token
- GET /api/oauth/userinfo - Get current user info (requires Bearer token)
"""
import datetime
from fastapi import APIRouter, Depends, Form, Header, HTTPException, Request, Query
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


@router.get("/authorize")
def oauth_authorize(
    request: Request,
    client_id: str = Query(...),
    redirect_uri: str = Query(...),
    scope: str = Query("read:events"),
    response_type: str = Query("code"),
    db: Session = Depends(get_db)
):
    """
    OAuth 2.0 Authorization Endpoint.
    
    Creates an authorization code for the authenticated user.
    Requires a valid session cookie. 
    If not logged in, redirects to login page.
    """
    from fastapi.responses import RedirectResponse
    import urllib.parse
    
    # Check if user is logged in via session cookie
    session_token = request.cookies.get("session_token")
    current_user = None
    if session_token:
        current_user = crud.get_user_by_session(db, session_token)
    
    # If not logged in, redirect to login page with return_url
    if not current_user:
        # Build current URL to return to after login
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "response_type": response_type
        }
        query_string = urllib.parse.urlencode(params)
        return_url = f"/api/oauth/authorize?{query_string}"
        
        # Redirect to login
        # We assume /login can handle ?next=... parameter or we just hope the user logs in and tries again
        # For now, let's redirect to /login and use a cookie or param to remember where to go
        # A simple way is to pass ?next=.... URI encoded
        next_url = urllib.parse.quote(return_url)
        return RedirectResponse(url=f"/login?next={next_url}")
    
    if response_type != "code":
        raise HTTPException(status_code=400, detail="Only response_type=code is supported")
    
    # Create authorization code
    auth_code = crud.create_authorization_code(
        db,
        client_id=client_id,
        user_id=current_user.id,
        redirect_uri=redirect_uri,
        scope=scope,
        expires_in_seconds=600  # 10 minutes
    )
    
    # Redirect back to the client app with the code
    # e.g. habiter://auth/callback?code=...
    separator = "&" if "?" in redirect_uri else "?"
    callback_url = f"{redirect_uri}{separator}code={auth_code.code}"
    
    return RedirectResponse(url=callback_url)


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
