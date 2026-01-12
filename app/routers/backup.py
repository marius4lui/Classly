from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.core.auth import require_admin, require_user
from app.core.backup import BackupManager
from app.models import User
import os

router = APIRouter(
    prefix="/backups",
    tags=["backups"]
)

@router.get("")
def list_backups(
    admin: User = Depends(require_admin)
):
    """List all available backups (Local & S3)"""
    # Security: Ensure only instance owner/admin accesses this.
    # require_admin checks for class role 'admin' or 'owner'.
    # We should probably add an extra check or warning in UI.
    return BackupManager.list_backups()

@router.post("")
def trigger_backup(
    background_tasks: BackgroundTasks,
    admin: User = Depends(require_admin)
):
    """Trigger a manual backup"""
    background_tasks.add_task(BackupManager.create_backup)
    return {"status": "Backup started in background"}

@router.post("/{filename}/restore")
def restore_backup(
    filename: str,
    source: str = "local",
    admin: User = Depends(require_admin)
):
    """Restore a backup (DANGEROUS: Overwrites DB)"""
    try:
        BackupManager.restore_backup(filename, source)
        return {"status": "Restore successful. Please restart the application if needed."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
