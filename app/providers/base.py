from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseProvider(ABC):
    @abstractmethod
    def connect(self):
        """Establishes connection to the provider"""
        pass

    @abstractmethod
    def close(self):
        """Closes the connection"""
        pass

    @abstractmethod
    def list_tables(self) -> List[str]:
        """Returns a list of table names"""
        pass

    @abstractmethod
    def read_table(self, table_name: str, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        """Reads rows from a table"""
        pass

    @abstractmethod
    def write_table(self, table_name: str, data: List[Dict[str, Any]], pk_field: str = "id"):
        """Writes rows to a table (Upsert logic preferred)"""
        pass

    @abstractmethod
    def count(self, table_name: str) -> int:
        """Counts rows in a table"""
        pass
