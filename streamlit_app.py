import streamlit as st
import requests
import sqlite3
import pandas as pd
import os

st.set_page_config(
    page_title="Text-to-SQL - Universal Database",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Text-to-SQL Converter")
st.markdown("Tanyakan sesuatu dalam bahasa Indonesia tentang database Anda, langsung lihat datanya!")

# Inisialisasi session state
if 'db_connected' not in st.session_state:
    st.session_state.db_connected = False
if 'current_sql' not in st.session_state:
    st.session_state.current_sql = ""
if 'current_data' not in st.session_state:
    st.session_state.current_data = None
if 'current_tables' not in st.session_state:
    st.session_state.current_tables = []
if 'current_db_path' not in st.session_state:
    st.session_state.current_db_path = ""

# ========== SIDEBAR ==========
with st.sidebar:
    st.header("🔌 Langkah 1: Pilih Database")
    
    # Pilihan sumber database
    db_source = st.radio(
        "Sumber Database:",
        ["📁 File .db lokal", "📤 Upload file database", "📝 Contoh database"]
    )
    
    db_path = None
    
    if db_source == "📁 File .db lokal":
        # Input path manual
        db_path = st.text_input(
            "Path ke file database (.db)", 
            value=st.session_state.current_db_path if st.session_state.current_db_path else "contoh.db",
            help="Contoh: C:/data/my_database.db atau ./database.db"
        )
        
        # Tombol browse (opsional, pilih file)
        if st.button("🔍 Cari file..."):
            st.info("Masukkan path lengkap file database Anda")
            
    elif db_source == "📤 Upload file database":
        # Upload file
        uploaded_file = st.file_uploader(
            "Upload file database (.db)", 
            type=['db', 'sqlite', 'sqlite3'],
            help="Upload file database SQLite dari komputer Anda"
        )
        if uploaded_file is not None:
            # Simpan file yang diupload
            db_path = f"uploaded_{uploaded_file.name}"
            with open(db_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"✅ File {uploaded_file.name} berhasil diupload!")
    
    else:  # "📝 Contoh database"
        # Pilih contoh database
        contoh_db = st.selectbox(
            "Pilih contoh database:",
            ["contoh.db", "chinook.db", "northwind.db", "sakila.db"]
        )
        
        # Cek apakah file contoh ada
        if os.path.exists(contoh_db):
            db_path = contoh_db
            st.success(f"✅ Database {contoh_db} ditemukan!")
        else:
            st.warning(f"⚠️ Database {contoh_db} tidak ditemukan. Buat dulu atau upload file.")
            # Tawarkan membuat database contoh
            if st.button("📝 Buat database contoh.db"):
                # Buat database contoh
                conn = sqlite3.connect("contoh.db")
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS siswa (
                        id INTEGER PRIMARY KEY,
                        nama TEXT,
                        umur INTEGER,
                        kelas TEXT
                    )
                ''')
                cursor.execute("DELETE FROM siswa")
                siswa_data = [
                    (1, 'Budi', 15, '10A'),
                    (2, 'Ani', 16, '10B'),
                    (3, 'Citra', 15, '10A'),
                ]
                cursor.executemany("INSERT INTO siswa VALUES (?, ?, ?, ?)", siswa_data)
                conn.commit()
                conn.close()
                st.success("✅ Database contoh.db berhasil dibuat!")
                st.rerun()
    
    # Tombol Connect Database
    if db_path:
        if st.button("🔗 CONNECT DATABASE", type="primary", use_container_width=True):
            with st.spinner(f"Menghubungkan ke {db_path}..."):
                try:
                    response = requests.post(
                        "http://localhost:8000/set_database",
                        json={"database_path": db_path}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.db_connected = True
                        st.session_state.current_db_path = db_path
                        st.session_state.current_tables = data.get('tables', [])
                        st.success(f"✅ DATABASE TERHUBUNG!")
                        st.info(f"📚 Tabel yang tersedia: {', '.join(st.session_state.current_tables)}")
                        
                        # Ambil skema lengkap untuk ditampilkan
                        try:
                            resp_status = requests.get("http://localhost:8000/status")
                            if resp_status.status_code == 200:
                                st.session_state.schema_data = resp_status.json()
                        except:
                            pass
                    else:
                        st.error(f"❌ Gagal: {response.text}")
                        st.session_state.db_connected = False
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                    st.session_state.db_connected = False
    
    # Status koneksi
    st.markdown("---")
    if st.session_state.db_connected:
        st.success(f"🟢 STATUS: TERHUBUNG")
        st.caption(f"📁 Database: {st.session_state.current_db_path}")
        st.caption(f"📊 Tabel: {', '.join(st.session_state.current_tables[:3])}{'...' if len(st.session_state.current_tables) > 3 else ''}")
    else:
        st.warning("🔴 STATUS: BELUM TERHUBUNG")
    
    st.markdown("---")
    
    # Tampilkan skema database jika sudah connect
    if st.session_state.db_connected and st.session_state.get('current_tables'):
        st.header("📋 Skema Database")
        
        for table in st.session_state.current_tables:
            with st.expander(f"📌 Tabel: {table}"):
                try:
                    conn = sqlite3.connect(st.session_state.current_db_path)
                    cursor = conn.cursor()
                    cursor.execute(f"PRAGMA table_info('{table}')")
                    columns = cursor.fetchall()
                    for col in columns:
                        st.text(f"  - {col[1]} ({col[2]}){' (PRIMARY KEY)' if col[5] else ''}")
                    conn.close()
                except:
                    st.write("Tidak dapat membaca skema")
    
    st.markdown("---")
    
    # Contoh pertanyaan (dinamis berdasarkan tabel)
    st.header("📝 Contoh Pertanyaan")
    
    if st.session_state.current_tables:
        main_table = st.session_state.current_tables[0]
        
        # Ambil beberapa kolom dari tabel utama
        try:
            conn = sqlite3.connect(st.session_state.current_db_path)
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info('{main_table}')")
            columns = [col[1] for col in cursor.fetchall()]
            conn.close()
            
            # Buat contoh pertanyaan berdasarkan tabel dan kolom
            contoh_list = [
                f"tampilkan semua {main_table}",
                f"hitung jumlah {main_table}",
            ]
            
            # Tambahkan contoh untuk kolom numerik
            for col in columns[:3]:
                if col in ['umur', 'usia', 'age', 'price', 'harga', 'jumlah']:
                    contoh_list.append(f"rata-rata {col} dari {main_table}")
                    contoh_list.append(f"{col} tertinggi dari {main_table}")
                    break
            
            # Tambahkan contoh filter
            if len(columns) > 1:
                contoh_list.append(f"tampilkan {columns[0]} dari {main_table} dimana {columns[1]} lebih dari 1")
            
            for q in contoh_list[:5]:
                if st.button(f"📌 {q}", use_container_width=True):
                    st.session_state.selected_question = q
                    st.rerun()
                    
        except:
            # Fallback contoh umum
            contoh_umum = [
                f"tampilkan semua {main_table}",
                f"hitung jumlah {main_table}"
            ]
            for q in contoh_umum:
                if st.button(f"📌 {q}", use_container_width=True):
                    st.session_state.selected_question = q
                    st.rerun()
    else:
        st.info("Connect database dulu untuk melihat contoh pertanyaan")

# ========== MAIN CONTENT ==========

# Tampilkan peringatan jika belum connect
if not st.session_state.db_connected:
    st.info("👈 **Silakan connect database terlebih dahulu di sidebar kiri!**")
    st.markdown("""
    ### Cara menggunakan:
    1. **Pilih sumber database**:
       - 📁 File .db lokal: masukkan path file database Anda
       - 📤 Upload file database: upload file .db dari komputer
       - 📝 Contoh database: gunakan database contoh
    
    2. **Klik tombol CONNECT DATABASE**
    
    3. **Tunggu status berubah menjadi TERHUBUNG**
    
    4. **Masukkan pertanyaan** (bisa klik contoh atau ketik sendiri)
    
    5. **Klik GENERATE & TAMPILKAN DATA**
    """)
    st.stop()

# Jika sudah connect, tampilkan form pertanyaan
st.subheader("💬 Langkah 2: Masukkan Prompt tentang Database Anda")

# Gunakan selected question jika ada
default_question = st.session_state.get('selected_question', '')
question = st.text_area(
    "",
    value=default_question,
    height=80,
    placeholder=f"Contoh: tampilkan semua {st.session_state.current_tables[0] if st.session_state.current_tables else 'siswa'}"
)

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    generate_btn = st.button("🚀 GENERATE & TAMPILKAN DATA", type="primary", use_container_width=True)
with col2:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.current_sql = ""
        st.session_state.current_data = None
        st.session_state.selected_question = ""
        st.rerun()

if generate_btn and question:
    with st.spinner("🧠 Memproses pertanyaan dan mengambil data..."):
        try:
            # Generate SQL
            response = requests.post(
                "http://localhost:8000/query",
                json={"question": question}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success', False):
                    sql = data.get('sql', '')
                    st.session_state.current_sql = sql
                    
                    # Eksekusi SQL
                    try:
                        conn = sqlite3.connect(st.session_state.current_db_path)
                        df = pd.read_sql_query(sql, conn)
                        conn.close()
                        
                        st.session_state.current_data = df
                        st.success(f"✅ Berhasil! Ditemukan {len(df)} baris data")
                        
                    except Exception as e:
                        st.error(f"❌ Error eksekusi SQL: {e}")
                        st.session_state.current_data = None
                else:
                    st.error(f"❌ Error: {data.get('error', 'Unknown error')}")
            else:
                st.error(f"❌ API Error: {response.text}")
                
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ========== TAMPILKAN HASIL ==========
if st.session_state.current_sql:
    st.markdown("---")
    st.subheader("📊 HASIL")
    
    # Tampilkan SQL
    with st.expander("📝 Lihat SQL Query", expanded=False):
        st.code(st.session_state.current_sql, language="sql")
    
    # Tampilkan Data
    if st.session_state.current_data is not None:
        if not st.session_state.current_data.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📊 Jumlah Baris", len(st.session_state.current_data))
            with col2:
                st.metric("📋 Jumlah Kolom", len(st.session_state.current_data.columns))
            
            st.dataframe(st.session_state.current_data, use_container_width=True)
            
            # Download
            csv = st.session_state.current_data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="query_result.csv",
                mime="text/csv",
            )
        else:
            st.info("📭 Query berhasil tetapi tidak menghasilkan data")
    else:
        st.info("💡 Klik 'GENERATE & TAMPILKAN DATA' untuk melihat hasil")

# Footer
st.markdown("---")
st.markdown(
    "<center>💡 Bisa pakai file database apapun (.db)! Upload atau masukkan path-nya.</center>",
    unsafe_allow_html=True
)