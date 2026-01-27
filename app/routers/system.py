import os
from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from app.jobs.manager import job_manager
from app.jobs.migration import run_migration
from app.jobs.backup import run_backup, run_restore

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

ADMIN_SECRET = os.getenv("CLASSLY_ADMIN_SECRET")

def verify_system_admin(request: Request):
    if not ADMIN_SECRET:
        raise HTTPException(status_code=503, detail="System Admin Panel disabled (CLASSLY_ADMIN_SECRET not set)")

    token = request.cookies.get("admin_secret")
    if not token or token != ADMIN_SECRET:
         raise HTTPException(status_code=401, detail="Unauthorized")
    return True

@router.get("/system/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("system/login.html", {"request": request})

@router.post("/system/login")
def login(response: Response, secret: str = Form(...)):
    if secret == ADMIN_SECRET:
        response = RedirectResponse(url="/system/dashboard", status_code=303)
        response.set_cookie(key="admin_secret", value=secret, httponly=True, max_age=3600*24)
        return response
    else:
        return RedirectResponse(url="/system/login?error=Invalid Secret", status_code=303)

@router.get("/system/logout")
def logout(response: Response):
    response = RedirectResponse(url="/system/login", status_code=303)
    response.delete_cookie("admin_secret")
    return response

@router.get("/system/dashboard", dependencies=[Depends(verify_system_admin)])
def dashboard(request: Request):
    jobs = job_manager.list_jobs(limit=20)

    db_primary = os.getenv("CLASSLY_DB_PRIMARY", "sqlite")

    return templates.TemplateResponse("system/dashboard.html", {
        "request": request,
        "jobs": jobs,
        "config": {
            "db_primary": db_primary,
            "backup_target": os.getenv("CLASSLY_BACKUP_TARGET", "local")
        }
    })

@router.get("/system/jobs", dependencies=[Depends(verify_system_admin)])
def list_jobs_partial(request: Request):
    jobs = job_manager.list_jobs(limit=20)
    return templates.TemplateResponse("system/_job_row.html", {"request": request, "jobs": jobs})

@router.post("/system/migrate", dependencies=[Depends(verify_system_admin)])
def trigger_migration(
    source_type: str = Form(...),
    target_type: str = Form(...),
):
    def get_config(type_name):
        if type_name == "sqlite":
            return {"type": "sqlite", "path": "classly.db"}
        elif type_name == "supabase":
             return {"type": "supabase", "url": os.getenv("SUPABASE_URL")}
        elif type_name == "appwrite":
             return {
                 "type": "appwrite",
                 "endpoint": os.getenv("APPWRITE_ENDPOINT"),
                 "project_id": os.getenv("APPWRITE_PROJECT_ID"),
                 "api_key": os.getenv("APPWRITE_API_KEY")
             }
        return {}

    source_config = get_config(source_type)
    target_config = get_config(target_type)

    job_id = job_manager.submit_job("migration", run_migration, source_config=source_config, target_config=target_config)

    if job_id:
        return RedirectResponse("/system/dashboard", status_code=303)
    else:
        return Response("Failed to start job", status_code=500)

@router.post("/system/backup", dependencies=[Depends(verify_system_admin)])
def trigger_backup(
    target_type: str = Form(...)
):
    source_type = os.getenv("CLASSLY_DB_PRIMARY", "sqlite")

    def get_config(type_name):
        if type_name == "sqlite":
            return {"type": "sqlite", "path": "classly.db"}
        elif type_name == "supabase":
             return {"type": "supabase", "url": os.getenv("SUPABASE_URL")}
        elif type_name == "appwrite":
             return {
                 "type": "appwrite",
                 "endpoint": os.getenv("APPWRITE_ENDPOINT"),
                 "project_id": os.getenv("APPWRITE_PROJECT_ID"),
                 "api_key": os.getenv("APPWRITE_API_KEY")
             }
        elif type_name == "s3":
             return {
                 "type": "s3",
                 "endpoint": os.getenv("S3_ENDPOINT"),
                 "access_key": os.getenv("S3_ACCESS_KEY"),
                 "secret_key": os.getenv("S3_SECRET_KEY"),
                 "bucket": os.getenv("S3_BUCKET")
             }
        elif type_name == "local":
             return {"type": "local", "path": "./backups"}
        return {}

    source_config = get_config(source_type)
    target_config = get_config(target_type)

    job_id = job_manager.submit_job("backup", run_backup, source_config=source_config, target_config=target_config)
    return RedirectResponse("/system/dashboard", status_code=303)

@router.post("/system/restore", dependencies=[Depends(verify_system_admin)])
def trigger_restore(
    backup_path: str = Form(...),
    source_type: str = Form(...)
):
    target_type = os.getenv("CLASSLY_DB_PRIMARY", "sqlite")

    def get_config(type_name):
        if type_name == "sqlite":
            return {"type": "sqlite", "path": "classly.db"}
        elif type_name == "supabase":
             return {"type": "supabase", "url": os.getenv("SUPABASE_URL")}
        elif type_name == "s3":
             return {
                 "type": "s3",
                 "endpoint": os.getenv("S3_ENDPOINT"),
                 "access_key": os.getenv("S3_ACCESS_KEY"),
                 "secret_key": os.getenv("S3_SECRET_KEY"),
                 "bucket": os.getenv("S3_BUCKET")
             }
        return {}

    target_config = get_config(target_type)

    backup_source = {
        "type": source_type,
    }
    if source_type == "s3":
        backup_source.update(get_config("s3"))
        backup_source["key"] = backup_path
    else:
        backup_source["path"] = backup_path

    job_id = job_manager.submit_job("restore", run_restore, target_config=target_config, backup_source=backup_source)
    return RedirectResponse("/system/dashboard", status_code=303)
