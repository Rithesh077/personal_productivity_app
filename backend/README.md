# Backend

Python + FastAPI. The data and logic layer for Stride.

Owns the planner logic (goals, tasks, subtasks, cascading completion), the priority task list, and analytics computation. Stores everything in SQLite.

## Setup

```bash
cd backend
uv sync
uvicorn app.main:app --reload --port 8000
```

## Structure

```
app/
├── main.py                # FastAPI app, CORS, lifespan
├── routes/
│   ├── goals.py           # /api/goals CRUD + task/subtask nesting
│   ├── tasks.py           # /api/task-list CRUD + reorder + complete
│   ├── analytics.py       # /api/analytics computed stats
│   └── tags.py            # /api/tags CRUD
├── models/
│   ├── goal.py            # Goal, Task, SubTask (Pydantic)
│   └── task_item.py       # TaskItem (Pydantic)
├── services/
│   └── database.py        # SQLite schema, triggers, CRUD
└── utils/
    ├── time_utils.py
    └── math_utils.py
stride.db                  # SQLite database (gitignored)
pyproject.toml
```

## Storage

SQLite with cascading completion via triggers (ADR-026). See `docs/ADR.md` for the full trigger definitions.

## Key design decisions

- **SQLite triggers** handle cascading completion (subtask done → auto-check task → auto-check goal). Route handlers don't contain cascade logic.
- **Every mutation returns the full updated Goal.** The frontend replaces its local state with the response. No partial merging.
- **Pydantic models** for serialization — FastAPI-native, replaces the old dataclass + `to_dict`/`from_dict` pattern.
