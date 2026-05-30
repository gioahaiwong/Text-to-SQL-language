# app/nlp/sql_generator.py (versi tanpa db_path di __init__)
import re
from typing import Dict, List, Optional
from ..database.schema_reader import SchemaReader

class SQLGenerator:
    """Meng-generate SQL dari hasil parsing - UNIVERSAL"""
    
    def __init__(self, schema_reader: SchemaReader):
        self.schema = schema_reader
        self.tables = schema_reader.get_tables()
        self.main_table = self.tables[0] if self.tables else None
        
        # Cache skema kolom untuk setiap tabel
        self.table_columns = {}
        for table in self.tables:
            self.table_columns[table] = self.schema.get_columns(table)
    
    def generate(self, question: str) -> str:
        """Generate SQL dari pertanyaan"""
        from .query_parser import QueryParser
        
        # Parse pertanyaan
        parser = QueryParser(self.tables, self.table_columns)
        parsed = parser.parse(question)
        
        target_table = parsed.get("table", self.main_table)
        table_columns = self.table_columns.get(target_table, [])
        
        # ========== HANDLE BERDASARKAN TIPE ==========
        
        # Tipe SEARCH (pencarian nama)
        if parsed["type"] == "search":
            search_value = parsed.get("search_value", "")
            if search_value:
                return self._generate_search_query(target_table, table_columns, search_value)
        
        # Tipe SELECT ALL
        if parsed["type"] == "select_all":
            return f"SELECT * FROM {target_table};"
        
        # Tipe COUNT
        if parsed["type"] == "count":
            return f"SELECT COUNT(*) FROM {target_table};"
        
        # Tipe SELECT COLUMNS
        if parsed["type"] == "select_columns":
            columns = parsed.get("columns", [])
            if columns:
                return f"SELECT {', '.join(columns)} FROM {target_table};"
        
        # Tipe FILTER
        if parsed["type"] == "filter":
            condition = parsed.get("condition")
            if condition:
                col = condition.get("column")
                op = condition.get("operator", "=")
                val = condition.get("value")
                if val and not val.replace('.', '').isdigit():
                    val = f"'{val}'"
                return f"SELECT * FROM {target_table} WHERE {col} {op} {val};"
        
        # ========== FALLBACK ==========
        return f"SELECT * FROM {target_table};"
    
    def _generate_search_query(self, table: str, columns: List[str], search_value: str) -> str:
        """Generate query pencarian"""
        # Cari kolom yang cocok untuk pencarian
        search_columns = []
        
        for col in columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['name', 'nama', 'email', 'title', 'judul', 'username', 'user']):
                search_columns.append(col)
        
        # Jika tidak ada kolom nama, gunakan semua kolom
        if not search_columns:
            search_columns = columns
        
        # Buat query dengan LIKE untuk pencarian parsial
        if search_columns:
            conditions = " OR ".join([f"{col} LIKE '%{search_value}%'" for col in search_columns])
            return f"SELECT * FROM {table} WHERE {conditions};"
        
        return f"SELECT * FROM {table};"