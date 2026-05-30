# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os

from .database.schema_reader import SchemaReader
from .nlp.sql_generator import SQLGenerator

app = FastAPI(
    title="Text-to-SQL API",
    description="API untuk mengubah pertanyaan bahasa alami menjadi query SQL",
    version="1.0.0"
)

# Global state
db_path: Optional[str] = None
schema_reader: Optional[SchemaReader] = None
sql_generator: Optional[SQLGenerator] = None

# Request/Response models
class SetDatabaseRequest(BaseModel):
    database_path: str

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    sql: str
    schema: str
    success: bool
    error: Optional[str] = None

class StatusResponse(BaseModel):
    database_connected: bool
    database_path: Optional[str] = None
    tables: list = []

# Endpoints
@app.get("/")
def root():
    return {
        "message": "Text-to-SQL API is running",
        "endpoints": {
            "POST /set_database": "Set database path",
            "POST /query": "Convert question to SQL",
            "GET /status": "Check API status"
        }
    }

# app/main.py bagian set_database
@app.post("/set_database")
def set_database(request: SetDatabaseRequest):
    global db_path, schema_reader, sql_generator
    
    if not os.path.exists(request.database_path):
        raise HTTPException(status_code=404, detail=f"Database tidak ditemukan: {request.database_path}")
    
    try:
        db_path = request.database_path
        schema_reader = SchemaReader(db_path)
        sql_generator = SQLGenerator(schema_reader)  # <-- tanpa db_path
        
        return {
            "message": "Database berhasil di-set",
            "database_path": db_path,
            "tables": schema_reader.get_tables()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error membaca database: {str(e)}")

@app.post("/query", response_model=QueryResponse)
def convert_to_sql(request: QueryRequest):
    if not sql_generator:
        raise HTTPException(status_code=400, detail="Database belum di-set. Gunakan endpoint /set_database terlebih dahulu.")
    
    try:
        sql = sql_generator.generate(request.question)
        schema = schema_reader.get_schema_string()
        
        return QueryResponse(
            question=request.question,
            sql=sql,
            schema=schema,
            success=True,
            error=None
        )
    except Exception as e:
        return QueryResponse(
            question=request.question,
            sql="",
            schema=schema_reader.get_schema_string() if schema_reader else "",
            success=False,
            error=str(e)
        )

@app.get("/status", response_model=StatusResponse)
def get_status():
    return StatusResponse(
        database_connected=db_path is not None,
        database_path=db_path,
        tables=schema_reader.get_tables() if schema_reader else []
    )