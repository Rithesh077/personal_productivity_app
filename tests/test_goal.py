"""tests for the goal model — completion logic, cascading, serialization."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from models.goal import Goal, Task, SubTask


class TestSubTask:
    """subtask model tests."""

    def test_defaults(self):
        st = SubTask(title="test")
        assert st.title == "test"
        assert st.is_completed is False
        assert st.completed_at is None
        assert st.position == 0

    def test_roundtrip_serialization(self):
        st = SubTask(id="abc", title="do thing", created_at="2026-01-01T00:00:00+00:00",
                     is_completed=True, completed_at="2026-01-02T00:00:00+00:00", position=3)
        data = st.to_dict()
        restored = SubTask.from_dict(data)
        assert restored.id == "abc"
        assert restored.title == "do thing"
        assert restored.is_completed is True
        assert restored.position == 3

    def test_from_dict_missing_fields(self):
        """from_dict handles missing fields gracefully."""
        st = SubTask.from_dict({"title": "minimal"})
        assert st.title == "minimal"
        assert st.is_completed is False
        assert st.id  # should auto-generate

    def test_from_dict_empty_id_generates_new(self):
        st = SubTask.from_dict({"id": "", "title": "test"})
        assert st.id  # should not be empty
        assert st.id != ""


class TestTask:
    """task model tests."""

    def test_completion_percentage_no_subtasks(self):
        t = Task(title="test", is_completed=False)
        assert t.completion_percentage() == 0
        t.is_completed = True
        assert t.completion_percentage() == 100

    def test_completion_percentage_with_subtasks(self):
        t = Task(title="test", sub_tasks=[
            SubTask(title="a", is_completed=True),
            SubTask(title="b", is_completed=False),
            SubTask(title="c", is_completed=True),
        ])
        assert t.completion_percentage() == 66  # 2/3 = 66%

    def test_completion_percentage_all_done(self):
        t = Task(title="test", sub_tasks=[
            SubTask(title="a", is_completed=True),
            SubTask(title="b", is_completed=True),
        ])
        assert t.completion_percentage() == 100

    def test_completion_percentage_none_done(self):
        t = Task(title="test", sub_tasks=[
            SubTask(title="a", is_completed=False),
            SubTask(title="b", is_completed=False),
        ])
        assert t.completion_percentage() == 0

    def test_roundtrip_serialization(self):
        t = Task(id="t1", title="build auth", sub_tasks=[
            SubTask(id="s1", title="jwt"),
            SubTask(id="s2", title="login page", is_completed=True),
        ])
        data = t.to_dict()
        restored = Task.from_dict(data)
        assert restored.id == "t1"
        assert len(restored.sub_tasks) == 2
        assert restored.sub_tasks[1].is_completed is True

    def test_backwards_compat_steps_key(self):
        """old 'steps' key should deserialize as sub_tasks."""
        data = {
            "title": "old task",
            "steps": [{"title": "step 1"}, {"title": "step 2"}],
        }
        t = Task.from_dict(data)
        assert len(t.sub_tasks) == 2
        assert t.sub_tasks[0].title == "step 1"


class TestGoal:
    """goal model tests."""

    def test_completion_percentage_no_tasks(self):
        g = Goal(title="empty", is_completed=False)
        assert g.completion_percentage() == 0
        g.is_completed = True
        assert g.completion_percentage() == 100

    def test_completion_percentage_flat_tasks(self):
        """tasks without subtasks: each task counts as 1 item."""
        g = Goal(title="test", tasks=[
            Task(title="a", is_completed=True),
            Task(title="b", is_completed=False),
        ])
        assert g.completion_percentage() == 50

    def test_completion_percentage_nested(self):
        """subtask-level counting: subtasks are the atoms, not tasks."""
        g = Goal(title="test", tasks=[
            Task(title="a", sub_tasks=[
                SubTask(title="a1", is_completed=True),
                SubTask(title="a2", is_completed=True),
            ]),
            Task(title="b", sub_tasks=[
                SubTask(title="b1", is_completed=False),
                SubTask(title="b2", is_completed=False),
            ]),
        ])
        # 2 out of 4 subtasks done = 50%
        assert g.completion_percentage() == 50

    def test_completion_percentage_mixed(self):
        """mix of tasks with and without subtasks."""
        g = Goal(title="test", tasks=[
            Task(title="flat", is_completed=True),  # counts as 1/1
            Task(title="nested", sub_tasks=[
                SubTask(title="n1", is_completed=True),
                SubTask(title="n2", is_completed=False),
            ]),  # counts as 1/2
        ])
        # total: 2 out of 3 = 66%
        assert g.completion_percentage() == 66

    def test_mark_complete_cascades(self):
        g = Goal(title="test", tasks=[
            Task(title="t1", sub_tasks=[
                SubTask(title="s1"),
                SubTask(title="s2"),
            ]),
            Task(title="t2"),
        ])
        g.mark_complete("2026-01-01T00:00:00+00:00")

        assert g.is_completed is True
        assert g.completed_at == "2026-01-01T00:00:00+00:00"
        assert all(t.is_completed for t in g.tasks)
        assert all(t.completed_at == "2026-01-01T00:00:00+00:00" for t in g.tasks)
        assert all(st.is_completed for t in g.tasks for st in t.sub_tasks)

    def test_mark_incomplete_preserves_children(self):
        g = Goal(title="test", is_completed=True, completed_at="2026-01-01T00:00:00+00:00",
                 tasks=[
                     Task(title="t1", is_completed=True, completed_at="2026-01-01T00:00:00+00:00"),
                 ])
        g.mark_incomplete()

        assert g.is_completed is False
        assert g.completed_at is None
        # children stay completed (mark_incomplete only affects the goal)
        assert g.tasks[0].is_completed is True

    def test_roundtrip_serialization(self):
        g = Goal(
            id="g1", title="launch", deadline="2026-12-31T23:59:59+00:00",
            has_custom_deadline=True,
            tasks=[
                Task(id="t1", title="build", sub_tasks=[
                    SubTask(id="s1", title="code"),
                ]),
            ],
        )
        data = g.to_dict()
        restored = Goal.from_dict(data)
        assert restored.id == "g1"
        assert restored.has_custom_deadline is True
        assert len(restored.tasks) == 1
        assert len(restored.tasks[0].sub_tasks) == 1

    def test_backwards_compat_sub_tasks_key(self):
        """old 'sub_tasks' key at goal level should deserialize as tasks."""
        data = {
            "title": "old goal",
            "sub_tasks": [{"title": "old task 1"}],
        }
        g = Goal.from_dict(data)
        assert len(g.tasks) == 1
        assert g.tasks[0].title == "old task 1"

    def test_from_dict_missing_fields(self):
        g = Goal.from_dict({"title": "minimal"})
        assert g.title == "minimal"
        assert g.is_completed is False
        assert g.has_custom_deadline is False
        assert g.tasks == []
        assert g.id  # auto-generated
