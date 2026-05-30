# cek_db.py
import sqlite3
import os

# Ganti dengan path database Anda
db_path = input("Masukkan path database: ")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Ambil semua tabel
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"\n📁 Database: {db_path}")
    print(f"📊 Tabel yang ditemukan: {len(tables)} tabel\n")
    
    for table in tables:
        table_name = table[0]
        print(f"\n📌 Tabel: {table_name}")
        print("-" * 40)
        
        # Ambil kolom
        cursor.execute(f"PRAGMA table_info('{table_name}')")
        columns = cursor.fetchall()
        
        for col in columns:
            print(f"   - {col[1]} ({col[2]}){' (PRIMARY KEY)' if col[5] else ''}")
        
        # Ambil sample data (3 baris)
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
        sample = cursor.fetchall()
        if sample:
            print(f"\n   📝 Sample data (3 baris):")
            for row in sample:
                print(f"      {row}")
    
    conn.close()
else:
    print(f"❌ File tidak ditemukan: {db_path}")