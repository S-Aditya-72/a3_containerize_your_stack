import sqlite3
from fastapi import FastAPI
from fastapi.responses import JSONResponse


def init_db():

    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                done BOOLEAN
            )
        """)

        cursor.execute("SELECT COUNT(*) FROM tasks")
        count = cursor.fetchone()[0]

        if count == 0:

            cursor.execute(
                "INSERT INTO tasks (title, done) VALUES ('Buy milk', 0)")
            cursor.execute(
                "INSERT INTO tasks (title, done) VALUES ('Walk the dog', 1)")
            cursor.execute(
                "INSERT INTO tasks (title, done) VALUES ('Learn FastAPI', 0)")

            conn.commit()


init_db()

app = FastAPI()


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
    with sqlite3.connect("tasks.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tasks")
        return cursor.fetchall()


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    """
    Returns a specific task by its ID.
    """
    with sqlite3.connect("tasks.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        task = cursor.fetchone()

        if task is None:
            return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})

        return task


@app.post("/tasks", status_code=201)
def create_task(task_data: dict):
    """
    Creates a new task and saves it to the database.
    """

    if "title" not in task_data or task_data["title"] == "":
        return JSONResponse(status_code=400, content={"error": "Task title is required"})

    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (task_data["title"], 0)
        )

        conn.commit()

        new_id = cursor.lastrowid

    return {"id": new_id, "title": task_data["title"], "done": False}


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_data: dict):
    """
    Updates an existing task in the database.
    """

    if not task_data or ("title" in task_data and task_data["title"] == ""):
        return JSONResponse(status_code=400, content={"error": "Invalid task data"})

    with sqlite3.connect("tasks.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        existing_task = cursor.fetchone()

        if existing_task is None:
            return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})

        new_title = task_data.get("title", existing_task["title"])
        new_done = task_data.get("done", existing_task["done"])

        cursor.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (new_title, int(new_done), task_id)
        )
        conn.commit()

        return {"id": task_id, "title": new_title, "done": bool(new_done)}


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    """
    Deletes a task from the database.
    """
    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()

        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})

    return


@app.get("/stats")
def get_stats():
    """
    Returns statistics about the tasks in the to-do list.
    """
    total_tasks = len(tasks)

    # List comprehension to filter only the completed tasks, then get the length
    completed_tasks = len([task for task in tasks if task.get("done") == True])

    # Protect against ZeroDivisionError
    if total_tasks > 0:
        percentage = (completed_tasks / total_tasks) * 100
    else:
        percentage = 0

    return {
        "total": total_tasks,
        "completed": completed_tasks,
        # round to 2 decimal places
        "completion_percentage": round(percentage, 2)
    }
