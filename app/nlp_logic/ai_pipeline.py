import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, T5Tokenizer, BitsAndBytesConfig
import time
import os
import sys
import json
import sqlite3
import numpy as np
from typing import List, Dict

# Path setup to localized utilities
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR)

from .utils.bridge_content_encoder import get_database_matches
from .classifier_model import MyClassifier
from .natsql2sql.natsql_parser import create_sql_from_natSQL
from .natsql2sql.natsql2sql import Args

class RESDSQLPipelineV2:
    def __init__(self, schema_reader=None, model_path="text2natsql-t5-large/checkpoint-21216", classifier_path="models/classifier"):
        self.schema = schema_reader
        self.model_path = model_path
        self.classifier_path = classifier_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # 1. Load Classifier
        print(f"Loading RESDSQL Classifier from {classifier_path}...")
        self.classifier_tokenizer = AutoTokenizer.from_pretrained(classifier_path)
        self.classifier_model = MyClassifier(
            model_name_or_path=classifier_path,
            vocab_size=len(self.classifier_tokenizer),
            mode="eval"
        )
        
        weights_file = os.path.join(classifier_path, "dense_classifier.pt")
        if os.path.exists(weights_file):
            state_dict = torch.load(weights_file, map_location=self.device)
            if "plm_encoder.embeddings.position_ids" in state_dict:
                del state_dict["plm_encoder.embeddings.position_ids"]
            self.classifier_model.load_state_dict(state_dict)
        self.classifier_model.to(self.device)
        self.classifier_model.eval()
        
        # 2. Load T5 Generator
        print(f"Loading T5 Generator from {model_path}...")
        self.gen_tokenizer = T5Tokenizer.from_pretrained(model_path)
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )
        self.gen_model = AutoModelForSeq2SeqLM.from_pretrained(
            model_path,
            device_map="auto",
            quantization_config=quantization_config,
            torch_dtype=torch.float16
        )
        self.gen_model.eval()
        
        # Load tables metadata
        self.tables_metadata = {}
        try:
            with open("data/spider/tables.json", "r") as f:
                data = json.load(f)
                for db in data:
                    self.tables_metadata[db["db_id"]] = db
        except:
            print("Warning: data/spider/tables.json not found.")
            
        # Load tables for NatSQL bridge
        self.natsql_tables = {}
        try:
            # Consistent path for localized tables_for_natsql.json
            natsql_tables_path = os.path.join(CURRENT_DIR, "NatSQLv1_6", "tables_for_natsql.json")
            if os.path.exists(natsql_tables_path):
                print(f"Loading NatSQL Bridge Tables from {natsql_tables_path}...")
                with open(natsql_tables_path, "r") as f:
                    data = json.load(f)
                    for db in data:
                        self.natsql_tables[db["db_id"]] = db
            else:
                print(f"Warning: {natsql_tables_path} not found.")
        except Exception as e:
            print(f"Error loading NatSQL bridge tables: {e}")

    def _get_schema_items(self, db_id):
        db = self.tables_metadata.get(db_id)
        if not db: return [], [], []
        # Return original casing (important for high performance)
        return db["table_names_original"], db["column_names_original"], db["foreign_keys"]

    def _prepare_classifier_input(self, question, table_names, column_names):
        input_tokens = [question]
        table_name_ids, column_info_ids = [], []
        column_number_in_each_table = []
        for table_id, table_name in enumerate(table_names):
            input_tokens.append("|")
            input_tokens.append(table_name.lower())
            table_name_ids.append(len(input_tokens) - 1)
            input_tokens.append(":")
            count = 0
            for t_idx, col_name in column_names:
                if t_idx == table_id:
                    input_tokens.append(col_name.lower())
                    column_info_ids.append(len(input_tokens) - 1)
                    input_tokens.append(",")
                    count += 1
            input_tokens = input_tokens[:-1]
            column_number_in_each_table.append(count)
        return input_tokens, table_name_ids, column_info_ids, column_number_in_each_table

    def _rank_schema(self, question, db_id):
        table_names, column_names, _ = self._get_schema_items(db_id)
        # Using Send All strategy as baseline for 80% accuracy
        ranked_schema = []
        for t_idx, t_name in enumerate(table_names):
            t_cols = [c[1] for c in column_names if c[0] == t_idx]
            ranked_schema.append({
                "table_name_original": t_name,
                "column_names_original": t_cols,
                "db_contents": [get_database_matches(question, t_name, c, self.schema.db_path) for c in t_cols]
            })
        return ranked_schema

    def _serialize(self, question, ranked_schema, db_id):
        table_names, _, fks = self._get_schema_items(db_id)
        schema_sequence = ""
        used_tables = [s["table_name_original"] for s in ranked_schema]
        for table in ranked_schema:
            t_name = table["table_name_original"]
            schema_sequence += " | " + t_name + " : "
            col_infos = []
            for c_idx, c_name in enumerate(table["column_names_original"]):
                contents = table["db_contents"][c_idx]
                if contents:
                    val_str = " , ".join(contents)
                    col_info = f"{t_name}.{c_name} ( {val_str} )"
                else:
                    col_info = f"{t_name}.{c_name}"
                col_infos.append(col_info)
            schema_sequence += " , ".join(col_infos)
        for source_idx, target_idx in fks:
            try:
                s_t = table_names[self.tables_metadata[db_id]["column_names_original"][source_idx][0]]
                t_t = table_names[self.tables_metadata[db_id]["column_names_original"][target_idx][0]]
                if s_t in used_tables and t_t in used_tables:
                    s_c = self.tables_metadata[db_id]["column_names_original"][source_idx][1]
                    t_c = self.tables_metadata[db_id]["column_names_original"][target_idx][1]
                    schema_sequence += f" | {s_t}.{s_c} = {t_t}.{t_c}"
            except: continue
        return (question + schema_sequence).replace("  ", " ")

    def _convert_natsql_to_sql(self, natsql, db_id):
        if db_id not in self.natsql_tables:
            return natsql
        try:
            natsql2sql_args = Args()
            natsql2sql_args.not_infer_group = True
            sql, _, _ = create_sql_from_natSQL(
                natsql, 
                db_id, 
                self.schema.db_path, 
                self.natsql_tables[db_id], 
                None, 
                args=natsql2sql_args
            )
            return sql
        except:
            return natsql

    def generate(self, question: str) -> str:
        db_id = os.path.basename(self.schema.db_path).replace(".sqlite", "")
        ranked_schema = self._rank_schema(question, db_id)
        input_str = self._serialize(question, ranked_schema, db_id)
        
        # Beam Search (8 candidates)
        inputs = self.gen_tokenizer(input_str, return_tensors="pt").to(self.device)
        outputs = self.gen_model.generate(**inputs, max_length=512, num_beams=8, num_return_sequences=8)
        
        # Execution-guided Decoding
        best_sql = None
        conn = sqlite3.connect(self.schema.db_path)
        cursor = conn.cursor()
        
        for i in range(len(outputs)):
            pred_seq = self.gen_tokenizer.decode(outputs[i], skip_special_tokens=True)
            pred_natsql = pred_seq.split("|")[-1].strip() if " | " in pred_seq else pred_seq.strip()

            # Convert NatSQL -> SQL
            pred_sql = self._convert_natsql_to_sql(pred_natsql, db_id)
            if pred_sql:
                pred_sql = pred_sql.replace("='", "= '").replace("!=", " !=").replace(",", " ,")
                try:
                    cursor.execute(pred_sql)
                    best_sql = pred_sql
                    break
                except:
                    continue
        
        conn.close()
        if best_sql is None:
            first_seq = self.gen_tokenizer.decode(outputs[0], skip_special_tokens=True)
            first_natsql = first_seq.split("|")[-1].strip() if " | " in first_seq else first_seq.strip()
            best_sql = self._convert_natsql_to_sql(first_natsql, db_id)
            best_sql = best_sql.replace("='", "= '").replace("!=", " !=").replace(",", " ,")
        return best_sql
