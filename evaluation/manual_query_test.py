import pandas as pd
import torch
from app.db_readers.schema_reader import SchemaReader
from app.nlp_logic.ai_pipeline import RESDSQLPipeline
import json
import os

def run_evaluation(db_path, test_cases):
    """
    Runs evaluation on a specific database with a list of questions.
    test_cases: list of dicts [{"question": "...", "expected_sql": "..."}]
    """
    if not os.path.exists(db_path):
        print(f"Error: Database {db_path} not found.")
        return

    # Load Reader and Pipeline
    reader = SchemaReader(db_path)
    # We use base model for evaluation speed
    pipeline = RESDSQLPipeline(reader, model_path="models/t5-base/checkpoint-39312")

    results = []
    correct_count = 0

    print("\n" + "="*60)
    print(f"STARTING EVALUATION ON: {os.path.basename(db_path)}")
    print("="*60)

    for i, case in enumerate(test_cases):
        question = case["question"]
        expected = case["expected_sql"].strip().lower().replace("  ", " ")
        
        # Generate SQL
        generated = pipeline.generate(question).strip().lower().replace("  ", " ")
        
        # Simple Exact Match (EM) logic
        is_correct = (generated == expected)
        if is_correct:
            correct_count += 1
            status = "✅ MATCH"
        else:
            status = "❌ MISMATCH"

        results.append({
            "id": i+1,
            "question": question,
            "expected": expected,
            "generated": generated,
            "status": status
        })

        print(f"[{i+1}/{len(test_cases)}] {status}")
        if not is_correct:
            print(f"   Exp: {expected}")
            print(f"   Gen: {generated}")

    accuracy = (correct_count / len(test_cases)) * 100
    
    print("\n" + "="*60)
    print(f"FINAL RESULT")
    print(f"Total Questions: {len(test_cases)}")
    print(f"Correct (EM): {correct_count}")
    print(f"Accuracy: {accuracy:.2f}%")
    print("="*60)

    return results, accuracy

if __name__ == "__main__":
    # ACADEMIC EXAMPLE: Testing on 'contoh.db'
    # In a real paper, you would use the Spider Dev Set here.
    
    db_to_test = "test_databases/contoh.db"
    
    # Define your academic test set here
    # These are questions that the model SHOULD be able to answer for 'contoh.db'
    academic_test_set = [
        {
            "question": "tampilkan semua siswa",
            "expected_sql": "SELECT * FROM siswa"
        },
        {
            "question": "hitung jumlah siswa",
            "expected_sql": "SELECT COUNT(*) FROM siswa"
        },
        {
            "question": "siapa nama guru yang mengajar fisika?",
            "expected_sql": "SELECT nama FROM guru WHERE mata_pelajaran = 'Fisika'"
        },
        {
            "question": "tampilkan nama dan umur siswa yang kelasnya 10A",
            "expected_sql": "SELECT nama ,  umur FROM siswa WHERE kelas = '10A'"
        }
    ]

    run_evaluation(db_to_test, academic_test_set)
