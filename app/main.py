import os
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base, SQLALCHEMY_DATABASE_URL, SessionLocal
from app.routers import (
    auth,
    pages,
    events,
    admin,
    caldav,
    preferences,
    grades,
    timetable,
    api,
    i18n_router,
    oauth,
    push,
)
from app.routers import api_v1
from app import fix_db_schema, crud, auto_migrate
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.limiter import limiter
from app.i18n import i18n
from app.core.csrf import (
    CSRF_COOKIE_NAME,
    CSRF_FORM_FIELD,
    CSRF_HEADER_NAME,
    csrf_enabled,
    get_csrf_token,
    is_path_exempt,
    is_state_changing,
    same_token,
)
from app.core.cookies import cookie_secure

# Fix DB Schema (Add missing columns to old SQLite volumes)
fix_db_schema.fix_schema(SQLALCHEMY_DATABASE_URL)
auto_migrate.run_auto_migrations()

# Create Tables
Base.metadata.create_all(bind=engine)


# Run Data Migrations
def run_migrations():
    db = SessionLocal()
    try:
        crud.migrate_capitalize_user_names(db)
    finally:
        db.close()



run_migrations()

# Check for Auto-Migration to Appwrite
if os.getenv("AUTOMIGRATE_TO") == "appwrite":
    from app.core.migration import migrate_to_appwrite
    migrate_to_appwrite()


app = FastAPI(title="Classly")

# CORS Middleware
from fastapi.middleware.cors import CORSMiddleware


def _cors_allow_origins() -> list[str]:
    raw = os.getenv("CORS_ALLOW_ORIGINS", "").strip()
    if not raw:
        return ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_allow_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Max File Size Middleware
from fastapi import Request
from fastapi.responses import JSONResponse
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
MAX_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

@app.middleware("http")
async def check_content_length(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            length = int(content_length)
            if length > MAX_BYTES:
                 return JSONResponse(status_code=413, content={"detail": f"Request entity too large. Max {MAX_FILE_SIZE_MB}MB."})
        except ValueError:
            pass
    return await call_next(request)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; script-src 'self' 'unsafe-inline' https://unpkg.com https://www.googletagmanager.com; "
        "style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self'; "
        "frame-ancestors 'none'; base-uri 'self'; form-action 'self'",
    )
    if os.getenv("COOKIE_SECURE", "true").lower() == "true":
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response


@app.middleware("http")
async def csrf_middleware(request: Request, call_next):
    exempt_paths = [
        "/api/",
        "/api/v1/",
        "/api/oauth/token",
        "/api/oauth/userinfo",
        "/docs",
        "/openapi.json",
    ]

    if csrf_enabled() and is_state_changing(request) and not is_path_exempt(request.url.path, exempt_paths):
        cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
        header_token = request.headers.get(CSRF_HEADER_NAME)
        submitted = header_token
        # Avoid reading/parsing form bodies when header token is present (e.g. HTMX),
        # because consuming form data in middleware can break downstream Form parsing.
        if not submitted:
            form_token = None
            ctype = request.headers.get("content-type", "")
            if "application/x-www-form-urlencoded" in ctype or "multipart/form-data" in ctype:
                try:
                    form = await request.form()
                    form_token = form.get(CSRF_FORM_FIELD)
                except Exception:
                    form_token = None
            submitted = form_token
        if not same_token(cookie_token, submitted):
            return JSONResponse(status_code=403, content={"detail": "Invalid CSRF token"})

    response = await call_next(request)
    if csrf_enabled() and not request.cookies.get(CSRF_COOKIE_NAME):
        response.set_cookie(
            key=CSRF_COOKIE_NAME,
            value=get_csrf_token(request),
            httponly=False,
            samesite="lax",
            secure=cookie_secure(request),
            max_age=60 * 60 * 24 * 30,
        )
    return response

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.middleware("http")
async def language_middleware(request: Request, call_next):
    # 1. Query Param
    lang = request.query_params.get("lang")

    # 2. Cookie
    if not lang:
        lang = request.cookies.get("NEXT_LOCALE") or request.cookies.get("lang")

    # 3. Accept-Language Header
    if not lang:
        accept = request.headers.get("Accept-Language")
        if accept:
            # Robust parser:
            # 1. Get first token (split by comma)
            # 2. Remove parameters (split by semicolon)
            # 3. Get subtag (split by dash or underscore)
            # 4. Normalize to lowercase
            token = accept.split(",")[0].split(";")[0].strip()
            if "-" in token:
                lang_candidate = token.split("-")[0]
            elif "_" in token:
                lang_candidate = token.split("_")[0]
            else:
                lang_candidate = token

            lang_candidate = lang_candidate.lower()

            # 5. Validate against available translations
            if lang_candidate in i18n.translations:
                lang = lang_candidate

    # 4. Fallback
    if not lang:
        lang = i18n.default_lang

    # Validation (check if we have translation)
    if lang not in i18n.translations:
        lang = i18n.default_lang

    request.state.lang = lang

    # Helper function for templates
    def t(key):
        return i18n.get_translation(request.state.lang, key)

    request.state.t = t

    response = await call_next(request)
    return response


@app.middleware("http")
async def domain_migration_middleware(request: Request, call_next):
    # Configuration via Environment Variables
    # Example: MIGRATE_FROM_DOMAIN="old.example.com", MIGRATE_TO_DOMAIN="new.example.com"
    old_domain = os.getenv("MIGRATE_FROM_DOMAIN")
    new_domain = os.getenv("MIGRATE_TO_DOMAIN")

    if old_domain and new_domain:
        host = request.headers.get("host", "").split(":")[0]

        if host == old_domain:
            # Check for session token
            session_token = request.cookies.get("session_token")

            if session_token:
                # Avoid leaking session tokens via query strings.
                return RedirectResponse(f"https://{new_domain}")
            # Just redirect guests
            return RedirectResponse(f"https://{new_domain}")

    return await call_next(request)


# Include Routers
app.include_router(auth.router)
app.include_router(pages.router)
app.include_router(events.router)
app.include_router(admin.router)
app.include_router(caldav.router)
app.include_router(preferences.router)
app.include_router(grades.router)
app.include_router(timetable.router)
app.include_router(api.router)  # Legacy API (/api/)
app.include_router(api_v1.router)  # New API v1 (/api/v1/)
app.include_router(i18n_router.router)
app.include_router(oauth.router)
app.include_router(push.router)
