import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

from ruamel.yaml import YAML

from scripts import classly_setup_cli, migrate_to_appwrite
from scripts.classly_client import ClasslyClient


class ClasslyClientQueryTests(unittest.TestCase):
    def test_events_send_integer_limit_and_optional_string_timestamp(self) -> None:
        client = ClasslyClient(api_key="test-api-key")
        events = [{"id": "event-1"}]
        for updated_since in (None, "", "2026-10-20T09:30:00Z"):
            with self.subTest(updated_since=updated_since):
                with patch.object(
                    client, "_request", return_value={"events": events}
                ) as request:
                    result = client.get_events(limit=50, updated_since=updated_since)

                expected: dict[str, int | str] = {"limit": 50}
                if updated_since:
                    expected["updated_since"] = updated_since
                request.assert_called_once_with("GET", "/events", params=expected)
                self.assertEqual(result, events)


class SetupOptionalDependencyTests(unittest.TestCase):
    def test_commands_without_optional_dependencies(self) -> None:
        script = (
            Path(__file__).resolve().parents[1] / "scripts" / "classly_setup_cli.py"
        )
        cases = [
            (["--help"], 0, "Classly interactive setup"),
            (["quick"], 1, "questionary is required for interactive mode"),
            (["validate"], 1, "ruamel.yaml is required"),
        ]
        with tempfile.TemporaryDirectory() as directory:
            for arguments, expected_code, expected_message in cases:
                with self.subTest(arguments=arguments):
                    # -S excludes site-packages to exercise genuine missing imports.
                    result = subprocess.run(
                        [sys.executable, "-S", str(script), *arguments],
                        cwd=directory,
                        capture_output=True,
                        text=True,
                        timeout=30,
                        check=False,
                    )
                    self.assertEqual(result.returncode, expected_code)
                    self.assertIn(expected_message, result.stdout + result.stderr)
                    self.assertNotIn("Traceback", result.stderr)

    def test_invalid_integer_input_retries_and_empty_input_uses_default(self) -> None:
        with patch.object(classly_setup_cli.questionary, "text") as text:
            text.return_value.ask.side_effect = ["not-an-integer", ""]
            with patch("sys.stdout", new_callable=io.StringIO) as output:
                port = classly_setup_cli._ask_int("Port:", default=8000)
        self.assertEqual(port, 8000)
        self.assertEqual(text.call_count, 2)
        self.assertIn("Please enter a valid integer.", output.getvalue())


class SetupComposeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = classly_setup_cli.WizardConfig(
            target="normal",
            port=8000,
            max_classes="",
            migrate_from_domain="",
            migrate_to_domain="",
            database_url="sqlite:////data/classly.db",
            appwrite=False,
            appwrite_endpoint="",
            appwrite_project_id="",
            appwrite_api_key="",
            appwrite_database_id="classly_db",
            automigrate_to="",
            secret_key="",
            timezone="Europe/Berlin",
        )

    def test_compose_round_trip_preserves_comments_and_existing_env_files(self) -> None:
        original = (
            "# Keep this deployment note\n"
            "services:\n"
            "  classly:\n"
            "    image: classly:test\n"
            "    env_file:\n"
            "      - .env.shared\n"
            "    ports:\n"
            "      - '9000:8000'\n"
        )
        for target in ("normal", "coolify"):
            with self.subTest(target=target):
                patched = classly_setup_cli.patch_compose_content(
                    original, self.config, target, ".env"
                )
                self.assertIn("# Keep this deployment note", patched)
                service = YAML().load(patched)["services"]["classly"]
                self.assertEqual(service["env_file"], [".env.shared", ".env"])
                self.assertIn("PORT=8000", service["environment"])
                if target == "normal":
                    self.assertEqual(service["ports"], ["${PORT:-8000}:8000"])
                else:
                    self.assertNotIn("ports", service)
                    self.assertEqual(service["expose"], ["8000"])

    def test_invalid_compose_structure_exits_with_a_useful_message(self) -> None:
        for content, message in (
            ("- not-a-mapping\n", "Compose content is not a mapping"),
            ("services: {}\n", "Compose file missing 'services.classly'"),
        ):
            with self.subTest(content=content):
                with patch("sys.stderr", new_callable=io.StringIO) as error:
                    with self.assertRaises(SystemExit) as raised:
                        classly_setup_cli.patch_compose_content(
                            content, self.config, "normal", ".env"
                        )
                self.assertEqual(raised.exception.code, 1)
                self.assertIn(message, error.getvalue())


class AttributePollingTests(unittest.TestCase):
    def test_available_attribute_does_not_sleep(self) -> None:
        database = Mock()
        database.get_attribute.return_value = {"status": "available"}
        with patch.object(migrate_to_appwrite.time, "sleep") as sleep:
            with patch("sys.stdout", new_callable=io.StringIO):
                migrate_to_appwrite.wait_for_attribute(database, "events", "date")
        database.get_attribute.assert_called_once_with(
            migrate_to_appwrite.APPWRITE_DB_ID, "events", "date"
        )
        sleep.assert_not_called()

    def test_polling_retries_pending_attributes_and_transient_errors(self) -> None:
        database = Mock()
        database.get_attribute.side_effect = [
            RuntimeError("Not ready"),
            {"status": "processing"},
            {"status": "available"},
        ]
        with patch.object(migrate_to_appwrite.time, "sleep") as sleep:
            with patch("sys.stdout", new_callable=io.StringIO) as output:
                migrate_to_appwrite.wait_for_attribute(database, "events", "date")
        self.assertEqual(database.get_attribute.call_count, 3)
        self.assertEqual(sleep.call_count, 2)
        sleep.assert_called_with(2)
        self.assertNotIn("Timeout", output.getvalue())

    def test_polling_times_out_after_thirty_attempts(self) -> None:
        database = Mock()
        database.get_attribute.return_value = {"status": "processing"}
        with patch.object(migrate_to_appwrite.time, "sleep") as sleep:
            with patch("sys.stdout", new_callable=io.StringIO) as output:
                migrate_to_appwrite.wait_for_attribute(database, "events", "date")
        self.assertEqual(database.get_attribute.call_count, 30)
        self.assertEqual(sleep.call_count, 30)
        self.assertIn("Timeout", output.getvalue())


if __name__ == "__main__":
    unittest.main()
