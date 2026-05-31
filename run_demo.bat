@echo off
echo ====================================================
echo      MENJALANKAN TEXT-TO-SQL LOCAL DEMO
echo ====================================================
echo.
echo [1/2] Memastikan dependencies terinstall...
pip install -r requirements.txt
echo.
echo [2/2] Membuka Streamlit di Browser...
streamlit run main_streamlit.py
pause
