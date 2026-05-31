# RESDSQL: Text-to-SQL Local Demo 🔍

Aplikasi berbasis Streamlit untuk mengubah bahasa alami (Inggris) menjadi query SQL menggunakan model T5-Large dan arsitektur RESDSQL. 

## 🛠️ Instalasi & Persiapan

Repositori ini hanya berisi source code utama. Karena ukuran file model dan database sangat besar, Anda perlu mengunduhnya secara terpisah.

### 1. Download Dependencies
Pastikan Anda menggunakan Python 3.10 atau 3.11, lalu jalankan:
```bash
pip install -r requirements.txt
```

### 2. Download Model & Database
Anda wajib menyiapkan folder berikut di dalam direktori `Text-to-SQL-language`:
*   `database/` : Berisi folder-folder database SQLite (misal: `concert_singer`, `car_1`).
*   `models/classifier/` : Berisi model Schema Item Classifier.
*   `text2natsql-t5-large/` : Berisi model utama T5-Large.

*(Catatan: Anda bisa meminta file `.zip` lengkap yang berisi folder-folder ini kepada pemilik repositori via Google Drive).*

## 🚀 Cara Menjalankan (Demo Lokal)

Cara paling mudah untuk menjalankan aplikasi ini di Windows adalah dengan mengklik ganda file:
👉 **`run_demo.bat`**

Atau jalankan manual via terminal:
```bash
streamlit run main_streamlit.py
```

## 💡 Fitur `q.txt` (Contoh Pertanyaan)
Aplikasi ini mendukung deteksi contoh pertanyaan otomatis. Jika Anda ingin menambahkan contoh pertanyaan untuk sebuah database agar muncul di UI Streamlit, cukup buat file bernama `q.txt` di dalam folder database tersebut (contoh: `database/car_1/q.txt`). Tulis satu pertanyaan per baris.

## ⚙️ Hugging Face Spaces
Repositori ini juga kompatibel untuk di-deploy ke Hugging Face Spaces (SDK: Streamlit) dengan nama file utama `main_streamlit.py`.

---
*Note: Folder `database`, `models`, dan `data` di-ignore dari git untuk menjaga repositori tetap ringan.*
