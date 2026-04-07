"""Goal card component for Stride - displays hierarchical goals with progress."""

import flet as ft
from typing import Callable, Optional

from models.goal import Goal, Task, SubTask
from utils.time_utils import (
    relative_time,
    time_until_deadline,
    is_past_deadline,
    format_local_datetime,
)

# Design tokens
TEAL = "#00D9A6"
AMBER = "#FFB547"
RED = "#FF5C5C"
CARD_BG = "#141927"
SURFACE = "#1E2436"
TEXT_PRIMARY = "#E0E0E0"
TEXT_SECONDARY = "#8A92A6"
TEXT_MUTED = "#5A6478"
BG = "#0B0F1A"


def GoalCard(
    goal: Goal,
    on_toggle_goal: Callable[[str, bool], None],
    on_toggle_task: Callable[[str, str, bool], None],
    on_toggle_subtask: Callable[[str, str, str, bool], None],
    on_delete_goal: Callable[[str], None],
    on_edit_goal: Callable[[str, str], None],
    on_edit_task: Callable[[str, str, str], None],
    on_edit_subtask: Callable[[str, str, str, str], None],
    on_delete_task: Callable[[str, str], None],
    on_delete_subtask: Callable[[str, str, str], None],
    on_move_task: Callable[[str, str, int], None],
    on_move_subtask: Callable[[str, str, str, int], None],
    on_add_task_inline: Callable[[str, str], None],
    on_add_subtask_inline: Callable[[str, str, str], None],
    on_change_deadline: Callable[[str], None],
    expanded: bool = False,
    on_expand: Callable[[str], None] = None,
    page: ft.Page = None,
):
    """Create an expandable goal card with hierarchy and progress."""
    is_done = goal.is_completed
    pct = goal.completion_percentage()
    deadline_status = time_until_deadline(goal.deadline)
    is_overdue = is_past_deadline(goal.deadline) and not is_done

    if is_done:
        progress_color = TEAL
    elif pct >= 75:
        progress_color = TEAL
    elif pct >= 40:
        progress_color = AMBER
    else:
        progress_color = RED if is_overdue else TEXT_MUTED

    # ── Metadata row ────────────────────────────────────────────
    metadata_controls = [
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
    ]

    # Show actual deadline date/time
    if goal.deadline:
        deadline_display = format_local_datetime(goal.deadline)
        deadline_color = RED if is_overdue else TEXT_SECONDARY

        metadata_controls.extend([
            ft.Text("•", size=12, color=TEXT_MUTED),
            ft.GestureDetector(
                content=ft.Text(
                    f"Due: {deadline_display}",
                    size=12,
                    color=deadline_color,
                    weight=ft.FontWeight.W_500,
                    italic=is_overdue,
                ),
                on_tap=lambda e: on_change_deadline(goal.id),
            ),
        ])

        if deadline_status:
            metadata_controls.extend([
                ft.Text("•", size=12, color=TEXT_MUTED),
                ft.Text(
                    deadline_status,
                    size=12,
                    color=RED if is_overdue else AMBER,
                    weight=ft.FontWeight.W_600,
                ),
            ])

    # ── Goal title (inline editable) ────────────────────────────
    goal_title = _build_inline_editor(
        value=goal.title,
        text_size=16,
        input_text_size=16,
        display_color=TEAL if is_done else TEXT_PRIMARY,
        on_save=lambda new_title: on_edit_goal(goal.id, new_title),
        page=page,
        expand=True,
        font_weight=ft.FontWeight.W_600,
        strike_through=is_done,
    )

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
                        goal_title,
                        ft.Row(
                            controls=metadata_controls,
                            spacing=6,
                            wrap=True,
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
    )

    progress_bar = ft.Container(
        content=ft.ProgressBar(
            value=pct / 100,
            color=progress_color,
            bgcolor=SURFACE,
        ),
        padding=ft.Padding.only(left=48, right=8, bottom=8),
    )

    # ── Expanded content ────────────────────────────────────────
    sorted_tasks = sorted(goal.tasks, key=lambda t: t.position)

    expanded_content = []
    if expanded:
        # Render existing tasks
        for idx, task in enumerate(sorted_tasks):
            expanded_content.append(
                _build_task(
                    goal.id,
                    task,
                    idx,
                    len(sorted_tasks),
                    on_toggle_task,
                    on_toggle_subtask,
                    on_edit_task,
                    on_edit_subtask,
                    on_delete_task,
                    on_delete_subtask,
                    on_move_task,
                    on_move_subtask,
                    on_add_subtask_inline,
                    page,
                )
            )

        # Inline "Add task..." field (always visible, subtle)
        expanded_content.append(
            _build_inline_add_field(
                placeholder="Add task...",
                on_submit=lambda title: on_add_task_inline(goal.id, title),
                indent_left=48,
                page=page,
            )
        )

    # ── Actions (only Delete Goal now) ──────────────────────────
    actions = (
        ft.Row(
            controls=[
                ft.Container(expand=True),
                ft.TextButton(
                    "Delete Goal",
                    icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                    on_click=lambda e: on_delete_goal(goal.id),
                    style=ft.ButtonStyle(color=RED),
                ),
            ],
            alignment=ft.MainAxisAlignment.END,
            spacing=0,
        )
        if expanded
        else ft.Container()
    )

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
    task: Task,
    task_idx: int,
    total_tasks: int,
    on_toggle_task: Callable,
    on_toggle_subtask: Callable,
    on_edit_task: Callable,
    on_edit_subtask: Callable,
    on_delete_task: Callable,
    on_delete_subtask: Callable,
    on_move_task: Callable,
    on_move_subtask: Callable,
    on_add_subtask_inline: Callable,
    page: ft.Page,
):
    """Build a task row with its sub-tasks and inline add field."""
    is_done = task.is_completed
    pct = task.completion_percentage()

    title_editor = _build_inline_editor(
        value=task.title,
        text_size=14,
        input_text_size=14,
        display_color=TEAL if is_done else TEXT_PRIMARY,
        on_save=lambda new_title: on_edit_task(goal_id, task.id, new_title),
        page=page,
        expand=True,
        strike_through=is_done,
    )

    up_button = ft.IconButton(
        icon=ft.Icons.ARROW_UPWARD_ROUNDED,
        icon_size=18,
        icon_color=TEXT_MUTED if task_idx == 0 else TEXT_SECONDARY,
        on_click=lambda e: on_move_task(goal_id, task.id, -1),
        opacity=0.3 if task_idx == 0 else 1.0,
        disabled=task_idx == 0,
    )

    down_button = ft.IconButton(
        icon=ft.Icons.ARROW_DOWNWARD_ROUNDED,
        icon_size=18,
        icon_color=TEXT_MUTED if task_idx == total_tasks - 1 else TEXT_SECONDARY,
        on_click=lambda e: on_move_task(goal_id, task.id, 1),
        opacity=0.3 if task_idx == total_tasks - 1 else 1.0,
        disabled=task_idx == total_tasks - 1,
    )

    delete_icon = ft.IconButton(
        icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
        icon_size=18,
        icon_color=RED,
        on_click=lambda e: on_delete_task(goal_id, task.id),
        opacity=0.3,
    )

    actions_container = ft.Container(
        content=ft.Row(
            controls=[up_button, down_button, delete_icon],
            spacing=4,
        ),
        opacity=0.3,
        on_hover=lambda e: _on_hover(e, actions_container),
    )

    sorted_subtasks = sorted(task.sub_tasks, key=lambda s: s.position)

    subtasks_content = []
    for subtask_idx, subtask in enumerate(sorted_subtasks):
        subtasks_content.append(
            _build_subtask(
                goal_id,
                task.id,
                subtask,
                subtask_idx,
                len(sorted_subtasks),
                on_toggle_subtask,
                on_edit_subtask,
                on_delete_subtask,
                on_move_subtask,
                page,
            )
        )

    # Inline "Add sub-task..." field (always visible, subtle)
    subtasks_content.append(
        _build_inline_add_field(
            placeholder="Add sub-task...",
            on_submit=lambda title: on_add_subtask_inline(goal_id, task.id, title),
            indent_left=56,
            page=page,
        )
    )

    task_row = ft.Row(
        controls=[
            ft.Checkbox(
                value=is_done,
                active_color=TEAL,
                check_color="#0B0F1A",
                scale=0.9,
                on_change=lambda e, tid=task.id: on_toggle_task(goal_id, tid, e.control.value),
            ),
            ft.Container(content=title_editor, expand=True),
            ft.Text(
                f"{pct}%",
                size=11,
                color=TEAL if pct == 100 else TEXT_MUTED,
            ),
            actions_container,
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                task_row,
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
    subtask: SubTask,
    subtask_idx: int,
    total_subtasks: int,
    on_toggle_subtask: Callable,
    on_edit_subtask: Callable,
    on_delete_subtask: Callable,
    on_move_subtask: Callable,
    page: ft.Page,
):
    """Build a sub-task row with edit, delete, and reorder controls."""
    is_done = subtask.is_completed

    title_editor = _build_inline_editor(
        value=subtask.title,
        text_size=13,
        input_text_size=13,
        display_color=TEAL if is_done else TEXT_SECONDARY,
        on_save=lambda new_title: on_edit_subtask(goal_id, task_id, subtask.id, new_title),
        page=page,
        expand=True,
        strike_through=is_done,
    )

    up_button = ft.IconButton(
        icon=ft.Icons.ARROW_UPWARD_ROUNDED,
        icon_size=16,
        icon_color=TEXT_MUTED if subtask_idx == 0 else TEXT_SECONDARY,
        on_click=lambda e: on_move_subtask(goal_id, task_id, subtask.id, -1),
        opacity=0.3 if subtask_idx == 0 else 1.0,
        disabled=subtask_idx == 0,
    )

    down_button = ft.IconButton(
        icon=ft.Icons.ARROW_DOWNWARD_ROUNDED,
        icon_size=16,
        icon_color=TEXT_MUTED if subtask_idx == total_subtasks - 1 else TEXT_SECONDARY,
        on_click=lambda e: on_move_subtask(goal_id, task_id, subtask.id, 1),
        opacity=0.3 if subtask_idx == total_subtasks - 1 else 1.0,
        disabled=subtask_idx == total_subtasks - 1,
    )

    delete_icon = ft.IconButton(
        icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
        icon_size=16,
        icon_color=RED,
        on_click=lambda e: on_delete_subtask(goal_id, task_id, subtask.id),
        opacity=0.3,
    )

    actions_container = ft.Container(
        content=ft.Row(
            controls=[up_button, down_button, delete_icon],
            spacing=4,
        ),
        opacity=0.3,
        on_hover=lambda e: _on_hover(e, actions_container),
    )

    subtask_row = ft.Row(
        controls=[
            ft.Checkbox(
                value=is_done,
                active_color=TEAL,
                check_color="#0B0F1A",
                scale=0.8,
                on_change=lambda e, stid=subtask.id: on_toggle_subtask(goal_id, task_id, stid, e.control.value),
            ),
            ft.Container(content=title_editor, expand=True),
            actions_container,
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    return ft.Container(
        content=subtask_row,
        padding=ft.Padding.only(left=56, right=8, top=2, bottom=2),
    )


# ── Inline add field (Notion-style) ─────────────────────────────

def _build_inline_add_field(
    placeholder: str,
    on_submit: Callable[[str], None],
    indent_left: int,
    page: Optional[ft.Page] = None,
) -> ft.Container:
    """Build a subtle, always-visible inline text field for adding items.

    Notion-style: subtle placeholder, no visible border by default,
    TEAL border on focus. Clears and stays open after Enter.
    """

    def handle_submit(e):
        title = e.control.value.strip()
        if title:
            e.control.value = ""
            if page:
                e.control.update()
            on_submit(title)

    add_field = ft.TextField(
        hint_text=placeholder,
        border_radius=8,
        bgcolor="transparent",
        border_color="transparent",
        focused_border_color=TEAL,
        cursor_color=TEAL,
        hint_style=ft.TextStyle(
            color="#3A4157",
            size=13,
            italic=True,
        ),
        text_style=ft.TextStyle(color=TEXT_PRIMARY, size=13),
        content_padding=ft.Padding.symmetric(horizontal=8, vertical=6),
        expand=True,
        on_submit=handle_submit,
    )

    add_icon = ft.Icon(
        ft.Icons.ADD_ROUNDED,
        color="#3A4157",
        size=16,
    )

    field_container = ft.Container(
        content=ft.Row(
            controls=[add_icon, add_field],
            spacing=4,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.only(left=indent_left, right=8, top=2, bottom=2),
        border_radius=8,
        opacity=0.5,
        on_hover=lambda e: _on_hover(e, field_container),
    )

    return field_container


# ── Inline editor (tap-to-edit) ─────────────────────────────────

def _build_inline_editor(
    value: str,
    text_size: int,
    input_text_size: int,
    display_color: str,
    on_save: Callable[[str], None],
    page: Optional[ft.Page] = None,
    expand: bool = False,
    font_weight: Optional[ft.FontWeight] = None,
    strike_through: bool = False,
) -> ft.Column:
    """Build a reusable inline text editor with tap-to-edit behavior."""
    state = {
        "editing": False,
        "original_value": value,
        "cancel_pending": False,
    }

    def update_visibility():
        title_tap_area.visible = not state["editing"]
        edit_row.visible = state["editing"]

    def finish_edit(save: bool):
        if not state["editing"]:
            return

        new_value = title_input.value.strip()
        should_save = save and not state["cancel_pending"] and new_value and new_value != state["original_value"]

        state["editing"] = False
        state["cancel_pending"] = False
        update_visibility()

        if should_save:
            on_save(new_value)
        elif page:
            page.update()

    def start_edit(e=None):
        if state["editing"]:
            return
        state["editing"] = True
        state["cancel_pending"] = False
        state["original_value"] = title_input.value
        update_visibility()
        if page:
            page.update()
            title_input.focus()

    title_display = ft.Text(
        value,
        size=text_size,
        color=display_color,
        weight=font_weight,
        style=ft.TextStyle(
            decoration=ft.TextDecoration.LINE_THROUGH
        ) if strike_through else None,
        expand=expand,
    )

    title_tap_area = ft.GestureDetector(
        content=title_display,
        on_tap=start_edit,
    )

    title_input = ft.TextField(
        value=value,
        border_radius=8,
        bgcolor=SURFACE,
        border_color=SURFACE,
        focused_border_color=TEAL,
        cursor_color=TEAL,
        text_style=ft.TextStyle(color=TEXT_PRIMARY, size=input_text_size),
        expand=True,
        on_submit=lambda e: finish_edit(True),
        on_blur=lambda e: finish_edit(True),
    )

    cancel_button = ft.GestureDetector(
        content=ft.Container(
            content=ft.Icon(ft.Icons.CLOSE_ROUNDED, color=RED, size=input_text_size + 4),
            padding=4,
        ),
        on_tap_down=lambda e: state.__setitem__("cancel_pending", True),
        on_tap=lambda e: finish_edit(False),
    )

    edit_row = ft.Row(
        controls=[title_input, cancel_button],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=4,
        expand=expand,
        visible=False,
    )

    update_visibility()

    return ft.Column(
        controls=[title_tap_area, edit_row],
        spacing=0,
        expand=expand,
    )


def _on_hover(e, container: ft.Container):
    """Handle hover effect — reveal on hover, fade on leave."""
    container.opacity = 1.0 if e.data == "true" else 0.5
    try:
        container.update()
    except Exception:
        pass
