"""client storage using SharedPreferences.

stores goals as json string in browser localStorage.
includes schema versioning so data survives app updates.
"""

import json
from typing import Optional
import uuid
from models.goal import Goal
import flet as ft

STORAGE_KEY = "stride.goals"
SCHEMA_KEY = "stride.schema_version"
SCHEMA_VERSION = 1

# skip repeated migration checks after first load
_migration_done = False


def _ensure_id(value: Optional[str]) -> str:
    return value or str(uuid.uuid4())


def _normalize_goal(goal: Goal) -> Goal:
    """ensure ids and positions are set before saving."""
    goal.id = _ensure_id(goal.id)
    for task_idx, task in enumerate(goal.tasks):
        task.id = _ensure_id(task.id)
        task.position = task_idx
        for subtask_idx, subtask in enumerate(task.sub_tasks):
            subtask.id = _ensure_id(subtask.id)
            subtask.position = subtask_idx
    return goal


async def _run_migrations(page) -> None:
    """run schema migrations if data version is behind.

    each version bump can transform stored json. from_dict
    handles missing fields with defaults, so additive changes
    (new fields) need no migration -- just bump SCHEMA_VERSION.

    destructive changes (renames, type changes) need an explicit
    migration block that loads, transforms, and saves the raw json.
    """
    global _migration_done
    if _migration_done:
        return

    prefs = ft.SharedPreferences()
    version_str = await prefs.get(SCHEMA_KEY)
    current = int(version_str) if version_str else 0

    if current < SCHEMA_VERSION:
        # v0 -> v1: initial stamp, no structural changes.
        # from_dict already handles missing fields.

        # future migrations:
        # if current < 2:
        #     raw = await prefs.get(STORAGE_KEY)
        #     if raw:
        #         data = json.loads(raw)
        #         for goal in data:
        #             goal["new_field"] = "default"
        #         await prefs.set(STORAGE_KEY, json.dumps(data))

        await prefs.set(SCHEMA_KEY, str(SCHEMA_VERSION))

    _migration_done = True


async def save_goals(page, goals: list[Goal]):
    """save all goals to client storage."""
    data = [_normalize_goal(g).to_dict() for g in goals]
    prefs = ft.SharedPreferences()
    await prefs.set(STORAGE_KEY, json.dumps(data))


async def load_goals(page) -> list[Goal]:
    """load all goals from client storage."""
    await _run_migrations(page)
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
    """save or update a single goal."""
    goal = _normalize_goal(goal)
    goals = await load_goals(page)
    found = False
    for i, g in enumerate(goals):
        if g.id == goal.id:
            goals[i] = goal
            found = True
            break
    if not found:
        goals.insert(0, goal)
    await save_goals(page, goals)


async def delete_goal(page, goal_id: str):
    """delete a goal by id."""
    goals = await load_goals(page)
    goals = [g for g in goals if g.id != goal_id]
    await save_goals(page, goals)


async def get_goal(page, goal_id: str) -> Optional[Goal]:
    """get a single goal by id."""
    goals = await load_goals(page)
    for g in goals:
        if g.id == goal_id:
            return g
    return None


async def clear_all_goals(page):
    """clear all goals from storage."""
    prefs = ft.SharedPreferences()
    await prefs.remove(STORAGE_KEY)
