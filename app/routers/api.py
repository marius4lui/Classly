import datetime
from fastapi import APIRouter, Depends, Form, Header, HTTPException, Query, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, models
from app.core.auth import get_current_user

router = APIRouter(prefix="/api", tags=["api"])


def _extract_bearer_token(authorization: str) -> str:
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) != 2:
        return None
    if parts[0].lower() != "bearer":
        return None
    return parts[1].strip()


def require_integration_auth(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    token_value = _extract_bearer_token(authorization)
    if not token_value:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = crud.use_integration_token(db, token_value)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = crud.get_user(db, token.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found for token")

    return {"user": user, "token": token}


@router.post("/token")
def issue_api_token(
    request: Request,
    email: str = Form(None),
    password: str = Form(None),
    expires_in_days: int = Form(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Issue a personal access token for API access.
    - Uses session cookie if present, otherwise email/password.
    - Tokens are class-bound and read-only (read:events).
    """
    user = current_user

    # Fallback to email/password if no session
    if not user:
        if not email or not password:
            raise HTTPException(status_code=401, detail="Credentials required")
        candidate = crud.get_user_by_email(db, email)
        if not candidate or not candidate.password_hash:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if not crud.verify_password(password, candidate.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        user = candidate

    expires_at = None
    if expires_in_days:
        try:
            expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=int(expires_in_days))
        except Exception:
            raise HTTPException(status_code=400, detail="expires_in_days must be an integer")

    token = crud.create_integration_token(
        db,
        user_id=user.id,
        class_id=user.class_id,
        scopes="read:events",
        expires_at=expires_at
    )

    return {
        "access_token": token.token,
        "token_type": "bearer",
        "expires_at": token.expires_at.isoformat() if token.expires_at else None,
        "class_id": token.class_id,
        "scopes": token.scopes
    }


@router.get("/me")
def get_me(auth = Depends(require_integration_auth)):
    user = auth["user"]
    token = auth["token"]
    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "role": user.role.value if hasattr(user.role, "value") else user.role,
            "class_id": user.class_id
        },
        "token": {
            "scopes": token.scopes,
            "expires_at": token.expires_at.isoformat() if token.expires_at else None,
            "last_used_at": token.last_used_at.isoformat() if token.last_used_at else None
        }
    }


@router.get("/events")
def list_events(
    auth = Depends(require_integration_auth),
    db: Session = Depends(get_db),
    updated_since: str = Query(None, description="ISO timestamp filter"),
    limit: int = Query(200, description="Max events to return")
):
    user = auth["user"]
    token = auth["token"]

    limit = min(max(limit, 1), 500)

    since_dt = None
    if updated_since:
        try:
            since_dt = datetime.datetime.fromisoformat(updated_since)
        except ValueError:
            raise HTTPException(status_code=400, detail="updated_since must be ISO format")

    query = db.query(models.Event).filter(models.Event.class_id == token.class_id)
    if since_dt:
        query = query.filter(models.Event.updated_at >= since_dt)
    events = query.order_by(models.Event.updated_at.desc()).limit(limit).all()

    def serialize_event(event: models.Event):
        return {
            "id": event.id,
            "class_id": event.class_id,
            "type": event.type.value if hasattr(event.type, "value") else event.type,
            "priority": event.priority.value if hasattr(event.priority, "value") else (event.priority or "MEDIUM"),
            "subject_id": event.subject_id,
            "subject_name": event.subject_name,
            "title": event.title,
            "date": event.date.isoformat() if event.date else None,
            "created_at": event.created_at.isoformat() if event.created_at else None,
            "updated_at": event.updated_at.isoformat() if event.updated_at else None,
            "author_id": event.author_id,
            "topics": [
                {
                    "id": t.id,
                    "topic_type": t.topic_type,
                    "content": t.content,
                    "count": t.count,
                    "pages": t.pages,
                    "order": t.order,
                    "parent_id": t.parent_id
                } for t in event.topics
            ],
            "links": [
                {
                    "id": l.id,
                    "url": l.url,
                    "label": l.label
                } for l in event.links
            ]
        }

    return {
        "class_id": token.class_id,
        "count": len(events),
        "events": [serialize_event(e) for e in events]
    }


@router.get("/subjects")
def list_subjects(
    auth = Depends(require_integration_auth),
    db: Session = Depends(get_db)
):
    token = auth["token"]
    subjects = crud.get_subjects_for_class(db, token.class_id)
    return {
        "class_id": token.class_id,
        "count": len(subjects),
        "subjects": [
            {"id": s.id, "name": s.name, "color": s.color}
            for s in subjects
        ]
    }
