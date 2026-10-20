"""Regression coverage for legacy NULL values without changing stored data."""

import unittest
from unittest.mock import patch

from fastapi import FastAPI, Response
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, insert, null
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import models
from app.core.auth import get_current_user
from app.database import Base, get_db
from app.repository.factory import get_repository
from app.repository.sql import SqlAlchemyRepository
from app.routers import api, auth, pages, timetable
from app.routers.api_v1 import users
from app.routers.api_v1.deps import require_users_read


class NullableRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.repo = SqlAlchemyRepository(self.db)
        self.clazz = models.Class(
            id="class",
            name="Example Class",
            join_token="class-join-token",
            join_enabled=True,
            timetable_public_enabled=True,
            timetable_public_token="public-token",
        )
        self.email = "member@example.test"
        self.user = models.User(
            id="user",
            name="Example Member",
            class_id="class",
            role=models.UserRole.MEMBER,
            email=self.email,
            password_hash="stored-password-hash",
            session_token="valid-session-token",
        )
        self.key = models.IntegrationToken(
            id="key",
            class_id="class",
            user_id="user",
            token="api-token",
            name="Example Key",
        )
        self.db.add_all([self.clazz, self.user, self.key])
        self.db.commit()

        app = FastAPI()
        app.include_router(auth.router)
        app.include_router(timetable.router)
        app.include_router(pages.router)
        app.include_router(api.router)
        app.include_router(users.router, prefix="/api/v1")
        app.dependency_overrides[get_db] = lambda: self.db
        app.dependency_overrides[get_repository] = lambda: self.repo
        app.dependency_overrides[get_current_user] = lambda: self.user
        app.dependency_overrides[api.require_integration_auth] = lambda: {
            "user": self.user,
            "token": self.key,
        }
        app.dependency_overrides[require_users_read] = lambda: {
            "user": self.user,
            "api_key": self.key,
            "class_id": self.clazz.id,
        }
        self.client = TestClient(
            app, base_url="https://testserver", follow_redirects=False
        )
        self.addCleanup(self.client.close)
        limiter_patch = patch.object(auth.limiter, "enabled", False)
        limiter_patch.start()
        self.addCleanup(limiter_patch.stop)
        password_patch = patch("app.crud.verify_password", return_value=True)
        password_patch.start()
        self.addCleanup(password_patch.stop)
        secure_patch = patch.dict("os.environ", {"COOKIE_SECURE": "true"})
        secure_patch.start()
        self.addCleanup(secure_patch.stop)

    def tearDown(self) -> None:
        self.db.close()
        self.engine.dispose()

    def add_login_token(
        self,
        *,
        user_id: str | None = None,
        user_name: str | None = None,
        role: models.UserRole | None = models.UserRole.MEMBER,
    ) -> models.LoginToken:
        token = models.LoginToken(
            id="login-token-id",
            token="login-token",
            class_id=self.clazz.id,
            created_by=self.user.id,
            user_id=user_id,
            user_name=user_name,
            role=models.UserRole.MEMBER,
        )
        self.db.add(token)
        self.db.flush()
        # Assign after INSERT so an explicit NULL is not replaced by the default.
        token.role = role
        self.db.commit()
        return token

    def add_timetable(self) -> models.TimetableSettings:
        self.db.execute(
            insert(models.TimetableSettings).values(
                id="settings",
                class_id=self.clazz.id,
                slot_duration=null(),
                break_duration=null(),
                day_start_hour=null(),
                day_start_minute=null(),
                day_end_hour=null(),
                day_end_minute=null(),
            )
        )
        self.db.add(
            models.TimetableSlot(
                id="slot",
                class_id=self.clazz.id,
                weekday=0,
                slot_number=2,
                subject_name="Mathematics",
            )
        )
        self.db.add(models.UserTimetableSelection(user_id=self.user.id, slot_id="slot"))
        self.db.commit()
        settings = self.db.get(models.TimetableSettings, "settings")
        assert settings is not None
        return settings

    def test_missing_session_token_fails_closed_for_all_existing_user_logins(
        self,
    ) -> None:
        self.add_login_token(user_id=self.user.id)
        for token in (None, ""):
            self.user.session_token = token
            self.db.commit()
            requests = [
                ("GET", "/join/login-token", None),
                (
                    "POST",
                    "/auth/login",
                    {"email": self.email, "password": "password"},
                ),
                (
                    "POST",
                    "/auth/login-class",
                    {
                        "class_id": self.clazz.id,
                        "email": self.email,
                        "password": "password",
                    },
                ),
                (
                    "POST",
                    "/auth/join",
                    {
                        "join_token": self.clazz.join_token,
                        "user_name": self.user.name,
                    },
                ),
            ]
            for method, path, data in requests:
                with self.subTest(token=token, path=path):
                    response = self.client.request(method, path, data=data)
                    self.assertEqual(response.status_code, 401)
                    self.assertNotIn("set-cookie", response.headers)
                    self.assertNotIn("hx-redirect", response.headers)
        self.assertEqual(self.db.query(models.User).count(), 1)

    def test_valid_password_login_retains_cookie_security_and_redirect(self) -> None:
        for path in ("/auth/login", "/auth/login-class"):
            with self.subTest(path=path):
                response = self.client.post(
                    path,
                    data={
                        "email": self.email,
                        "password": "password",
                        "class_id": self.clazz.id,
                    },
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.headers["hx-redirect"], "/")
                self.assertEqual(
                    response.cookies["session_token"], "valid-session-token"
                )
                for flag in ("HttpOnly", "Secure", "SameSite=lax", "Max-Age=2592000"):
                    self.assertIn(flag, response.headers["set-cookie"])

    def test_invalid_password_still_rejects_login(self) -> None:
        with patch("app.crud.verify_password", return_value=False):
            response = self.client.post(
                "/auth/login",
                data={"email": self.email, "password": "wrong"},
            )
        self.assertEqual(response.status_code, 401)
        self.assertNotIn("set-cookie", response.headers)

    def test_existing_user_login_link_does_not_require_predefined_name(self) -> None:
        self.add_login_token(user_id=self.user.id)
        response = self.client.get("/join/login-token")
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["location"], "/")
        self.assertEqual(response.cookies["session_token"], "valid-session-token")
        self.assertEqual(self.db.query(models.User).count(), 1)

    def test_new_user_login_link_rejects_missing_or_blank_name(self) -> None:
        token = self.add_login_token(role=None)
        for name in (None, "", "   "):
            token.user_name = name
            self.db.commit()
            with self.subTest(name=name):
                response = self.client.get("/join/login-token")
                self.assertEqual(response.status_code, 404)
                self.assertNotIn("set-cookie", response.headers)
                self.assertEqual(self.db.query(models.User).count(), 1)

    def test_new_user_login_link_defaults_null_role_to_member(self) -> None:
        self.add_login_token(user_name="new member", role=None)
        response = self.client.get("/join/login-token")
        self.assertEqual(response.status_code, 303)
        new_user = (
            self.db.query(models.User).filter(models.User.id != self.user.id).one()
        )
        self.assertEqual(new_user.name, "New Member")
        self.assertEqual(new_user.role, models.UserRole.MEMBER)
        self.assertEqual(response.cookies["session_token"], new_user.session_token)

    def test_new_user_login_link_preserves_explicit_role(self) -> None:
        self.add_login_token(user_name="invited guest", role=models.UserRole.GUEST)
        response = self.client.get("/join/login-token")
        self.assertEqual(response.status_code, 303)
        new_user = (
            self.db.query(models.User).filter(models.User.id != self.user.id).one()
        )
        self.assertEqual(new_user.role, models.UserRole.GUEST)

    def test_session_cookie_helper_rejects_null_without_mutating_response(self) -> None:
        from fastapi import HTTPException

        response = Response()
        with self.assertRaises(HTTPException) as raised:
            auth.set_session_cookie(response, None)
        self.assertEqual(raised.exception.status_code, 401)
        self.assertNotIn("set-cookie", response.headers)

    def test_legacy_null_timetable_settings_use_defaults_without_writing(self) -> None:
        settings = self.add_timetable()
        expected = {
            "slot_duration": 45,
            "break_duration": 15,
            "day_start_hour": 8,
            "day_start_minute": 0,
            "day_end_hour": 16,
            "day_end_minute": 0,
        }
        response = self.client.get("/timetable/settings")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"id": "settings", **expected})
        for path in (
            "/timetable/slots",
            "/timetable/my",
            "/public/stundenplan/public-token/data",
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                payload = response.json()
                slot = payload["slots"][0]
                self.assertEqual(slot["start_time"], "09:00")
                self.assertEqual(slot["end_time"], "09:45")
                if path.startswith("/public/"):
                    self.assertEqual(payload["settings"], expected)
        self.db.expire_all()
        for name in expected:
            self.assertIsNone(getattr(settings, name))
        self.assertFalse(self.db.dirty)

    def test_timetable_zero_values_are_not_replaced_by_defaults(self) -> None:
        settings = self.add_timetable()
        settings.slot_duration = 0
        settings.break_duration = 0
        settings.day_start_hour = 0
        settings.day_start_minute = 0
        settings.day_end_hour = 0
        settings.day_end_minute = 0
        self.db.commit()
        self.assertTrue(
            all(
                value == 0
                for value in timetable.timetable_settings_values(settings).values()
            )
        )
        response = self.client.get("/public/stundenplan/public-token/data")
        self.assertEqual(response.status_code, 200)
        slot = response.json()["slots"][0]
        self.assertEqual(slot["start_time"], "00:00")
        self.assertEqual(slot["end_time"], "00:00")

    def test_configured_timetable_values_are_unchanged(self) -> None:
        settings = self.add_timetable()
        settings.slot_duration = 50
        settings.break_duration = 10
        settings.day_start_hour = 7
        settings.day_start_minute = 30
        self.db.commit()
        self.assertEqual(timetable.calculate_slot_time(settings, 2), ("08:30", "09:20"))
        response = self.client.get("/timetable/slots")
        slot = response.json()["slots"][0]
        self.assertEqual(slot["start_time"], "08:30")
        self.assertEqual(slot["end_time"], "09:20")

    def test_user_api_role_defaults_do_not_grant_admin_access(self) -> None:
        self.user.role = None
        self.db.commit()
        for path in ("/api/me", "/api/v1/users/me"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()["user"]["role"], "member")
        response = self.client.get("/api/v1/users")
        self.assertEqual(response.json()["users"][0]["role"], "member")
        response = self.client.get("/api/v1/users/user")
        self.assertEqual(response.json()["role"], "member")
        response = self.client.put("/timetable/settings")
        self.assertEqual(response.status_code, 403)
        self.db.expire_all()
        self.assertIsNone(self.user.role)

    def test_user_api_preserves_existing_enum_and_string_roles(self) -> None:
        for role in models.UserRole:
            self.user.role = role
            self.db.commit()
            with self.subTest(role=role):
                response = self.client.get("/api/v1/users/user")
                self.assertEqual(response.json()["role"], role.value)
                # Appwrite maps a role from JSON, which can be a plain string.
                appwrite_user = models.User(role=role.value)
                payload = api.get_me({"user": appwrite_user, "token": self.key})
                self.assertEqual(payload["user"]["role"], role.value)

    def test_legacy_null_event_priority_defaults_to_medium(self) -> None:
        event = models.Event(
            id="event",
            class_id=self.clazz.id,
            author_id=self.user.id,
            type=models.EventType.INFO,
        )
        self.db.add(event)
        self.db.flush()
        event.priority = None
        self.db.commit()
        for priority in (None, *models.Priority):
            event.priority = priority
            self.db.commit()
            with self.subTest(priority=priority):
                response = self.client.get("/api/events")
                self.assertEqual(response.status_code, 200)
                expected = (priority or models.Priority.MEDIUM).value
                self.assertEqual(response.json()["events"][0]["priority"], expected)
                self.db.expire_all()
                self.assertEqual(event.priority, priority)


if __name__ == "__main__":
    unittest.main()
