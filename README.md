---
title: Text To Sql
emoji: 🔍
colorFrom: blue
colorTo: indigo
sdk: streamlit
app_file: app.py
pinned: false
---

# Text-to-SQL with T5 and RESDSQL

Aplikasi Text-to-SQL menggunakan model T5-Large dan Classifier untuk menghasilkan query SQL dari bahasa alami.

## Setup
Model ini menggunakan Git LFS untuk menyimpan bobot model yang besar.
- **T5 Model:** text2natsql-t5-large
- **Classifier:** models/classifier
- **Database:** SQLite files in `database/`
