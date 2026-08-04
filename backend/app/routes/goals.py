"""goals routes — CRUD for goals, tasks, and subtasks.

Every mutation returns the full updated Goal. The frontend
replaces its local state with the response (no partial merging).
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.goal import Goal, Task, SubTask
from app.services.database import (
    get_db, load_goals, get_goal, save_goal, delete_goal,
)
from app.utils.time_utils import utc_now

router = APIRouter(tags=["goals"])


# ── Request schemas ──────────────────────────────────────────────


class CreateGoalRequest(BaseModel):
    title: str
    deadline: str | None = None
    has_custom_deadline: bool = False
    tasks: list[Task] | None = None


class UpdateGoalRequest(BaseModel):
    title: str | None = None
    deadline: str | None = None
    has_custom_deadline: bool | None = None


class ToggleRequest(BaseModel):
    value: bool


class TitleRequest(BaseModel):
    title: str


class MoveRequest(BaseModel):
    direction: int


# ── Goal routes ──────────────────────────────────────────────────


@router.get("/goals", response_model=list[Goal])
def list_goals():
    with get_db() as conn:
        return load_goals(conn)


@router.post("/goals", response_model=Goal, status_code=201)
def create_goal(req: CreateGoalRequest):
    goal = Goal(
        title=req.title,
        deadline=req.deadline,
        has_custom_deadline=req.has_custom_deadline,
        tasks=req.tasks or [],
    )
    with get_db() as conn:
        return save_goal(conn, goal)


@router.get("/goals/{goal_id}", response_model=Goal)
def read_goal(goal_id: str):
    with get_db() as conn:
        goal = get_goal(conn, goal_id)
        if not goal:
            raise HTTPException(404, "Goal not found")
        return goal


@router.put("/goals/{goal_id}", response_model=Goal)
def update_goal(goal_id: str, req: UpdateGoalRequest):
    with get_db() as conn:
        goal = get_goal(conn, goal_id)
        if not goal:
            raise HTTPException(404, "Goal not found")
        if req.title is not None:
            goal.title = req.title
        if req.deadline is not None:
            goal.deadline = req.deadline
        if req.has_custom_deadline is not None:
            goal.has_custom_deadline = req.has_custom_deadline
        goal.updated_at = utc_now()
        return save_goal(conn, goal)


@router.delete("/goals/{goal_id}", status_code=204)
def remove_goal(goal_id: str):
    with get_db() as conn:
        if not delete_goal(conn, goal_id):
            raise HTTPException(404, "Goal not found")


@router.patch("/goals/{goal_id}/complete", response_model=Goal)
def toggle_goal_completion(goal_id: str, req: ToggleRequest):
    with get_db() as conn:
        goal = get_goal(conn, goal_id)
        if not goal:
            raise HTTPException(404, "Goal not found")
        now = utc_now()
        goal.is_completed = req.value
        goal.completed_at = now if req.value else None
        if req.value:
            for task in goal.tasks:
                task.is_completed = True
                task.completed_at = task.completed_at or now
                for st in task.sub_tasks:
                    st.is_completed = True
                    st.completed_at = st.completed_at or now
        else:
            for task in goal.tasks:
                task.is_completed = False
                task.completed_at = None
                for st in task.sub_tasks:
                    st.is_completed = False
                    st.completed_at = None
        return save_goal(conn, goal)


@router.patch("/goals/{goal_id}/deadline", response_model=Goal)
def update_deadline(goal_id: str, req: UpdateGoalRequest):
    with get_db() as conn:
        goal = get_goal(conn, goal_id)
        if not goal:
            raise HTTPException(404, "Goal not found")
        goal.deadline = req.deadline
        goal.has_custom_deadline = req.has_custom_deadline or False
        goal.updated_at = utc_now()
        return save_goal(conn, goal)


# ── Task routes (nested under goals) ────────────────────────────


@router.post("/goals/{goal_id}/tasks", response_model=Goal, status_code=201)
def add_task(goal_id: str, req: TitleRequest):
    with get_db() as conn:
        goal = get_goal(conn, goal_id)
        if not goal:
            raise HTTPException(404, "Goal not found")
        goal.tasks.append(
            Task(title=req.title, position=len(goal.tasks))
        )
        goal.is_completed = False
        goal.completed_at = None
        return save_goal(conn, goal)


@router.put("/goals/{goal_id}/tasks/{task_id}", response_model=Goal)
def update_task(goal_id: str, task_id: str, req: TitleRequest):
    with get_db() as conn:
        goal = get_goal(conn, goal_id)
        if not goal:
            raise HTTPException(404, "Goal not found")
        task = next((t for t in goal.tasks if t.id == task_id), None)
        if not task:
            raise HTTPException(404, "Task not found")
        task.title = req.title
        task.updated_at = utc_now()
        return save_goal(conn, goal)


@router.delete("/goals/{goal_id}/tasks/{task_id}", response_model=Goal)
def remove_task(goal_id: str, task_id: str):
    with get_db() as conn:
        goal = get_goal(conn, goal_id)
        if not goal:
            raise HTTPException(404, "Goal not found")
        goal.tasks = [t for t in goal.tasks if t.id != task_id]
        for idx, t in enumerate(goal.tasks):
            t.position = idx
        # check if remaining tasks are all done
        if goal.tasks and all(t.is_completed for t in goal.tasks):
            goal.is_completed = True
            goal.completed_at = goal.completed_at or utc_now()
        return save_goal(conn, goal)


@router.patch("/goals/{goal_id}/tasks/{task_id}/complete", response_model=Goal)
def toggle_task_completion(goal_id: str, task_id: str, req: ToggleRequest):
    with get_db() as conn:
        goal = get_goal(conn, goal_id)
        if not goal:
            raise HTTPException(404, "Goal not found")
        now = utc_now()
        task = next((t for t in goal.tasks if t.id == task_id), None)
        if not task:
            raise HTTPException(404, "Task not found")
        task.is_completed = req.value
        task.completed_at = now if req.value else None
        for st in task.sub_tasks:
            st.is_completed = req.value
            st.completed_at = now if req.value else None
        # triggers handle goal auto-complete, but we set it here too
        # for the returned Goal to be correct
        if req.value and all(t.is_completed for t in goal.tasks):
            goal.is_completed = True
            goal.completed_at = now
        elif not req.value:
            goal.is_completed = False
            goal.completed_at = None
        return save_goal(conn, goal)


@router.patch(
    "/goals/{goal_id}/tasks/{task_id}/move", response_model=Goal
)
def move_task(goal_id: str, task_id: str, req: MoveRequest):
    with get_db() as conn:
        goal = get_goal(conn, goal_id)
        if not goal:
            raise HTTPException(404, "Goal not found")
        idx = next((i for i, t in enumerate(goal.tasks) if t.id == task_id), None)
        if idx is None:
            raise HTTPException(404, "Task not found")
        new_idx = idx + req.direction
        if 0 <= new_idx < len(goal.tasks):
            goal.tasks[idx], goal.tasks[new_idx] = goal.tasks[new_idx], goal.tasks[idx]
            for i, t in enumerate(goal.tasks):
                t.position = i
        return save_goal(conn, goal)


# ── Subtask routes (nested under tasks) ──────────────────────────


@router.post(
    "/goals/{goal_id}/tasks/{task_id}/subtasks",
    response_model=Goal, status_code=201,
)
def add_subtask(goal_id: str, task_id: str, req: TitleRequest):
    with get_db() as conn:
        goal = get_goal(conn, goal_id)
        if not goal:
            raise HTTPException(404, "Goal not found")
        task = next((t for t in goal.tasks if t.id == task_id), None)
        if not task:
            raise HTTPException(404, "Task not found")
        task.sub_tasks.append(
            SubTask(title=req.title, position=len(task.sub_tasks))
        )
        task.is_completed = False
        task.completed_at = None
        goal.is_completed = False
        goal.completed_at = None
        return save_goal(conn, goal)


@router.put(
    "/goals/{goal_id}/tasks/{task_id}/subtasks/{subtask_id}",
    response_model=Goal,
)
def update_subtask(goal_id: str, task_id: str, subtask_id: str, req: TitleRequest):
    with get_db() as conn:
        goal = get_goal(conn, goal_id)
        if not goal:
            raise HTTPException(404, "Goal not found")
        task = next((t for t in goal.tasks if t.id == task_id), None)
        if not task:
            raise HTTPException(404, "Task not found")
        st = next((s for s in task.sub_tasks if s.id == subtask_id), None)
        if not st:
            raise HTTPException(404, "Subtask not found")
        st.title = req.title
        st.updated_at = utc_now()
        return save_goal(conn, goal)


@router.delete(
    "/goals/{goal_id}/tasks/{task_id}/subtasks/{subtask_id}",
    response_model=Goal,
)
def remove_subtask(goal_id: str, task_id: str, subtask_id: str):
    with get_db() as conn:
        goal = get_goal(conn, goal_id)
        if not goal:
            raise HTTPException(404, "Goal not found")
        task = next((t for t in goal.tasks if t.id == task_id), None)
        if not task:
            raise HTTPException(404, "Task not found")
        task.sub_tasks = [s for s in task.sub_tasks if s.id != subtask_id]
        for idx, s in enumerate(task.sub_tasks):
            s.position = idx
        if task.sub_tasks and all(s.is_completed for s in task.sub_tasks):
            task.is_completed = True
            task.completed_at = task.completed_at or utc_now()
        if goal.tasks and all(t.is_completed for t in goal.tasks):
            goal.is_completed = True
            goal.completed_at = goal.completed_at or utc_now()
        return save_goal(conn, goal)


@router.patch(
    "/goals/{goal_id}/tasks/{task_id}/subtasks/{subtask_id}/complete",
    response_model=Goal,
)
def toggle_subtask_completion(
    goal_id: str, task_id: str, subtask_id: str, req: ToggleRequest
):
    with get_db() as conn:
        goal = get_goal(conn, goal_id)
        if not goal:
            raise HTTPException(404, "Goal not found")
        now = utc_now()
        task = next((t for t in goal.tasks if t.id == task_id), None)
        if not task:
            raise HTTPException(404, "Task not found")
        st = next((s for s in task.sub_tasks if s.id == subtask_id), None)
        if not st:
            raise HTTPException(404, "Subtask not found")
        st.is_completed = req.value
        st.completed_at = now if req.value else None
        # auto-complete task if all subtasks done
        if req.value and all(s.is_completed for s in task.sub_tasks):
            task.is_completed = True
            task.completed_at = now
        elif not req.value:
            task.is_completed = False
            task.completed_at = None
        # auto-complete goal if all tasks done
        if task.is_completed and all(t.is_completed for t in goal.tasks):
            goal.is_completed = True
            goal.completed_at = now
        elif not req.value:
            goal.is_completed = False
            goal.completed_at = None
        return save_goal(conn, goal)


@router.patch(
    "/goals/{goal_id}/tasks/{task_id}/subtasks/{subtask_id}/move",
    response_model=Goal,
)
def move_subtask(
    goal_id: str, task_id: str, subtask_id: str, req: MoveRequest
):
    with get_db() as conn:
        goal = get_goal(conn, goal_id)
        if not goal:
            raise HTTPException(404, "Goal not found")
        task = next((t for t in goal.tasks if t.id == task_id), None)
        if not task:
            raise HTTPException(404, "Task not found")
        idx = next(
            (i for i, s in enumerate(task.sub_tasks) if s.id == subtask_id), None
        )
        if idx is None:
            raise HTTPException(404, "Subtask not found")
        new_idx = idx + req.direction
        if 0 <= new_idx < len(task.sub_tasks):
            task.sub_tasks[idx], task.sub_tasks[new_idx] = (
                task.sub_tasks[new_idx], task.sub_tasks[idx],
            )
            for i, s in enumerate(task.sub_tasks):
                s.position = i
        return save_goal(conn, goal)
