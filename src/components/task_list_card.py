"""task list card component — card for a single priority task list item."""

import flet as ft
from typing import Callable, Optional

from models.task_item import TaskItem
from constants.design import (
    TEAL, RED, CARD_BG, SURFACE, BG,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    TAG_COLORS, MUTED,
)
from utils.time_utils import relative_time


def TaskListCard(
    item: TaskItem,
    is_next: bool,
    linked_goal_title: Optional[str],
    on_complete: Callable[[str], None],
    on_delete: Callable[[str], None],
    on_edit: Callable[[str], None],
):
    """card for a single task list item.

    is_next=True gives the position-0 item a highlighted 'NEXT UP' style.
    """

    # tag chips
    tag_chips = []
    for tag in item.tags:
        color = TAG_COLORS.get(tag, MUTED)
        is_urgent = tag == "urgent"
        tag_chips.append(
            ft.Container(
                content=ft.Text(
                    tag,
                    size=10,
                    color=color,
                    weight=ft.FontWeight.BOLD if is_urgent else ft.FontWeight.W_500,
                ),
                bgcolor=f"{color}18",
                border_radius=6,
                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
            )
        )

    # goal link chip
    if linked_goal_title:
        tag_chips.append(
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.LINK_ROUNDED, size=10, color=TEXT_SECONDARY),
                        ft.Text(
                            linked_goal_title if len(linked_goal_title) <= 20
                            else linked_goal_title[:20] + "...",
                            size=10, color=TEXT_SECONDARY,
                        ),
                    ],
                    spacing=3,
                ),
                bgcolor=f"{SURFACE}",
                border_radius=6,
                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
            )
        )

    # title
    title_text = ft.Text(
        item.title,
        size=15 if is_next else 14,
        weight=ft.FontWeight.W_600,
        color=TEXT_PRIMARY,
        expand=True,
    )

    # description
    description_row = ft.Container()
    if item.description:
        description_row = ft.Text(
            item.description,
            size=12,
            color=TEXT_SECONDARY,
            max_lines=2,
        )

    # "NEXT UP" badge for position 0
    next_up_badge = ft.Container()
    if is_next:
        next_up_badge = ft.Container(
            content=ft.Text(
                "NEXT UP",
                size=9,
                weight=ft.FontWeight.BOLD,
                color=TEAL,
            ),
            bgcolor=f"{TEAL}18",
            border_radius=4,
            padding=ft.Padding.symmetric(horizontal=6, vertical=2),
        )

    # complete button
    complete_btn = ft.IconButton(
        icon=ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED,
        icon_color=TEAL if is_next else TEXT_MUTED,
        icon_size=22,
        on_click=lambda e: on_complete(item.id),
        tooltip="Complete",
    )

    # popup menu (edit + delete)
    popup_menu = ft.PopupMenuButton(
        icon=ft.Icons.MORE_VERT_ROUNDED,
        icon_color=TEXT_MUTED,
        icon_size=18,
        items=[
            ft.PopupMenuItem(
                content=ft.Text("Edit"),
                icon=ft.Icons.EDIT_ROUNDED,
                on_click=lambda e: on_edit(item.id),
            ),
            ft.PopupMenuItem(
                content=ft.Text("Delete"),
                icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                on_click=lambda e: on_delete(item.id),
            ),
        ],
    )

    # created time
    time_text = ft.Text(
        relative_time(item.created_at),
        size=11,
        color=TEXT_MUTED,
    )

    # card content
    card_content = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    title_text,
                    next_up_badge,
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            *([] if not item.description else [description_row]),
            ft.Row(
                controls=[
                    *(tag_chips if tag_chips else []),
                    ft.Container(expand=True),
                    time_text,
                ],
                spacing=6,
                wrap=True,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ],
        spacing=4,
    )

    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(content=card_content, expand=True),
                ft.Column(
                    controls=[complete_btn, popup_menu],
                    spacing=0,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=4,
        ),
        bgcolor=CARD_BG,
        border_radius=12,
        border=ft.Border.all(
            2 if is_next else 1,
            TEAL if is_next else SURFACE,
        ),
        padding=ft.Padding.symmetric(horizontal=14, vertical=12),
        animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
    )
