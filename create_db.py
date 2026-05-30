import sqlite3

# Buat database
conn = sqlite3.connect('contoh.db')
cursor = conn.cursor()

# Buat tabel siswa
cursor.execute('''
    CREATE TABLE IF NOT EXISTS siswa (
        id INTEGER PRIMARY KEY,
        nama TEXT,
        umur INTEGER,
        kelas TEXT
    )
''')

# Insert data contoh
cursor.execute("DELETE FROM siswa")  # Hapus data lama

siswa_data = [
    (1, 'Budi', 15, '10A'),
    (2, 'Ani', 16, '10B'),
    (3, 'Citra', 15, '10A'),
    (4, 'Dedi', 17, '11A'),
    (5, 'Eka', 16, '10B'),
]

cursor.executemany("INSERT INTO siswa VALUES (?, ?, ?, ?)", siswa_data)

# Buat tabel guru (opsional)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS guru (
        id INTEGER PRIMARY KEY,
        nama TEXT,
        mata_pelajaran TEXT
    )
''')

guru_data = [
    (1, 'Pak Ahmad', 'Matematika'),
    (2, 'Bu Dewi', 'Fisika'),
    (3, 'Pak Budi', 'Kimia'),
]

cursor.executemany("INSERT INTO guru VALUES (?, ?, ?)", guru_data)

conn.commit()
conn.close()

print("Database 'contoh.db' berhasil dibuat!")
print("Tabel yang tersedia: siswa, guru")
print("\nData siswa:")
print("-" * 30)
print("ID | Nama | Umur | Kelas")
print("-" * 30)
for row in siswa_data:
    print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]}")