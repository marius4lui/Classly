from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import RedirectResponse
from app.core.auth import get_current_user
from app import models
from app.database import get_db
from sqlalchemy.orm import Session
from app.i18n import i18n
from urllib.parse import urlparse

router = APIRouter(prefix="/i18n", tags=["i18n"])


@router.post("/set-language")
def set_language(
    request: Request,
    lang: str = Form(...),
    redirect_url: str = Form(default="/"),
    user: models.User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Validate language
    if lang not in i18n.translations:
        lang = i18n.default_lang

    # Update user if logged in
    if user:
        user.language = lang
        db.commit()

    # Validate redirect_url to prevent open redirects
    # Allow relative paths (e.g. /dashboard) or absolute URLs with same hostname
    parsed_url = urlparse(redirect_url)
    if parsed_url.scheme or parsed_url.netloc:
        # It's an absolute URL
        if parsed_url.netloc != request.url.hostname:
            # Different host -> potentially unsafe
            redirect_url = "/"
    else:
        # Relative path, ensure it starts with /
        if not redirect_url.startswith("/"):
            redirect_url = "/"

    # Redirect
    response = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)

    # Set cookie (valid for 1 year)
    response.set_cookie(
        key="NEXT_LOCALE",
        value=lang,
        max_age=365 * 24 * 60 * 60,
        httponly=False,  # Allow JS to read if needed
        samesite="lax",
    )
    # Also set 'lang' for compatibility
    response.set_cookie(
        key="lang",
        value=lang,
        max_age=365 * 24 * 60 * 60,
        httponly=False,
        samesite="lax",
    )

    return response
