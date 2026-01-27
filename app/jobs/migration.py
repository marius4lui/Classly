import os
from typing import List
from app.providers.base import BaseProvider
from app.providers.sqlite import SqliteProvider
from app.providers.supabase import SupabaseProvider
from app.providers.appwrite import AppwriteProvider

# Order matters for Foreign Keys!
MIGRATION_ORDER = [
    "classes",
    "users",
    "subjects",
    "events",
    "event_topics",
    "event_links",
    "login_tokens",
    "integration_tokens",
    "audit_logs",
    "user_preferences",
    "grades",
    "timetable_settings",
    "timetable_slots",
    "user_timetable_selections",
    "oauth_clients",
    "oauth_authorization_codes",
    "device_tokens"
]

def get_provider(name: str, config: dict) -> BaseProvider:
    if name == "sqlite":
        return SqliteProvider(config.get("path", "classly.db"))
    elif name == "supabase":
        return SupabaseProvider(config.get("url"))
    elif name == "appwrite":
        return AppwriteProvider(
            endpoint=config.get("endpoint"),
            project_id=config.get("project_id"),
            api_key=config.get("api_key"),
            database_id=config.get("database_id", "classly_db")
        )
    raise ValueError(f"Unknown provider: {name}")

def run_migration(job_id, log, progress, source_config, target_config, **kwargs):
    log("Initializing migration...")

    source = get_provider(source_config["type"], source_config)
    target = get_provider(target_config["type"], target_config)

    try:
        source.connect()
        target.connect()

        # Calculate total work
        total_rows = 0
        tables_to_migrate = MIGRATION_ORDER

        # Verify tables exist in source
        source_tables = source.list_tables()
        # Filter MIGRATION_ORDER to only those present in source
        tables_to_migrate = [t for t in MIGRATION_ORDER if t in source_tables]

        log(f"Found {len(tables_to_migrate)} tables to migrate.")

        for table in tables_to_migrate:
            c = source.count(table)
            total_rows += c

        current_row = 0
        log(f"Total rows to migrate: {total_rows}")

        for table in tables_to_migrate:
            log(f"Migrating table: {table}")

            table_count = source.count(table)
            offset = 0
            limit = 1000

            while offset < table_count:
                chunk = source.read_table(table, limit, offset)
                if not chunk:
                    break

                target.write_table(table, chunk)

                offset += len(chunk)
                current_row += len(chunk)

                progress(current_row, total_rows, f"Migrating {table} ({offset}/{table_count})")

            log(f"Table {table} completed.")

        log("Migration finished successfully.")

    except Exception as e:
        log(f"Migration Failed: {str(e)}")
        raise e
    finally:
        source.close()
        target.close()
