import sqlite3
import os
from typing import List, Dict, Any
from .base import BaseProvider

class SqliteProvider(BaseProvider):
    def __init__(self, db_path: str = "classly.db"):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        # Allow creating new DB if writing, but usually we read from existing
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        if self.conn:
            self.conn.close()

    def list_tables(self) -> List[str]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [row[0] for row in cursor.fetchall() if row[0] not in ['sqlite_sequence', 'alembic_version', 'sys_jobs']]

    def read_table(self, table_name: str, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        try:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT ? OFFSET ?", (limit, offset))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            return []

    def write_table(self, table_name: str, data: List[Dict[str, Any]], pk_field: str = "id"):
        if not data:
            return

        cursor = self.conn.cursor()

        # Ensure table exists?
        # For migration, we assume schema exists via SQLAlchemy `create_all`.
        # But if we restore to empty DB, we rely on `Base.metadata.create_all` running before.

        keys = list(data[0].keys())
        columns = ", ".join(keys)
        placeholders = ", ".join(["?" for _ in keys])

        # Simple INSERT OR REPLACE
        sql = f"INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})"

        for row in data:
            values = [row.get(k) for k in keys]
            cursor.execute(sql, values)

        self.conn.commit()

    def count(self, table_name: str) -> int:
        cursor = self.conn.cursor()
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            return cursor.fetchone()[0]
        except sqlite3.OperationalError:
            return 0
