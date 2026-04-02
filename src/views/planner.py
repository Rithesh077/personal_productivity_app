"""Planner view for Stride — manage goals with tasks and sub-tasks."""

import flet as ft
from typing import Optional

from services.storage import load_goals, save_goals, save_goal, delete_goal, get_goal
from models.goal import Goal, SubTask, Step
from components.goal_card import GoalCard
from components.goal_wizard import GoalWizard
from utils.time_utils import utc_now

# Design tokens
TEAL = "#00D9A6"
MUTED = "#3A4157"
CARD_BG = "#141927"
SURFACE = "#1E2436"
TEXT_PRIMARY = "#E0E0E0"
TEXT_SECONDARY = "#8A92A6"
TEXT_MUTED = "#5A6478"
BG = "#0B0F1A"


def build_planner(page: ft.Page):
    """Build the planner view. Returns a Column control."""

    # State
    state = {
        "goals": [],
        "expanded_goal_id": None,
        "show_wizard": False,
        "editing_goal_id": None,
    }

    # ── Goal list container ─────────────────────────────────────
    goals_column = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
    wizard_container = ft.Container(visible=False, expand=True)
    main_content = ft.Column(expand=True)

    def sort_goals(goals: list[Goal]) -> list[Goal]:
        """Sort: incomplete first (newest on top), then completed (newest on top)."""
        incomplete = [g for g in goals if not g.is_completed]
        completed = [g for g in goals if g.is_completed]
        incomplete.sort(key=lambda g: g.created_at, reverse=True)
        completed.sort(key=lambda g: g.completed_at or g.created_at, reverse=True)
        return incomplete + completed

    async def refresh_goals():
        """Load and display goals."""
        goals = await load_goals(page)
        state["goals"] = sort_goals(goals)
        goals_column.controls.clear()

        if not state["goals"]:
            goals_column.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.FLAG_ROUNDED, color=MUTED, size=48),
                            ft.Text(
                                "No goals yet",
                                size=16, color=TEXT_MUTED, text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                "Tap + to create your first goal",
                                size=13, color="#3A4157", text_align=ft.TextAlign.CENTER,
                            ),
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
                        on_add_task=handle_add_task,
                        expanded=state["expanded_goal_id"] == goal.id,
                        on_expand=handle_expand,
                    )
                )

        await update_stats()
        page.update()

    # ── Toggle handlers ─────────────────────────────────────────
    async def toggle_goal_async(goal_id: str, value: bool):
        goal = await get_goal(page, goal_id)
        if goal:
            if value:
                goal.mark_complete(utc_now())
            else:
                goal.mark_incomplete()
            await save_goal(page, goal)
            await refresh_goals()

    def toggle_goal(goal_id: str, value: bool):
        page.run_task(toggle_goal_async, goal_id, value)

    async def toggle_task_async(goal_id: str, task_id: str, value: bool):
        """Toggle a task. If ticked, all sub-tasks get ticked. If unticked, all sub-tasks get unticked."""
        goal = await get_goal(page, goal_id)
        if goal:
            now = utc_now()
            for task in goal.sub_tasks:
                if task.id == task_id:
                    task.is_completed = value
                    task.completed_at = now if value else None
                    # Cascade to all sub-tasks
                    for subtask in task.steps:
                        subtask.is_completed = value
                        subtask.completed_at = now if value else None
                    break
            
            # Check if all tasks are done to auto-complete goal
            all_done = all(t.is_completed for t in goal.sub_tasks) if goal.sub_tasks else False
            if all_done and goal.sub_tasks:
                goal.is_completed = True
                goal.completed_at = now
            else:
                goal.is_completed = False
                goal.completed_at = None
            
            await save_goal(page, goal)
            await refresh_goals()

    def toggle_task(goal_id: str, task_id: str, value: bool):
        page.run_task(toggle_task_async, goal_id, task_id, value)

    async def toggle_subtask_async(goal_id: str, task_id: str, subtask_id: str, value: bool):
        """Toggle a sub-task (was step)."""
        goal = await get_goal(page, goal_id)
        if goal:
            now = utc_now()
            for task in goal.sub_tasks:
                if task.id == task_id:
                    for subtask in task.steps:
                        if subtask.id == subtask_id:
                            subtask.is_completed = value
                            subtask.completed_at = now if value else None
                            break
                    
                    # Check if all sub-tasks are done to auto-complete task
                    all_subtasks_done = all(s.is_completed for s in task.steps) if task.steps else True
                    if all_subtasks_done:
                        task.is_completed = True
                        task.completed_at = now
                    elif not value:
                        task.is_completed = False
                        task.completed_at = None
                    break
            
            # Check if all tasks are done to auto-complete goal
            all_done = all(t.is_completed for t in goal.sub_tasks) if goal.sub_tasks else False
            if all_done and goal.sub_tasks:
                goal.is_completed = True
                goal.completed_at = now
            else:
                goal.is_completed = False
                goal.completed_at = None
            
            await save_goal(page, goal)
            await refresh_goals()

    def toggle_subtask(goal_id: str, task_id: str, subtask_id: str, value: bool):
        page.run_task(toggle_subtask_async, goal_id, task_id, subtask_id, value)

    # ── Action handlers ─────────────────────────────────────────
    def handle_expand(goal_id: str):
        if state["expanded_goal_id"] == goal_id:
            state["expanded_goal_id"] = None
        else:
            state["expanded_goal_id"] = goal_id
        page.run_task(refresh_goals)

    async def handle_delete_goal_async(goal_id: str):
        await delete_goal(page, goal_id)
        state["expanded_goal_id"] = None
        await refresh_goals()

    def handle_delete_goal(goal_id: str):
        page.run_task(handle_delete_goal_async, goal_id)

    def handle_edit_goal(goal_id: str):
        # TODO: Implement edit dialog
        pass

    def handle_add_task(goal_id: str):
        # TODO: Implement add task dialog
        pass

    # ── Wizard handlers ─────────────────────────────────────────
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

    async def save_new_goal_async(goal: Goal):
        await save_goal(page, goal)
        hide_wizard()
        await refresh_goals()

    def save_new_goal(goal: Goal):
        page.run_task(save_new_goal_async, goal)

    # ── Header ──────────────────────────────────────────────────
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
                bgcolor=TEAL,
                foreground_color=BG,
                mini=True,
                on_click=lambda e: show_wizard(),
            ),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ── Stats bar ───────────────────────────────────────────────
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

    # ── Main content ────────────────────────────────────────────
    main_content.controls = [
        header,
        ft.Container(content=stats_container, padding=ft.Padding.symmetric(vertical=8)),
        ft.Text("Goals", size=14, weight=ft.FontWeight.W_600, color=TEXT_SECONDARY),
        goals_column,
    ]
    main_content.spacing = 12

    # ── Initial load ────────────────────────────────────────────
    page.run_task(refresh_goals)

    return ft.Stack(
        controls=[
            main_content,
            wizard_container,
        ],
        expand=True,
    )
