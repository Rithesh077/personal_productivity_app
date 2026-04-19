"""goal card component - expandable card with hierarchy and progress."""

import flet as ft
from typing import Callable, Optional

from models.goal import Goal, Task, SubTask
from constants.design import (
    TEAL, AMBER, RED, BG, CARD_BG, SURFACE,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
)
from utils.time_utils import (
    relative_time,
    time_until_deadline,
    is_past_deadline,
    format_local_datetime,
)

# tree line color
TREE_LINE = "#2A3450"


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
    """expandable goal card with task hierarchy and progress."""
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

    # metadata row
    metadata_controls = [
        ft.Text(f"{pct}%", size=12, color=progress_color, weight=ft.FontWeight.W_500),
        ft.Text(".", size=12, color=TEXT_MUTED),
        ft.Text(relative_time(goal.created_at), size=12, color=TEXT_MUTED),
    ]

    if goal.deadline:
        deadline_display = format_local_datetime(goal.deadline)
        deadline_color = RED if is_overdue else TEXT_SECONDARY

        metadata_controls.extend([
            ft.Text(".", size=12, color=TEXT_MUTED),
            ft.GestureDetector(
                content=ft.Text(
                    f"Due: {deadline_display}",
                    size=12, color=deadline_color,
                    weight=ft.FontWeight.W_500,
                    italic=is_overdue,
                ),
                on_tap=lambda e: on_change_deadline(goal.id),
            ),
        ])

        if deadline_status:
            metadata_controls.extend([
                ft.Text(".", size=12, color=TEXT_MUTED),
                ft.Text(
                    deadline_status, size=12,
                    color=RED if is_overdue else AMBER,
                    weight=ft.FontWeight.W_600,
                ),
            ])

    # goal title (inline editable)
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
                    value=is_done, active_color=TEAL, check_color=BG,
                    scale=1.15,
                    on_change=lambda e: on_toggle_goal(goal.id, e.control.value),
                ),
                ft.Column(
                    controls=[
                        goal_title,
                        ft.Row(controls=metadata_controls, spacing=6, wrap=True),
                    ],
                    spacing=2, expand=True,
                ),
                ft.IconButton(
                    icon=ft.Icons.EXPAND_MORE_ROUNDED if not expanded else ft.Icons.EXPAND_LESS_ROUNDED,
                    icon_color=TEXT_SECONDARY, icon_size=20,
                    on_click=lambda e: on_expand(goal.id) if on_expand else None,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.symmetric(horizontal=8, vertical=4),
    )

    progress_bar = ft.Container(
        content=ft.ProgressBar(value=pct / 100, color=progress_color, bgcolor=SURFACE),
        padding=ft.Padding.only(left=48, right=8, bottom=8),
    )

    # expanded content with tree structure
    sorted_tasks = sorted(goal.tasks, key=lambda t: t.position)
    tree_children = []

    if expanded:
        for idx, task in enumerate(sorted_tasks):
            tree_children.append(
                _build_task(
                    goal.id, task, idx, len(sorted_tasks),
                    on_toggle_task, on_toggle_subtask,
                    on_edit_task, on_edit_subtask,
                    on_delete_task, on_delete_subtask,
                    on_move_task, on_move_subtask,
                    on_add_subtask_inline, page,
                )
            )

        # inline "add task..." field inside tree
        tree_children.append(
            _build_inline_add_field(
                placeholder="Add task...",
                on_submit=lambda title: on_add_task_inline(goal.id, title),
                indent_left=8, page=page,
            )
        )

    # wrap tree children in a container with left tree line
    tree_container = ft.Container(
        content=ft.Column(controls=tree_children, spacing=0),
        padding=ft.Padding.only(left=36, right=4, top=0, bottom=0),
        border=ft.Border(left=ft.BorderSide(2, TREE_LINE)) if tree_children else None,
        margin=ft.Margin.only(left=12),
    ) if tree_children else ft.Container()

    # actions (delete goal)
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
            alignment=ft.MainAxisAlignment.END, spacing=0,
        )
        if expanded
        else ft.Container()
    )

    return ft.Container(
        content=ft.Column(
            controls=[header, progress_bar, tree_container, actions],
            spacing=0,
        ),
        bgcolor=CARD_BG,
        border_radius=12,
        border=ft.Border.all(1, TEAL if is_done else SURFACE),
        animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        margin=ft.Margin.only(bottom=8),
    )


def _build_task(
    goal_id, task, task_idx, total_tasks,
    on_toggle_task, on_toggle_subtask,
    on_edit_task, on_edit_subtask,
    on_delete_task, on_delete_subtask,
    on_move_task, on_move_subtask,
    on_add_subtask_inline, page,
):
    """task row with subtasks and inline add field."""
    is_done = task.is_completed
    pct = task.completion_percentage()

    title_editor = _build_inline_editor(
        value=task.title, text_size=14, input_text_size=14,
        display_color=TEAL if is_done else TEXT_PRIMARY,
        on_save=lambda new_title: on_edit_task(goal_id, task.id, new_title),
        page=page, expand=True, strike_through=is_done,
    )

    # action buttons with circular backgrounds
    up_btn = _action_circle(
        ft.Icons.ARROW_UPWARD_ROUNDED, TEXT_SECONDARY, SURFACE, 14,
        on_click=lambda e: on_move_task(goal_id, task.id, -1),
        disabled=task_idx == 0,
    )
    down_btn = _action_circle(
        ft.Icons.ARROW_DOWNWARD_ROUNDED, TEXT_SECONDARY, SURFACE, 14,
        on_click=lambda e: on_move_task(goal_id, task.id, 1),
        disabled=task_idx == total_tasks - 1,
    )
    del_btn = _action_circle(
        ft.Icons.DELETE_OUTLINE_ROUNDED, RED, f"{RED}18", 14,
        on_click=lambda e: on_delete_task(goal_id, task.id),
    )

    actions_container = ft.Container(
        content=ft.Row(
            controls=[up_btn, down_btn, ft.Container(width=6), del_btn],
            spacing=6,
        ),
        opacity=0.4,
        on_hover=lambda e: _on_hover(e, actions_container),
    )

    # subtask tree
    sorted_subtasks = sorted(task.sub_tasks, key=lambda s: s.position)
    subtask_children = []

    for subtask_idx, subtask in enumerate(sorted_subtasks):
        subtask_children.append(
            _build_subtask(
                goal_id, task.id, subtask, subtask_idx, len(sorted_subtasks),
                on_toggle_subtask, on_edit_subtask,
                on_delete_subtask, on_move_subtask, page,
            )
        )

    # inline "add sub-task..." field
    subtask_children.append(
        _build_inline_add_field(
            placeholder="Add sub-task...",
            on_submit=lambda title: on_add_subtask_inline(goal_id, task.id, title),
            indent_left=8, page=page,
        )
    )

    # subtask tree container with nested line
    subtask_tree = ft.Container(
        content=ft.Column(controls=subtask_children, spacing=0),
        padding=ft.Padding.only(left=28, top=0, bottom=0),
        border=ft.Border(left=ft.BorderSide(1.5, TREE_LINE)),
        margin=ft.Margin.only(left=8),
    )

    # horizontal connector dash
    connector = ft.Container(width=10, height=1.5, bgcolor=TREE_LINE)

    task_row = ft.Row(
        controls=[
            connector,
            ft.Checkbox(
                value=is_done, active_color=TEAL, check_color=BG, scale=0.95,
                on_change=lambda e, tid=task.id: on_toggle_task(goal_id, tid, e.control.value),
            ),
            ft.Container(content=title_editor, expand=True),
            ft.Text(f"{pct}%", size=11, color=TEAL if pct == 100 else TEXT_MUTED),
            actions_container,
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    return ft.Container(
        content=ft.Column(controls=[task_row, subtask_tree], spacing=0),
        padding=ft.Padding.only(top=4, bottom=4, right=4),
    )


def _build_subtask(
    goal_id, task_id, subtask, subtask_idx, total_subtasks,
    on_toggle_subtask, on_edit_subtask,
    on_delete_subtask, on_move_subtask, page,
):
    """subtask row with edit, delete, and reorder."""
    is_done = subtask.is_completed

    title_editor = _build_inline_editor(
        value=subtask.title, text_size=13, input_text_size=13,
        display_color=TEAL if is_done else TEXT_SECONDARY,
        on_save=lambda new_title: on_edit_subtask(goal_id, task_id, subtask.id, new_title),
        page=page, expand=True, strike_through=is_done,
    )

    # action buttons with circular backgrounds
    up_btn = _action_circle(
        ft.Icons.ARROW_UPWARD_ROUNDED, TEXT_SECONDARY, SURFACE, 12,
        on_click=lambda e: on_move_subtask(goal_id, task_id, subtask.id, -1),
        disabled=subtask_idx == 0,
    )
    down_btn = _action_circle(
        ft.Icons.ARROW_DOWNWARD_ROUNDED, TEXT_SECONDARY, SURFACE, 12,
        on_click=lambda e: on_move_subtask(goal_id, task_id, subtask.id, 1),
        disabled=subtask_idx == total_subtasks - 1,
    )
    del_btn = _action_circle(
        ft.Icons.DELETE_OUTLINE_ROUNDED, RED, f"{RED}18", 12,
        on_click=lambda e: on_delete_subtask(goal_id, task_id, subtask.id),
    )

    actions_container = ft.Container(
        content=ft.Row(
            controls=[up_btn, down_btn, ft.Container(width=4), del_btn],
            spacing=4,
        ),
        opacity=0.4,
        on_hover=lambda e: _on_hover(e, actions_container),
    )

    # horizontal connector dash
    connector = ft.Container(width=8, height=1.5, bgcolor=TREE_LINE)

    subtask_row = ft.Row(
        controls=[
            connector,
            ft.Checkbox(
                value=is_done, active_color=TEAL, check_color=BG, scale=0.75,
                on_change=lambda e, stid=subtask.id: on_toggle_subtask(goal_id, task_id, stid, e.control.value),
            ),
            ft.Container(content=title_editor, expand=True),
            actions_container,
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    return ft.Container(
        content=subtask_row,
        padding=ft.Padding.only(top=2, bottom=2, right=4),
    )


def _action_circle(icon, color, bg_color, size=14, on_click=None, disabled=False):
    """circular icon button with colored background."""
    container = ft.Container(
        content=ft.Icon(icon, size=size, color=color if not disabled else TEXT_MUTED),
        width=28, height=28,
        bgcolor=bg_color if not disabled else "transparent",
        border_radius=14,
        alignment=ft.Alignment(0, 0),
        opacity=0.4 if disabled else 1.0,
    )
    if on_click and not disabled:
        return ft.GestureDetector(content=container, on_tap=on_click)
    return container


# inline add field (notion-style)

def _build_inline_add_field(placeholder, on_submit, indent_left, page=None):
    """subtle always-visible text field. clears and stays open after enter."""

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
        hint_style=ft.TextStyle(color="#5A6478", size=13, italic=True),
        text_style=ft.TextStyle(color=TEXT_PRIMARY, size=13),
        content_padding=ft.Padding.symmetric(horizontal=8, vertical=6),
        expand=True,
        on_submit=handle_submit,
    )

    add_icon = ft.Icon(ft.Icons.ADD_ROUNDED, color="#5A6478", size=16)

    field_container = ft.Container(
        content=ft.Row(
            controls=[add_icon, add_field], spacing=4,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.only(left=indent_left, right=8, top=2, bottom=2),
        border_radius=8, opacity=0.6,
        on_hover=lambda e: _on_hover(e, field_container),
    )

    return field_container


# inline editor (tap-to-edit)

def _build_inline_editor(
    value, text_size, input_text_size, display_color, on_save,
    page=None, expand=False, font_weight=None, strike_through=False,
):
    """tap-to-edit inline text editor."""
    state = {"editing": False, "original_value": value, "cancel_pending": False}

    def update_visibility():
        title_tap_area.visible = not state["editing"]
        edit_row.visible = state["editing"]

    def finish_edit(save):
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
        value, size=text_size, color=display_color, weight=font_weight,
        style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH) if strike_through else None,
        expand=expand,
    )

    title_tap_area = ft.GestureDetector(content=title_display, on_tap=start_edit)

    title_input = ft.TextField(
        value=value, border_radius=8, bgcolor=SURFACE, border_color=SURFACE,
        focused_border_color=TEAL, cursor_color=TEAL,
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
        spacing=4, expand=expand, visible=False,
    )

    update_visibility()

    return ft.Column(
        controls=[title_tap_area, edit_row],
        spacing=0, expand=expand,
    )


def _on_hover(e, container):
    """hover effect - reveal on hover, fade on leave."""
    container.opacity = 1.0 if e.data == "true" else 0.6
    try:
        container.update()
    except Exception:
        pass
