import streamlit as st
import os
import sqlite3
import pandas as pd
import sys

# Tambahkan root directory ke sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from app.nlp_logic.ai_pipeline import RESDSQLPipelineV2
from app.nlp_logic.utils.schema_reader import SchemaReader

st.set_page_config(page_title="RESDSQL Explorer", layout="wide")

@st.cache_resource
def load_pipeline():
    # Initialize with a dummy DB path
    db_root = "database"
    first_db = "concert_singer"
    db_path = os.path.join(db_root, first_db, f"{first_db}.sqlite")
    return RESDSQLPipelineV2(SchemaReader(db_path))

st.title("🔍 RESDSQL Text-to-SQL Explorer")

# 1. Database Selection
db_root = "database"
# Shortlist database yang datanya lengkap, akurasi tinggi, dan mudah dipahami
shortlist_dbs = [
    "concert_singer",
    "car_1",
    "student_1",
    "flight_2",
    "stadium_and_event",
    "world_1",
    "bakery_1",
    "wine_1",
    "club_1",
    "bike_1"
]

# Pastikan folder database tersebut memang ada sebelum ditampilkan
available_dbs = [d for d in shortlist_dbs if os.path.isdir(os.path.join(db_root, d))]

selected_db = st.selectbox("📁 Pilih Database Demo:", available_dbs)

db_path = os.path.join(db_root, selected_db, f"{selected_db}.sqlite")
schema_reader = SchemaReader(db_path)

# 2. Show Schema Structure
with st.expander("📊 Lihat Struktur Database (Schema)", expanded=True):
    tables = schema_reader.get_tables()
    cols = st.columns(len(tables) if len(tables) < 4 else 4)
    for i, table in enumerate(tables):
        with cols[i % 4]:
            st.markdown(f"**Table: `{table}`**")
            columns = schema_reader.get_columns(table)
            st.text("\n".join([f"- {c}" for c in columns]))

st.markdown("---")

# 3. Input Question
st.markdown("---")
st.subheader("💬 Masukkan Pertanyaan")

# Logic to load example questions
example_questions = []
q_file_path = os.path.join(db_root, selected_db, "q.txt")
if os.path.exists(q_file_path):
    with open(q_file_path, "r") as f:
        # Read lines and filter empty ones
        example_questions = [line.strip() for line in f.readlines() if line.strip()]

# UI for Examples
if example_questions:
    with st.expander("💡 Lihat Contoh Pertanyaan untuk Database ini:"):
        for ex in example_questions[:5]: # Show top 5
            if st.button(ex, key=ex):
                st.session_state.question_input = ex

# Use session state to allow button to fill text input
if "question_input" not in st.session_state:
    st.session_state.question_input = ""

question = st.text_input("Masukkan pertanyaan (Bahasa Inggris):", 
                          value=st.session_state.question_input,
                          placeholder="Example: How many records are there?")

if st.button("🚀 Generate & Execute"):
    if not question:
        st.warning("Tulis pertanyaan dulu ya!")
    else:
        pipeline = load_pipeline()
        pipeline.schema = schema_reader
        
        with st.spinner("Model sedang berpikir..."):
            pred_sql = pipeline.generate(question)
        
        st.subheader("📝 Generated SQL")
        st.code(pred_sql, language="sql")
        
        st.subheader("📋 Execution Result")
        try:
            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query(pred_sql, conn)
            st.dataframe(df, use_container_width=True)
            conn.close()
        except Exception as e:
            st.error(f"Execution Error: {e}")

st.sidebar.markdown("---")
st.sidebar.info("""
**Stats:**
- Model: T5-Large
- Accuracy: 82.00%
- Logic: Localized RESDSQL
""")
