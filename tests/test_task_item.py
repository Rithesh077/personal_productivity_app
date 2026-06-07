"""tests for the task item model — serialization, defaults."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from models.task_item import TaskItem, DEFAULT_TAGS


class TestTaskItem:
    """task item model tests."""

    def test_defaults(self):
        item = TaskItem(title="learn redis")
        assert item.title == "learn redis"
        assert item.description == ""
        assert item.tags == []
        assert item.linked_goal_id is None
        assert item.position == 0
        assert item.is_completed is False
        assert item.completed_at is None

    def test_with_all_fields(self):
        item = TaskItem(
            title="fix bug",
            description="login redirect issue",
            tags=["bug", "urgent"],
            linked_goal_id="goal-123",
            position=2,
            created_at="2026-06-07T10:00:00+00:00",
        )
        assert item.tags == ["bug", "urgent"]
        assert item.linked_goal_id == "goal-123"
        assert item.position == 2

    def test_roundtrip_serialization(self):
        item = TaskItem(
            id="item-1",
            title="refactor auth",
            description="move to middleware",
            tags=["admin", "creative"],
            linked_goal_id="goal-456",
            position=1,
            created_at="2026-06-07T10:00:00+00:00",
            completed_at="2026-06-07T12:00:00+00:00",
            is_completed=True,
        )
        data = item.to_dict()
        restored = TaskItem.from_dict(data)

        assert restored.id == "item-1"
        assert restored.title == "refactor auth"
        assert restored.description == "move to middleware"
        assert restored.tags == ["admin", "creative"]
        assert restored.linked_goal_id == "goal-456"
        assert restored.position == 1
        assert restored.is_completed is True
        assert restored.completed_at == "2026-06-07T12:00:00+00:00"

    def test_from_dict_missing_fields(self):
        """from_dict handles minimal data gracefully."""
        item = TaskItem.from_dict({"title": "quick task"})
        assert item.title == "quick task"
        assert item.tags == []
        assert item.linked_goal_id is None
        assert item.is_completed is False
        assert item.id  # auto-generated

    def test_from_dict_empty_id_generates_new(self):
        item = TaskItem.from_dict({"id": "", "title": "test"})
        assert item.id
        assert item.id != ""

    def test_from_dict_empty_dict(self):
        """completely empty dict should not crash."""
        item = TaskItem.from_dict({})
        assert item.title == ""
        assert item.tags == []

    def test_tags_are_independent_copies(self):
        """to_dict should create a copy of tags, not a reference."""
        item = TaskItem(title="test", tags=["bug"])
        data = item.to_dict()
        data["tags"].append("admin")
        assert item.tags == ["bug"]  # original unmodified


class TestDefaultTags:
    """verify default tag list."""

    def test_default_tags_exist(self):
        assert "learning" in DEFAULT_TAGS
        assert "bug" in DEFAULT_TAGS
        assert "admin" in DEFAULT_TAGS
        assert "creative" in DEFAULT_TAGS
        assert "health" in DEFAULT_TAGS
        assert "urgent" in DEFAULT_TAGS

    def test_default_tags_count(self):
        assert len(DEFAULT_TAGS) == 6
