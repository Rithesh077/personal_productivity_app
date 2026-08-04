"""goal models — Goal, Task, SubTask hierarchy.

Framework-independent dataclasses. Serialization uses pydantic
for FastAPI compatibility, but the classes themselves carry no
framework dependency beyond that.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field


def _new_id() -> str:
    return str(uuid.uuid4())


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── SubTask ──────────────────────────────────────────────────────


class SubTask(BaseModel):
    id: str = Field(default_factory=_new_id)
    title: str
    position: int = 0
    is_completed: bool = False
    created_at: str = Field(default_factory=_utc_now)
    updated_at: str | None = None
    completed_at: str | None = None


# ── Task ─────────────────────────────────────────────────────────


class Task(BaseModel):
    id: str = Field(default_factory=_new_id)
    title: str
    position: int = 0
    is_completed: bool = False
    created_at: str = Field(default_factory=_utc_now)
    updated_at: str | None = None
    completed_at: str | None = None
    sub_tasks: list[SubTask] = Field(default_factory=list)


# ── Goal ─────────────────────────────────────────────────────────


class Goal(BaseModel):
    id: str = Field(default_factory=_new_id)
    title: str
    is_completed: bool = False
    created_at: str = Field(default_factory=_utc_now)
    updated_at: str | None = None
    completed_at: str | None = None
    deadline: str | None = None
    has_custom_deadline: bool = False
    tasks: list[Task] = Field(default_factory=list)

    def completion_percentage(self) -> int:
        """percentage of completed sub-items across all tasks."""
        total = 0
        completed = 0
        for task in self.tasks:
            if task.sub_tasks:
                total += len(task.sub_tasks)
                completed += sum(1 for s in task.sub_tasks if s.is_completed)
            else:
                total += 1
                completed += 1 if task.is_completed else 0
        if total == 0:
            return 100 if self.is_completed else 0
        return int(completed / total * 100)
