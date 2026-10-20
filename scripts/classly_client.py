#!/usr/bin/env python3
"""
Classly API Client Script
=========================
Ein optimiertes Python-Script für die Integration mit der Classly API.
Lädt den API-Key aus der Umgebungsvariable CLASSLY_API_KEY.

Installation:
    pip install requests python-dotenv

Verwendung:
    export CLASSLY_API_KEY="cl_live_xxx..."
    python classly_client.py events list
    python classly_client.py events create --type HA --date 2026-02-15 --subject Mathe --title "S. 42"

GitHub: https://github.com/marius4lui/Classly
Docs: https://docs.classly.site/development/api-integration
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Optional, Dict, Any, List

try:
    import requests
except ImportError:
    print("❌ requests nicht installiert. Bitte ausführen: pip install requests")
    sys.exit(1)

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # python-dotenv ist optional

# =============================================================================
# KONFIGURATION
# =============================================================================

CLASSLY_BASE_URL = os.getenv("CLASSLY_BASE_URL", "https://classly.site")
CLASSLY_API_KEY = os.getenv("CLASSLY_API_KEY", "")
API_VERSION = "v1"

# =============================================================================
# API CLIENT
# =============================================================================


class ClasslyClient:
    """
    Classly API Client für die Interaktion mit der Classly REST API.

    Beispiel:
        client = ClasslyClient(api_key="cl_live_xxx...")
        events = client.get_events()
        client.create_event(type="HA", date="2026-02-15", title="Aufgabe")
    """

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        """
        Initialisiert den Classly Client.

        Args:
            api_key: Classly API-Key (oder aus CLASSLY_API_KEY Env-Variable)
            base_url: Basis-URL (Standard: https://classly.site)
        """
        self.api_key = api_key or CLASSLY_API_KEY
        self.base_url = (base_url or CLASSLY_BASE_URL).rstrip("/")
        self.api_url = f"{self.base_url}/api/{API_VERSION}"

        if not self.api_key:
            raise ValueError(
                "❌ Kein API-Key gefunden!\n"
                "Setze die Umgebungsvariable CLASSLY_API_KEY oder übergebe api_key."
            )

    @property
    def headers(self) -> Dict[str, str]:
        """Gibt die HTTP-Headers für API-Requests zurück."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ClasslyClient/1.0",
        }

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Führt einen HTTP-Request zur API aus.

        Args:
            method: HTTP-Methode (GET, POST, PUT, DELETE)
            endpoint: API-Endpoint (z.B. "/events")
            **kwargs: Weitere requests-Parameter

        Returns:
            JSON-Response als Dictionary

        Raises:
            requests.HTTPError: Bei HTTP-Fehlern
        """
        url = f"{self.api_url}{endpoint}"

        response = requests.request(
            method=method, url=url, headers=self.headers, **kwargs
        )

        if not response.ok:
            try:
                error = response.json()
                detail = error.get("detail", response.text)
            except:
                detail = response.text
            raise requests.HTTPError(
                f"API-Fehler {response.status_code}: {detail}", response=response
            )

        if response.text:
            return response.json()
        return {"success": True}

    # =========================================================================
    # EVENTS
    # =========================================================================

    def get_events(
        self, limit: int = 200, updated_since: str | None = None
    ) -> List[Dict]:
        """
        Ruft alle Events der Klasse ab.

        Args:
            limit: Maximale Anzahl Events (Standard: 200, Max: 500)
            updated_since: ISO-Datum für inkrementelle Sync

        Returns:
            Liste von Event-Dictionaries
        """
        params = {"limit": limit}
        if updated_since:
            params["updated_since"] = updated_since

        result = self._request("GET", "/events", params=params)
        return result.get("events", [])

    def get_event(self, event_id: str) -> Dict:
        """Ruft ein einzelnes Event ab."""
        return self._request("GET", f"/events/{event_id}")

    def create_event(
        self, type: str, date: str, title: str, subject: str | None = None
    ) -> Dict:
        """
        Erstellt ein neues Event.

        Args:
            type: Event-Typ (KA, TEST, HA, INFO)
            date: Datum im ISO-Format (YYYY-MM-DD oder YYYY-MM-DDTHH:MM:SS)
            title: Titel/Beschreibung des Events
            subject: Fächername (optional)

        Returns:
            Erstelltes Event-Dictionary
        """
        # Datum normalisieren
        if "T" not in date:
            date = f"{date}T00:00:00"

        payload = {"type": type.upper(), "date": date, "title": title}
        if subject:
            payload["subject"] = subject

        result = self._request("POST", "/events", json=payload)
        return result.get("event", result)

    def update_event(self, event_id: str, **updates) -> Dict:
        """
        Aktualisiert ein Event.

        Args:
            event_id: ID des Events
            **updates: Zu aktualisierende Felder (type, date, title, subject)

        Returns:
            Aktualisiertes Event-Dictionary
        """
        return self._request("PUT", f"/events/{event_id}", json=updates)

    def delete_event(self, event_id: str) -> bool:
        """
        Löscht ein Event.

        Args:
            event_id: ID des Events

        Returns:
            True bei Erfolg
        """
        self._request("DELETE", f"/events/{event_id}")
        return True

    # =========================================================================
    # KLASSEN
    # =========================================================================

    def get_class_info(self) -> Dict:
        """Ruft Informationen über die Klasse ab."""
        return self._request("GET", "/classes")

    # =========================================================================
    # BENUTZER
    # =========================================================================

    def get_users(self) -> List[Dict]:
        """Ruft alle Benutzer der Klasse ab."""
        result = self._request("GET", "/users")
        return result.get("users", [])

    def get_current_user(self) -> Dict:
        """Ruft den aktuellen Benutzer ab."""
        return self._request("GET", "/users/me")

    # =========================================================================
    # FÄCHER
    # =========================================================================

    def get_subjects(self) -> List[Dict]:
        """Ruft alle Fächer der Klasse ab."""
        result = self._request("GET", "/subjects")
        return result.get("subjects", [])

    # =========================================================================
    # STUNDENPLAN
    # =========================================================================

    def get_timetable(self, weekday: int | None = None) -> Dict:
        """
        Ruft den Stundenplan ab.

        Args:
            weekday: Wochentag-Filter (0=Montag, 4=Freitag)

        Returns:
            Stundenplan-Dictionary
        """
        params = {}
        if weekday is not None:
            params["weekday"] = weekday

        return self._request("GET", "/timetable", params=params)

    def get_timetable_settings(self) -> Dict:
        """Ruft die Stundenplan-Einstellungen ab."""
        return self._request("GET", "/timetable/settings")


# =============================================================================
# CLI INTERFACE
# =============================================================================


def format_event(event: Dict) -> str:
    """Formatiert ein Event für die Ausgabe."""
    type_emoji = {"KA": "🔴", "TEST": "🟠", "HA": "🟢", "INFO": "🔵"}
    emoji = type_emoji.get(event.get("type", ""), "⚪")
    date = event.get("date", "")[:10]
    title = event.get("title", "")
    subject = event.get("subject", "")

    if subject:
        return f"{emoji} [{date}] {subject}: {title}"
    return f"{emoji} [{date}] {title}"


def cmd_events_list(client: ClasslyClient, args):
    """Listet alle Events auf."""
    events = client.get_events(limit=args.limit)

    if not events:
        print("📭 Keine Events gefunden.")
        return

    print(f"📅 {len(events)} Events:\n")
    for event in events:
        print(format_event(event))


def cmd_events_create(client: ClasslyClient, args):
    """Erstellt ein neues Event."""
    event = client.create_event(
        type=args.type, date=args.date, title=args.title, subject=args.subject
    )
    print(f"✅ Event erstellt: {format_event(event)}")


def cmd_events_delete(client: ClasslyClient, args):
    """Löscht ein Event."""
    client.delete_event(args.id)
    print(f"🗑️ Event {args.id} gelöscht.")


def cmd_class_info(client: ClasslyClient, args):
    """Zeigt Klassen-Info."""
    info = client.get_class_info()
    print(f"🏫 Klasse: {info.get('name', 'N/A')}")
    print(f"   ID: {info.get('id', 'N/A')}")
    print(f"   Mitglieder: {info.get('member_count', 'N/A')}")


def cmd_users_list(client: ClasslyClient, args):
    """Listet alle Benutzer auf."""
    users = client.get_users()

    print(f"👥 {len(users)} Benutzer:\n")
    for user in users:
        role = "👑" if user.get("role") == "admin" else "👤"
        print(f"  {role} {user.get('name', 'N/A')}")


def cmd_subjects_list(client: ClasslyClient, args):
    """Listet alle Fächer auf."""
    subjects = client.get_subjects()

    print(f"📚 {len(subjects)} Fächer:\n")
    for subject in subjects:
        name = subject.get("name", "N/A")
        short = subject.get("short_name", "")
        print(f"  • {name}" + (f" ({short})" if short else ""))


def cmd_timetable(client: ClasslyClient, args):
    """Zeigt den Stundenplan."""
    timetable = client.get_timetable()

    print("📋 Stundenplan:\n")
    for day, slots in timetable.get("timetable", {}).items():
        print(f"  {day}:")
        for slot in slots:
            print(
                f"    {slot.get('slot_number', '?')}. {slot.get('subject_name', 'N/A')}"
            )


def main():
    parser = argparse.ArgumentParser(
        description="Classly API Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python classly_client.py events list
  python classly_client.py events create --type HA --date 2026-02-15 --title "Aufgabe"
  python classly_client.py class info
  python classly_client.py users list
  python classly_client.py subjects list

Umgebungsvariablen:
  CLASSLY_API_KEY     API-Key (erforderlich)
  CLASSLY_BASE_URL    Server-URL (Standard: https://classly.site)
""",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Events
    events_parser = subparsers.add_parser("events", help="Event-Verwaltung")
    events_sub = events_parser.add_subparsers(dest="action", required=True)

    # events list
    list_parser = events_sub.add_parser("list", help="Events auflisten")
    list_parser.add_argument("--limit", type=int, default=50, help="Max. Anzahl")

    # events create
    create_parser = events_sub.add_parser("create", help="Event erstellen")
    create_parser.add_argument(
        "--type", required=True, choices=["KA", "TEST", "HA", "INFO"]
    )
    create_parser.add_argument("--date", required=True, help="Datum (YYYY-MM-DD)")
    create_parser.add_argument("--title", required=True, help="Titel")
    create_parser.add_argument("--subject", help="Fach (optional)")

    # events delete
    delete_parser = events_sub.add_parser("delete", help="Event löschen")
    delete_parser.add_argument("--id", required=True, help="Event-ID")

    # Class
    class_parser = subparsers.add_parser("class", help="Klassen-Info")
    class_sub = class_parser.add_subparsers(dest="action", required=True)
    class_sub.add_parser("info", help="Klassen-Informationen")

    # Users
    users_parser = subparsers.add_parser("users", help="Benutzer")
    users_sub = users_parser.add_subparsers(dest="action", required=True)
    users_sub.add_parser("list", help="Benutzer auflisten")

    # Subjects
    subjects_parser = subparsers.add_parser("subjects", help="Fächer")
    subjects_sub = subjects_parser.add_subparsers(dest="action", required=True)
    subjects_sub.add_parser("list", help="Fächer auflisten")

    # Timetable
    timetable_parser = subparsers.add_parser("timetable", help="Stundenplan")
    timetable_sub = timetable_parser.add_subparsers(dest="action", required=True)
    timetable_sub.add_parser("show", help="Stundenplan anzeigen")

    args = parser.parse_args()

    try:
        client = ClasslyClient()

        if args.command == "events":
            if args.action == "list":
                cmd_events_list(client, args)
            elif args.action == "create":
                cmd_events_create(client, args)
            elif args.action == "delete":
                cmd_events_delete(client, args)
        elif args.command == "class":
            cmd_class_info(client, args)
        elif args.command == "users":
            cmd_users_list(client, args)
        elif args.command == "subjects":
            cmd_subjects_list(client, args)
        elif args.command == "timetable":
            cmd_timetable(client, args)

    except ValueError as e:
        print(str(e))
        sys.exit(1)
    except requests.HTTPError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fehler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
