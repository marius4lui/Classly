import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from typing import List, Dict, Any
from .base import BaseProvider

class SupabaseProvider(BaseProvider):
    def __init__(self, connection_url: str):
        self.url = connection_url
        self.engine = None
        self.conn = None

    def connect(self):
        self.engine = create_engine(self.url)
        self.conn = self.engine.connect()

    def close(self):
        if self.conn:
            self.conn.close()
        if self.engine:
            self.engine.dispose()

    def list_tables(self) -> List[str]:
        # Postgres specific query
        query = text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """)
        result = self.conn.execute(query)
        return [row[0] for row in result]

    def read_table(self, table_name: str, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        query = text(f"SELECT * FROM {table_name} LIMIT :limit OFFSET :offset")
        result = self.conn.execute(query, {"limit": limit, "offset": offset})
        # SQLAlchemy 1.4+ RowProxy mapping
        return [dict(row._mapping) for row in result]

    def write_table(self, table_name: str, data: List[Dict[str, Any]], pk_field: str = "id"):
        if not data:
            return

        keys = list(data[0].keys())

        # Construct INSERT statement
        cols = ", ".join(keys)
        vals = ", ".join([f":{k}" for k in keys])

        # ON CONFLICT update logic
        # Note: This assumes the table exists and pk_field is actually the PK constraint
        updates = ", ".join([f"{k} = EXCLUDED.{k}" for k in keys if k != pk_field])

        if updates:
            sql = f"""
                INSERT INTO {table_name} ({cols}) VALUES ({vals})
                ON CONFLICT ({pk_field}) DO UPDATE SET {updates}
            """
        else:
            # Case where only PK exists (rare) or no update needed
             sql = f"""
                INSERT INTO {table_name} ({cols}) VALUES ({vals})
                ON CONFLICT ({pk_field}) DO NOTHING
            """

        self.conn.execute(text(sql), data)
        self.conn.commit()

    def count(self, table_name: str) -> int:
        query = text(f"SELECT COUNT(*) FROM {table_name}")
        return self.conn.execute(query).scalar()
