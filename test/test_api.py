import requests
import json

BASE_URL = "http://localhost:8000"

def test_set_database(db_path: str):
    """Test set database endpoint"""
    response = requests.post(
        f"{BASE_URL}/set_database",
        json={"database_path": db_path}
    )
    print(f"Set database: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def test_query(question: str):
    """Test query endpoint"""
    response = requests.post(
        f"{BASE_URL}/query",
        json={"question": question}
    )
    print(f"\nQuery: {question}")
    print(f"Response: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(response.text)
    return response

def test_status():
    """Test status endpoint"""
    response = requests.get(f"{BASE_URL}/status")
    print(f"\nStatus: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response

if __name__ == "__main__":
    # Ganti dengan path database Anda
    DB_PATH = "contoh.db"
    
    print("="*50)
    print("TESTING TEXT-TO-SQL API")
    print("="*50)
    
    # Test status awal
    test_status()
    
    # Test set database
    test_set_database(DB_PATH)
    
    # Test queries
    test_questions = [
        "tampilkan semua siswa",
        "hitung jumlah siswa",
        "rata-rata umur siswa",
        "siswa yang berumur lebih dari 15"
    ]
    
    for q in test_questions:
        test_query(q)