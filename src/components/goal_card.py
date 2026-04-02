"""Goal card component for Stride - displays hierarchical goals with progress."""

import flet as ft
from typing import Callable

from models.goal import Goal, SubTask, Step
from utils.time_utils import relative_time, time_until_deadline, is_past_deadline

# Design tokens
TEAL = "#00D9A6"
AMBER = "#FFB547"
RED = "#FF5C5C"
CARD_BG = "#141927"
SURFACE = "#1E2436"
TEXT_PRIMARY = "#E0E0E0"
TEXT_SECONDARY = "#8A92A6"
TEXT_MUTED = "#5A6478"


def GoalCard(
    goal: Goal,
    on_toggle_goal: Callable[[str, bool], None],
    on_toggle_task: Callable[[str, str, bool], None],
    on_toggle_subtask: Callable[[str, str, str, bool], None],
    on_delete_goal: Callable[[str], None],
    on_edit_goal: Callable[[str], None],
    on_add_task: Callable[[str], None],
    expanded: bool = False,
    on_expand: Callable[[str], None] = None,
):
    """Create an expandable goal card with hierarchy and progress."""
    is_done = goal.is_completed
    pct = goal.completion_percentage()
    deadline_status = time_until_deadline(goal.deadline)
    is_overdue = is_past_deadline(goal.deadline) and not is_done

    # Progress color
    if is_done:
        progress_color = TEAL
    elif pct >= 75:
        progress_color = TEAL
    elif pct >= 40:
        progress_color = AMBER
    else:
        progress_color = RED if is_overdue else TEXT_MUTED

    # Header row with checkbox, title, progress, expand button
    header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Checkbox(
                    value=is_done,
                    active_color=TEAL,
                    check_color="#0B0F1A",
                    on_change=lambda e: on_toggle_goal(goal.id, e.control.value),
                ),
                ft.Column(
                    controls=[
                        ft.Text(
                            goal.title,
                            size=16,
                            weight=ft.FontWeight.W_600,
                            color=TEAL if is_done else TEXT_PRIMARY,
                            style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH) if is_done else None,
                            expand=True,
                        ),
                        ft.Row(
                            controls=[
                                ft.Text(
                                    f"{pct}%",
                                    size=12,
                                    color=progress_color,
                                    weight=ft.FontWeight.W_500,
                                ),
                                ft.Text("•", size=12, color=TEXT_MUTED),
                                ft.Text(
                                    relative_time(goal.created_at),
                                    size=12,
                                    color=TEXT_MUTED,
                                ),
                                ft.Text("•", size=12, color=TEXT_MUTED) if deadline_status else ft.Container(),
                                ft.Text(
                                    deadline_status,
                                    size=12,
                                    color=RED if is_overdue else TEXT_SECONDARY,
                                ) if deadline_status else ft.Container(),
                            ],
                            spacing=6,
                        ),
                    ],
                    spacing=2,
                    expand=True,
                ),
                ft.IconButton(
                    icon=ft.Icons.EXPAND_MORE_ROUNDED if not expanded else ft.Icons.EXPAND_LESS_ROUNDED,
                    icon_color=TEXT_SECONDARY,
                    icon_size=20,
                    on_click=lambda e: on_expand(goal.id) if on_expand else None,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.symmetric(horizontal=8, vertical=4),
        on_click=lambda e: on_expand(goal.id) if on_expand else None,
    )

    # Progress bar
    progress_bar = ft.Container(
        content=ft.ProgressBar(
            value=pct / 100,
            color=progress_color,
            bgcolor=SURFACE,
        ),
        padding=ft.Padding.only(left=48, right=8, bottom=8),
    )

    # Expanded content: tasks and sub-tasks
    expanded_content = []
    if expanded and goal.sub_tasks:
        for task in goal.sub_tasks:
            expanded_content.append(_build_task(
                goal.id, task, on_toggle_task, on_toggle_subtask
            ))

    # Action buttons when expanded
    actions = ft.Row(
        controls=[
            ft.TextButton(
                "Add Task",
                icon=ft.Icons.ADD_ROUNDED,
                on_click=lambda e: on_add_task(goal.id),
                style=ft.ButtonStyle(color=TEAL),
            ),
            ft.TextButton(
                "Edit",
                icon=ft.Icons.EDIT_ROUNDED,
                on_click=lambda e: on_edit_goal(goal.id),
                style=ft.ButtonStyle(color=TEXT_SECONDARY),
            ),
            ft.TextButton(
                "Delete",
                icon=ft.Icons.DELETE_ROUNDED,
                on_click=lambda e: on_delete_goal(goal.id),
                style=ft.ButtonStyle(color=RED),
            ),
        ],
        alignment=ft.MainAxisAlignment.END,
        spacing=0,
    ) if expanded else ft.Container()

    return ft.Container(
        content=ft.Column(
            controls=[
                header,
                progress_bar,
                *expanded_content,
                actions,
            ],
            spacing=0,
        ),
        bgcolor=CARD_BG,
        border_radius=12,
        border=ft.Border.all(1, TEAL if is_done else SURFACE),
        animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        margin=ft.Margin.only(bottom=8),
    )


def _build_task(
    goal_id: str,
    task: SubTask,
    on_toggle_task: Callable,
    on_toggle_subtask: Callable,
):
    """Build a task row with its sub-tasks (steps)."""
    is_done = task.is_completed
    pct = task.completion_percentage()

    subtasks_content = []
    for subtask in task.steps:
        subtasks_content.append(_build_subtask(
            goal_id, task.id, subtask, on_toggle_subtask))

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Checkbox(
                            value=is_done,
                            active_color=TEAL,
                            check_color="#0B0F1A",
                            scale=0.9,
                            on_change=lambda e, tid=task.id: on_toggle_task(
                                goal_id, tid, e.control.value
                            ),
                        ),
                        ft.Text(
                            task.title,
                            size=14,
                            color=TEAL if is_done else TEXT_PRIMARY,
                            style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH) if is_done else None,
                            expand=True,
                        ),
                        ft.Text(
                            f"{pct}%",
                            size=11,
                            color=TEAL if pct == 100 else TEXT_MUTED,
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                *subtasks_content,
            ],
            spacing=0,
        ),
        padding=ft.Padding.only(left=32, right=8, top=4, bottom=4),
        border=ft.Border(left=ft.BorderSide(2, SURFACE)),
    )


def _build_subtask(
    goal_id: str,
    task_id: str,
    subtask: Step,
    on_toggle_subtask: Callable,
):
    """Build a sub-task row (was called step)."""
    is_done = subtask.is_completed

    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Checkbox(
                    value=is_done,
                    active_color=TEAL,
                    check_color="#0B0F1A",
                    scale=0.8,
                    on_change=lambda e, stid=subtask.id: on_toggle_subtask(
                        goal_id, task_id, stid, e.control.value
                    ),
                ),
                ft.Text(
                    subtask.title,
                    size=13,
                    color=TEAL if is_done else TEXT_SECONDARY,
                    style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH) if is_done else None,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.only(left=24),
    )
