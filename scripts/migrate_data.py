#!/usr/bin/env python3
"""migrate data from the Flet PWA's localStorage JSON export into the new SQLite database.

Usage:
    1. Open the deployed Flet PWA in your browser
    2. Open DevTools → Console
    3. Run:
         copy(JSON.stringify({
           goals: JSON.parse(localStorage.getItem('stride.goals') || '[]'),
           schema_version: localStorage.getItem('stride.schema_version'),
           task_list: JSON.parse(localStorage.getItem('stride.task_list') || '[]'),
           task_list_completed: JSON.parse(localStorage.getItem('stride.task_list_completed') || '[]'),
           custom_tags: JSON.parse(localStorage.getItem('stride.custom_tags') || '[]'),
         }))
    4. Paste into a file: data/export.json
    5. Run: python scripts/migrate_data.py data/export.json
"""

import json
import sys
import uuid
from pathlib import Path

# add backend to path so we can import the database module
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.services.database import init_db, get_db, DB_PATH
from app.models.goal import Goal, Task, SubTask
from app.models.task_item import TaskItem


def migrate(export_path: str) -> None:
    data = json.loads(Path(export_path).read_text())

    print(f"Loaded export from: {export_path}")
    print(f"  Goals:           {len(data.get('goals', []))}")
    print(f"  Task list:       {len(data.get('task_list', []))}")
    print(f"  Completed tasks: {len(data.get('task_list_completed', []))}")
    print(f"  Custom tags:     {len(data.get('custom_tags', []))}")
    print()

    # initialize the database
    init_db()
    print(f"Database initialized at: {DB_PATH}")

    with get_db() as conn:
        # ── Goals ────────────────────────────────
        for g in data.get("goals", []):
            tasks = []
            for i, t in enumerate(g.get("tasks", [])):
                subtasks = []
                for j, st in enumerate(t.get("sub_tasks", [])):
                    subtasks.append(SubTask(
                        id=st.get("id", str(uuid.uuid4())),
                        title=st["title"],
                        position=st.get("position", j),
                        is_completed=st.get("is_completed", False),
                        created_at=st.get("created_at", ""),
                        updated_at=st.get("updated_at"),
                        completed_at=st.get("completed_at"),
                    ))
                tasks.append(Task(
                    id=t.get("id", str(uuid.uuid4())),
                    title=t["title"],
                    position=t.get("position", i),
                    is_completed=t.get("is_completed", False),
                    created_at=t.get("created_at", ""),
                    updated_at=t.get("updated_at"),
                    completed_at=t.get("completed_at"),
                    sub_tasks=subtasks,
                ))

            goal = Goal(
                id=g.get("id", str(uuid.uuid4())),
                title=g["title"],
                is_completed=g.get("is_completed", False),
                created_at=g.get("created_at", ""),
                updated_at=g.get("updated_at"),
                completed_at=g.get("completed_at"),
                deadline=g.get("deadline"),
                has_custom_deadline=g.get("has_custom_deadline", False),
                tasks=tasks,
            )

            # insert goal
            conn.execute(
                """INSERT OR REPLACE INTO goals
                   (id, title, is_completed, created_at, updated_at,
                    completed_at, deadline, has_custom_deadline)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (goal.id, goal.title, int(goal.is_completed),
                 goal.created_at, goal.updated_at, goal.completed_at,
                 goal.deadline, int(goal.has_custom_deadline)),
            )

            for task in goal.tasks:
                conn.execute(
                    """INSERT OR REPLACE INTO tasks
                       (id, goal_id, title, position, is_completed,
                        created_at, updated_at, completed_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (task.id, goal.id, task.title, task.position,
                     int(task.is_completed), task.created_at,
                     task.updated_at, task.completed_at),
                )
                for st in task.sub_tasks:
                    conn.execute(
                        """INSERT OR REPLACE INTO subtasks
                           (id, task_id, title, position, is_completed,
                            created_at, updated_at, completed_at)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (st.id, task.id, st.title, st.position,
                         int(st.is_completed), st.created_at,
                         st.updated_at, st.completed_at),
                    )

            print(f"  ✓ Goal: {goal.title} ({len(goal.tasks)} tasks)")

        # ── Task list (active) ───────────────────
        for i, item in enumerate(data.get("task_list", [])):
            tags = item.get("tags", [])
            if isinstance(tags, str):
                tags = json.loads(tags)
            conn.execute(
                """INSERT OR REPLACE INTO task_list_items
                   (id, title, description, tags, linked_goal_id,
                    position, is_completed, created_at, completed_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (item.get("id", str(uuid.uuid4())),
                 item["title"],
                 item.get("description", ""),
                 json.dumps(tags),
                 item.get("linked_goal_id"),
                 item.get("position", i),
                 0,
                 item.get("created_at", ""),
                 None),
            )
            print(f"  ✓ Task: {item['title']}")

        # ── Task list (completed) ────────────────
        for i, item in enumerate(data.get("task_list_completed", [])):
            tags = item.get("tags", [])
            if isinstance(tags, str):
                tags = json.loads(tags)
            conn.execute(
                """INSERT OR REPLACE INTO task_list_items
                   (id, title, description, tags, linked_goal_id,
                    position, is_completed, created_at, completed_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (item.get("id", str(uuid.uuid4())),
                 item["title"],
                 item.get("description", ""),
                 json.dumps(tags),
                 item.get("linked_goal_id"),
                 item.get("position", i),
                 1,
                 item.get("created_at", ""),
                 item.get("completed_at")),
            )

        if data.get("task_list_completed"):
            print(f"  ✓ {len(data['task_list_completed'])} completed tasks")

        # ── Custom tags ──────────────────────────
        for tag in data.get("custom_tags", []):
            conn.execute(
                "INSERT OR IGNORE INTO custom_tags (tag) VALUES (?)",
                (tag,),
            )

        if data.get("custom_tags"):
            print(f"  ✓ {len(data['custom_tags'])} custom tags")

    print()
    print("Migration complete.")
    print(f"Database: {DB_PATH}")
    print(f"Start the new stack: ./scripts/dev.sh")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    migrate(sys.argv[1])
