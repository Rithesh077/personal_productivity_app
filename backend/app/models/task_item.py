"""task item model — standalone priority list items.

Separate from the goal hierarchy. These are the DMN-rescue
queue items that exist independently of goals.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field


DEFAULT_TAGS = ["learning", "bug", "admin", "creative", "health", "urgent"]


def _new_id() -> str:
    return str(uuid.uuid4())


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class TaskItem(BaseModel):
    id: str = Field(default_factory=_new_id)
    title: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    linked_goal_id: str | None = None
    position: int = 0
    is_completed: bool = False
    created_at: str = Field(default_factory=_utc_now)
    completed_at: str | None = None
