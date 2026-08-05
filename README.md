This is a simple CRUD API for managing a to-do list, built with Python and FastAPI. It runs entirely in memory.

How to Run:

To start the server on localhost, run:
`uvicorn main:app --reload`

Endpoints:

| Method | Path | Description |
|---|---|---|
| GET | `/` | API info |
| GET | `/health` | Health check |
| GET | `/tasks` | List all tasks |
| GET | `/tasks/{id}` | Get a specific task |
| POST | `/tasks` | Create a new task |
| PUT | `/tasks/{id}` | Update a task |
| DELETE | `/tasks/{id}` | Delete a task |
| GET | `/stats` | Get task statistics |

Example request:

Here is an example of fetching the health endpoint using curl:

{
  "status": "ok"
}

Swagger UI
![alt text](<Screenshot 2026-07-17 200346.png>)

My Database-Backed Task API

Assignment 2: Stage 4 SQL Query Observation:
I ran `SELECT COUNT(*) FROM tasks;` directly in DB Browser, and it returned the total number of tasks currently in my database file.