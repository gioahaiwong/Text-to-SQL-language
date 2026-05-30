# app/nlp/query_parser.py
import re
from typing import Dict, List, Optional

class QueryParser:
    """Mem-parsing pertanyaan natural language ke SQL - UNIVERSAL"""
    
    def __init__(self, tables: List[str], columns: Dict[str, List[str]]):
        """
        tables: daftar nama tabel
        columns: dictionary {nama_tabel: [daftar_kolom]}
        """
        self.tables = tables
        self.columns = columns
        self.main_table = tables[0] if tables else None
    
    def parse(self, question: str) -> Dict:
        """Parse pertanyaan dan kembalikan komponen SQL"""
        question = question.lower().strip()
        
        # Default result
        result = {
            "type": "select",
            "table": self.main_table,
            "columns": ["*"],
            "condition": None,
            "aggregate": None,
            "search_value": None
        }
        
        # ========== DETEKSI TABEL ==========
        target_table = self.main_table
        for table in self.tables:
            if table.lower() in question:
                target_table = table
                break
        
        result["table"] = target_table
        table_columns = self.columns.get(target_table, [])
        
        # ========== POLA SELECT KOLOM TERTENTU ==========
        
        # Pola 1: "tampilkan [nama_kolom]"
        # Contoh: "tampilkan id", "tampilkan email", "tampilkan umur"
        match = re.search(r'tampilkan (\w+)', question)
        if match:
            potential_column = match.group(1)
            if potential_column in table_columns:
                return {
                    "type": "select_columns",
                    "table": target_table,
                    "columns": [potential_column]
                }
        
        # Pola 2: "tampilkan [kolom1] dan [kolom2]"
        # Contoh: "tampilkan id dan nama"
        match = re.search(r'tampilkan (\w+) dan (\w+)', question)
        if match:
            col1, col2 = match.group(1), match.group(2)
            cols = []
            for col in [col1, col2]:
                if col in table_columns:
                    cols.append(col)
            if cols:
                return {
                    "type": "select_columns",
                    "table": target_table,
                    "columns": cols
                }
        
        # Pola 3: "tampilkan [kolom1], [kolom2], [kolom3]"
        # Contoh: "tampilkan id, nama, email"
        match = re.search(r'tampilkan ([\w\s,]+)', question)
        if match:
            col_names = [c.strip() for c in match.group(1).split(',')]
            existing_cols = [c for c in col_names if c in table_columns]
            if existing_cols:
                return {
                    "type": "select_columns",
                    "table": target_table,
                    "columns": existing_cols
                }
        
        # Pola 4: "[kolom] saja"
        # Contoh: "id saja", "email saja", "task saja"
        match = re.search(r'(\w+) saja', question)
        if match:
            potential_column = match.group(1)
            if potential_column in table_columns:
                return {
                    "type": "select_columns",
                    "table": target_table,
                    "columns": [potential_column]
                }
        
        # Pola 5: "lihat [kolom]"
        # Contoh: "lihat id", "lihat nama"
        match = re.search(r'lihat (\w+)', question)
        if match:
            potential_column = match.group(1)
            if potential_column in table_columns:
                return {
                    "type": "select_columns",
                    "table": target_table,
                    "columns": [potential_column]
                }
        
        # Pola 6: "daftar [kolom]"
        # Contoh: "daftar nama", "daftar email"
        match = re.search(r'daftar (\w+)', question)
        if match:
            potential_column = match.group(1)
            if potential_column in table_columns:
                return {
                    "type": "select_columns",
                    "table": target_table,
                    "columns": [potential_column]
                }
        
        # Pola 7: "munculkan [kolom]"
        match = re.search(r'munculkan (\w+)', question)
        if match:
            potential_column = match.group(1)
            if potential_column in table_columns:
                return {
                    "type": "select_columns",
                    "table": target_table,
                    "columns": [potential_column]
                }
        
        # ========== POLA SELECT SEMUA DATA ==========
        
        if re.search(r'tampilkan semua (?:data )?' + target_table, question) or \
           re.search(r'semua (?:data )?' + target_table, question) or \
           question in ['semua', 'all', 'tampilkan semua']:
            result["type"] = "select_all"
            return result
        
        # ========== POLA HITUNG JUMLAH ==========
        
        if re.search(r'(?:hitung|jumlah|berapa banyak|count) (?:data )?' + target_table, question):
            result["type"] = "count"
            return result
        
        # ========== POLA PENCARIAN (BERDASARKAN NAMA) ==========
        
        # Pola: "cari user yang bernama Giovan"
        patterns = [
            r'(?:cari|tampilkan|ambil) (?:data )?(?:yang)? ?(?:bernama|nama|namanya|dengan nama) ["\']?([\w\s]+)["\']?',
            r'tampilkan data ([\w\s]+)',
            r'cari ([\w\s]+)',
            r'(?:nama|name) (?:saya|kamu)? ?(?:adalah|:)? ?["\']?([\w\s]+)["\']?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, question)
            if match:
                search_value = match.group(1).strip()
                result["type"] = "search"
                result["search_value"] = search_value
                return result
        
        # ========== POLA FILTER SEDERHANA ==========
        
        # "users dengan role admin"
        match = re.search(r'(?:dengan|where) (\w+) (\w+)', question)
        if match and len(match.groups()) >= 2:
            col = match.group(1)
            val = match.group(2)
            if col in table_columns:
                result["type"] = "filter"
                result["condition"] = {"column": col, "operator": "=", "value": val}
                return result
        
        # "tampilkan [kolom] dari [tabel] dimana [kolom] = [nilai]"
        match = re.search(r'tampilkan (\w+) dari (\w+) (?:dimana|where) (\w+) = (\w+)', question)
        if match:
            col_display = match.group(1)
            table_name = match.group(2)
            col_condition = match.group(3)
            val_condition = match.group(4)
            return {
                "type": "select_condition",
                "table": table_name,
                "columns": [col_display],
                "condition": {
                    "column": col_condition,
                    "operator": "=",
                    "value": val_condition
                }
            }
        
        # ========== DETEKSI JIKA SUDAH SQL ==========
        
        if question.upper().strip().startswith(('SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE')):
            result["type"] = "raw_sql"
            result["raw_sql"] = question
            return result
        
        # ========== DEFAULT ==========
        return result