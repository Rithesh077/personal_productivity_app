"""Client storage abstraction for Stride using SharedPreferences.

Note: SharedPreferences only supports str, int, float, bool, list[str].
We serialize goals to JSON string for storage.
"""

import json
from typing import Optional
from models.goal import Goal

STORAGE_KEY = "stride.goals"


async def save_goals(page, goals: list[Goal]):
    """Save all goals to client storage as JSON string."""
    data = [g.to_dict() for g in goals]
    json_str = json.dumps(data)
    await page.shared_preferences.set(STORAGE_KEY, json_str)


async def load_goals(page) -> list[Goal]:
    """Load all goals from client storage."""
    json_str = await page.shared_preferences.get(STORAGE_KEY)
    if not json_str:
        return []
    try:
        data = json.loads(json_str)
        return [Goal.from_dict(g) for g in data]
    except (json.JSONDecodeError, TypeError):
        return []


async def save_goal(page, goal: Goal):
    """Save or update a single goal."""
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
    await page.shared_preferences.remove(STORAGE_KEY)

