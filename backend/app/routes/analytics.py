"""analytics routes — computed stats for goals and task list."""

from fastapi import APIRouter

from app.services.database import (
    get_db, load_goals, load_task_list, load_completed_task_items,
)
from app.utils.time_utils import (
    is_past_deadline, was_completed_before_deadline, was_same_day_execution,
)
from app.utils.math_utils import safe_percentage

router = APIRouter(tags=["analytics"])


@router.get("/analytics/goals")
def goal_analytics():
    """computed analytics for the goal hierarchy."""
    with get_db() as conn:
        goals = load_goals(conn)

    total = len(goals)
    completed = sum(1 for g in goals if g.is_completed)
    active = total - completed
    overdue = sum(
        1 for g in goals
        if not g.is_completed and is_past_deadline(g.deadline)
    )

    # per-level stats
    goal_stats = _empty_stats()
    task_stats = _empty_stats()
    subtask_stats = _empty_stats()

    for goal in goals:
        has_custom = goal.has_custom_deadline
        _count_item(goal_stats, goal.is_completed, has_custom,
                    goal.completed_at, goal.deadline,
                    goal.created_at, goal.completed_at)

        for task in goal.tasks:
            _count_item(task_stats, task.is_completed, has_custom,
                        task.completed_at, goal.deadline,
                        task.created_at, task.completed_at)

            for subtask in task.sub_tasks:
                _count_item(subtask_stats, subtask.is_completed, has_custom,
                            subtask.completed_at, goal.deadline,
                            subtask.created_at, subtask.completed_at)

    completion_pct = safe_percentage(completed, total)
    on_time_pct = safe_percentage(
        goal_stats["on_time"], goal_stats["custom_deadline_count"]
    )
    same_day_pct = safe_percentage(
        goal_stats["same_day"], goal_stats["default_deadline_count"]
    )

    return {
        "summary": {
            "total": total,
            "active": active,
            "completed": completed,
            "overdue": overdue,
        },
        "performance": {
            "completion_pct": completion_pct,
            "on_time_pct": on_time_pct,
            "same_day_pct": same_day_pct,
            "has_custom_deadlines": goal_stats["custom_deadline_count"] > 0,
            "has_default_deadlines": goal_stats["default_deadline_count"] > 0,
        },
        "by_level": {
            "goals": goal_stats,
            "tasks": task_stats,
            "subtasks": subtask_stats,
        },
        "recent_goals": [
            {
                "id": g.id,
                "title": g.title,
                "completion_pct": g.completion_percentage(),
                "is_completed": g.is_completed,
                "is_overdue": is_past_deadline(g.deadline) and not g.is_completed,
                "has_custom_deadline": g.has_custom_deadline,
                "on_time": (
                    was_completed_before_deadline(g.completed_at, g.deadline)
                    if g.is_completed and g.has_custom_deadline else None
                ),
                "same_day": (
                    was_same_day_execution(g.created_at, g.completed_at)
                    if g.is_completed and not g.has_custom_deadline else None
                ),
            }
            for g in sorted(goals, key=lambda g: g.created_at, reverse=True)[:5]
        ],
    }


@router.get("/analytics/task-list")
def task_list_analytics():
    """computed analytics for the priority task list."""
    with get_db() as conn:
        active_items = load_task_list(conn)
        completed_items = load_completed_task_items(conn)

    # tag breakdown
    tag_counts: dict[str, int] = {}
    for item in completed_items:
        for tag in item.tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # average time in list
    total_seconds = 0
    valid_count = 0
    for item in completed_items:
        if item.created_at and item.completed_at:
            try:
                from app.utils.time_utils import parse_iso
                created = parse_iso(item.created_at)
                completed = parse_iso(item.completed_at)
                if created and completed:
                    diff = completed - created
                    total_seconds += diff.total_seconds()
                    valid_count += 1
            except Exception:
                pass

    avg_seconds = total_seconds / valid_count if valid_count > 0 else 0

    return {
        "active_count": len(active_items),
        "completed_count": len(completed_items),
        "avg_time_seconds": avg_seconds,
        "tag_breakdown": dict(
            sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        ),
        "completed_items": [
            item.model_dump() for item in completed_items[:10]
        ],
    }


def _empty_stats() -> dict:
    return {
        "total": 0, "completed": 0, "on_time": 0, "same_day": 0,
        "custom_deadline_count": 0, "default_deadline_count": 0,
    }


def _count_item(
    stats: dict,
    is_completed: bool,
    has_custom_deadline: bool,
    completed_at: str | None,
    deadline: str | None,
    created_at: str | None,
    item_completed_at: str | None,
) -> None:
    """accumulate stats for a single item."""
    stats["total"] += 1
    if has_custom_deadline:
        stats["custom_deadline_count"] += 1
    else:
        stats["default_deadline_count"] += 1

    if is_completed:
        stats["completed"] += 1
        if has_custom_deadline:
            if was_completed_before_deadline(completed_at, deadline):
                stats["on_time"] += 1
        else:
            if was_same_day_execution(created_at, item_completed_at):
                stats["same_day"] += 1
