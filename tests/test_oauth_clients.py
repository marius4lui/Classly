import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import crud
from app.database import Base


class OAuthClientRedirectTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
        )
        TestingSessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )
        Base.metadata.create_all(bind=self.engine)
        self.db = TestingSessionLocal()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_create_oauth_client_registers_multiple_redirect_uris(self):
        client = crud.create_oauth_client(
            self.db,
            client_id="classly-mobile",
            client_secret="",
            name="Classly Mobile",
            redirect_uris=[
                "classly://auth/callback",
                "classly-dev://auth/callback",
            ],
        )

        redirect_uris = crud.get_oauth_redirect_uris_for_client(self.db, client.id)

        self.assertEqual(client.redirect_uri, "classly://auth/callback")
        self.assertEqual(
            sorted(entry.redirect_uri for entry in redirect_uris),
            ["classly-dev://auth/callback", "classly://auth/callback"],
        )

    def test_ensure_oauth_client_backfills_missing_redirect_uri(self):
        client = crud.create_oauth_client(
            self.db,
            client_id="classly-mobile",
            client_secret="",
            name="Classly Mobile",
            redirect_uri="classly://auth/callback",
        )

        crud.ensure_oauth_client(
            self.db,
            client_id="classly-mobile",
            client_secret="",
            name="Classly Mobile",
            redirect_uris=[
                "classly://auth/callback",
                "classly-dev://auth/callback",
            ],
        )

        self.assertTrue(
            crud.oauth_client_allows_redirect_uri(
                self.db,
                client,
                "classly-dev://auth/callback",
            )
        )
        self.assertFalse(
            crud.oauth_client_allows_redirect_uri(
                self.db,
                client,
                "classly://invalid",
            )
        )


if __name__ == "__main__":
    unittest.main()
