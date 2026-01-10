from fastapi import APIRouter, Depends, Form, HTTPException, Response, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, models
from app.core.auth import require_admin, require_class_admin, require_user
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
    
    # Permission Check
    if target.role == models.UserRole.OWNER:
        raise HTTPException(status_code=403, detail="Cannot kick owner")
    
    
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

@router.patch("/admin/members/{user_id}/role")
def set_user_role(
    user_id: str,
    response: Response,
    role: str = Form(...),
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Set user role (Admin only)"""
    target = crud.get_user(db, user_id)
    if not target or target.class_id != admin.class_id:
        raise HTTPException(status_code=404, detail="User not found")
    
    if target.role == models.UserRole.OWNER:
        raise HTTPException(status_code=403, detail="Cannot change owner role")
        
    new_role = models.UserRole(role)
    if new_role == models.UserRole.OWNER:
         raise HTTPException(status_code=403, detail="Cannot assign owner role manually")

    crud.update_user_role(db, user_id, new_role)
    response.headers["HX-Redirect"] = "/"
    return {"status": "role_updated"}

# --- Login Token Management ---
@router.post("/admin/login-tokens")
def create_login_token(
    response: Response,
    user_id: str = Form(None),  # Existing user
    user_name: str = Form(None),  # New user name
    max_uses: int = Form(None),
    expires_hours: int = Form(None),
    role: str = Form("member"),
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
        expires_at=expires_at,
        role=models.UserRole(role)
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

@router.get("/admin/download-db")
def download_db(
    background_tasks: BackgroundTasks,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    from fastapi.responses import FileResponse
    from fastapi import BackgroundTasks
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, make_transient
    import tempfile
    import os
    import shutil
    
    # 1. Create a secure temporary file
    fd, temp_path = tempfile.mkstemp(suffix=".db", prefix=f"classly_{admin.class_id}_")
    os.close(fd) # Close the file descriptor, we will access by path
    
    try:
        # 2. Setup destination database (Temp SQLite)
        dst_engine = create_engine(f"sqlite:///{temp_path}")
        models.Base.metadata.create_all(bind=dst_engine)
        DstSession = sessionmaker(bind=dst_engine)
        dst_db = DstSession()
        
        # 3. Fetch Data for this Class ONLY
        cid = admin.class_id
        
        # Entities to export
        # IMPORTANT: We use Detached objects to copy them
        
        # Class
        clazz = db.query(models.Class).filter(models.Class.id == cid).first()
        if clazz:
            db.expunge(clazz) # Detach from source session
            make_transient(clazz) # Remove session state
            dst_db.add(clazz)
            
        # Subjects
        subjects = db.query(models.Subject).filter(models.Subject.class_id == cid).all()
        for obj in subjects:
            db.expunge(obj)
            make_transient(obj)
            dst_db.add(obj)

        # Users & Preferences
        users = db.query(models.User).filter(models.User.class_id == cid).all()
        user_ids = [u.id for u in users]
        for obj in users:
            db.expunge(obj)
            make_transient(obj)
            dst_db.add(obj)
            
        prefs = db.query(models.UserPreferences).filter(models.UserPreferences.user_id.in_(user_ids)).all()
        for obj in prefs:
            db.expunge(obj)
            make_transient(obj)
            dst_db.add(obj)

        # Events & Related
        events = db.query(models.Event).filter(models.Event.class_id == cid).all()
        event_ids = [e.id for e in events]
        for obj in events:
            # Manually load relations if lazy=True to ensure they export, 
            # OR just query them separately if they are separate tables.
            # Eager loading is safer but let's just query tables.
            db.expunge(obj)
            make_transient(obj)
            dst_db.add(obj)
            
        topics = db.query(models.EventTopic).filter(models.EventTopic.event_id.in_(event_ids)).all()
        for obj in topics:
            db.expunge(obj)
            make_transient(obj)
            dst_db.add(obj)

        links = db.query(models.EventLink).filter(models.EventLink.event_id.in_(event_ids)).all()
        for obj in links:
            db.expunge(obj)
            make_transient(obj)
            dst_db.add(obj)
            
        # Login Tokens
        tokens = db.query(models.LoginToken).filter(models.LoginToken.class_id == cid).all()
        for obj in tokens:
            db.expunge(obj)
            make_transient(obj)
            dst_db.add(obj)
            
        # Audit Logs
        logs = db.query(models.AuditLog).filter(models.AuditLog.class_id == cid).all()
        for obj in logs:
            db.expunge(obj)
            make_transient(obj)
            dst_db.add(obj)

        # 4. Commit and Close Logic
        dst_db.commit()
        dst_db.close()
        
        # 5. Serve File w/ Cleanup
        def remove_file():
            try:
                os.unlink(temp_path)
            except Exception:
                pass
                
        background_tasks.add_task(remove_file)
        
        return FileResponse(
            temp_path, 
            media_type='application/octet-stream', 
            filename=f"classly_backup_{datetime.date.today()}.db"
        )

    except Exception as e:
        # Cleanup on error
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")
