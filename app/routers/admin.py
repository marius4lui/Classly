from fastapi import APIRouter, Depends, Form, HTTPException, Response, BackgroundTasks, Request
from app.repository.base import BaseRepository
from app.repository.factory import get_repository
from app import models
from app.core.auth import require_admin, require_class_admin, require_user
from app.core import security
import datetime
import secrets
from fastapi.templating import Jinja2Templates
import os
from app.quotas import MAX_EVENTS_PER_CLASS, MAX_SUBJECTS_PER_USER, MAX_CLASSES_PER_USER, MAX_TOTAL_STORAGE_MB

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/admin/quotas")
def admin_quotas_overview(
    request: Request,
    user: models.User = Depends(require_admin),
    repo: BaseRepository = Depends(get_repository)
):
    # Calculate stats (Class Scoped)
    # Using repository count methods.
    
    total_classes = 1 # repo doesn't support global class count yet, assuming context of current class
    total_events = repo.count_events(user.class_id)
    total_subjects = repo.count_subjects(user.class_id)

    db_size_mb = 0
    # Basic size check for SQL/Appwrite generic
    if os.path.exists("classly.db"): # Check actual DB file if SQL default
        db_size_mb = os.path.getsize("classly.db") / (1024 * 1024)
    elif os.path.exists("app.db"): # Fallback
        db_size_mb = os.path.getsize("app.db") / (1024 * 1024)

    return templates.TemplateResponse("admin_quotas.html", {
        "request": request,
        "user": user,
        "stats": {
            "classes": total_classes,
            "events": total_events,
            "subjects": total_subjects,
            "db_size_mb": round(db_size_mb, 2)
        },
        "limits": {
            "max_events": MAX_EVENTS_PER_CLASS,
            "max_subjects": MAX_SUBJECTS_PER_USER,
            "max_classes": MAX_CLASSES_PER_USER,
            "max_storage_mb": MAX_TOTAL_STORAGE_MB
        }
    })

@router.delete("/admin/members/{user_id}")
def kick_member(
    user_id: str,
    response: Response,
    admin: models.User = Depends(require_admin),
    repo: BaseRepository = Depends(get_repository)
):
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot kick yourself")
    
    target = repo.get_user(user_id)
    if not target or target.class_id != admin.class_id:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Permission Check
    if target.role == models.UserRole.OWNER:
        raise HTTPException(status_code=403, detail="Cannot kick owner")
    
    repo.delete_user(user_id)
    response.headers["HX-Redirect"] = "/"
    return {"status": "kicked"}

@router.post("/admin/rotate-token")
def rotate_token(
    response: Response,
    admin: models.User = Depends(require_admin),
    repo: BaseRepository = Depends(get_repository)
):
    # Generate new unique token
    new_token = secrets.token_urlsafe(16)
    while repo.get_class_by_token(new_token):
        new_token = secrets.token_urlsafe(16)
        
    repo.update_class(admin.class_id, join_token=new_token)
    
    response.headers["HX-Redirect"] = "/"
    return {"status": "rotated"}

@router.post("/admin/promote/{user_id}")
def promote_user(
    user_id: str,
    response: Response,
    admin: models.User = Depends(require_admin),
    repo: BaseRepository = Depends(get_repository)
):
    """Promote a user to Admin role"""
    target = repo.get_user(user_id)
    if not target or target.class_id != admin.class_id:
        raise HTTPException(status_code=404, detail="User not found")
    
    if target.role == models.UserRole.OWNER:
        raise HTTPException(status_code=400, detail="Cannot change owner role")
    
    repo.update_user_role(user_id, models.UserRole.ADMIN)
    response.headers["HX-Redirect"] = "/"
    return {"status": "promoted"}

@router.post("/admin/demote/{user_id}")
def demote_user(
    user_id: str,
    response: Response,
    admin: models.User = Depends(require_admin),
    repo: BaseRepository = Depends(get_repository)
):
    """Demote an admin to Member role"""
    target = repo.get_user(user_id)
    if not target or target.class_id != admin.class_id:
        raise HTTPException(status_code=404, detail="User not found")
    
    if target.role == models.UserRole.OWNER:
        raise HTTPException(status_code=400, detail="Cannot change owner role")
    
    repo.update_user_role(user_id, models.UserRole.MEMBER)
    response.headers["HX-Redirect"] = "/"
    return {"status": "demoted"}

@router.patch("/admin/members/{user_id}/role")
def set_user_role(
    user_id: str,
    response: Response,
    role: str = Form(...),
    admin: models.User = Depends(require_admin),
    repo: BaseRepository = Depends(get_repository)
):
    """Set user role (Admin only)"""
    target = repo.get_user(user_id)
    if not target or target.class_id != admin.class_id:
        raise HTTPException(status_code=404, detail="User not found")
    
    if target.role == models.UserRole.OWNER:
        raise HTTPException(status_code=403, detail="Cannot change owner role")
        
    new_role = models.UserRole(role)
    if new_role == models.UserRole.OWNER:
         raise HTTPException(status_code=403, detail="Cannot assign owner role manually")

    repo.update_user_role(user_id, new_role)
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
    repo: BaseRepository = Depends(get_repository)
):
    # Must have either user_id OR user_name
    if not user_id and not user_name:
        raise HTTPException(status_code=400, detail="User ID or Name required")
    
    # If user_id, verify user exists
    if user_id:
        target = repo.get_user(user_id)
        if not target or target.class_id != admin.class_id:
            raise HTTPException(status_code=404, detail="User not found")
        user_name = None  # Clear user_name if user_id is set
    
    expires_at = None
    if expires_hours:
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=expires_hours)
    
    token = repo.create_login_token(
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
    repo: BaseRepository = Depends(get_repository)
):
    repo.delete_login_token(token_id)
    response.headers["HX-Redirect"] = "/"
    return {"status": "deleted"}

@router.get("/admin/download-db")
def download_db(
    background_tasks: BackgroundTasks,
    admin: models.User = Depends(require_admin),
    repo: BaseRepository = Depends(get_repository)
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
        
        # 3. Fetch Data for this Class ONLY via Repo
        cid = admin.class_id
        
        # Class
        clazz = repo.get_class(cid)
        if clazz:
            dst_db.merge(clazz)
            
        # Subjects
        subjects = repo.get_subjects_for_class(cid)
        for obj in subjects:
            dst_db.merge(obj)

        # Users & Preferences
        users = repo.get_class_members(cid)
        for obj in users:
            dst_db.merge(obj)
            # Merge UserPreferences if available? 
            # Current implementation of Repo might not load them fully or Appwrite might miss them.
            # We skip explicit preference merge for now unless attached.
            
        # Events & Related
        events = repo.list_events(cid, limit=10000) # Get all
        for obj in events:
            dst_db.merge(obj)
            # Topics/Links might be missing if lazy loaded and not fetched.
            
        # Login Tokens
        tokens = repo.list_login_tokens(cid)
        for obj in tokens:
            dst_db.merge(obj)
            
        # Audit Logs
        logs = repo.list_audit_logs(cid, limit=10000)
        for obj in logs:
            dst_db.merge(obj)

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


# --- API-Key Management ---

@router.get("/api-keys")
def list_api_keys(
    request: Request,
    user: models.User = Depends(require_class_admin),
    repo: BaseRepository = Depends(get_repository)
):
    """
    Seite für API-Keys der eigenen Klasse.
    Class-Admins und höher können Keys erstellen.
    """
    from app import crud
    keys = crud.list_api_keys_for_class(repo.db, user.class_id)
    
    # Sicherstellen, dass keine Secrets im Template laden (Security Fix)
    safe_keys = []
    for k in keys:
        # Display-Token berechnen (Prefix oder Legacy-Teil)
        if k.token_prefix:
            display = k.token_prefix
        elif k.token: # Legacy
            display = f"{k.token[:12]}..."
        else:
            display = "N/A"
            
        safe_keys.append({
            "id": k.id,
            "name": k.name,
            "scopes": k.scopes,
            "created_at": k.created_at,
            "last_used_at": k.last_used_at,
            "expires_at": k.expires_at,
            "revoked": k.revoked,
            "revoked_at": k.revoked_at,
            "token_display": display
        })
    
    return templates.TemplateResponse("api_keys.html", {
        "request": request,
        "user": user,
        "api_keys": safe_keys,
        "now": datetime.datetime.utcnow()
    })


@router.post("/api-keys")
def create_api_key(
    response: Response,
    request: Request,
    name: str = Form(...),
    scopes: list = Form([]),
    expires_days: str = Form(""),
    user: models.User = Depends(require_class_admin),
    repo: BaseRepository = Depends(get_repository)
):
    """
    Erstellt einen neuen API-Key für die eigene Klasse.
    Der Key kann nur für die Klasse verwendet werden, in der der Admin ist.
    """
    from app import crud
    
    # Name validieren
    name = name.strip()
    if not name or len(name) < 3:
        raise HTTPException(status_code=400, detail="Name muss mindestens 3 Zeichen haben")
    
    if len(name) > 50:
        raise HTTPException(status_code=400, detail="Name darf maximal 50 Zeichen haben")
    
    # Ablaufdatum berechnen
    expires_at = None
    if expires_days and expires_days.strip():
        try:
            days = int(expires_days)
            if days > 0:
                expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=days)
        except ValueError:
            pass  # Ignoriere ungültige Werte
    
    # Scopes als String zusammenfügen
    if isinstance(scopes, list):
        scopes_str = ",".join(scopes)
    else:
        scopes_str = scopes if scopes else "events:read"
    
    # Key erstellen (nur für eigene Klasse!)
    key, raw_token = crud.create_api_key(
        repo.db,
        name=name,
        user_id=user.id,
        class_id=user.class_id,
        created_by=user.id,
        scopes=scopes_str,
        expires_at=expires_at
    )
    
    # Audit-Log
    repo.create_audit_log(
        class_id=user.class_id,
        user_id=user.id,
        action=models.AuditAction.API_KEY_CREATE,
        target_id=key.id,
        data=f'{{"name": "{name}", "scopes": "{scopes_str}"}}'
    )
    
    # Return Token für einmalige Anzeige (JSON für JS-Modal)
    return {"token": raw_token, "key_id": key.id, "name": name}


@router.delete("/api-keys/{key_id}")
def revoke_api_key(
    key_id: str,
    response: Response,
    user: models.User = Depends(require_class_admin),
    repo: BaseRepository = Depends(get_repository)
):
    """
    Widerruft einen API-Key der eigenen Klasse.
    """
    from app import crud
    
    # Prüfen ob Key zur Klasse gehört
    key = repo.db.query(models.IntegrationToken).filter_by(id=key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API-Key nicht gefunden")
    
    if key.class_id != user.class_id:
        raise HTTPException(status_code=403, detail="Kein Zugriff auf diesen Key")
    
    success = crud.revoke_api_key(repo.db, key_id, user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Key nicht gefunden")
    
    # Audit-Log
    repo.create_audit_log(
        class_id=user.class_id,
        user_id=user.id,
        action=models.AuditAction.API_KEY_REVOKE,
        target_id=key_id
    )
    
    response.headers["HX-Redirect"] = "/api-keys"
    return {"revoked": True}


@router.post("/api-keys/{key_id}/rotate")
def rotate_api_key(
    key_id: str,
    user: models.User = Depends(require_class_admin),
    repo: BaseRepository = Depends(get_repository)
):
    """
    Rotiert einen API-Key der eigenen Klasse.
    Der alte Key bleibt noch 24h aktiv.
    """
    from app import crud
    
    # Prüfen ob Key zur Klasse gehört
    key = repo.db.query(models.IntegrationToken).filter_by(id=key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API-Key nicht gefunden")
    
    if key.class_id != user.class_id:
        raise HTTPException(status_code=403, detail="Kein Zugriff auf diesen Key")
    
    result = crud.rotate_api_key(repo.db, key_id)
    if not result:
        raise HTTPException(status_code=404, detail="Key nicht gefunden oder bereits widerrufen")
    
    new_key, raw_token = result
    
    # Audit-Log
    repo.create_audit_log(
        class_id=user.class_id,
        user_id=user.id,
        action=models.AuditAction.API_KEY_ROTATE,
        target_id=key_id,
        data=f'{{"new_key_id": "{new_key.id}"}}'
    )
    
    return {"token": raw_token, "key_id": new_key.id, "old_key_expires": "24 Stunden"}


@router.get("/api-keys/json")
def list_api_keys_json(
    user: models.User = Depends(require_class_admin),
    repo: BaseRepository = Depends(get_repository)
):
    """
    API-Keys als JSON für HTMX/JS.
    """
    from app import crud
    keys = crud.list_api_keys_for_class(repo.db, user.class_id)
    
    return {
        "class_id": user.class_id,
        "count": len(keys),
        "keys": [
            {
                "id": k.id,
                "name": k.name or "Unbenannt",
                "token_prefix": k.token_prefix or (k.token[:12] + "..." if k.token else "N/A"),
                "scopes": k.scopes,
                "created_at": k.created_at.isoformat() if k.created_at else None,
                "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None,
                "expires_at": k.expires_at.isoformat() if k.expires_at else None,
                "revoked": k.revoked,
                "revoked_at": k.revoked_at.isoformat() if k.revoked_at else None
            }
            for k in keys
        ]
    }
