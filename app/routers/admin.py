from fastapi import APIRouter, Depends, Form, HTTPException, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, models
from app.core.auth import require_admin, require_user
from app.core import security
import datetime

router = APIRouter()

@router.delete("/admin/members/{user_id}")
def kick_member(
    user_id: str,
    response: Response,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot kick yourself")
    
    target = crud.get_user(db, user_id)
    if not target or target.class_id != admin.class_id:
        raise HTTPException(status_code=404, detail="User not found")
    
    crud.delete_user(db, user_id)
    response.headers["HX-Redirect"] = "/"
    return {"status": "kicked"}

@router.post("/admin/rotate-token")
def rotate_token(
    response: Response,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    clazz = crud.get_class(db, admin.class_id)
    
    new_token = security.generate_join_token()
    while crud.get_class_by_token(db, new_token):
        new_token = security.generate_join_token()
        
    clazz.join_token = new_token
    db.commit()
    
    response.headers["HX-Redirect"] = "/"
    return {"status": "rotated"}

@router.post("/admin/promote/{user_id}")
def promote_user(
    user_id: str,
    response: Response,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Promote a user to Admin role"""
    target = crud.get_user(db, user_id)
    if not target or target.class_id != admin.class_id:
        raise HTTPException(status_code=404, detail="User not found")
    
    if target.role == models.UserRole.OWNER:
        raise HTTPException(status_code=400, detail="Cannot change owner role")
    
    crud.update_user_role(db, user_id, models.UserRole.ADMIN)
    response.headers["HX-Redirect"] = "/"
    return {"status": "promoted"}

@router.post("/admin/demote/{user_id}")
def demote_user(
    user_id: str,
    response: Response,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Demote an admin to Member role"""
    target = crud.get_user(db, user_id)
    if not target or target.class_id != admin.class_id:
        raise HTTPException(status_code=404, detail="User not found")
    
    if target.role == models.UserRole.OWNER:
        raise HTTPException(status_code=400, detail="Cannot change owner role")
    
    crud.update_user_role(db, user_id, models.UserRole.MEMBER)
    response.headers["HX-Redirect"] = "/"
    return {"status": "demoted"}

# --- Login Token Management ---
@router.post("/admin/login-tokens")
def create_login_token(
    response: Response,
    user_id: str = Form(None),  # Existing user
    user_name: str = Form(None),  # New user name
    max_uses: int = Form(None),
    expires_hours: int = Form(None),
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    # Must have either user_id OR user_name
    if not user_id and not user_name:
        raise HTTPException(status_code=400, detail="User ID or Name required")
    
    # If user_id, verify user exists
    if user_id:
        target = crud.get_user(db, user_id)
        if not target or target.class_id != admin.class_id:
            raise HTTPException(status_code=404, detail="User not found")
        user_name = None  # Clear user_name if user_id is set
    
    expires_at = None
    if expires_hours:
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=expires_hours)
    
    token = crud.create_login_token(
        db,
        class_id=admin.class_id,
        created_by=admin.id,
        user_id=user_id,
        user_name=user_name.strip() if user_name else None,
        max_uses=max_uses if max_uses and max_uses > 0 else None,
        expires_at=expires_at
    )
    
    response.headers["HX-Redirect"] = "/"
    return {"status": "created", "token": token.token}

@router.delete("/admin/login-tokens/{token_id}")
def delete_login_token(
    token_id: str,
    response: Response,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    crud.delete_login_token(db, token_id)
    response.headers["HX-Redirect"] = "/"
    return {"status": "deleted"}
