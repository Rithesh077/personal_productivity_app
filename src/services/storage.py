"""Client storage abstraction for Stride using SharedPreferences.

Note: SharedPreferences only supports str, int, float, bool, list[str].
We serialize goals to JSON string for storage.
"""

import json
from typing import Optional
import uuid
from models.goal import Goal
import flet as ft

STORAGE_KEY = "stride.goals"


def _ensure_id(value: Optional[str]) -> str:
    """Return an existing ID or generate a new one."""
    return value or str(uuid.uuid4())


def _normalize_goal(goal: Goal) -> Goal:
    """Ensure IDs and positions are present before saving."""
    goal.id = _ensure_id(goal.id)

    for task_idx, task in enumerate(goal.tasks):
        task.id = _ensure_id(task.id)
        task.position = task_idx

        for subtask_idx, subtask in enumerate(task.sub_tasks):
            subtask.id = _ensure_id(subtask.id)
            subtask.position = subtask_idx

    return goal


async def save_goals(page, goals: list[Goal]):
    """Save all goals to client storage as JSON string."""
    data = [_normalize_goal(g).to_dict() for g in goals]
    json_str = json.dumps(data)
    prefs = ft.SharedPreferences()
    await prefs.set(STORAGE_KEY, json_str)


async def load_goals(page) -> list[Goal]:
    """Load all goals from client storage."""
    prefs = ft.SharedPreferences()
    json_str = await prefs.get(STORAGE_KEY)
    if not json_str:
        return []
    try:
        data = json.loads(json_str)
        return [Goal.from_dict(g) for g in data]
    except (json.JSONDecodeError, TypeError):
        return []


async def save_goal(page, goal: Goal):
    """Save or update a single goal."""
    goal = _normalize_goal(goal)
    goals = await load_goals(page)
    # Find and replace if exists, otherwise append
    found = False
    for i, g in enumerate(goals):
        if g.id == goal.id:
            goals[i] = goal
            found = True
            break
    if not found:
        goals.insert(0, goal)  # New goals at the top
    await save_goals(page, goals)


async def delete_goal(page, goal_id: str):
    """Delete a goal by ID."""
    goals = await load_goals(page)
    goals = [g for g in goals if g.id != goal_id]
    await save_goals(page, goals)


async def get_goal(page, goal_id: str) -> Optional[Goal]:
    """Get a single goal by ID."""
    goals = await load_goals(page)
    for g in goals:
        if g.id == goal_id:
            return g
    return None


async def clear_all_goals(page):
    """Clear all goals from storage."""
    prefs = ft.SharedPreferences()
    await prefs.remove(STORAGE_KEY)
