"""data models: goal > task > subtask hierarchy."""

from dataclasses import dataclass, field, asdict
from typing import Optional
import uuid


@dataclass
class SubTask:
    """lowest level item within a task."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    created_at: str = ""
    updated_at: Optional[str] = None
    completed_at: Optional[str] = None
    is_completed: bool = False
    position: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "SubTask":
        return cls(
            id=data.get("id") or str(uuid.uuid4()),
            title=data.get("title", ""),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at"),
            completed_at=data.get("completed_at"),
            is_completed=data.get("is_completed", False),
            position=data.get("position", 0),
        )


@dataclass
class Task:
    """mid-level item within a goal, contains subtasks."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    created_at: str = ""
    updated_at: Optional[str] = None
    completed_at: Optional[str] = None
    is_completed: bool = False
    position: int = 0
    sub_tasks: list[SubTask] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "is_completed": self.is_completed,
            "position": self.position,
            "sub_tasks": [s.to_dict() for s in self.sub_tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        # backwards compat: old key was 'steps'
        sub_tasks_data = data.get("sub_tasks", data.get("steps", []))
        return cls(
            id=data.get("id") or str(uuid.uuid4()),
            title=data.get("title", ""),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at"),
            completed_at=data.get("completed_at"),
            is_completed=data.get("is_completed", False),
            position=data.get("position", 0),
            sub_tasks=[SubTask.from_dict(s) for s in sub_tasks_data],
        )

    def completion_percentage(self) -> int:
        if not self.sub_tasks:
            return 100 if self.is_completed else 0
        completed = sum(1 for s in self.sub_tasks if s.is_completed)
        return int((completed / len(self.sub_tasks)) * 100)


@dataclass
class Goal:
    """top-level objective containing tasks."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    created_at: str = ""
    updated_at: Optional[str] = None
    completed_at: Optional[str] = None
    deadline: Optional[str] = None
    has_custom_deadline: bool = False
    is_completed: bool = False
    tasks: list[Task] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "deadline": self.deadline,
            "has_custom_deadline": self.has_custom_deadline,
            "is_completed": self.is_completed,
            "tasks": [t.to_dict() for t in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Goal":
        # backwards compat: old key was 'sub_tasks'
        tasks_data = data.get("tasks", data.get("sub_tasks", []))
        return cls(
            id=data.get("id") or str(uuid.uuid4()),
            title=data.get("title", ""),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at"),
            completed_at=data.get("completed_at"),
            deadline=data.get("deadline"),
            has_custom_deadline=data.get("has_custom_deadline", False),
            is_completed=data.get("is_completed", False),
            tasks=[Task.from_dict(t) for t in tasks_data],
        )

    def completion_percentage(self) -> int:
        if not self.tasks:
            return 100 if self.is_completed else 0

        total_items = 0
        completed_items = 0

        for t in self.tasks:
            if t.sub_tasks:
                total_items += len(t.sub_tasks)
                completed_items += sum(1 for st in t.sub_tasks if st.is_completed)
            else:
                total_items += 1
                if t.is_completed:
                    completed_items += 1

        return int((completed_items / total_items) * 100) if total_items > 0 else 0

    def mark_complete(self, completed_at: str):
        """mark goal and all children as complete."""
        self.is_completed = True
        self.completed_at = completed_at
        for t in self.tasks:
            t.is_completed = True
            t.completed_at = completed_at
            for st in t.sub_tasks:
                st.is_completed = True
                st.completed_at = completed_at

    def mark_incomplete(self):
        """mark goal as incomplete, preserves child progress."""
        self.is_completed = False
        self.completed_at = None
