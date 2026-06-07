"""data model: task list item for the priority tasks list."""

from dataclasses import dataclass, field, asdict
from typing import Optional
import uuid


# predefined tag options (user can also add custom tags)
DEFAULT_TAGS = ["learning", "bug", "admin", "creative", "health", "urgent"]


@dataclass
class TaskItem:
    """a single item in the priority tasks list.

    represents an immediate, actionable task that the user can pull
    from when they need to redirect attention away from low-quality
    input or default-mode-network drift.

    optionally linked to a goal from the planner.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)
    linked_goal_id: Optional[str] = None
    position: int = 0
    created_at: str = ""
    completed_at: Optional[str] = None
    is_completed: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "tags": list(self.tags),
            "linked_goal_id": self.linked_goal_id,
            "position": self.position,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "is_completed": self.is_completed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TaskItem":
        return cls(
            id=data.get("id") or str(uuid.uuid4()),
            title=data.get("title", ""),
            description=data.get("description", ""),
            tags=data.get("tags", []),
            linked_goal_id=data.get("linked_goal_id"),
            position=data.get("position", 0),
            created_at=data.get("created_at", ""),
            completed_at=data.get("completed_at"),
            is_completed=data.get("is_completed", False),
        )
