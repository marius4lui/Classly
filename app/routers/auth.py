from fastapi import APIRouter, Depends, Form, HTTPException, Response, Request
import os
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, models
from app.core import security
from app.core.oauth import oauth
from app.core.auth_config import get_auth_settings
from app.core import auth_utils
import pyotp
import qrcode
import io
import base64

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
settings = get_auth_settings()

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

# --- OAuth Routes ---

@router.get("/login/{provider}")
async def oauth_login(provider: str, request: Request):
    client = oauth.create_client(provider)
    if not client:
        raise HTTPException(status_code=404, detail=f"Provider {provider} not configured")

    redirect_uri = request.url_for('oauth_callback', provider=provider)
    return await client.authorize_redirect(request, redirect_uri)

@router.get("/auth/{provider}/callback")
async def oauth_callback(provider: str, request: Request, db: Session = Depends(get_db)):
    from fastapi.responses import RedirectResponse

    client = oauth.create_client(provider)
    if not client:
        raise HTTPException(status_code=404, detail=f"Provider {provider} not configured")

    try:
        token = await client.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth Error: {str(e)}")

    user_info = token.get('userinfo')
    if not user_info:
        user_info = await client.userinfo(token=token)

    email = user_info.get('email')
    name = user_info.get('name', email)
    provider_id = user_info.get('sub') or user_info.get('id')

    if not email:
         raise HTTPException(status_code=400, detail="Email not provided by provider")

    # Check if user exists
    user = crud.get_user_by_email(db, email)

    response = RedirectResponse(url="/")

    if user:
        # Link provider if not linked
        if user.auth_provider == 'local':
            user.auth_provider = provider
            user.auth_provider_id = str(provider_id)
            db.commit()

        # Check 2FA
        if user.totp_enabled:
            response = RedirectResponse(url="/auth/2fa-check")
            # Use signed cookie for partial auth
            response.set_cookie(
                key="partial_auth_user_id",
                value=security.sign_data({"user_id": user.id}),
                httponly=True,
                max_age=300
            )
            return response

        # Login
        set_session_cookie(response, user.session_token)
        return response
    else:
        # New user - redirect to Join Class page with pre-filled info
        pending_info = {
            "provider": provider,
            "provider_id": str(provider_id),
            "email": email,
            "name": name
        }
        response = RedirectResponse(url="/join?mode=oauth")
        # Use signed cookie
        response.set_cookie(
            key="oauth_pending",
            value=security.sign_data(pending_info),
            httponly=True,
            max_age=3600
        )
        return response

# --- LDAP & SAML Placeholders ---
# (Basic implementation for LDAP inside login)

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
    """Login with email/password (or LDAP username/password)"""
    user = crud.get_user_by_email(db, email)
    
    # If not found in DB, try LDAP if enabled
    if not user and settings.ldap.enabled:
        ldap_user = auth_utils.verify_ldap_credentials(email, password) # email here is username
        if ldap_user:
            # Check if user exists by LDAP DN or email
            # We already checked email, so user not found by email.
            # But maybe we need to create it?
            # Or maybe the email in LDAP is different?
            # For simplicity, if LDAP auth works but user not in DB, we treat as "New User" logic?
            # Or we require invitation?
            # The prompt says "LDAP for school networks". Usually means auto-provisioning or matching.
            # I'll Assume: If LDAP valid, but no local user -> Error "User not registered in Classly"
            # OR we match by email returned from LDAP?
            if ldap_user['email']:
                user = crud.get_user_by_email(db, ldap_user['email'])

            if not user:
                 raise HTTPException(status_code=401, detail="LDAP Login successful, but user not found in Classly. Please join a class first.")
        else:
             # LDAP failed
             pass

    # Verify local password if user found and not using LDAP (or if LDAP failed)
    # Note: If user found, we check local password.
    # If LDAP is enabled and user has auth_provider='ldap', we should verify LDAP instead?
    # Logic:
    # 1. Find user by email.
    # 2. If user.auth_provider == 'ldap', verify LDAP.
    # 3. If user.auth_provider == 'local', verify DB hash.
    
    if user:
        valid_password = False
        if user.auth_provider == 'ldap':
             # We need the username for LDAP, but we have email.
             # We'll assume email or username was passed in 'email' field.
             # We might need to store the ldap username in auth_provider_id or similar?
             # Or just try binding with the email if the server supports it.
             if auth_utils.verify_ldap_credentials(email, password):
                 valid_password = True
        elif user.auth_provider == 'local':
             if user.password_hash and crud.verify_password(password, user.password_hash):
                 valid_password = True

        # If not valid yet, maybe it's a fallback or migration?
        if not valid_password:
             raise HTTPException(status_code=401, detail="Invalid credentials")

        # Check 2FA
        if user.totp_enabled:
            # Redirect to 2FA page with temp token
            from fastapi.responses import RedirectResponse
            # Can't return RedirectResponse from HX-Post easily, HTMX expects 200 with HX-Redirect header.
            # But for 2FA we might want to return a partial success or JSON to show 2FA modal.
            # Given the simple HTMX flow:
            response.headers["HX-Redirect"] = "/auth/2fa-check" # Frontend should handle this page
            response.set_cookie(key="partial_auth_user_id", value=user.id, httponly=True, max_age=300)
            return {"status": "2fa_required"}

        # Success
        set_session_cookie(response, user.session_token)
        response.headers["HX-Redirect"] = "/"
        return {"status": "logged in"}

    else:
        # User not found locally.
        # Check LDAP purely?
        if settings.ldap.enabled:
             ldap_info = auth_utils.verify_ldap_credentials(email, password)
             if ldap_info:
                 # LDAP valid, but no user.
                 # We could redirect to join page?
                 # Similar to OAuth.
                 import json
                 pending_info = {
                    "provider": "ldap",
                    "provider_id": ldap_info['dn'],
                    "email": ldap_info['email'],
                    "name": ldap_info['name']
                 }
                 response.headers["HX-Redirect"] = "/join?mode=ldap"
                 response.set_cookie(key="oauth_pending", value=json.dumps(pending_info), httponly=True, max_age=3600)
                 return {"status": "ldap_success_needs_join"}

    raise HTTPException(status_code=401, detail="Invalid credentials")

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
            return RedirectResponse(url="/?welcome_back=1")

    # Check for pending OAuth
    pending_auth = None
    cookie_val = request.cookies.get("oauth_pending")
    if cookie_val:
        pending_auth = security.unsign_data(cookie_val)

    # First check if it's a class join token
    clazz = crud.get_class_by_token(db, token)
    if clazz:
        if not clazz.join_enabled:
            raise HTTPException(status_code=403, detail="Joining is disabled")
        return templates.TemplateResponse("join.html", {
            "request": request,
            "clazz": clazz,
            "token_type": "class",
            "pending_auth": pending_auth
        })
    
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
    request: Request,
    join_token: str = Form(None),
    login_token: str = Form(None),
    user_name: str = Form(...),
    email: str = Form(None),
    password: str = Form(None),
    # auth_provider inputs are insecure, we should look at cookie for trust
    auth_provider_form: str = Form("local", alias="auth_provider"),
    db: Session = Depends(get_db)
):
    # Verify secure cookie for non-local auth
    oauth_data = None
    if auth_provider_form != "local":
        cookie_val = request.cookies.get("oauth_pending")
        if cookie_val:
            oauth_data = security.unsign_data(cookie_val)

        if not oauth_data or oauth_data.get("provider") != auth_provider_form:
             # Fallback to local if manipulation detected or cookie expired
             # Or raise error. Let's raise error to be safe.
             # Unless user intended to switch back to password.
             raise HTTPException(status_code=400, detail="Invalid authentication state")

        # Use trusted data
        auth_provider = oauth_data["provider"]
        auth_provider_id = oauth_data["provider_id"]
        # Also ensure email matches?
        # email from form is what user sees.
    else:
        auth_provider = "local"
        auth_provider_id = None

    if join_token:
        # Class join token
        clazz = crud.get_class_by_token(db, join_token)
        if not clazz:
            raise HTTPException(status_code=404, detail="Class not found")
        if not clazz.join_enabled:
            raise HTTPException(status_code=403, detail="Joining disabled")
        
        # Check if name is already taken in this class -> Login as that user
        # Only if local auth
        existing_users = crud.get_class_members(db, clazz.id)
        target_user = None
        for user in existing_users:
            if user.name.lower() == user_name.lower():
                target_user = user
                break
        
        if target_user and auth_provider == 'local':
            new_user = target_user
        else:
            # Create new user
            new_user = crud.create_user(
                db,
                name=user_name,
                class_id=clazz.id,
                role=models.UserRole.MEMBER,
                email=email,
                password=password
            )
            # Update auth provider info
            if auth_provider != 'local':
                new_user.auth_provider = auth_provider
                new_user.auth_provider_id = auth_provider_id
                db.commit()
                # Clear pending cookie
                response.delete_cookie("oauth_pending")
        
    elif login_token:
        # Login token
        token_obj = crud.use_login_token(db, login_token)
        if not token_obj:
            raise HTTPException(status_code=403, detail="Invalid or expired link")
        
        new_user = crud.create_user(db, name=user_name, class_id=token_obj.class_id, role=models.UserRole.MEMBER, email=email, password=password)
        if auth_provider != 'local':
            new_user.auth_provider = auth_provider
            new_user.auth_provider_id = auth_provider_id
            db.commit()
            response.delete_cookie("oauth_pending")
    else:
        raise HTTPException(status_code=400, detail="No token provided")
    
    # Set cookie with proper settings
    set_session_cookie(response, new_user.session_token)
    response.headers["HX-Redirect"] = "/"
    return {"status": "success"}

# --- SAML Routes ---

@router.get("/login/saml")
def saml_login(request: Request):
    client = auth_utils.get_saml_client(get_saml_request_data(request))
    if not client:
        raise HTTPException(status_code=404, detail="SAML not configured")

    auth_url = client.login()
    from fastapi.responses import RedirectResponse
    return RedirectResponse(auth_url)

@router.post("/auth/saml/callback")
async def saml_callback(request: Request, db: Session = Depends(get_db)):
    req_data = await get_saml_request_data_async(request)
    client = auth_utils.get_saml_client(req_data)
    if not client:
        raise HTTPException(status_code=404, detail="SAML not configured")

    client.process_response()
    errors = client.get_errors()

    if errors:
        raise HTTPException(status_code=400, detail=f"SAML Error: {errors}")

    if not client.is_authenticated():
        raise HTTPException(status_code=401, detail="SAML Authentication failed")

    attributes = client.get_attributes()
    # Assume email is in attributes, or name_id
    email = client.get_nameid()
    # Map attributes
    # ... (need to know attribute names from IdP)

    if not email:
        raise HTTPException(status_code=400, detail="No email found in SAML response")

    # Same logic as OAuth
    user = crud.get_user_by_email(db, email)

    from fastapi.responses import RedirectResponse
    response = RedirectResponse(url="/")

    if user:
         if user.auth_provider == 'local':
             user.auth_provider = 'saml'
             db.commit()

         if user.totp_enabled:
             response = RedirectResponse(url="/auth/2fa-check") # Frontend page
             response.set_cookie(key="partial_auth_user_id", value=user.id, httponly=True, max_age=300)
             return response

         set_session_cookie(response, user.session_token)
         return response
    else:
         # New user
         import json
         pending_info = {
            "provider": "saml",
            "provider_id": email,
            "email": email,
            "name": email.split("@")[0]
         }
         response = RedirectResponse(url="/join?mode=saml")
         response.set_cookie(key="oauth_pending", value=json.dumps(pending_info), httponly=True, max_age=3600)
         return response

# Helper for SAML
def get_saml_request_data(request: Request):
    return {
        'http_host': request.headers.get('host'),
        'script_name': request.url.path,
        'server_port': request.url.port,
        'get_data': request.query_params,
        'post_data': {}, # Only needed for callback which is POST
        'query_string': request.url.query
    }

async def get_saml_request_data_async(request: Request):
    form = await request.form()
    return {
        'http_host': request.headers.get('host'),
        'script_name': request.url.path,
        'server_port': request.url.port,
        'get_data': request.query_params,
        'post_data': form,
        'query_string': request.url.query
    }

@router.post("/auth/login-class")
def login_class(
    response: Response,
    class_id: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Login with email/password but verify user belongs to specific class"""
    user = crud.get_user_by_email(db, email)
    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")
    
    if not crud.verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")
    
    # Verify user belongs to this class
    if user.class_id != class_id:
        raise HTTPException(status_code=401, detail="Du bist nicht Mitglied dieser Klasse")
    
    # Set cookie with proper settings
    set_session_cookie(response, user.session_token)
    response.headers["HX-Redirect"] = "/"
    return {"status": "logged in"}

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

# --- 2FA Verification Routes ---

@router.get("/auth/2fa-check")
def show_2fa_check(request: Request):
    """Show 2FA verification page during login"""
    # Check if we have the partial auth cookie
    partial_user_id = request.cookies.get("partial_auth_user_id")
    if not partial_user_id:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login")

    return templates.TemplateResponse("2fa_check.html", {"request": request})

@router.post("/auth/2fa-check")
def verify_2fa_check(
    response: Response,
    request: Request,
    code: str = Form(...),
    db: Session = Depends(get_db)
):
    partial_user_id = request.cookies.get("partial_auth_user_id")
    if not partial_user_id:
        raise HTTPException(status_code=401, detail="Session expired")

    user = crud.get_user(db, partial_user_id)
    if not user or not user.totp_enabled or not user.totp_secret:
         raise HTTPException(status_code=400, detail="Invalid user state")

    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(code):
        raise HTTPException(status_code=400, detail="Invalid code")

    # Success
    set_session_cookie(response, user.session_token)
    response.delete_cookie("partial_auth_user_id")
    response.headers["HX-Redirect"] = "/"
    return {"status": "success"}
