import sqlite3
import os
from typing import Dict, List, Tuple

class SchemaReader:
    """Membaca dan memproses skema database SQLite"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.schema = self._read_schema()

    def _read_schema(self) -> Dict[str, List[str]]:
        if not os.path.exists(self.db_path):
            return {}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
        
        schema = {}
        for table in tables:
            cursor.execute(f"PRAGMA table_info('{table}');")
            columns = [row[1] for row in cursor.fetchall()]
            schema[table] = columns
            
        conn.close()
        return schema

    def get_tables(self) -> List[str]:
        return list(self.schema.keys())

    def get_columns(self, table_name: str) -> List[str]:
        return self.schema.get(table_name, [])

    def get_db_contents(self, table_name: str, column_name: str, limit: int = 3) -> List[str]:
        """Ambil contoh isi data dari kolom tertentu untuk context model"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            query = f'SELECT DISTINCT "{column_name}" FROM "{table_name}" WHERE "{column_name}" IS NOT NULL LIMIT {limit}'
            samples = cursor.execute(query).fetchall()
            conn.close()
            return [str(s[0]) for s in samples]
        except:
            return []
