from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud
from app.i18n import i18n


def get_current_user(request: Request, db: Session = Depends(get_db)):
    session_token = request.cookies.get("session_token")
    if not session_token:
        return None

    user = crud.get_user_by_session(db, session_token)

    if user and hasattr(user, "language") and user.language in i18n.translations:
        request.state.lang = user.language
        request.state.t = lambda key: i18n.get_translation(request.state.lang, key)

    return user


def require_user(user=Depends(get_current_user)):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    return user


def require_admin(user=Depends(require_user)):
    # Assuming UserRole enum import or check string
    if user.role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    return user


def require_class_admin(user=Depends(require_user)):
    if user.role not in ["admin", "owner", "class_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    return user
