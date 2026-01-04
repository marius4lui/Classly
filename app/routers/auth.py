from fastapi import APIRouter, Depends, Form, HTTPException, Response, status, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, models
from app.core import security

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/auth/create-class")
def create_class(
    response: Response,
    class_name: str = Form(...),
    user_name: str = Form(...),
    db: Session = Depends(get_db)
):
    # Generate unique token
    token = security.generate_join_token()
    while crud.get_class_by_token(db, token):
        token = security.generate_join_token()
    
    # Create Class
    new_class = crud.create_class(db, name=class_name, join_token=token)
    
    # Create Owner (User)
    new_user = crud.create_user(db, name=user_name, class_id=new_class.id, role=models.UserRole.OWNER)
    
    # Update Class owner
    new_class.owner_id = new_user.id
    db.commit()
    
    # Set Cookie
    response.set_cookie(key="session_token", value=new_user.session_token, httponly=True)
    
    # HTMX Redirect (or standard)
    response.headers["HX-Redirect"] = "/"
    return {"status": "success"}

@router.get("/join/{token}")
def show_join_page(
    token: str,
    request: Request,
    db: Session = Depends(get_db)
):
    clazz = crud.get_class_by_token(db, token)
    if not clazz:
        raise HTTPException(status_code=404, detail="Class not found")
    if not clazz.join_enabled:
         raise HTTPException(status_code=403, detail="Joining is disabled")
         
    return templates.TemplateResponse("join.html", {"request": request, "clazz": clazz})

@router.post("/auth/join")
def join_class(
    response: Response,
    join_token: str = Form(...),
    user_name: str = Form(...),
    db: Session = Depends(get_db)
):
    clazz = crud.get_class_by_token(db, join_token)
    if not clazz:
        raise HTTPException(status_code=404, detail="Class not found or invalid token")
        
    if not clazz.join_enabled:
         raise HTTPException(status_code=403, detail="Joining is disabled for this class")

    # Create Member
    new_user = crud.create_user(db, name=user_name, class_id=clazz.id, role=models.UserRole.MEMBER)
    
    # Set Cookie
    response.set_cookie(key="session_token", value=new_user.session_token, httponly=True)
    
    response.headers["HX-Redirect"] = "/"
    return {"status": "success"}

@router.get("/auth/logout")
def logout(response: Response):
    response.delete_cookie("session_token")
    response.headers["HX-Redirect"] = "/"
    return {"status": "logged out"}
