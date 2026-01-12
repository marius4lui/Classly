from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud

def get_current_user(request: Request, db: Session = Depends(get_db)):
    session_token = request.cookies.get("session_token")
    if not session_token:
        return None
    
    user = crud.get_user_by_session(db, session_token)

    # If user is found, update language preference in request state
    if user and hasattr(user, 'language') and user.language:
        # User preference overrides everything else except maybe explicit query param
        # But for simplicity, let's say user setting in DB wins if logged in
        # (unless user explicitly requested ?lang=xx, but that usually sets cookie/db too)

        # Check if query param was provided (we can't easily know if it was checked in middleware
        # without re-parsing, but middleware set request.state.lang)

        # Logic: If user has a saved language, we should use it,
        # unless the user is trying to switch language via query param RIGHT NOW.
        # But switching language usually goes to a specific endpoint.
        # So we can safely update request.state.lang to user.language
        from app.i18n import i18n
        if user.language in i18n.translations:
             request.state.lang = user.language
             # Re-bind t with new lang
             request.state.t = lambda key: i18n.get_translation(request.state.lang, key)

    return user

def require_user(user = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user

def require_admin(user = Depends(require_user)):
    # Assuming UserRole enum import or check string
    if user.role not in ["admin", "owner"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return user

def require_class_admin(user = Depends(require_user)):
    if user.role not in ["admin", "owner", "class_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return user
