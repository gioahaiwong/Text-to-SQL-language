import os
import json
import sqlite3
import pandas as pd
from app.nlp_logic.utils.schema_reader import SchemaReader
from app.nlp_logic.ai_pipeline import RESDSQLPipelineV2

def compare_results(gold_result, pred_result):
    if gold_result is None or pred_result is None:
        return False
    try:
        g = gold_result.copy()
        p = pred_result.copy()
        # Normalisasi kolom agar tidak peduli nama kolom (EX match fokus ke data)
        g.columns = range(len(g.columns))
        p.columns = range(len(p.columns))
        # Sorting data agar tidak peduli urutan baris
        g_sorted = g.sort_values(by=list(g.columns)).reset_index(drop=True)
        p_sorted = p.sort_values(by=list(p.columns)).reset_index(drop=True)
        return g_sorted.equals(p_sorted)
    except:
        return False

def run_natsql_benchmark(dev_json_path, db_root_path, num_samples=100):
    if not os.path.exists(dev_json_path):
        print(f"Error: {dev_json_path} not found.")
        return

    with open(dev_json_path, 'r') as f:
        dev_data = json.load(f)
    
    # Pre-select first DB for init
    first_db_id = dev_data[0]['db_id']
    first_db_path = os.path.join(db_root_path, first_db_id, f"{first_db_id}.sqlite")
    
    print(f"Initializing RESDSQL Pipeline V2...")
    pipeline = RESDSQLPipelineV2(
        SchemaReader(first_db_path), 
        model_path="text2natsql-t5-large/checkpoint-21216",
        classifier_path="models/classifier"
    )
    
    correct = 0
    total = min(num_samples, len(dev_data))
    db_stats = {}

    print(f"\n🚀 STARTING NATSQL BENCHMARK (Total: {total} samples)")
    print("="*80)

    for i in range(total):
        item = dev_data[i]
        db_id = item['db_id']
        question = item['question']
        gold_sql = item['query']
        
        db_path = os.path.join(db_root_path, db_id, f"{db_id}.sqlite")
        if not os.path.exists(db_path):
            continue

        pipeline.schema = SchemaReader(db_path)
        
        # Generation now includes NatSQL to SQL conversion internally
        pred_sql = pipeline.generate(question)
        
        conn = sqlite3.connect(db_path)
        try:
            gold_res = pd.read_sql_query(gold_sql, conn)
            pred_res = pd.read_sql_query(pred_sql, conn)
            is_correct = compare_results(gold_res, pred_res)
        except:
            is_correct = False
        conn.close()
        
        if is_correct:
            correct += 1
            
        if (i+1) % 10 == 0:
            print(f"Processed {i+1}/{total}... Accuracy: {(correct/(i+1))*100:.2f}%")

    print("\n" + "="*80)
    print(f"📊 FINAL NATSQL RESULTS")
    print(f"   Accuracy (EX) : {(correct / total) * 100:.2f}%")
    print("="*80)

if __name__ == "__main__":
    DEV_JSON = "data/spider/dev.json"
    DB_ROOT = "database"
    run_natsql_benchmark(DEV_JSON, DB_ROOT)
