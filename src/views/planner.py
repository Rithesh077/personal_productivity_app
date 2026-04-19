"""planner view - manage goals with tasks and subtasks."""

import flet as ft
from datetime import datetime, time

from services.storage import load_goals, save_goal, delete_goal, get_goal
from models.goal import Goal, Task, SubTask
from components.goal_card import GoalCard
from components.goal_wizard import GoalWizard
from constants.design import (
    TEAL, RED, MUTED, BG, CARD_BG, SURFACE,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
)
from utils.time_utils import utc_now, local_to_utc, extract_local_date, today_midnight


def build_planner(page: ft.Page):
    """build the planner view, returns a column control."""

    state = {
        "goals": [],
        "expanded_goal_id": None,
        "show_wizard": False,
        "undo_stack": [],
    }

    goals_column = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
    wizard_container = ft.Container(visible=False, expand=True)
    main_content = ft.Column(expand=True)

    # loading skeleton shown before goals load
    def _skeleton_card():
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(width=22, height=22, bgcolor=SURFACE, border_radius=4),
                    ft.Container(expand=True, height=16, bgcolor=SURFACE, border_radius=4),
                ], spacing=12),
                ft.Container(height=6, bgcolor=SURFACE, border_radius=4,
                             margin=ft.Margin.only(left=34, top=4, right=0, bottom=0)),
            ], spacing=8),
            bgcolor=CARD_BG, border_radius=12, padding=16,
            border=ft.Border.all(1, SURFACE),
        )

    # show skeleton immediately
    goals_column.controls = [_skeleton_card(), _skeleton_card(), _skeleton_card()]

    def sort_goals(goals: list[Goal]) -> list[Goal]:
        """incomplete first (newest on top), then completed (newest on top)."""
        incomplete = [g for g in goals if not g.is_completed]
        completed = [g for g in goals if g.is_completed]
        incomplete.sort(key=lambda g: g.created_at, reverse=True)
        completed.sort(key=lambda g: g.completed_at or g.created_at, reverse=True)
        return incomplete + completed

    async def refresh_goals():
        """load and display goals."""
        goals = await load_goals(page)
        state["goals"] = sort_goals(goals)
        goals_column.controls.clear()

        if not state["goals"]:
            goals_column.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.FLAG_ROUNDED, color=MUTED, size=48),
                            ft.Text("No goals yet", size=16, color=TEXT_MUTED,
                                    text_align=ft.TextAlign.CENTER),
                            ft.Text("Tap + to create your first goal", size=13,
                                    color="#3A4157", text_align=ft.TextAlign.CENTER),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    alignment=ft.Alignment(0, 0),
                    padding=40,
                )
            )
        else:
            for goal in state["goals"]:
                goals_column.controls.append(
                    GoalCard(
                        goal=goal,
                        on_toggle_goal=toggle_goal,
                        on_toggle_task=toggle_task,
                        on_toggle_subtask=toggle_subtask,
                        on_delete_goal=handle_delete_goal,
                        on_edit_goal=handle_edit_goal,
                        on_edit_task=handle_edit_task,
                        on_edit_subtask=handle_edit_subtask,
                        on_delete_task=handle_delete_task,
                        on_delete_subtask=handle_delete_subtask,
                        on_move_task=handle_move_task,
                        on_move_subtask=handle_move_subtask,
                        on_add_task_inline=handle_add_task_inline,
                        on_add_subtask_inline=handle_add_subtask_inline,
                        on_change_deadline=handle_change_deadline,
                        expanded=state["expanded_goal_id"] == goal.id,
                        on_expand=handle_expand,
                        page=page,
                    )
                )

        await update_stats()
        page.update()

    # toggle handlers

    async def toggle_goal_async(goal_id, value):
        goal = await get_goal(page, goal_id)
        if goal:
            if value:
                goal.mark_complete(utc_now())
            else:
                goal.mark_incomplete()
            await save_goal(page, goal)
            await refresh_goals()

    def toggle_goal(goal_id, value):
        page.run_task(toggle_goal_async, goal_id, value)

    async def toggle_task_async(goal_id, task_id, value):
        """toggle task. cascades to all subtasks."""
        goal = await get_goal(page, goal_id)
        if goal:
            now = utc_now()
            for task in goal.tasks:
                if task.id == task_id:
                    task.is_completed = value
                    task.completed_at = now if value else None
                    for subtask in task.sub_tasks:
                        subtask.is_completed = value
                        subtask.completed_at = now if value else None
                    break

            all_done = all(t.is_completed for t in goal.tasks) if goal.tasks else False
            if all_done and goal.tasks:
                goal.is_completed = True
                goal.completed_at = now
            elif not value:
                goal.is_completed = False
                goal.completed_at = None

            await save_goal(page, goal)
            await refresh_goals()

    def toggle_task(goal_id, task_id, value):
        page.run_task(toggle_task_async, goal_id, task_id, value)

    async def toggle_subtask_async(goal_id, task_id, subtask_id, value):
        """toggle subtask. auto-completes parent task/goal if all done."""
        goal = await get_goal(page, goal_id)
        if goal:
            now = utc_now()
            for task in goal.tasks:
                if task.id == task_id:
                    for subtask in task.sub_tasks:
                        if subtask.id == subtask_id:
                            subtask.is_completed = value
                            subtask.completed_at = now if value else None
                            break

                    all_subtasks_done = all(
                        s.is_completed for s in task.sub_tasks) if task.sub_tasks else True
                    if all_subtasks_done:
                        task.is_completed = True
                        task.completed_at = now
                    else:
                        task.is_completed = False
                        task.completed_at = None
                    break

            all_done = all(t.is_completed for t in goal.tasks) if goal.tasks else False
            if all_done and goal.tasks:
                goal.is_completed = True
                goal.completed_at = now
            elif not value:
                goal.is_completed = False
                goal.completed_at = None

            await save_goal(page, goal)
            await refresh_goals()

    def toggle_subtask(goal_id, task_id, subtask_id, value):
        page.run_task(toggle_subtask_async, goal_id, task_id, subtask_id, value)

    # action handlers

    def handle_expand(goal_id):
        if state["expanded_goal_id"] == goal_id:
            state["expanded_goal_id"] = None
        else:
            state["expanded_goal_id"] = goal_id
        page.run_task(refresh_goals)

    def handle_delete_goal(goal_id):
        """show confirmation dialog before deleting goal."""
        async def show_confirmation():
            goal = await get_goal(page, goal_id)
            if not goal:
                return

            total_tasks = len(goal.tasks)
            total_subtasks = sum(len(t.sub_tasks) for t in goal.tasks)

            def close_dialog(e=None):
                page.pop_dialog()

            def confirm_delete(e=None):
                page.pop_dialog()
                page.run_task(delete_goal_with_undo, goal_id, goal)

            dlg = ft.AlertDialog(
                title=ft.Text("Delete Goal?", size=18, weight=ft.FontWeight.BOLD),
                content=ft.Column(
                    controls=[
                        ft.Text(f"Goal: {goal.title}", size=14, color=TEXT_PRIMARY),
                        ft.Container(height=8),
                        ft.Text(
                            f"This will delete {total_tasks} task{'s' if total_tasks != 1 else ''} "
                            f"and {total_subtasks} subtask{'s' if total_subtasks != 1 else ''}.",
                            size=12, color=TEXT_SECONDARY,
                        ),
                    ],
                    spacing=4, tight=True,
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=close_dialog),
                    ft.FilledButton(
                        "Delete", bgcolor=RED, color="white", on_click=confirm_delete,
                    ),
                ],
            )
            page.show_dialog(dlg)

        page.run_task(show_confirmation)

    async def delete_goal_with_undo(goal_id, goal_backup):
        """delete goal and show undo snackbar."""
        await delete_goal(page, goal_id)

        undo_entry = {"goal_id": goal_id, "goal": goal_backup}
        state["undo_stack"].append(undo_entry)

        undo_bar = ft.SnackBar(
            content=ft.Row(
                controls=[
                    ft.Text(f"Deleted '{goal_backup.title}'", color=TEXT_PRIMARY),
                    ft.Container(expand=True),
                    ft.TextButton("Undo", on_click=lambda e: _undo_delete(undo_entry)),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=SURFACE,
        )
        page.show_dialog(undo_bar)
        await refresh_goals()

    def _undo_delete(undo_entry):
        """restore deleted goal."""
        async def restore():
            goal = undo_entry["goal"]
            await save_goal(page, goal)
            if undo_entry in state["undo_stack"]:
                state["undo_stack"].remove(undo_entry)
            page.pop_dialog()
            await refresh_goals()
        page.run_task(restore)

    # inline add handlers

    def handle_add_task_inline(goal_id, title):
        """add a task from the inline field."""
        async def add_task_async():
            goal = await get_goal(page, goal_id)
            if not goal:
                return
            goal.tasks.append(Task(
                title=title, created_at=utc_now(), position=len(goal.tasks),
            ))
            # new incomplete task means goal can't be complete
            goal.is_completed = False
            goal.completed_at = None
            await save_goal(page, goal)
            await refresh_goals()
        page.run_task(add_task_async)

    def handle_add_subtask_inline(goal_id, task_id, title):
        """add a subtask from the inline field."""
        async def add_subtask_async():
            goal = await get_goal(page, goal_id)
            if not goal:
                return
            for task in goal.tasks:
                if task.id == task_id:
                    task.sub_tasks.append(SubTask(
                        title=title, created_at=utc_now(), position=len(task.sub_tasks),
                    ))
                    task.is_completed = False
                    task.completed_at = None
                    break
            goal.is_completed = False
            goal.completed_at = None
            await save_goal(page, goal)
            await refresh_goals()
        page.run_task(add_subtask_async)

    # deadline picker flow

    def handle_change_deadline(goal_id):
        """datepicker -> optional timepicker -> save deadline."""
        picker_state = {"selected_date": None}

        def on_date_selected(e):
            picker_state["selected_date"] = date_picker.value
            page.run_task(show_time_option)

        date_picker = ft.DatePicker(
            value=datetime.now(),
            first_date=today_midnight(),
            last_date=datetime(year=2030, month=12, day=31),
            help_text="Set deadline date",
            confirm_text="Next",
            on_change=on_date_selected,
        )

        async def show_time_option():
            """ask user if they want to set a specific time."""
            def use_default_time(e=None):
                page.pop_dialog()
                selected = picker_state["selected_date"]
                target_date = extract_local_date(selected)
                deadline_dt = datetime.combine(target_date, time(23, 59, 59))
                page.run_task(save_deadline, goal_id, deadline_dt)

            def open_time_picker(e=None):
                page.pop_dialog()

                def on_time_selected(e):
                    selected = picker_state["selected_date"]
                    target_date = extract_local_date(selected)
                    deadline_dt = datetime.combine(target_date, time_picker.value)
                    page.run_task(save_deadline, goal_id, deadline_dt)

                time_picker = ft.TimePicker(
                    value=time(23, 59),
                    help_text="Set deadline time",
                    on_change=on_time_selected,
                )
                page.show_dialog(time_picker)

            dlg = ft.AlertDialog(
                title=ft.Text("Set specific time?", size=16, weight=ft.FontWeight.BOLD),
                content=ft.Text(
                    "Default deadline time is 11:59 PM",
                    size=13, color=TEXT_SECONDARY,
                ),
                actions=[
                    ft.TextButton(
                        "Use Default (11:59 PM)",
                        on_click=use_default_time,
                        style=ft.ButtonStyle(color=TEXT_SECONDARY),
                    ),
                    ft.FilledButton(
                        "Set Time", bgcolor=TEAL, color=BG,
                        on_click=open_time_picker,
                    ),
                ],
            )
            page.show_dialog(dlg)

        async def save_deadline(gid, deadline_dt):
            """save the combined deadline to the goal."""
            goal = await get_goal(page, gid)
            if goal:
                goal.deadline = local_to_utc(deadline_dt)
                goal.has_custom_deadline = True
                await save_goal(page, goal)
                await refresh_goals()

        page.show_dialog(date_picker)

    # edit handlers

    def handle_edit_task(goal_id, task_id, new_title):
        async def edit_task_async():
            goal = await get_goal(page, goal_id)
            if goal:
                for task in goal.tasks:
                    if task.id == task_id:
                        task.title = new_title
                        task.updated_at = utc_now()
                        break
                await save_goal(page, goal)
                await refresh_goals()
        page.run_task(edit_task_async)

    def handle_edit_subtask(goal_id, task_id, subtask_id, new_title):
        async def edit_subtask_async():
            goal = await get_goal(page, goal_id)
            if goal:
                for task in goal.tasks:
                    if task.id == task_id:
                        for subtask in task.sub_tasks:
                            if subtask.id == subtask_id:
                                subtask.title = new_title
                                subtask.updated_at = utc_now()
                                break
                        break
                await save_goal(page, goal)
                await refresh_goals()
        page.run_task(edit_subtask_async)

    def handle_delete_task(goal_id, task_id):
        """show confirmation before deleting a task."""
        async def show_confirm():
            goal = await get_goal(page, goal_id)
            if not goal:
                return
            task_obj = next((t for t in goal.tasks if t.id == task_id), None)
            if not task_obj:
                return
            subtask_count = len(task_obj.sub_tasks)

            def close(e=None):
                page.pop_dialog()

            def confirm(e=None):
                page.pop_dialog()
                page.run_task(do_delete_task, goal_id, task_id)

            dlg = ft.AlertDialog(
                title=ft.Text("Delete Task?", size=16, weight=ft.FontWeight.BOLD),
                content=ft.Column([
                    ft.Text(f"Task: {task_obj.title}", size=14, color=TEXT_PRIMARY),
                    ft.Text(
                        f"This will also delete {subtask_count} sub-task{'s' if subtask_count != 1 else ''}."
                        if subtask_count > 0 else "This task has no sub-tasks.",
                        size=12, color=TEXT_SECONDARY,
                    ),
                ], spacing=4, tight=True),
                actions=[
                    ft.TextButton("Cancel", on_click=close),
                    ft.FilledButton("Delete", bgcolor=RED, color="white", on_click=confirm),
                ],
            )
            page.show_dialog(dlg)
        page.run_task(show_confirm)

    async def do_delete_task(goal_id, task_id):
        goal = await get_goal(page, goal_id)
        if goal:
            goal.tasks = [t for t in goal.tasks if t.id != task_id]
            for idx, task in enumerate(goal.tasks):
                task.position = idx
            if goal.tasks:
                all_done = all(t.is_completed for t in goal.tasks)
                if all_done:
                    goal.is_completed = True
                    goal.completed_at = goal.completed_at or utc_now()
            await save_goal(page, goal)
            await refresh_goals()

    def handle_delete_subtask(goal_id, task_id, subtask_id):
        """show confirmation before deleting a subtask."""
        async def show_confirm():
            goal = await get_goal(page, goal_id)
            if not goal:
                return
            task_obj = next((t for t in goal.tasks if t.id == task_id), None)
            if not task_obj:
                return
            subtask_obj = next((s for s in task_obj.sub_tasks if s.id == subtask_id), None)
            if not subtask_obj:
                return

            def close(e=None):
                page.pop_dialog()

            def confirm(e=None):
                page.pop_dialog()
                page.run_task(do_delete_subtask, goal_id, task_id, subtask_id)

            dlg = ft.AlertDialog(
                title=ft.Text("Delete Sub-task?", size=16, weight=ft.FontWeight.BOLD),
                content=ft.Text(f"Sub-task: {subtask_obj.title}", size=14, color=TEXT_PRIMARY),
                actions=[
                    ft.TextButton("Cancel", on_click=close),
                    ft.FilledButton("Delete", bgcolor=RED, color="white", on_click=confirm),
                ],
            )
            page.show_dialog(dlg)
        page.run_task(show_confirm)

    async def do_delete_subtask(goal_id, task_id, subtask_id):
        goal = await get_goal(page, goal_id)
        if goal:
            for task in goal.tasks:
                if task.id == task_id:
                    task.sub_tasks = [s for s in task.sub_tasks if s.id != subtask_id]
                    for idx, subtask in enumerate(task.sub_tasks):
                        subtask.position = idx
                    if task.sub_tasks:
                        all_subtasks_done = all(s.is_completed for s in task.sub_tasks)
                        if all_subtasks_done:
                            task.is_completed = True
                            task.completed_at = task.completed_at or utc_now()
                    if goal.tasks:
                        all_done = all(t.is_completed for t in goal.tasks)
                        if all_done:
                            goal.is_completed = True
                            goal.completed_at = goal.completed_at or utc_now()
                    break
            await save_goal(page, goal)
            await refresh_goals()

    def handle_move_task(goal_id, task_id, direction):
        async def move_task_async():
            goal = await get_goal(page, goal_id)
            if goal:
                task_idx = None
                for idx, t in enumerate(goal.tasks):
                    if t.id == task_id:
                        task_idx = idx
                        break
                if task_idx is not None:
                    new_idx = task_idx + direction
                    if 0 <= new_idx < len(goal.tasks):
                        goal.tasks[task_idx], goal.tasks[new_idx] = goal.tasks[new_idx], goal.tasks[task_idx]
                        for idx, task in enumerate(goal.tasks):
                            task.position = idx
                        await save_goal(page, goal)
                        await refresh_goals()
        page.run_task(move_task_async)

    def handle_move_subtask(goal_id, task_id, subtask_id, direction):
        async def move_subtask_async():
            goal = await get_goal(page, goal_id)
            if goal:
                for task in goal.tasks:
                    if task.id == task_id:
                        subtask_idx = None
                        for idx, st in enumerate(task.sub_tasks):
                            if st.id == subtask_id:
                                subtask_idx = idx
                                break
                        if subtask_idx is not None:
                            new_idx = subtask_idx + direction
                            if 0 <= new_idx < len(task.sub_tasks):
                                task.sub_tasks[subtask_idx], task.sub_tasks[new_idx] = task.sub_tasks[new_idx], task.sub_tasks[subtask_idx]
                                for idx, subtask in enumerate(task.sub_tasks):
                                    subtask.position = idx
                                await save_goal(page, goal)
                                await refresh_goals()
                        break
        page.run_task(move_subtask_async)

    def handle_edit_goal(goal_id, new_title):
        async def edit_goal_async():
            goal = await get_goal(page, goal_id)
            if goal:
                goal.title = new_title
                goal.updated_at = utc_now()
                await save_goal(page, goal)
                await refresh_goals()
        page.run_task(edit_goal_async)

    # wizard handlers

    def show_wizard():
        state["show_wizard"] = True
        wizard = GoalWizard(page, on_save=save_new_goal, on_cancel=hide_wizard)
        wizard_container.content = wizard.build()
        wizard_container.visible = True
        main_content.visible = False
        page.update()

    def hide_wizard():
        state["show_wizard"] = False
        wizard_container.visible = False
        wizard_container.content = None
        main_content.visible = True
        page.update()

    async def save_new_goal_async(goal):
        await save_goal(page, goal)
        hide_wizard()
        await refresh_goals()

    def save_new_goal(goal):
        page.run_task(save_new_goal_async, goal)

    # header
    header = ft.Row(
        controls=[
            ft.Column(
                controls=[
                    ft.Text("Stride", size=28, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Text("Plan. Execute. Improve.", size=13, color=TEXT_SECONDARY),
                ],
                spacing=2,
            ),
            ft.Container(expand=True),
            ft.FloatingActionButton(
                icon=ft.Icons.ADD_ROUNDED,
                bgcolor=TEAL, foreground_color=BG,
                mini=True,
                on_click=lambda e: show_wizard(),
            ),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # stats bar
    stats_container = ft.Container()

    async def update_stats():
        total = len(state["goals"])
        completed = sum(1 for g in state["goals"] if g.is_completed)
        active = total - completed
        stats_container.content = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.FLAG_ROUNDED, color=TEAL, size=16),
                            ft.Text(f"{active} active", size=13, color=TEXT_SECONDARY),
                        ],
                        spacing=4,
                    ),
                ),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, color=TEXT_MUTED, size=16),
                            ft.Text(f"{completed} done", size=13, color=TEXT_MUTED),
                        ],
                        spacing=4,
                    ),
                ),
            ],
            spacing=16,
        )

    # main content layout
    main_content.controls = [
        header,
        ft.Container(content=stats_container, padding=ft.Padding.symmetric(vertical=8)),
        ft.Text("Goals", size=14, weight=ft.FontWeight.W_600, color=TEXT_SECONDARY),
        goals_column,
    ]
    main_content.spacing = 12

    # initial load
    page.run_task(refresh_goals)

    return ft.Stack(
        controls=[main_content, wizard_container],
        expand=True,
    )
