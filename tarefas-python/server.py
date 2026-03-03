from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sqlite3
import os
from typing import Optional, List

DB = os.path.join(os.path.dirname(__file__), "tasks.db")
app = FastAPI()
static_dir = os.path.join(os.path.dirname(__file__), 'static')
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

def get_conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

class TaskIn(BaseModel):
    title: str
    parent_id: Optional[int] = None


@app.get("/api/tasks")
def get_tasks():
    c = get_conn()
    rows = c.execute("SELECT * FROM tasks ORDER BY ord, created_at").fetchall()
    return [dict(r) for r in rows]


@app.post("/api/tasks")
def add_task(t: TaskIn):
    c = get_conn()
    cur = c.cursor()
    cur.execute("INSERT INTO tasks (parent_id, title, created_at) VALUES (?, ?, ?)", (t.parent_id, t.title, sqlite3.datetime.datetime.now()))
    c.commit()
    return {"id": cur.lastrowid}


@app.patch("/api/tasks/{task_id}/rename")
def rename(task_id: int, payload: dict):
    title = payload.get("title")
    if not title:
        raise HTTPException(status_code=400, detail="title required")
    c = get_conn()
    c.execute("UPDATE tasks SET title = ? WHERE id = ?", (title, task_id))
    c.commit()
    return {"ok": True}


def _delete_rec(c, tid: int):
    for r in c.execute("SELECT id FROM tasks WHERE parent_id = ?", (tid,)).fetchall():
        _delete_rec(c, r['id'])
    c.execute("DELETE FROM tasks WHERE id = ?", (tid,))


@app.delete("/api/tasks/{task_id}")
def delete(task_id: int):
    c = get_conn()
    _delete_rec(c, task_id)
    c.commit()
    return {"ok": True}


@app.patch("/api/tasks/{task_id}/toggle")
def toggle(task_id: int, payload: dict):
    expanded = 1 if payload.get("expanded") else 0
    c = get_conn()
    c.execute("UPDATE tasks SET expanded = ? WHERE id = ?", (expanded, task_id))
    c.commit()
    return {"ok": True}


@app.post("/api/expand_all")
def expand_all():
    c = get_conn()
    c.execute("UPDATE tasks SET expanded = 1")
    c.commit()
    return {"ok": True}


@app.post("/api/collapse_all")
def collapse_all():
    c = get_conn()
    c.execute("UPDATE tasks SET expanded = 0")
    c.commit()
    return {"ok": True}


@app.get("/")
def index():
    return {"static": "/static/"}
