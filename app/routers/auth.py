from fastapi import APIRouter, Depends, Form, HTTPException, Response, Request
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
    email: str = Form(None),
    password: str = Form(None),
    db: Session = Depends(get_db)
):
    # Generate unique token
    token = security.generate_join_token()
    while crud.get_class_by_token(db, token):
        token = security.generate_join_token()
    
    # Create Class
    new_class = crud.create_class(db, name=class_name, join_token=token)
    
    # Create Owner (with optional email/password)
    new_user = crud.create_user(
        db, 
        name=user_name, 
        class_id=new_class.id, 
        role=models.UserRole.OWNER,
        email=email,
        password=password
    )
    
    # Update Class owner
    new_class.owner_id = new_user.id
    db.commit()
    
    # Set Cookie
    response.set_cookie(key="session_token", value=new_user.session_token, httponly=True)
    
    response.headers["HX-Redirect"] = "/"
    return {"status": "success"}

@router.post("/auth/register")
def register_admin(
    response: Response,
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Register current user with email/password"""
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = crud.get_user_by_session(db, session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check if email already taken
    existing = crud.get_user_by_email(db, email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    crud.register_user(db, user.id, email, password)
    
    response.headers["HX-Redirect"] = "/"
    return {"status": "registered"}

@router.post("/auth/login")
def login(
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Login with email/password"""
    user = crud.get_user_by_email(db, email)
    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not crud.verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Set cookie
    response.set_cookie(key="session_token", value=user.session_token, httponly=True)
    
    response.headers["HX-Redirect"] = "/"
    return {"status": "logged in"}

@router.get("/login")
def show_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/join/{token}")
def show_join_page(
    token: str,
    request: Request,
    db: Session = Depends(get_db)
):
    # First check if it's a class join token
    clazz = crud.get_class_by_token(db, token)
    if clazz:
        if not clazz.join_enabled:
            raise HTTPException(status_code=403, detail="Joining is disabled")
        return templates.TemplateResponse("join.html", {"request": request, "clazz": clazz, "token_type": "class"})
    
    # Then check if it's a login token
    login_token = crud.get_login_token(db, token)
    if login_token:
        # Validate token
        if login_token.expires_at and login_token.expires_at < __import__('datetime').datetime.utcnow():
            raise HTTPException(status_code=403, detail="Link expired")
        if login_token.max_uses is not None and login_token.uses >= login_token.max_uses:
            raise HTTPException(status_code=403, detail="Link already used")
        
        clazz = crud.get_class(db, login_token.class_id)
        return templates.TemplateResponse("join.html", {"request": request, "clazz": clazz, "token_type": "login", "login_token": token})
    
    raise HTTPException(status_code=404, detail="Invalid link")

@router.post("/auth/join")
def join_class(
    response: Response,
    join_token: str = Form(None),
    login_token: str = Form(None),
    user_name: str = Form(...),
    db: Session = Depends(get_db)
):
    if join_token:
        # Class join token
        clazz = crud.get_class_by_token(db, join_token)
        if not clazz:
            raise HTTPException(status_code=404, detail="Class not found")
        if not clazz.join_enabled:
            raise HTTPException(status_code=403, detail="Joining disabled")
        
        new_user = crud.create_user(db, name=user_name, class_id=clazz.id, role=models.UserRole.MEMBER)
        
    elif login_token:
        # Login token
        token_obj = crud.use_login_token(db, login_token)
        if not token_obj:
            raise HTTPException(status_code=403, detail="Invalid or expired link")
        
        new_user = crud.create_user(db, name=user_name, class_id=token_obj.class_id, role=models.UserRole.MEMBER)
    else:
        raise HTTPException(status_code=400, detail="No token provided")
    
    response.set_cookie(key="session_token", value=new_user.session_token, httponly=True)
    response.headers["HX-Redirect"] = "/"
    return {"status": "success"}

@router.get("/auth/logout")
def logout(response: Response):
    response.delete_cookie("session_token")
    response.headers["HX-Redirect"] = "/"
    return {"status": "logged out"}
