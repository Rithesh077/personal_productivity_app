"""Goal, Task (SubTask), and Sub-Task (Step) data models for Stride.

Hierarchy:
- Goal: The main objective
  - Task (internally SubTask): Major component of the goal
    - Sub-Task (internally Step): Detailed action item
"""

from dataclasses import dataclass, field, asdict
from typing import Optional
import uuid


@dataclass
class Step:
    """A sub-task within a task (displayed as 'Sub-Task' in UI)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    created_at: str = ""  # UTC ISO timestamp
    completed_at: Optional[str] = None  # UTC ISO timestamp
    is_completed: bool = False

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Step":
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            title=data.get("title", ""),
            created_at=data.get("created_at", ""),
            completed_at=data.get("completed_at"),
            is_completed=data.get("is_completed", False),
        )


@dataclass
class SubTask:
    """A task within a goal (displayed as 'Task' in UI), containing sub-tasks."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    created_at: str = ""  # UTC ISO timestamp
    completed_at: Optional[str] = None  # UTC ISO timestamp
    is_completed: bool = False
    steps: list[Step] = field(default_factory=list)  # steps = sub-tasks in UI

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "is_completed": self.is_completed,
            "steps": [s.to_dict() for s in self.steps],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SubTask":
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            title=data.get("title", ""),
            created_at=data.get("created_at", ""),
            completed_at=data.get("completed_at"),
            is_completed=data.get("is_completed", False),
            steps=[Step.from_dict(s) for s in data.get("steps", [])],
        )

    def completion_percentage(self) -> int:
        """Calculate completion percentage based on steps."""
        if not self.steps:
            return 100 if self.is_completed else 0
        completed = sum(1 for s in self.steps if s.is_completed)
        return int((completed / len(self.steps)) * 100)


@dataclass
class Goal:
    """A main goal containing tasks (displayed as 'Tasks' in UI)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    created_at: str = ""  # UTC ISO timestamp
    completed_at: Optional[str] = None  # UTC ISO timestamp
    deadline: Optional[str] = None  # UTC ISO timestamp
    is_completed: bool = False
    sub_tasks: list[SubTask] = field(default_factory=list)  # sub_tasks = tasks in UI

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "deadline": self.deadline,
            "is_completed": self.is_completed,
            "sub_tasks": [st.to_dict() for st in self.sub_tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Goal":
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            title=data.get("title", ""),
            created_at=data.get("created_at", ""),
            completed_at=data.get("completed_at"),
            deadline=data.get("deadline"),
            is_completed=data.get("is_completed", False),
            sub_tasks=[SubTask.from_dict(st)
                       for st in data.get("sub_tasks", [])],
        )

    def completion_percentage(self) -> int:
        """Calculate completion percentage based on sub-tasks and their steps."""
        if not self.sub_tasks:
            return 100 if self.is_completed else 0

        total_items = 0
        completed_items = 0

        for st in self.sub_tasks:
            if st.steps:
                total_items += len(st.steps)
                completed_items += sum(1 for s in st.steps if s.is_completed)
            else:
                total_items += 1
                if st.is_completed:
                    completed_items += 1

        return int((completed_items / total_items) * 100) if total_items > 0 else 0

    def mark_complete(self, completed_at: str):
        """Mark goal and all children as complete."""
        self.is_completed = True
        self.completed_at = completed_at
        for st in self.sub_tasks:
            st.is_completed = True
            st.completed_at = completed_at
            for step in st.steps:
                step.is_completed = True
                step.completed_at = completed_at

    def mark_incomplete(self):
        """Mark goal and all children as incomplete."""
        self.is_completed = False
        self.completed_at = None
        for st in self.sub_tasks:
            st.is_completed = False
            st.completed_at = None
            for step in st.steps:
                step.is_completed = False
                step.completed_at = None
