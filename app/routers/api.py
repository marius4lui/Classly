import datetime
from fastapi import APIRouter, Depends, Form, Header, HTTPException, Query, Request
from app.repository.base import BaseRepository
from app.repository.factory import get_repository
from app import models
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
    repo: BaseRepository = Depends(get_repository)
):
    token_value = _extract_bearer_token(authorization)
    if not token_value:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = repo.use_integration_token(token_value)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = repo.get_user(token.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found for token")

    return {"user": user, "token": token}


@router.post("/token")
def issue_api_token(
    request: Request,
    email: str = Form(None),
    password: str = Form(None),
    expires_in_days: int = Form(None),
    repo: BaseRepository = Depends(get_repository),
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
        candidate = repo.get_user_by_email(email)
        
        from app.crud import verify_password
        
        if not candidate or not candidate.password_hash:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if not verify_password(password, candidate.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        user = candidate

    expires_at = None
    if expires_in_days:
        try:
            expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=int(expires_in_days))
        except Exception:
            raise HTTPException(status_code=400, detail="expires_in_days must be an integer")

    token = repo.create_integration_token(
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
    repo: BaseRepository = Depends(get_repository),
    updated_since: str = Query(None, description="ISO timestamp filter"),
    limit: int = Query(200, description="Max events to return")
):
    token = auth["token"]
    
    limit = min(max(limit, 1), 500)

    since_dt = None
    if updated_since:
        try:
            since_dt = datetime.datetime.fromisoformat(updated_since)
        except ValueError:
            raise HTTPException(status_code=400, detail="updated_since must be ISO format")

    events = repo.list_events(class_id=token.class_id, limit=limit, updated_since=since_dt)

    def serialize_event(event: models.Event):
        # Fetch relationships if using repo that doesn't eager load (e.g. Appwrite, or optimized SQL)
        # Assuming event object MIGHT have topics/links loaded if from SQL OR we need to fetch.
        # But repo interface returns models.Event which has .topics .links attributes.
        # For Appwrite, these might be empty/None if not loaded.
        # Check if topics are loaded? No easy way in simple model.
        # We will fetch them explicitly if we are being safe, or assume lazy load works for SQL and unimplemented for Appwrite in list?
        # Appwrite listing didn't populate children.
        # For now, we return empty topics/links for Appwrite list to be performant, OR we fetch one by one (slow).
        # Let's try to fetch if not present?
        # Actually, let's leave topics/links empty in list view for performance on Appwrite,
        # or implement bulk fetch.
        
        # If topics is list, use it.
        topics_list = []
        links_list = []
        
        # Safe access attempts?
        try:
             # This will trigger SQL query in SQLAlchemy
             if event.topics: topics_list = event.topics
        except Exception:
             pass
             
        try:
             if event.links: links_list = event.links
        except Exception:
             pass

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
                } for t in topics_list
            ],
            "links": [
                {
                    "id": l.id,
                    "url": l.url,
                    "label": l.label
                } for l in links_list
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
    repo: BaseRepository = Depends(get_repository)
):
    token = auth["token"]
    subjects = repo.get_subjects_for_class(token.class_id)
    return {
        "class_id": token.class_id,
        "count": len(subjects),
        "subjects": [
            {"id": s.id, "name": s.name, "color": s.color}
            for s in subjects
        ]
    }
