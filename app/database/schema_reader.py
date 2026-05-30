import sqlite3
import os
from typing import Dict, List, Tuple

class SchemaReader:
    """Membaca dan memproses skema database SQLite"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.tables = {}
        self._load_schema()
    
    def _load_schema(self):
        """Load semua tabel dan kolom dari database"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database tidak ditemukan: {self.db_path}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Ambil semua tabel
        tables = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()
        
        for table in tables:
            table_name = table[0]
            columns = cursor.execute(
                f"PRAGMA table_info('{table_name}');"
            ).fetchall()
            
            self.tables[table_name] = [
                {"name": col[1], "type": col[2], "pk": col[5] == 1}
                for col in columns
            ]
        
        conn.close()
    
    def get_schema_string(self) -> str:
        """Mengembalikan skema sebagai string untuk ditampilkan"""
        result = []
        for table_name, columns in self.tables.items():
            result.append(f"Table: {table_name}")
            for col in columns:
                pk_marker = " (PRIMARY KEY)" if col["pk"] else ""
                result.append(f"  - {col['name']} ({col['type']}){pk_marker}")
        return "\n".join(result)
    
    def get_tables(self) -> List[str]:
        """Mengembalikan daftar nama tabel"""
        return list(self.tables.keys())
    
    def get_columns(self, table_name: str) -> List[str]:
        """Mengembalikan daftar kolom untuk tabel tertentu"""
        if table_name in self.tables:
            return [col["name"] for col in self.tables[table_name]]
        return []
    
    def get_primary_key(self, table_name: str) -> str:
        """Mengembalikan nama kolom primary key"""
        if table_name in self.tables:
            for col in self.tables[table_name]:
                if col["pk"]:
                    return col["name"]
        return "id"  # default