from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI(title="Test Environment Backend API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "testdb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres123")
ENV_NAME = os.getenv("ENV_NAME", "preview-feature-pr42")

class TaskCreate(BaseModel):
    title: str
    description: str = ""

def get_db_connection():
    max_retries = 5
    for attempt in range(max_retries):
        try:
            return psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                cursor_factory=RealDictCursor
            )
        except psycopg2.OperationalError:
            if attempt == max_retries - 1:
                raise HTTPException(status_code=503, detail="Database connection failed")
            time.sleep(1)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "backend-api",
        "environment": ENV_NAME,
        "message": "Платформа динамических тестовых сред активна"
    }

@app.get("/health")
def healthcheck():
    db_status = "unknown"
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
        conn.close()
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "environment": ENV_NAME,
        "database": db_status,
        "timestamp": time.time()
    }

@app.get("/api/tasks")
def list_tasks():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, description, status, created_at FROM test_tasks ORDER BY id ASC;")
            tasks = cur.fetchall()
        return {"environment": ENV_NAME, "tasks": tasks}
    finally:
        conn.close()

@app.post("/api/tasks", status_code=201)
def create_task(task: TaskCreate):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO test_tasks (title, description, status) VALUES (%s, %s, %s) RETURNING id, title, description, status, created_at;",
                (task.title, task.description, "pending")
            )
            new_task = cur.fetchone()
            conn.commit()
        return {"message": "Task created successfully", "task": new_task}
    finally:
        conn.close()