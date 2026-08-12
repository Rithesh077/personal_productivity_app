"""SQLite database service.

Manages schema creation, triggers for cascading completion,
and all CRUD operations. Single-file database, portable.

Triggers (ADR-026) handle cascading completion logic that was
previously scattered across planner.py view closures.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from app.models.goal import Goal, Task, SubTask
from app.models.task_item import TaskItem
from app.utils.time_utils import utc_now

SCHEMA_VERSION = 1
DB_PATH = Path(__file__).parent.parent.parent / "stride.db"


# ── Connection management ────────────────────────────────────────


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """create a connection with WAL mode and foreign keys enabled."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def get_db(db_path: Path = DB_PATH) -> Generator[sqlite3.Connection, None, None]:
    """context manager for database transactions."""
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ── Schema ───────────────────────────────────────────────────────


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS goals (
    id                  TEXT PRIMARY KEY,
    title               TEXT NOT NULL,
    is_completed        INTEGER DEFAULT 0,
    created_at          TEXT NOT NULL,
    updated_at          TEXT,
    completed_at        TEXT,
    deadline            TEXT,
    has_custom_deadline INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS tasks (
    id              TEXT PRIMARY KEY,
    goal_id         TEXT NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
    title           TEXT NOT NULL,
    position        INTEGER DEFAULT 0,
    is_completed    INTEGER DEFAULT 0,
    created_at      TEXT NOT NULL,
    updated_at      TEXT,
    completed_at    TEXT
);

CREATE TABLE IF NOT EXISTS subtasks (
    id              TEXT PRIMARY KEY,
    task_id         TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    title           TEXT NOT NULL,
    position        INTEGER DEFAULT 0,
    is_completed    INTEGER DEFAULT 0,
    created_at      TEXT NOT NULL,
    updated_at      TEXT,
    completed_at    TEXT
);

CREATE TABLE IF NOT EXISTS task_list_items (
    id              TEXT PRIMARY KEY,
    title           TEXT NOT NULL,
    description     TEXT DEFAULT '',
    tags            TEXT DEFAULT '[]',
    linked_goal_id  TEXT,
    position        INTEGER DEFAULT 0,
    is_completed    INTEGER DEFAULT 0,
    created_at      TEXT NOT NULL,
    completed_at    TEXT
);

CREATE TABLE IF NOT EXISTS custom_tags (
    tag TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER NOT NULL
);
"""

# ── Triggers (ADR-026) ──────────────────────────────────────────

TRIGGERS_SQL = """
-- when all subtasks of a task are completed, auto-complete the task
CREATE TRIGGER IF NOT EXISTS auto_complete_task
AFTER UPDATE OF is_completed ON subtasks
WHEN NEW.is_completed = 1
BEGIN
    UPDATE tasks SET
        is_completed = 1,
        completed_at = datetime('now')
    WHERE id = NEW.task_id
      AND NOT EXISTS (
          SELECT 1 FROM subtasks
          WHERE task_id = NEW.task_id AND is_completed = 0
      );
END;

-- when all tasks of a goal are completed, auto-complete the goal
CREATE TRIGGER IF NOT EXISTS auto_complete_goal
AFTER UPDATE OF is_completed ON tasks
WHEN NEW.is_completed = 1
BEGIN
    UPDATE goals SET
        is_completed = 1,
        completed_at = datetime('now')
    WHERE id = NEW.goal_id
      AND NOT EXISTS (
          SELECT 1 FROM tasks
          WHERE goal_id = NEW.goal_id AND is_completed = 0
      );
END;

-- when a subtask is uncompleted, uncomplete its parent task
CREATE TRIGGER IF NOT EXISTS uncomplete_task_on_subtask
AFTER UPDATE OF is_completed ON subtasks
WHEN NEW.is_completed = 0
BEGIN
    UPDATE tasks SET is_completed = 0, completed_at = NULL
    WHERE id = NEW.task_id AND is_completed = 1;
END;

-- when a task is uncompleted, uncomplete its parent goal
CREATE TRIGGER IF NOT EXISTS uncomplete_goal_on_task
AFTER UPDATE OF is_completed ON tasks
WHEN NEW.is_completed = 0
BEGIN
    UPDATE goals SET is_completed = 0, completed_at = NULL
    WHERE id = NEW.goal_id AND is_completed = 1;
END;

-- when a task is completed directly (not via subtask trigger),
-- also complete all its subtasks
CREATE TRIGGER IF NOT EXISTS cascade_complete_subtasks
AFTER UPDATE OF is_completed ON tasks
WHEN NEW.is_completed = 1
BEGIN
    UPDATE subtasks SET
        is_completed = 1,
        completed_at = COALESCE(completed_at, datetime('now'))
    WHERE task_id = NEW.id AND is_completed = 0;
END;

-- when a task is uncompleted directly, uncomplete all its subtasks
CREATE TRIGGER IF NOT EXISTS cascade_uncomplete_subtasks
AFTER UPDATE OF is_completed ON tasks
WHEN NEW.is_completed = 0
BEGIN
    UPDATE subtasks SET is_completed = 0, completed_at = NULL
    WHERE task_id = NEW.id AND is_completed = 1;
END;
"""


def init_db(db_path: Path = DB_PATH) -> None:
    """create tables, triggers, and set schema version."""
    with get_db(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
        conn.executescript(TRIGGERS_SQL)
        existing = conn.execute(
            "SELECT version FROM schema_version LIMIT 1"
        ).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO schema_version (version) VALUES (?)",
                (SCHEMA_VERSION,),
            )


# ── Goal CRUD ────────────────────────────────────────────────────


def _row_to_subtask(row: sqlite3.Row) -> SubTask:
    return SubTask(
        id=row["id"],
        title=row["title"],
        position=row["position"],
        is_completed=bool(row["is_completed"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        completed_at=row["completed_at"],
    )


def _row_to_task(row: sqlite3.Row, subtasks: list[SubTask]) -> Task:
    return Task(
        id=row["id"],
        title=row["title"],
        position=row["position"],
        is_completed=bool(row["is_completed"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        completed_at=row["completed_at"],
        sub_tasks=subtasks,
    )


def _load_goal_from_db(conn: sqlite3.Connection, goal_row: sqlite3.Row) -> Goal:
    """assemble a full Goal with tasks and subtasks from db rows."""
    goal_id = goal_row["id"]
    task_rows = conn.execute(
        "SELECT * FROM tasks WHERE goal_id = ? ORDER BY position",
        (goal_id,),
    ).fetchall()

    tasks = []
    for tr in task_rows:
        subtask_rows = conn.execute(
            "SELECT * FROM subtasks WHERE task_id = ? ORDER BY position",
            (tr["id"],),
        ).fetchall()
        subtasks = [_row_to_subtask(sr) for sr in subtask_rows]
        tasks.append(_row_to_task(tr, subtasks))

    return Goal(
        id=goal_row["id"],
        title=goal_row["title"],
        is_completed=bool(goal_row["is_completed"]),
        created_at=goal_row["created_at"],
        updated_at=goal_row["updated_at"],
        completed_at=goal_row["completed_at"],
        deadline=goal_row["deadline"],
        has_custom_deadline=bool(goal_row["has_custom_deadline"]),
        tasks=tasks,
    )


def load_goals(conn: sqlite3.Connection) -> list[Goal]:
    """load all goals with their full hierarchy."""
    goal_rows = conn.execute(
        "SELECT * FROM goals ORDER BY is_completed ASC, created_at DESC"
    ).fetchall()
    return [_load_goal_from_db(conn, gr) for gr in goal_rows]


def get_goal(conn: sqlite3.Connection, goal_id: str) -> Goal | None:
    """load a single goal by ID with full hierarchy."""
    row = conn.execute("SELECT * FROM goals WHERE id = ?", (goal_id,)).fetchone()
    if row is None:
        return None
    return _load_goal_from_db(conn, row)


def save_goal(conn: sqlite3.Connection, goal: Goal) -> Goal:
    """insert or replace a goal and all its children.

    Uses a delete-and-reinsert strategy for children to handle
    additions, deletions, and reordering cleanly.
    """
    conn.execute(
        """INSERT INTO goals (id, title, is_completed, created_at, updated_at,
           completed_at, deadline, has_custom_deadline)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(id) DO UPDATE SET
               title=excluded.title,
               is_completed=excluded.is_completed,
               updated_at=excluded.updated_at,
               completed_at=excluded.completed_at,
               deadline=excluded.deadline,
               has_custom_deadline=excluded.has_custom_deadline""",
        (
            goal.id, goal.title, int(goal.is_completed), goal.created_at,
            goal.updated_at, goal.completed_at, goal.deadline,
            int(goal.has_custom_deadline),
        ),
    )

    # delete existing children and reinsert (handles reordering + deletions)
    conn.execute("DELETE FROM tasks WHERE goal_id = ?", (goal.id,))

    for task in goal.tasks:
        conn.execute(
            """INSERT INTO tasks (id, goal_id, title, position, is_completed,
               created_at, updated_at, completed_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                task.id, goal.id, task.title, task.position,
                int(task.is_completed), task.created_at,
                task.updated_at, task.completed_at,
            ),
        )
        for subtask in task.sub_tasks:
            conn.execute(
                """INSERT INTO subtasks (id, task_id, title, position, is_completed,
                   created_at, updated_at, completed_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    subtask.id, task.id, subtask.title, subtask.position,
                    int(subtask.is_completed), subtask.created_at,
                    subtask.updated_at, subtask.completed_at,
                ),
            )

    return get_goal(conn, goal.id)


def delete_goal(conn: sqlite3.Connection, goal_id: str) -> bool:
    """delete a goal and all children (CASCADE handles tasks/subtasks)."""
    cursor = conn.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
    return cursor.rowcount > 0


# ── Task List CRUD ───────────────────────────────────────────────


def _row_to_task_item(row: sqlite3.Row) -> TaskItem:
    return TaskItem(
        id=row["id"],
        title=row["title"],
        description=row["description"] or "",
        tags=json.loads(row["tags"]) if row["tags"] else [],
        linked_goal_id=row["linked_goal_id"],
        position=row["position"],
        is_completed=bool(row["is_completed"]),
        created_at=row["created_at"],
        completed_at=row["completed_at"],
    )


def load_task_list(conn: sqlite3.Connection) -> list[TaskItem]:
    """load active (non-completed) task list items."""
    rows = conn.execute(
        "SELECT * FROM task_list_items WHERE is_completed = 0 ORDER BY position"
    ).fetchall()
    return [_row_to_task_item(r) for r in rows]


def load_completed_task_items(conn: sqlite3.Connection) -> list[TaskItem]:
    """load completed task list items, newest first."""
    rows = conn.execute(
        "SELECT * FROM task_list_items WHERE is_completed = 1 ORDER BY completed_at DESC"
    ).fetchall()
    return [_row_to_task_item(r) for r in rows]


def save_task_item(conn: sqlite3.Connection, item: TaskItem) -> TaskItem:
    """insert or update a task list item."""
    conn.execute(
        """INSERT INTO task_list_items (id, title, description, tags,
           linked_goal_id, position, is_completed, created_at, completed_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(id) DO UPDATE SET
               title=excluded.title,
               description=excluded.description,
               tags=excluded.tags,
               linked_goal_id=excluded.linked_goal_id,
               position=excluded.position,
               is_completed=excluded.is_completed,
               completed_at=excluded.completed_at""",
        (
            item.id, item.title, item.description, json.dumps(item.tags),
            item.linked_goal_id, item.position, int(item.is_completed),
            item.created_at, item.completed_at,
        ),
    )
    row = conn.execute(
        "SELECT * FROM task_list_items WHERE id = ?", (item.id,)
    ).fetchone()
    return _row_to_task_item(row)


def delete_task_item(conn: sqlite3.Connection, item_id: str) -> bool:
    """delete a task list item."""
    cursor = conn.execute("DELETE FROM task_list_items WHERE id = ?", (item_id,))
    return cursor.rowcount > 0


def reorder_task_list(
    conn: sqlite3.Connection, item_id: str, new_position: int
) -> list[TaskItem]:
    """move an item to a new position and reindex others."""
    items = load_task_list(conn)
    source_idx = next((i for i, it in enumerate(items) if it.id == item_id), None)
    if source_idx is None:
        return items

    item = items.pop(source_idx)
    new_position = max(0, min(new_position, len(items)))
    items.insert(new_position, item)

    for idx, it in enumerate(items):
        conn.execute(
            "UPDATE task_list_items SET position = ? WHERE id = ?",
            (idx, it.id),
        )

    return load_task_list(conn)


def clear_completed_task_items(conn: sqlite3.Connection) -> None:
    """delete all completed task list items."""
    conn.execute("DELETE FROM task_list_items WHERE is_completed = 1")


# ── Tags CRUD ────────────────────────────────────────────────────


def load_custom_tags(conn: sqlite3.Connection) -> list[str]:
    """load user-created custom tags."""
    rows = conn.execute("SELECT tag FROM custom_tags ORDER BY tag").fetchall()
    return [r["tag"] for r in rows]


def save_custom_tag(conn: sqlite3.Connection, tag: str) -> list[str]:
    """add a custom tag, returns updated list."""
    conn.execute(
        "INSERT OR IGNORE INTO custom_tags (tag) VALUES (?)", (tag,)
    )
    return load_custom_tags(conn)


def delete_custom_tag(conn: sqlite3.Connection, tag: str) -> list[str]:
    """remove a custom tag, returns updated list."""
    conn.execute("DELETE FROM custom_tags WHERE tag = ?", (tag,))
    return load_custom_tags(conn)
