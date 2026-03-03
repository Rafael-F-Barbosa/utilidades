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

# ensure DB and schema
def ensure_schema():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        parent_id INTEGER,
        title TEXT,
        details TEXT,
        expanded INTEGER DEFAULT 0,
        created_at DATETIME,
        ord INTEGER,
        due_date TEXT
    )
    ''')
    # ensure columns exist (for older DBs) - check pragma
    cols = [r[1] for r in cur.execute("PRAGMA table_info(tasks)").fetchall()]
    if 'ord' not in cols:
        cur.execute("ALTER TABLE tasks ADD COLUMN ord INTEGER")
    if 'due_date' not in cols:
        cur.execute("ALTER TABLE tasks ADD COLUMN due_date TEXT")
    conn.commit()
    # initialize ord for existing rows where ord is NULL or 0
    rows = cur.execute("SELECT id, parent_id FROM tasks ORDER BY parent_id, created_at, id").fetchall()
    cur_parent = object()
    counter = 0
    for r in rows:
        rid = r[0]
        pid = r[1]
        if pid != cur_parent:
            cur_parent = pid
            counter = 1
        else:
            counter += 1
        cur.execute("UPDATE tasks SET ord = ? WHERE id = ? AND (ord IS NULL OR ord = 0)", (counter, rid))
    conn.commit()
    conn.close()

ensure_schema()

def get_conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

class TaskIn(BaseModel):
    title: str
    parent_id: Optional[int] = None
    due_date: Optional[str] = None


@app.get("/api/tasks")
def get_tasks():
    c = get_conn()
    rows = c.execute("SELECT * FROM tasks ORDER BY parent_id, ord, created_at").fetchall()
    return [dict(r) for r in rows]


@app.post("/api/tasks")
def add_task(t: TaskIn):
    c = get_conn()
    cur = c.cursor()
    # determine next ord within parent (handle NULL parent)
    if t.parent_id is None:
        row = c.execute("SELECT COALESCE(MAX(ord), 0) as m FROM tasks WHERE parent_id IS NULL").fetchone()
    else:
        row = c.execute("SELECT COALESCE(MAX(ord), 0) as m FROM tasks WHERE parent_id = ?", (t.parent_id,)).fetchone()
    next_ord = (row['m'] or 0) + 1
    cur.execute("INSERT INTO tasks (parent_id, title, created_at, ord, due_date) VALUES (?, ?, ?, ?, ?)", (t.parent_id, t.title, sqlite3.datetime.datetime.now(), next_ord, t.due_date))
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


@app.patch("/api/tasks/{task_id}/move")
def move_task(task_id: int, payload: dict):
    dir = payload.get('dir')
    if dir not in ('up', 'down'):
        raise HTTPException(status_code=400, detail='dir must be "up" or "down"')
    c = get_conn()
    cur = c.cursor()
    # fetch task
    t = cur.execute("SELECT id, parent_id, ord FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not t:
        raise HTTPException(status_code=404, detail='task not found')
    parent = t['parent_id']
    ord = t['ord'] or 0
    if parent is None:
        if dir == 'up':
            neighbor = cur.execute("SELECT id, ord FROM tasks WHERE parent_id IS NULL AND ord < ? ORDER BY ord DESC LIMIT 1", (ord,)).fetchone()
        else:
            neighbor = cur.execute("SELECT id, ord FROM tasks WHERE parent_id IS NULL AND ord > ? ORDER BY ord ASC LIMIT 1", (ord,)).fetchone()
    else:
        if dir == 'up':
            neighbor = cur.execute("SELECT id, ord FROM tasks WHERE parent_id = ? AND ord < ? ORDER BY ord DESC LIMIT 1", (parent, ord)).fetchone()
        else:
            neighbor = cur.execute("SELECT id, ord FROM tasks WHERE parent_id = ? AND ord > ? ORDER BY ord ASC LIMIT 1", (parent, ord)).fetchone()
    if not neighbor:
        return {"ok": True}
    # swap ord
    cur.execute("UPDATE tasks SET ord = ? WHERE id = ?", (neighbor['ord'], task_id))
    cur.execute("UPDATE tasks SET ord = ? WHERE id = ?", (ord, neighbor['id']))
    c.commit()
    return {"ok": True}


@app.patch("/api/tasks/{task_id}/due_date")
def set_due_date(task_id: int, payload: dict):
    date = payload.get('date')
    if date is None:
        raise HTTPException(status_code=400, detail='date required')
    c = get_conn()
    c.execute("UPDATE tasks SET due_date = ? WHERE id = ?", (date, task_id))
    c.commit()
    return {"ok": True}


@app.patch("/api/tasks/{task_id}/details")
def update_details(task_id: int, payload: dict):
    details = payload.get("details")
    if details is None:
        raise HTTPException(status_code=400, detail="details required")
    c = get_conn()
    c.execute("UPDATE tasks SET details = ? WHERE id = ?", (details, task_id))
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
