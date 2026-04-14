"""goal creation wizard - multi-step guided flow."""

import flet as ft
from datetime import datetime, time
from typing import Callable, Optional
from models.goal import Goal, Task, SubTask
from constants.design import (
    TEAL, BG, CARD_BG, SURFACE,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
)
from utils.time_utils import utc_now, get_default_deadline, local_to_utc, extract_local_date, today_midnight


class GoalWizard:
    """two-step wizard: 1) goal title + deadline, 2) tasks with subtasks."""

    def __init__(self, page: ft.Page, on_save: Callable[[Goal], None],
                 on_cancel: Callable, initial_goal: Optional[Goal] = None):
        self.page = page
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.initial_goal = initial_goal
        self.editing = initial_goal is not None
        self.original_goal_id = initial_goal.id if initial_goal else None

        # wizard state
        self.step = 0
        self.goal_title = initial_goal.title if initial_goal else ""

        # task entries preserve original model objects when editing
        self.tasks: list[dict] = []
        if initial_goal:
            for task in initial_goal.tasks:
                self.tasks.append({
                    "title": task.title,
                    "subtasks": [st.title for st in task.sub_tasks],
                    "expanded": False,
                    "_task": task,
                    "_subtask_models": list(task.sub_tasks),
                })

        self.use_custom_deadline = initial_goal.has_custom_deadline if initial_goal else False
        self.custom_deadline_dt: Optional[datetime] = None
        if initial_goal and initial_goal.has_custom_deadline and initial_goal.deadline:
            try:
                self.custom_deadline_dt = datetime.fromisoformat(
                    initial_goal.deadline.replace("Z", "+00:00")
                ).astimezone()
            except Exception:
                self.custom_deadline_dt = None

        # ui elements
        self.content = ft.Container()
        self.deadline_display = ft.Text("", size=12, color=TEAL)
        self._build_step_0()

    def _build_step_0(self):
        """step 0: goal title + deadline settings."""
        self.title_input = ft.TextField(
            hint_text="What's your goal?",
            value=self.goal_title,
            border_radius=12, bgcolor=CARD_BG,
            border_color=SURFACE, focused_border_color=TEAL,
            cursor_color=TEAL,
            hint_style=ft.TextStyle(color=TEXT_MUTED),
            text_style=ft.TextStyle(color=TEXT_PRIMARY, size=18),
            autofocus=True,
            on_submit=lambda e: self._next_step(),
        )

        self._update_deadline_display()

        deadline_section = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Checkbox(
                            label="Custom deadline",
                            value=self.use_custom_deadline,
                            active_color=TEAL,
                            label_style=ft.TextStyle(color=TEXT_SECONDARY, size=13),
                            on_change=lambda e: self._toggle_deadline(e.control.value),
                        ),
                        ft.Container(expand=True),
                        ft.TextButton(
                            "Pick date",
                            icon=ft.Icons.CALENDAR_MONTH_ROUNDED,
                            on_click=lambda e: self._open_date_picker(),
                            style=ft.ButtonStyle(color=TEAL),
                            visible=self.use_custom_deadline,
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                self.deadline_display,
            ],
            spacing=4,
        )

        self.content.content = ft.Column(
            controls=[
                ft.Text(
                    "Create New Goal" if not self.editing else "Edit Goal",
                    size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY,
                ),
                ft.Text("Step 1 of 2: Define your goal", size=13, color=TEXT_SECONDARY),
                ft.Container(height=16),
                self.title_input,
                ft.Container(height=8),
                deadline_section,
                ft.Container(height=16),
                ft.Row(
                    controls=[
                        ft.TextButton(
                            "Cancel", on_click=lambda e: self.on_cancel(),
                            style=ft.ButtonStyle(color=TEXT_SECONDARY),
                        ),
                        ft.Container(expand=True),
                        ft.FilledButton(
                            "Next: Add Tasks",
                            icon=ft.Icons.ARROW_FORWARD_ROUNDED,
                            bgcolor=TEAL, color=BG,
                            on_click=lambda e: self._next_step(),
                        ),
                    ],
                ),
            ],
            spacing=8,
        )
        self.page.update()

    def _update_deadline_display(self):
        """update the deadline display text."""
        if self.use_custom_deadline and self.custom_deadline_dt:
            self.deadline_display.value = f"Due: {self.custom_deadline_dt.strftime('%b %d, %Y, %I:%M %p')}"
            self.deadline_display.color = TEAL
            self.deadline_display.visible = True
        elif not self.use_custom_deadline:
            self.deadline_display.value = "Default: 24 hours from creation"
            self.deadline_display.color = TEXT_MUTED
            self.deadline_display.visible = True
        else:
            self.deadline_display.value = "No date selected. Tap 'Pick date'."
            self.deadline_display.color = TEXT_MUTED
            self.deadline_display.visible = True

    def _toggle_deadline(self, value: bool):
        self.use_custom_deadline = value
        if not value:
            self.custom_deadline_dt = None
        self._build_step_0()

    def _open_date_picker(self):
        """open datepicker dialog."""
        initial_date = self.custom_deadline_dt or datetime.now()

        def on_date_change(e):
            self._show_time_option(date_picker.value)

        date_picker = ft.DatePicker(
            value=initial_date,
            first_date=today_midnight(),
            last_date=datetime(year=2030, month=12, day=31),
            help_text="Set deadline date",
            confirm_text="Next",
            on_change=on_date_change,
        )
        self.page.show_dialog(date_picker)

    def _show_time_option(self, selected_date):
        """after date selected, ask if user wants specific time."""

        def use_default_time(e=None):
            self.page.pop_dialog()
            target_date = extract_local_date(selected_date)
            self.custom_deadline_dt = datetime.combine(target_date, time(23, 59, 59))
            self._update_deadline_display()
            self._build_step_0()

        def open_time_picker(e=None):
            self.page.pop_dialog()

            def on_time_change(e):
                target_date = extract_local_date(selected_date)
                self.custom_deadline_dt = datetime.combine(
                    target_date, time(time_picker.value.hour, time_picker.value.minute, 0),
                )
                self._update_deadline_display()
                self._build_step_0()

            time_picker = ft.TimePicker(
                value=time(23, 59),
                help_text="Set deadline time",
                on_change=on_time_change,
            )
            self.page.show_dialog(time_picker)

        dlg = ft.AlertDialog(
            title=ft.Text("Set specific time?", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Text(
                "Default deadline time is 11:59 PM.\nChoose a specific time or use the default.",
                size=13, color=TEXT_SECONDARY,
            ),
            actions=[
                ft.TextButton(
                    "Use Default (11:59 PM)",
                    on_click=use_default_time,
                    style=ft.ButtonStyle(color=TEXT_SECONDARY),
                ),
                ft.FilledButton(
                    "Set Time",
                    icon=ft.Icons.ACCESS_TIME_ROUNDED,
                    bgcolor=TEAL, color=BG,
                    on_click=open_time_picker,
                ),
            ],
        )
        self.page.show_dialog(dlg)

    def _build_step_1(self):
        """step 1: add tasks, click to expand for subtasks."""
        self.task_input = ft.TextField(
            hint_text="Add a task...",
            border_radius=12, bgcolor=CARD_BG,
            border_color=SURFACE, focused_border_color=TEAL,
            cursor_color=TEAL,
            hint_style=ft.TextStyle(color=TEXT_MUTED),
            text_style=ft.TextStyle(color=TEXT_PRIMARY),
            autofocus=True, expand=True,
            on_submit=lambda e: self._add_task(),
        )

        self.tasks_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
        self._refresh_tasks_list()

        self.content.content = ft.Column(
            controls=[
                ft.Text(
                    "Create New Goal" if not self.editing else "Edit Goal",
                    size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY,
                ),
                ft.Text(
                    f'Step 2 of 2: Add tasks for "{self.goal_title}"',
                    size=13, color=TEXT_SECONDARY,
                ),
                ft.Text("Click on a task to add sub-tasks", size=12, color=TEXT_MUTED, italic=True),
                ft.Container(height=12),
                ft.Row(
                    controls=[
                        self.task_input,
                        ft.IconButton(
                            icon=ft.Icons.ADD_CIRCLE_ROUNDED,
                            icon_color=TEAL, icon_size=36,
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
                            "Back", icon=ft.Icons.ARROW_BACK_ROUNDED,
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
                            "Update Goal" if self.editing else "Save Goal",
                            icon=ft.Icons.CHECK_ROUNDED,
                            bgcolor=TEAL, color=BG,
                            on_click=lambda e: self._save_goal(),
                        ),
                    ],
                ),
            ],
            spacing=8, expand=True,
        )
        self.page.update()

    def _refresh_tasks_list(self):
        """refresh the displayed task list."""
        self.tasks_list.controls.clear()
        if not self.tasks:
            self.tasks_list.controls.append(
                ft.Text("No tasks added yet", size=13, color=TEXT_MUTED, italic=True)
            )
        else:
            for i, task in enumerate(self.tasks):
                self.tasks_list.controls.append(self._build_task_card(i, task))

    def _build_task_card(self, index: int, task: dict):
        """expandable task card for adding subtasks."""
        is_expanded = task.get("expanded", False)

        subtasks_column = ft.Column(spacing=4)
        for j, subtask_text in enumerate(task["subtasks"]):
            subtasks_column.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(f"{j + 1}.", size=12, color=TEXT_MUTED),
                            ft.Text(subtask_text, size=13, color=TEXT_SECONDARY, expand=True),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE_ROUNDED, icon_color=TEXT_MUTED, icon_size=14,
                                on_click=lambda e, idx=index, sidx=j: self._remove_subtask(idx, sidx),
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding.only(left=16),
                )
            )

        subtask_input_field = ft.TextField(
            hint_text="Add a sub-task...",
            border_radius=8, bgcolor=BG,
            border_color=SURFACE, focused_border_color=TEAL,
            cursor_color=TEAL,
            hint_style=ft.TextStyle(color=TEXT_MUTED, size=13),
            text_style=ft.TextStyle(color=TEXT_PRIMARY, size=13),
            expand=True, data=index,
            on_submit=lambda e: self._add_subtask_from_field(e.control),
        )

        expanded_content = ft.Column(
            controls=[
                ft.Container(height=8),
                ft.Row(
                    controls=[
                        subtask_input_field,
                        ft.IconButton(
                            icon=ft.Icons.ADD_ROUNDED, icon_color=TEAL, icon_size=24,
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
                                ft.Icon(
                                    ft.Icons.SUBDIRECTORY_ARROW_RIGHT_ROUNDED,
                                    color=TEAL if is_expanded else TEXT_MUTED, size=18,
                                ),
                                ft.Text(task["title"], size=14, color=TEXT_PRIMARY, expand=True),
                                ft.Text(f"{len(task['subtasks'])} sub-tasks", size=12, color=TEXT_MUTED),
                                ft.Icon(
                                    ft.Icons.EXPAND_LESS_ROUNDED if is_expanded else ft.Icons.EXPAND_MORE_ROUNDED,
                                    color=TEXT_SECONDARY, size=20,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_ROUNDED, icon_color=TEXT_MUTED, icon_size=16,
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
        for i, task in enumerate(self.tasks):
            task["expanded"] = (i == index) and not task.get("expanded", False)
        self._refresh_tasks_list()
        self.page.update()

    def _add_subtask_from_field(self, input_field):
        if input_field and input_field.value and input_field.value.strip():
            idx = input_field.data
            self.tasks[idx]["subtasks"].append(input_field.value.strip())
            if "_subtask_models" in self.tasks[idx]:
                self.tasks[idx]["_subtask_models"].append(None)
            input_field.value = ""
            self._refresh_tasks_list()
            self.page.update()

    def _remove_subtask(self, task_index: int, subtask_index: int):
        self.tasks[task_index]["subtasks"].pop(subtask_index)
        if "_subtask_models" in self.tasks[task_index]:
            models = self.tasks[task_index]["_subtask_models"]
            if subtask_index < len(models):
                models.pop(subtask_index)
        self._refresh_tasks_list()
        self.page.update()

    def _add_task(self):
        title = self.task_input.value.strip()
        if title:
            self.tasks.append({
                "title": title, "subtasks": [], "expanded": False,
                "_task": None, "_subtask_models": [],
            })
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
        """build the goal model, preserving existing state when editing."""
        now = utc_now()

        if self.use_custom_deadline and self.custom_deadline_dt:
            deadline = local_to_utc(self.custom_deadline_dt)
        else:
            deadline = get_default_deadline()

        tasks = []
        for task_position, task_data in enumerate(self.tasks):
            original_task = task_data.get("_task")
            subtask_models = task_data.get("_subtask_models", [])

            sub_tasks = []
            for subtask_position, subtask_title in enumerate(task_data["subtasks"]):
                original_subtask = subtask_models[subtask_position] if subtask_position < len(subtask_models) else None
                if original_subtask is not None:
                    if subtask_title != original_subtask.title:
                        original_subtask.updated_at = now
                    original_subtask.title = subtask_title
                    original_subtask.position = subtask_position
                    sub_tasks.append(original_subtask)
                else:
                    sub_tasks.append(SubTask(
                        title=subtask_title, created_at=now, position=subtask_position,
                    ))

            if original_task is not None:
                if task_data["title"] != original_task.title:
                    original_task.updated_at = now
                original_task.title = task_data["title"]
                original_task.position = task_position
                original_task.sub_tasks = sub_tasks
                tasks.append(original_task)
            else:
                tasks.append(Task(
                    title=task_data["title"], created_at=now,
                    position=task_position, sub_tasks=sub_tasks,
                ))

        goal_kwargs = {
            "title": self.goal_title,
            "created_at": self.initial_goal.created_at if self.initial_goal else now,
            "updated_at": now if self.initial_goal else None,
            "deadline": deadline,
            "has_custom_deadline": self.use_custom_deadline,
            "tasks": tasks,
        }

        if self.initial_goal:
            goal_kwargs["id"] = self.initial_goal.id
            goal_kwargs["is_completed"] = self.initial_goal.is_completed
            goal_kwargs["completed_at"] = self.initial_goal.completed_at

        self.on_save(Goal(**goal_kwargs))

    def build(self) -> ft.Container:
        """return the wizard container."""
        return ft.Container(
            content=self.content,
            bgcolor=BG, border_radius=16,
            padding=ft.Padding.all(20),
            border=ft.Border.all(1, SURFACE),
            expand=True,
        )
