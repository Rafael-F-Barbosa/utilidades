#!/usr/bin/env python3
import os
import sqlite3
from datetime import datetime, timezone
import curses
import subprocess
import sys
import termios
import tty
from simple_term_menu import TerminalMenu

DB_NAME = os.path.join(os.path.dirname(__file__), 'tasks.db')


class TaskDB:
    def __init__(self, path=DB_NAME):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self._ensure()

    def _ensure(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                parent_id INTEGER,
                title TEXT NOT NULL,
                details TEXT DEFAULT '',
                created_at TEXT,
                ord INTEGER DEFAULT 0
            )
            """
        )
        # ensure expanded column exists (migration for older DBs)
        cols = [r[1] for r in cur.execute("PRAGMA table_info(tasks)").fetchall()]
        if 'expanded' not in cols:
            try:
                cur.execute("ALTER TABLE tasks ADD COLUMN expanded INTEGER DEFAULT 0")
            except Exception:
                pass
        self.conn.commit()
        self.conn.commit()

    def add_task(self, title, parent_id=None):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO tasks (parent_id, title, created_at) VALUES (?, ?, ?)",
            (parent_id, title, datetime.now(timezone.utc).isoformat()),
        )
        self.conn.commit()
        return cur.lastrowid


    def set_expanded(self, task_id, expanded: bool):
        cur = self.conn.cursor()
        cur.execute("UPDATE tasks SET expanded = ? WHERE id = ?", (1 if expanded else 0, task_id))
        self.conn.commit()

    def clear_all_expanded(self):
        cur = self.conn.cursor()
        cur.execute("UPDATE tasks SET expanded = 0")
        self.conn.commit()

    def set_expanded_for_ids(self, ids):
        cur = self.conn.cursor()
        # clear then set
        cur.execute("UPDATE tasks SET expanded = 0")
        if ids:
            placeholders = ','.join('?' for _ in ids)
            cur.execute(f"UPDATE tasks SET expanded = 1 WHERE id IN ({placeholders})", tuple(ids))
        self.conn.commit()

    def get_expanded_set(self):
        cur = self.conn.cursor()
        rows = cur.execute("SELECT id FROM tasks WHERE expanded = 1").fetchall()
        return set(r['id'] for r in rows)

    def rename(self, task_id, title):
        cur = self.conn.cursor()
        cur.execute("UPDATE tasks SET title = ? WHERE id = ?", (title, task_id))
        self.conn.commit()

    def delete(self, task_id):
        cur = self.conn.cursor()
        # delete children recursively
        children = cur.execute("SELECT id FROM tasks WHERE parent_id = ?", (task_id,)).fetchall()
        for c in children:
            self.delete(c['id'])
        cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()

    def all_tasks(self):
        cur = self.conn.cursor()
        rows = cur.execute("SELECT * FROM tasks ORDER BY ord, created_at").fetchall()
        return [dict(r) for r in rows]


def build_tree(tasks):
    by_id = {t['id']: t for t in tasks}
    children = {}
    roots = []
    for t in tasks:
        pid = t['parent_id']
        if pid is None:
            roots.append(t['id'])
        else:
            children.setdefault(pid, []).append(t['id'])
    return by_id, children, roots


def flatten_for_menu(by_id, children, roots, expanded):
    entries = []
    ids = []

    def walk(tid, depth=0):
        t = by_id[tid]
        prefix = '  ' * depth
        # if has children and is collapsed, show count
        cnt = len(children.get(tid, []))
        label = t['title']
        if cnt and tid not in expanded:
            label = f"{label} [{cnt}]"
        entries.append(f"{prefix}{label}")
        ids.append(tid)
        # only walk into children if expanded
        if tid in expanded:
            for c in children.get(tid, []):
                walk(c, depth + 1)

    for r in roots:
        walk(r, 0)

    if not entries:
        entries = ['<sem tarefas>']
        ids = [None]
    return entries, ids


def simple_md_preview(text, width):
    # Minimal markdown -> plain preview: headings uppercased, lists bullet, paragraphs wrapped
    import textwrap
    out_lines = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            out_lines.append('')
            continue
        if s.startswith('#'):
            # heading
            heading = s.lstrip('#').strip().upper()
            out_lines.append(heading)
            out_lines.append('-' * min(len(heading), width))
            continue
        if s.startswith(('-', '*')):
            out_lines.extend(textwrap.wrap('• ' + s[1:].strip(), width))
            continue
        # bold/italic simple removal
        s = s.replace('**', '').replace('*', '')
        out_lines.extend(textwrap.wrap(s, width))
    return out_lines


def main():
    # On POSIX disable terminal flow control so Ctrl-S/Ctrl-Q are delivered
    try:
        subprocess.run(['stty', '-ixon'])
    except Exception:
        pass
    db = TaskDB()
    # expanded set: which task ids are currently expanded (showing children)
    expanded = db.get_expanded_set()
    try:
        while True:
            os.system('clear')
            tasks = db.all_tasks()
            by_id, children, roots = build_tree(tasks)
            entries, ids = flatten_for_menu(by_id, children, roots, expanded)

            header = 'Use ↑/↓ e Enter para selecionar.'
            status = 'Comandos: p:Add  s:Sub  r:Renomear  x:Deletar  o:Toggle  a:ExpandirTodas  h:OcultarTodas  q:Sair  Enter:Selecionar'

            menu = TerminalMenu(
                entries,
                title=header,
                accept_keys=["enter", "p", "s", "r", "x", "q", "o", "a", "h"],
                clear_screen=True,
                status_bar=status,
            )

            sel = menu.show()
            # chosen accept key when user pressed a configured shortcut while menu active
            chosen_key = getattr(menu, 'chosen_accept_key', None)

            # selected item id (can be None)
            selected_id = ids[sel] if sel is not None else None

            # If user pressed a shortcut key directly, use it as the command
            if chosen_key and chosen_key != 'enter':
                cmd = chosen_key
            else:
                # read single key for command (no Enter required)
                print('\nComandos: p=add raiz  s=add subtarefa  r=renomear  x=deletar  q=sair')
                print('Pressione a letra do comando: ', end='', flush=True)

                def read_single_key():
                    fd = sys.stdin.fileno()
                    old = termios.tcgetattr(fd)
                    try:
                        tty.setraw(fd)
                        ch = sys.stdin.read(1)
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old)
                    return ch

                cmd = read_single_key()
                print(cmd)

            # ----- new commands: toggle/show/hide subtasks -----
            if cmd == 'o':
                # toggle selected collapse/expand
                if selected_id is None:
                    input('\nNenhuma tarefa selecionada. Pressione Enter...')
                    continue
                if selected_id in expanded:
                    expanded.remove(selected_id)
                    db.set_expanded(selected_id, False)
                else:
                    expanded.add(selected_id)
                    db.set_expanded(selected_id, True)
                continue

            if cmd == 'a':
                # expand all parents that have children
                expanded = set(children.keys())
                db.set_expanded_for_ids(list(expanded))
                continue

            if cmd == 'h':
                # hide all
                expanded.clear()
                db.clear_all_expanded()
                continue
            if not cmd:
                continue
            cmd = cmd.lower()
            if cmd == 'q':
                break
            if cmd == 'p':
                title = input('\nTítulo (nível principal): ').strip()
                if title:
                    db.add_task(title, parent_id=None)
                continue
            if cmd == 's':
                if selected_id is None:
                    input('\nNenhuma tarefa selecionada para adicionar subtarefa. Pressione Enter...')
                    continue
                title = input('\nTítulo (subtarefa): ').strip()
                if title:
                    db.add_task(title, parent_id=selected_id)
                continue
            if cmd == 'r':
                if selected_id is None:
                    continue
                new = input('\nNovo título: ').strip()
                if new:
                    db.rename(selected_id, new)
                continue
            if cmd == 'x':
                if selected_id is None:
                    continue
                confirm = input('\nConfirma exclusão (y/N)? ').strip().lower()
                if confirm == 'y':
                    db.delete(selected_id)
                continue
            # details functionality removed
            else:
                input('\nComando não reconhecido. Pressione Enter...')
                continue
    finally:
        # restore flow control (best-effort)
        try:
            subprocess.run(['stty', 'ixon'])
        except Exception:
            pass


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nSaindo...')
