"""task list routes — priority queue CRUD."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.task_item import TaskItem
from app.services.database import (
    get_db, load_task_list, load_completed_task_items,
    save_task_item, delete_task_item, reorder_task_list,
    clear_completed_task_items,
)
from app.utils.time_utils import utc_now

router = APIRouter(tags=["task-list"])


class CreateTaskItemRequest(BaseModel):
    title: str
    description: str = ""
    tags: list[str] = []
    linked_goal_id: str | None = None


class UpdateTaskItemRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    linked_goal_id: str | None = None


class ReorderRequest(BaseModel):
    new_position: int


@router.get("/task-list", response_model=list[TaskItem])
def list_task_items():
    with get_db() as conn:
        return load_task_list(conn)


@router.post("/task-list", response_model=TaskItem, status_code=201)
def create_task_item(req: CreateTaskItemRequest):
    with get_db() as conn:
        existing = load_task_list(conn)
        item = TaskItem(
            title=req.title,
            description=req.description,
            tags=req.tags,
            linked_goal_id=req.linked_goal_id,
            position=len(existing),
        )
        return save_task_item(conn, item)


@router.put("/task-list/{item_id}", response_model=TaskItem)
def update_task_item(item_id: str, req: UpdateTaskItemRequest):
    with get_db() as conn:
        items = load_task_list(conn)
        item = next((i for i in items if i.id == item_id), None)
        if not item:
            raise HTTPException(404, "Task item not found")
        if req.title is not None:
            item.title = req.title
        if req.description is not None:
            item.description = req.description
        if req.tags is not None:
            item.tags = req.tags
        if req.linked_goal_id is not None:
            item.linked_goal_id = req.linked_goal_id
        return save_task_item(conn, item)


@router.delete("/task-list/{item_id}", status_code=204)
def remove_task_item(item_id: str):
    with get_db() as conn:
        if not delete_task_item(conn, item_id):
            raise HTTPException(404, "Task item not found")


@router.patch("/task-list/{item_id}/complete", response_model=TaskItem)
def complete_task_item(item_id: str):
    with get_db() as conn:
        items = load_task_list(conn)
        item = next((i for i in items if i.id == item_id), None)
        if not item:
            raise HTTPException(404, "Task item not found")
        item.is_completed = True
        item.completed_at = utc_now()
        return save_task_item(conn, item)


@router.patch("/task-list/reorder", response_model=list[TaskItem])
def reorder_items(item_id: str, req: ReorderRequest):
    with get_db() as conn:
        return reorder_task_list(conn, item_id, req.new_position)


@router.get("/task-list/completed", response_model=list[TaskItem])
def list_completed_items():
    with get_db() as conn:
        return load_completed_task_items(conn)


@router.delete("/task-list/completed", status_code=204)
def clear_completed():
    with get_db() as conn:
        clear_completed_task_items(conn)
