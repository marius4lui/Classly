"""Regression coverage for the runtime contracts exposed by static checking."""

from unittest.mock import Mock

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, null
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import crud, models
from app.database import Base, get_db
from app.limiter import limiter
from app.repository.appwrite import AppwriteRepository
from app.repository.factory import get_repository, require_sql_repository
from app.repository.sql import SqlAlchemyRepository
from app.routers import admin, api_v1, events
from app.routers.api_v1 import audit


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


@pytest.fixture
def owner(db):
    clazz = crud.create_class(db, "Contracts", "contracts-test")
    return crud.create_user(db, "Test Owner", clazz.id, models.UserRole.OWNER)


@pytest.fixture
def client(db):
    app = FastAPI()
    app.state.limiter = limiter
    app.include_router(admin.router)
    app.include_router(api_v1.router)
    app.include_router(events.router)
    # The existing audit router is tested in isolation, not enabled in production.
    app.include_router(audit.router, prefix="/api/v1")
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_repository] = lambda: SqlAlchemyRepository(db)
    with TestClient(app) as client:
        yield client


def use_appwrite(client):
    # No external service calls or credentials are needed to test capability checks.
    repository = object.__new__(AppwriteRepository)
    client.app.dependency_overrides[get_repository] = lambda: repository


def authenticate_owner(client, owner):
    client.cookies.set("session_token", owner.session_token)


def api_headers(db, owner, scopes="timetable:read,audit:read,events:write"):
    _, raw = crud.create_api_key(
        db, "Test key", owner.id, owner.class_id, owner.id, scopes
    )
    return {"Authorization": f"Bearer {raw}"}


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/api-keys"),
        ("GET", "/api-keys/json"),
        ("POST", "/api-keys"),
        ("POST", "/api-keys/missing/rotate"),
        ("DELETE", "/api-keys/missing"),
    ],
)
def test_admin_sql_only_operations_fail_closed_on_appwrite(client, owner, method, path):
    use_appwrite(client)
    kwargs = (
        {"data": {"name": "Test key"}}
        if path == "/api-keys" and method == "POST"
        else {}
    )
    # Authentication remains before capability checks.
    assert client.request(method, path, **kwargs).status_code == 401
    authenticate_owner(client, owner)
    response = client.request(method, path, **kwargs)
    assert response.status_code == 501
    assert (
        response.json()["detail"]
        == "This operation is unavailable for the configured storage backend."
    )


@pytest.mark.parametrize(
    "path", ["/api/v1/timetable", "/api/v1/timetable/settings", "/api/v1/audit-log"]
)
def test_api_sql_only_operations_keep_header_validation_before_appwrite_rejection(
    client, path
):
    use_appwrite(client)
    assert client.get(path).status_code == 401
    assert (
        client.get(path, headers={"Authorization": "Basic invalid"}).status_code == 401
    )
    assert (
        client.get(path, headers={"Authorization": "Bearer test-token"}).status_code
        == 501
    )


def test_sql_key_lifecycle_and_timetable_and_audit_remain_available(client, db, owner):
    authenticate_owner(client, owner)
    assert client.get("/api-keys").status_code == 200
    created = client.post(
        "/api-keys", data={"name": "New test key", "scopes": "timetable:read"}
    )
    assert created.status_code == 200
    key_id = created.json()["key_id"]
    assert client.get("/api-keys/json").json()["count"] == 1
    rotated = client.post(f"/api-keys/{key_id}/rotate")
    assert rotated.status_code == 200
    assert client.delete(f"/api-keys/{key_id}").status_code == 200
    headers = api_headers(db, owner)
    for path in (
        "/api/v1/timetable",
        "/api/v1/timetable/settings",
        "/api/v1/audit-log",
    ):
        assert client.get(path, headers=headers).status_code == 200
    # A timetable key cannot read audit records.
    headers = api_headers(db, owner, scopes="timetable:read")
    assert client.get("/api/v1/audit-log", headers=headers).status_code == 403


def test_undated_event_uses_enum_and_invalid_type_is_rejected(client, db, owner):
    authenticate_owner(client, owner)
    response = client.post("/events", data={"type": "INFO", "title": "Announcement"})
    assert response.status_code == 200
    event = db.get(models.Event, response.json()["event_id"])
    assert event.type == models.EventType.INFO
    assert event.date is None
    assert client.post("/events", data={"type": "invalid"}).status_code == 400
    assert db.query(models.Event).count() == 1


def test_disappearing_event_is_not_reported_as_success(client, db, owner):
    event = crud.create_event(db, owner.class_id, owner.id, models.EventType.INFO, None)
    repo = SqlAlchemyRepository(db)
    repo.update_event = Mock(return_value=None)
    client.app.dependency_overrides[get_repository] = lambda: repo
    response = client.put(
        f"/api/v1/events/{event.id}",
        json={"title": "Changed"},
        headers=api_headers(db, owner),
    )
    assert response.status_code == 404
    assert (
        db.query(models.AuditLog)
        .filter_by(action=models.AuditAction.EVENT_EDIT)
        .count()
        == 0
    )


def test_grade_statistics_uses_default_weight_for_null_and_preserves_zero(db, owner):
    first = crud.create_event(db, owner.class_id, owner.id, models.EventType.TEST, None)
    second = crud.create_event(
        db, owner.class_id, owner.id, models.EventType.TEST, None
    )
    db.add(models.Grade(user_id=owner.id, event_id=first.id, grade=2.0, weight=null()))
    db.add(models.Grade(user_id=owner.id, event_id=second.id, grade=6.0, weight=0.0))
    db.commit()
    stats = crud.get_grade_statistics(db, owner.id, owner.class_id)
    assert stats["overall"] == 2.0
    assert sorted(grade["weight"] for grade in stats["grades"]) == [0.0, 1.0]


@pytest.mark.parametrize(
    "mapper",
    [
        "_map_doc_to_user",
        "_map_doc_to_class",
        "_map_doc_to_event",
        "_map_doc_to_topic",
        "_map_doc_to_subject",
    ],
)
def test_appwrite_required_identifiers_are_validated(mapper):
    repo = object.__new__(AppwriteRepository)
    with pytest.raises(ValueError, match="Invalid Appwrite document field"):
        getattr(repo, mapper)({})


def test_sql_capability_check_keeps_same_repository_instance(db):
    repo = SqlAlchemyRepository(db)
    assert require_sql_repository(repo) is repo
    with pytest.raises(HTTPException) as exc:
        require_sql_repository(object.__new__(AppwriteRepository))
    assert exc.value.status_code == 501


def test_api_timetable_settings_resolve_null_defaults_without_overwriting_zero(
    client, db, owner
):
    settings = models.TimetableSettings(
        class_id=owner.class_id,
        slot_duration=null(),
        break_duration=0,
        day_start_hour=0,
        day_start_minute=null(),
        day_end_hour=null(),
        day_end_minute=null(),
    )
    db.add(settings)
    db.commit()
    response = client.get("/api/v1/timetable/settings", headers=api_headers(db, owner))
    assert response.status_code == 200
    assert response.json() == {
        "class_id": owner.class_id,
        "slot_duration": 45,
        "break_duration": 0,
        "day_start": "00:00",
        "day_end": "16:00",
    }
    db.refresh(settings)
    assert settings.slot_duration is None
    assert settings.break_duration == 0
