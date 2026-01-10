from fastapi import APIRouter, Depends, Form, HTTPException, Response, Request
import os
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, models
from app.core import security

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Cookie settings - 30 days persistent login
COOKIE_MAX_AGE = 60 * 60 * 24 * 30  # 30 days in seconds

def set_session_cookie(response: Response, session_token: str):
    """Set session cookie with proper security settings"""
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=COOKIE_MAX_AGE,
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )

@router.post("/auth/create-class")
def create_class(
    response: Response,
    class_name: str = Form(...),
    user_name: str = Form(...),
    email: str = Form(None),
    password: str = Form(None),
    db: Session = Depends(get_db)
):
    # Check Max Classes Limit
    max_classes = os.getenv("MAX_CLASSES")
    if max_classes:
        try:
            limit = int(max_classes)
            if limit > 0:
                count = db.query(models.Class).count()
                if count >= limit:
                    raise HTTPException(status_code=403, detail=f"Maximum number of classes ({limit}) reached on this server.")
        except ValueError:
            pass # Ignore invalid config

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
    
    # Set Cookie with proper settings
    set_session_cookie(response, new_user.session_token)
    
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
    
    # Set cookie with proper settings
    set_session_cookie(response, user.session_token)
    
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
    from fastapi.responses import RedirectResponse
    
    # Check if already logged in
    session_token = request.cookies.get("session_token")
    if session_token:
        user = crud.get_user_by_session(db, session_token)
        if user:
            return RedirectResponse(url="/")

    # First check if it's a class join token
    clazz = crud.get_class_by_token(db, token)
    if clazz:
        if not clazz.join_enabled:
            raise HTTPException(status_code=403, detail="Joining is disabled")
        return templates.TemplateResponse("join.html", {"request": request, "clazz": clazz, "token_type": "class"})
    
    # Then check if it's a login token - DIRECT LOGIN
    login_token = crud.use_login_token(db, token)
    if login_token:
        # Get or create user
        if login_token.user_id:
            # Existing user - log them in directly
            user = crud.get_user(db, login_token.user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
        else:
            # New user - create with predefined name
            user = crud.create_user(db, name=login_token.user_name, class_id=login_token.class_id, role=login_token.role)
            # Bind token to this user so reuse doesn't create dupes
            login_token.user_id = user.id
            db.commit()
        
        # Create redirect response and set cookie with proper settings
        redirect = RedirectResponse(url="/", status_code=303)
        redirect.set_cookie(
            key="session_token",
            value=user.session_token,
            httponly=True,
            max_age=COOKIE_MAX_AGE,
            samesite="lax",
            secure=False
        )
        return redirect
    
    raise HTTPException(status_code=404, detail="Invalid or expired link")

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
    
    # Set cookie with proper settings
    set_session_cookie(response, new_user.session_token)
    response.headers["HX-Redirect"] = "/"
    return {"status": "success"}

@router.get("/auth/logout")
def logout():
    from fastapi.responses import RedirectResponse
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session_token")
    return response

@router.get("/auth/migrate-session")
def migrate_session(
    token: str,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Migrates a session from another domain.
    Validates the token exists in DB before setting the cookie.
    """
    from fastapi.responses import RedirectResponse
    
    # Validate token exists
    user = crud.get_user_by_session(db, token)
    if not user:
        # Invalid token, just redirect to home
        return RedirectResponse(url="/")
        
    # Set the cookie for this domain
    redirect = RedirectResponse(url="/", status_code=303)
    redirect.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        max_age=COOKIE_MAX_AGE,
        samesite="lax",
        secure=False # Should be true in prod
    )
    return redirect
