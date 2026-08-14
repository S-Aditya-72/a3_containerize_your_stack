import os
import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from psycopg.rows import dict_row
from supabase import create_client, Client


load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:dev@localhost:5432/tasks")


def init_db():

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cursor:

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    done BOOLEAN NOT NULL
                )
            """)

            cursor.execute("SELECT COUNT(*) FROM tasks")
            count = cursor.fetchone()[0]

            if count == 0:

                cursor.execute(
                    "INSERT INTO tasks (title, done) VALUES ('Buy milk', False)")
                cursor.execute(
                    "INSERT INTO tasks (title, done) VALUES ('Walk the dog', True)")
                cursor.execute(
                    "INSERT INTO tasks (title, done) VALUES ('Learn FastAPI', False)")

            conn.commit()


init_db()

app = FastAPI()
print("Server running and connected to Supabase")


@app.get("/")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health():
    """
    Returns the health status of the API.
    """
    return {"status": "ok"}


@app.get("/tasks")
def get_tasks():
    """
    Returns a list of all current tasks in the database.
    """
    # Use psycopg and the dictionary row factory
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM tasks")
            return cursor.fetchall()


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    """
    Returns a specific task by its ID.
    """
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        with conn.cursor() as cursor:
            # Postgres uses %s instead of ? for safe parameters
            cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
            task = cursor.fetchone()

            if task is None:
                return JSONResponse(status_code=404, content={"error": "Task not found"})

            return task


@app.post("/tasks", status_code=201)
def create_task(task_data: dict):
    """
    Creates a new task and saves it to Postgres.
    """
    if "title" not in task_data or task_data["title"] == "":
        return JSONResponse(status_code=400, content={"error": "Task title is required"})

    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *",
                (task_data["title"], False)
            )

            new_task = cursor.fetchone()
            conn.commit()

    return new_task


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_data: dict):
    """
    Updates an existing task in Postgres.
    """
    if not task_data or ("title" in task_data and task_data["title"] == ""):
        return JSONResponse(status_code=400, content={"error": "Invalid task data"})

    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        with conn.cursor() as cursor:

            cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
            existing_task = cursor.fetchone()

            if existing_task is None:
                return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})

            new_title = task_data.get("title", existing_task["title"])
            new_done = task_data.get("done", existing_task["done"])

            cursor.execute(
                "UPDATE tasks SET title = %s, done = %s WHERE id = %s",
                (new_title, bool(new_done), task_id)
            )
            conn.commit()

            return {"id": task_id, "title": new_title, "done": bool(new_done)}


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    """
    Deletes a task from Postgres.
    """
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            conn.commit()

            if cursor.rowcount == 0:
                return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})

    return
