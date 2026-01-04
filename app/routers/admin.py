from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, models
from app.core.auth import require_admin, require_user
from app.core import security

router = APIRouter()

@router.delete("/admin/members/{user_id}")
def kick_member(
    user_id: str,
    response: Response,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    # Prevent self-kick
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot kick yourself")
        
    # Check if target user is in same class
    target = crud.get_user(db, user_id)
    if not target or target.class_id != admin.class_id:
        raise HTTPException(status_code=404, detail="User not found in this class")
    
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
    return {"status": "rotated", "token": new_token}
