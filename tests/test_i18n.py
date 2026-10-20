"""Exercise the language selector through the real application middleware."""

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import crud, database


@pytest.fixture(scope="module")
def application(tmp_path_factory):
    # Importing main runs migrations. Keep them, and every request, on a test DB.
    database_url = f"sqlite:///{tmp_path_factory.mktemp('i18n') / 'test.db'}"
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    session_factory = sessionmaker(bind=engine)
    with (
        patch.dict(
            os.environ,
            {
                "DATABASE_URL": database_url,
                "AUTOMIGRATE_TO": "",
                "APPWRITE": "false",
                "CSRF_PROTECTION_ENABLED": "true",
                "COOKIE_SECURE": "true",
                "MIGRATE_FROM_DOMAIN": "",
                "MIGRATE_TO_DOMAIN": "",
            },
        ),
        patch.multiple(
            database,
            SQLALCHEMY_DATABASE_URL=database_url,
            engine=engine,
            SessionLocal=session_factory,
        ),
    ):
        from app.main import app

        yield app
    engine.dispose()


@pytest.fixture
def db(application):
    database.Base.metadata.drop_all(bind=database.engine)
    database.Base.metadata.create_all(bind=database.engine)
    with database.SessionLocal() as session:
        yield session


@pytest.fixture
def client(application, db):
    with TestClient(application, base_url="https://testserver") as client:
        assert client.get("/login").status_code == 200
        yield client


@pytest.fixture
def user(db):
    clazz = crud.create_class(db, name="Language test", join_token="test-class")
    return crud.create_user(db, name="Test User", class_id=clazz.id)


def submit_language(client, lang, **kwargs):
    data = {
        "lang": lang,
        "csrf_token": client.cookies["csrf_token"],
        "redirect_url": "/login",
    }
    data.update(kwargs)
    return client.post("/i18n/set-language", data=data, follow_redirects=False)


@pytest.mark.parametrize("logged_in", [False, True])
def test_selector_switches_both_languages_and_persists(client, db, user, logged_in):
    if logged_in:
        client.cookies.set("session_token", user.session_token)

    # A native form submit has a hidden token, but no custom CSRF header.
    for lang in ("en", "de", "en"):
        response = submit_language(client, lang, redirect_url="/?month=10&year=2026")
        assert response.status_code == 302
        assert response.headers["location"] == "/?month=10&year=2026"
        assert client.cookies["NEXT_LOCALE"] == lang
        assert client.cookies["lang"] == lang
        page = client.get(response.headers["location"])
        assert page.status_code == 200
        assert f'<option value="{lang}" selected' in page.text
        assert f'<html lang="{lang}">' in page.text
        if logged_in:
            db.refresh(user)
            assert user.language == lang
            # The saved profile language also survives removal of locale cookies.
            client.cookies.delete("NEXT_LOCALE")
            client.cookies.delete("lang")
            page = client.get("/")
            assert f'<option value="{lang}" selected' in page.text


@pytest.mark.parametrize("transport", ["header", "multipart"])
def test_csrf_transports_preserve_downstream_form_fields(client, transport):
    token = client.cookies["csrf_token"]
    if transport == "header":
        kwargs = {"data": {"lang": "en"}, "headers": {"x-csrf-token": token}}
    else:
        kwargs = {"files": {"lang": (None, "en"), "csrf_token": (None, token)}}
    response = client.post("/i18n/set-language", follow_redirects=False, **kwargs)
    assert response.status_code == 302
    assert client.cookies["NEXT_LOCALE"] == "en"


@pytest.mark.parametrize("token", [None, "incorrect"])
def test_missing_or_invalid_csrf_is_rejected_without_changing_language(
    client, db, user, token
):
    client.cookies.set("session_token", user.session_token)
    data = {"lang": "en"}
    if token is not None:
        data["csrf_token"] = token
    response = client.post("/i18n/set-language", data=data, follow_redirects=False)
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid CSRF token"}
    assert "NEXT_LOCALE" not in client.cookies
    db.refresh(user)
    assert user.language == "de"


def test_csrf_cookie_is_required_even_with_form_token(client):
    token = client.cookies["csrf_token"]
    client.cookies.delete("csrf_token")
    response = client.post(
        "/i18n/set-language", data={"lang": "en", "csrf_token": token}
    )
    assert response.status_code == 403


@pytest.mark.parametrize(
    ("redirect_url", "expected"),
    [
        ("/login?view=test", "/login?view=test"),
        ("https://testserver/login", "https://testserver/login"),
        ("https://example.com/login", "/"),
        ("//example.com/login", "/"),
        ("login", "/"),
    ],
)
def test_language_change_keeps_safe_redirects(client, redirect_url, expected):
    response = submit_language(client, "en", redirect_url=redirect_url)
    assert response.status_code == 302
    assert response.headers["location"] == expected


def test_unknown_language_falls_back_to_default(client):
    response = submit_language(client, "unknown")
    assert response.status_code == 302
    assert client.cookies["NEXT_LOCALE"] == "de"


def test_file_is_not_a_valid_csrf_token(client):
    response = client.post(
        "/i18n/set-language",
        files={"lang": (None, "en"), "csrf_token": ("token.txt", b"not-a-token")},
        follow_redirects=False,
    )
    assert response.status_code == 403
    assert "NEXT_LOCALE" not in client.cookies


@pytest.mark.parametrize("encoding", ["urlencoded", "multipart"])
@pytest.mark.parametrize("length", ["accurate", "missing", "understated"])
def test_csrf_body_cache_enforces_size_limit(client, monkeypatch, encoding, length):
    from app import main

    monkeypatch.setattr(main, "MAX_BYTES", 256)
    data = {
        "lang": "en",
        "csrf_token": client.cookies["csrf_token"],
        "extra": "x" * 512,
    }
    if encoding == "multipart":
        request = client.build_request(
            "POST",
            "/i18n/set-language",
            files={key: (None, value) for key, value in data.items()},
        )
    else:
        request = client.build_request("POST", "/i18n/set-language", data=data)
    if length == "missing":
        del request.headers["content-length"]
    elif length == "understated":
        request.headers["content-length"] = "1"
    response = client.send(request, follow_redirects=False)
    assert response.status_code == 413
    assert "NEXT_LOCALE" not in client.cookies
