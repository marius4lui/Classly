import os
from typing import List, Dict, Any
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
from .base import BaseProvider

class AppwriteProvider(BaseProvider):
    def __init__(self, endpoint: str, project_id: str, api_key: str, database_id: str = "classly_db"):
        self.endpoint = endpoint
        self.project_id = project_id
        self.api_key = api_key
        self.database_id = database_id
        self.client = None
        self.db_service = None

    def connect(self):
        self.client = Client()
        self.client.set_endpoint(self.endpoint)
        self.client.set_project(self.project_id)
        self.client.set_key(self.api_key)
        self.db_service = Databases(self.client)

    def close(self):
        pass

    def list_tables(self) -> List[str]:
        try:
            collections = self.db_service.list_collections(self.database_id, limit=100)
            return [c['name'] for c in collections['collections']]
        except:
            return []

    def read_table(self, table_name: str, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        try:
            docs = self.db_service.list_documents(
                self.database_id,
                table_name,
                [Query.limit(limit), Query.offset(offset)]
            )
            return [self._clean_doc(d) for d in docs['documents']]
        except Exception as e:
            # Collection might not exist
            return []

    def write_table(self, table_name: str, data: List[Dict[str, Any]], pk_field: str = "id"):
        for row in data:
            doc_id = row.get(pk_field)
            if not doc_id:
                continue

            # Sanitize ID for Appwrite (only chars, numbers, .- max 36)
            safe_id = str(doc_id).replace("-", "").replace("_", "")[:36]

            try:
                self.db_service.create_document(self.database_id, table_name, safe_id, row)
            except Exception as e:
                # Assuming 409 is conflict, try update
                 try:
                    self.db_service.update_document(self.database_id, table_name, safe_id, row)
                 except:
                     pass

    def count(self, table_name: str) -> int:
        try:
             docs = self.db_service.list_documents(self.database_id, table_name, [Query.limit(1)])
             return docs['total']
        except:
            return 0

    def _clean_doc(self, doc):
        excludes = ['$id', '$createdAt', '$updatedAt', '$permissions', '$databaseId', '$collectionId']
        return {k: v for k, v in doc.items() if k not in excludes}
