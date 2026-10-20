"""Guard the schema during the SQLAlchemy 2 typed-mapping migration.

The fixture was captured from origin/main at
69b82d81221a406df9915445be990bb7c68a526a, before changing the mappings.
In particular, a Python-side default does not make a legacy column NOT NULL.
"""

import json
from pathlib import Path
import unittest
from typing import get_args, get_type_hints

from sqlalchemy import ColumnDefault, create_engine, insert, null
from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy.orm import Session, configure_mappers
from sqlalchemy.schema import CreateIndex, CreateTable, DefaultGenerator

from app import models
from app.database import Base


def default_description(default: DefaultGenerator | None) -> object:
    if default is None:
        return None
    assert isinstance(default, ColumnDefault)
    if default.is_callable:
        return f"{default.arg.__module__}.{default.arg.__qualname__}"
    return default.arg


def schema_snapshot() -> dict[str, object]:
    """Capture physical schema, Python defaults and effective ORM relationships."""
    configure_mappers()
    tables = {}
    for table in Base.metadata.sorted_tables:
        tables[table.name] = {
            "sqlite": str(CreateTable(table).compile(dialect=sqlite.dialect())),
            "postgresql": str(CreateTable(table).compile(dialect=postgresql.dialect())),
            "indexes": sorted(
                str(CreateIndex(index).compile(dialect=sqlite.dialect()))
                for index in table.indexes
            ),
            "defaults": {
                column.name: {
                    "default": default_description(column.default),
                    "onupdate": default_description(column.onupdate),
                }
                for column in table.columns
                if column.default is not None or column.onupdate is not None
            },
            "enums": {
                column.name: {
                    "name": column.type.name,
                    "values": column.type.enums,
                    "native_enum": column.type.native_enum,
                    "create_constraint": column.type.create_constraint,
                    "validate_strings": column.type.validate_strings,
                }
                for column in table.columns
                if isinstance(column.type, models.Enum)
            },
        }
    relationships = {}
    for mapper in Base.registry.mappers:
        relationships[mapper.class_.__name__] = {
            relationship.key: {
                "target": relationship.mapper.class_.__name__,
                "direction": relationship.direction.name,
                "uselist": relationship.uselist,
                "back_populates": relationship.back_populates,
                "cascade": sorted(relationship.cascade),
                "local_remote_pairs": sorted(
                    [str(local), str(remote)]
                    for local, remote in relationship.local_remote_pairs or ()
                ),
                "primaryjoin": str(relationship.primaryjoin),
                "viewonly": relationship.viewonly,
                "passive_deletes": relationship.passive_deletes,
                "passive_updates": relationship.passive_updates,
                "single_parent": relationship.single_parent,
                "innerjoin": relationship.innerjoin,
                "post_update": relationship.post_update,
            }
            for relationship in mapper.relationships
        }
    return {"tables": tables, "relationships": relationships}


class ModelSchemaTests(unittest.TestCase):
    def test_typed_models_preserve_legacy_schema_and_relationships(self) -> None:
        snapshot_path = Path(__file__).parent / "fixtures" / "model_schema.json"
        expected = json.loads(snapshot_path.read_text(encoding="utf-8"))
        self.assertEqual(schema_snapshot(), expected)

    def test_column_annotations_reflect_actual_nullability(self) -> None:
        for mapper in Base.registry.mappers:
            hints = get_type_hints(mapper.class_)
            for column in mapper.columns:
                with self.subTest(model=mapper.class_.__name__, column=column.key):
                    mapped_type = get_args(hints[column.key])[0]
                    allows_none = type(None) in get_args(mapped_type)
                    self.assertEqual(allows_none, column.nullable)

    def test_nullable_defaults_remain_nullable_when_loading_existing_rows(self) -> None:
        engine = create_engine("sqlite:///:memory:")
        try:
            Base.metadata.create_all(engine)
            with Session(engine) as session:
                session.execute(
                    insert(models.Class).values(
                        id="legacy-class",
                        name="Legacy Class",
                        join_token="legacy-join-token",
                        join_enabled=null(),
                        created_at=null(),
                    )
                )
                session.execute(
                    insert(models.User).values(
                        id="legacy-user",
                        name="Legacy User",
                        class_id="legacy-class",
                        role=null(),
                        language=null(),
                        is_registered=null(),
                        created_at=null(),
                    )
                )
                session.commit()
                user = session.get(models.User, "legacy-user")
                self.assertIsNotNone(user)
                assert user is not None
                self.assertIsNone(user.role)
                self.assertIsNone(user.language)
                self.assertIsNone(user.is_registered)
                self.assertIsNone(user.created_at)
                self.assertIsNone(user.clazz.join_enabled)
                self.assertIsNone(user.clazz.created_at)
        finally:
            engine.dispose()


if __name__ == "__main__":
    unittest.main()
