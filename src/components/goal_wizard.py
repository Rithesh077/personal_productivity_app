"""Goal creation wizard for Stride - multi-step guided flow."""

import flet as ft
from typing import Callable, Optional
from models.goal import Goal, SubTask, Step
from utils.time_utils import utc_now, get_default_deadline

# Design tokens
TEAL = "#00D9A6"
CARD_BG = "#141927"
SURFACE = "#1E2436"
TEXT_PRIMARY = "#E0E0E0"
TEXT_SECONDARY = "#8A92A6"
TEXT_MUTED = "#5A6478"
BG = "#0B0F1A"


class GoalWizard:
    """Multi-step wizard for creating goals with tasks and sub-tasks."""

    def __init__(self, page: ft.Page, on_save: Callable[[Goal], None], on_cancel: Callable):
        self.page = page
        self.on_save = on_save
        self.on_cancel = on_cancel

        # Wizard state
        self.step = 0  # 0=goal title, 1=tasks (with inline sub-tasks)
        self.goal_title = ""
        self.tasks: list[dict] = []  # [{title, subtasks: [str], expanded: bool}]
        self.use_custom_deadline = False
        self.custom_deadline: Optional[str] = None

        # UI elements
        self.content = ft.Container()
        self._build_step_0()

    def _build_step_0(self):
        """Step 0: Enter goal title."""
        self.title_input = ft.TextField(
            hint_text="What's your goal?",
            border_radius=12,
            bgcolor=CARD_BG,
            border_color=SURFACE,
            focused_border_color=TEAL,
            cursor_color=TEAL,
            hint_style=ft.TextStyle(color=TEXT_MUTED),
            text_style=ft.TextStyle(color=TEXT_PRIMARY, size=18),
            autofocus=True,
            on_submit=lambda e: self._next_step(),
        )

        self.content.content = ft.Column(
            controls=[
                ft.Text("Create New Goal", size=22,
                        weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Text("Step 1 of 2: Define your goal",
                        size=13, color=TEXT_SECONDARY),
                ft.Container(height=16),
                self.title_input,
                ft.Container(height=8),
                ft.Row(
                    controls=[
                        ft.Checkbox(
                            label="Set custom deadline",
                            value=self.use_custom_deadline,
                            active_color=TEAL,
                            label_style=ft.TextStyle(
                                color=TEXT_SECONDARY, size=13),
                            on_change=lambda e: self._toggle_deadline(
                                e.control.value),
                        ),
                    ],
                ),
                ft.Container(height=16),
                ft.Row(
                    controls=[
                        ft.TextButton(
                            "Cancel",
                            on_click=lambda e: self.on_cancel(),
                            style=ft.ButtonStyle(color=TEXT_SECONDARY),
                        ),
                        ft.Container(expand=True),
                        ft.FilledButton(
                            "Next: Add Tasks",
                            icon=ft.Icons.ARROW_FORWARD_ROUNDED,
                            bgcolor=TEAL,
                            color=BG,
                            on_click=lambda e: self._next_step(),
                        ),
                    ],
                ),
            ],
            spacing=8,
        )
        self.page.update()

    def _toggle_deadline(self, value: bool):
        self.use_custom_deadline = value
        # Could add date picker here in future
        self.page.update()

    def _build_step_1(self):
        """Step 1: Add tasks. Click on them to add sub-tasks."""
        self.task_input = ft.TextField(
            hint_text="Add a task...",
            border_radius=12,
            bgcolor=CARD_BG,
            border_color=SURFACE,
            focused_border_color=TEAL,
            cursor_color=TEAL,
            hint_style=ft.TextStyle(color=TEXT_MUTED),
            text_style=ft.TextStyle(color=TEXT_PRIMARY),
            autofocus=True,
            expand=True,
            on_submit=lambda e: self._add_task(),
        )

        self.tasks_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
        self._refresh_tasks_list()

        self.content.content = ft.Column(
            controls=[
                ft.Text("Create New Goal", size=22,
                        weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Text(f"Step 2 of 2: Add tasks for \"{self.goal_title}\"",
                        size=13, color=TEXT_SECONDARY),
                ft.Text("Click on a task to add sub-tasks", size=12, color=TEXT_MUTED, italic=True),
                ft.Container(height=12),
                ft.Row(
                    controls=[
                        self.task_input,
                        ft.IconButton(
                            icon=ft.Icons.ADD_CIRCLE_ROUNDED,
                            icon_color=TEAL,
                            icon_size=36,
                            on_click=lambda e: self._add_task(),
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(height=8),
                self.tasks_list,
                ft.Container(expand=True),
                ft.Row(
                    controls=[
                        ft.TextButton(
                            "Back",
                            icon=ft.Icons.ARROW_BACK_ROUNDED,
                            on_click=lambda e: self._prev_step(),
                            style=ft.ButtonStyle(color=TEXT_SECONDARY),
                        ),
                        ft.Container(expand=True),
                        ft.TextButton(
                            "Skip (no tasks)",
                            on_click=lambda e: self._save_goal(),
                            style=ft.ButtonStyle(color=TEXT_MUTED),
                        ) if not self.tasks else ft.Container(),
                        ft.FilledButton(
                            "Save Goal",
                            icon=ft.Icons.CHECK_ROUNDED,
                            bgcolor=TEAL,
                            color=BG,
                            on_click=lambda e: self._save_goal(),
                        ),
                    ],
                ),
            ],
            spacing=8,
            expand=True,
        )
        self.page.update()

    def _refresh_tasks_list(self):
        """Refresh the list of added tasks with expandable sub-task input."""
        self.tasks_list.controls.clear()
        if not self.tasks:
            self.tasks_list.controls.append(
                ft.Text("No tasks added yet", size=13,
                        color=TEXT_MUTED, italic=True)
            )
        else:
            for i, task in enumerate(self.tasks):
                self.tasks_list.controls.append(
                    self._build_task_card(i, task)
                )

    def _build_task_card(self, index: int, task: dict):
        """Build a task card that can be expanded to add sub-tasks."""
        is_expanded = task.get("expanded", False)

        # Sub-tasks list
        subtasks_column = ft.Column(spacing=4)
        for j, subtask_text in enumerate(task["subtasks"]):
            subtasks_column.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(f"{j + 1}.", size=12, color=TEXT_MUTED),
                            ft.Text(subtask_text, size=13, color=TEXT_SECONDARY, expand=True),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE_ROUNDED,
                                icon_color=TEXT_MUTED,
                                icon_size=14,
                                on_click=lambda e, idx=index, sidx=j: self._remove_subtask(idx, sidx),
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding.only(left=16),
                )
            )

        # Sub-task input field
        subtask_input_field = ft.TextField(
            hint_text="Add a sub-task...",
            border_radius=8,
            bgcolor=BG,
            border_color=SURFACE,
            focused_border_color=TEAL,
            cursor_color=TEAL,
            hint_style=ft.TextStyle(color=TEXT_MUTED, size=13),
            text_style=ft.TextStyle(color=TEXT_PRIMARY, size=13),
            expand=True,
            data=index,
            on_submit=lambda e: self._add_subtask_from_field(e.control),
        )

        expanded_content = ft.Column(
            controls=[
                ft.Container(height=8),
                ft.Row(
                    controls=[
                        subtask_input_field,
                        ft.IconButton(
                            icon=ft.Icons.ADD_ROUNDED,
                            icon_color=TEAL,
                            icon_size=24,
                            data=subtask_input_field,
                            on_click=lambda e: self._add_subtask_from_field(e.control.data),
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                subtasks_column if task["subtasks"] else ft.Container(),
            ],
            spacing=4,
        ) if is_expanded else ft.Container()

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.SUBDIRECTORY_ARROW_RIGHT_ROUNDED,
                                        color=TEAL if is_expanded else TEXT_MUTED, size=18),
                                ft.Text(task["title"], size=14, color=TEXT_PRIMARY, expand=True),
                                ft.Text(f"{len(task['subtasks'])} sub-tasks", size=12, color=TEXT_MUTED),
                                ft.Icon(
                                    ft.Icons.EXPAND_LESS_ROUNDED if is_expanded else ft.Icons.EXPAND_MORE_ROUNDED,
                                    color=TEXT_SECONDARY,
                                    size=20,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_ROUNDED,
                                    icon_color=TEXT_MUTED,
                                    icon_size=16,
                                    on_click=lambda e, idx=index: self._remove_task(idx),
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        on_click=lambda e, idx=index: self._toggle_task_expand(idx),
                        padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                    ),
                    expanded_content,
                ],
                spacing=0,
            ),
            bgcolor=SURFACE,
            border_radius=8,
            border=ft.Border.all(1, TEAL) if is_expanded else None,
        )

    def _toggle_task_expand(self, index: int):
        """Toggle expansion of a task to show/hide sub-task input."""
        for i, task in enumerate(self.tasks):
            if i == index:
                task["expanded"] = not task.get("expanded", False)
            else:
                task["expanded"] = False
        self._refresh_tasks_list()
        self.page.update()

    def _add_subtask_from_field(self, input_field):
        """Add sub-task from the input field."""
        if input_field and input_field.value and input_field.value.strip():
            idx = input_field.data
            self.tasks[idx]["subtasks"].append(input_field.value.strip())
            input_field.value = ""
            self._refresh_tasks_list()
            self.page.update()

    def _remove_subtask(self, task_index: int, subtask_index: int):
        """Remove a sub-task from a task."""
        self.tasks[task_index]["subtasks"].pop(subtask_index)
        self._refresh_tasks_list()
        self.page.update()

    def _add_task(self):
        title = self.task_input.value.strip()
        if title:
            self.tasks.append({"title": title, "subtasks": [], "expanded": False})
            self.task_input.value = ""
            self._refresh_tasks_list()
            self.page.update()

    def _remove_task(self, index: int):
        self.tasks.pop(index)
        self._refresh_tasks_list()
        self.page.update()

    def _next_step(self):
        if self.step == 0:
            title = self.title_input.value.strip()
            if not title:
                return
            self.goal_title = title
            self.step = 1
            self._build_step_1()

    def _prev_step(self):
        if self.step == 1:
            self.step = 0
            self._build_step_0()

    def _save_goal(self):
        """Create and save the goal."""
        now = utc_now()
        deadline = self.custom_deadline if self.use_custom_deadline else get_default_deadline()

        # Build goal structure (tasks -> SubTask, subtasks -> Step)
        sub_tasks = []
        for task_data in self.tasks:
            steps = [
                Step(title=subtask_title, created_at=now)
                for subtask_title in task_data["subtasks"]
            ]
            sub_tasks.append(SubTask(
                title=task_data["title"],
                created_at=now,
                steps=steps,
            ))

        goal = Goal(
            title=self.goal_title,
            created_at=now,
            deadline=deadline,
            sub_tasks=sub_tasks,
        )

        self.on_save(goal)

    def build(self) -> ft.Container:
        """Return the wizard container."""
        return ft.Container(
            content=self.content,
            bgcolor=BG,
            border_radius=16,
            padding=ft.Padding.all(20),
            border=ft.Border.all(1, SURFACE),
            expand=True,
        )
