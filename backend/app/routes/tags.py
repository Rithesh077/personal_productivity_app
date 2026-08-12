"""tags routes — custom tag management."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.models.task_item import DEFAULT_TAGS
from app.services.database import (
    get_db, load_custom_tags, save_custom_tag, delete_custom_tag,
)

router = APIRouter(tags=["tags"])


class TagRequest(BaseModel):
    tag: str


@router.get("/tags")
def list_tags():
    """returns default tags + custom tags."""
    with get_db() as conn:
        custom = load_custom_tags(conn)
    return {
        "default": DEFAULT_TAGS,
        "custom": custom,
        "all": DEFAULT_TAGS + custom,
    }


@router.post("/tags")
def add_tag(req: TagRequest):
    with get_db() as conn:
        custom = save_custom_tag(conn, req.tag)
    return {
        "default": DEFAULT_TAGS,
        "custom": custom,
        "all": DEFAULT_TAGS + custom,
    }


@router.delete("/tags/{tag}")
def remove_tag(tag: str):
    with get_db() as conn:
        custom = delete_custom_tag(conn, tag)
    return {
        "default": DEFAULT_TAGS,
        "custom": custom,
        "all": DEFAULT_TAGS + custom,
    }
