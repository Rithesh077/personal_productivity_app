"""priority tasks list view — ordered list of immediate tasks.

designed to tackle a faulty default mode network (DMN) or low-quality
input from the environment. when you catch yourself drifting, pull your
NEXT UP task and start working on it.

not to be confused with the Planner tab, where goals and tasks that
require deep focus are nested hierarchically.
"""

import flet as ft
from typing import Optional

from services.storage import (
    load_task_list, save_task_list, save_task_item, delete_task_item,
    complete_task_item, load_goals, load_custom_tags, save_custom_tags,
)
from models.task_item import TaskItem, DEFAULT_TAGS
from components.task_list_card import TaskListCard
from constants.design import (
    TEAL, RED, BG, CARD_BG, SURFACE, MUTED,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    TAG_COLORS, DEFAULT_TAGS as DESIGN_DEFAULT_TAGS,
)
from utils.time_utils import utc_now


def build_task_list(page: ft.Page):
    """build the priority tasks list view."""

    state = {
        "items": [],
        "goals": [],
        "custom_tags": [],
        "insert_mode": False,
        "insert_position": 0,
    }

    list_column = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)

    # ── loading skeleton ──

    def _skeleton_card():
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(expand=True, height=16, bgcolor=SURFACE, border_radius=4),
                    ft.Container(width=22, height=22, bgcolor=SURFACE, border_radius=4),
                ], spacing=12),
                ft.Container(height=8, bgcolor=SURFACE, border_radius=4,
                             margin=ft.Margin.only(top=4, right=40, left=0, bottom=0)),
            ], spacing=8),
            bgcolor=CARD_BG, border_radius=12, padding=16,
            border=ft.Border.all(1, SURFACE),
        )

    list_column.controls = [_skeleton_card(), _skeleton_card()]

    # ── refresh ──

    async def refresh_list():
        """load and display task list items."""
        state["items"] = await load_task_list(page)
        state["goals"] = await load_goals(page)
        state["custom_tags"] = await load_custom_tags(page)

        list_column.controls.clear()

        if not state["items"]:
            list_column.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.PLAYLIST_ADD_ROUNDED, color=MUTED, size=48),
                            ft.Text("Your task list is empty", size=16, color=TEXT_MUTED,
                                    text_align=ft.TextAlign.CENTER),
                            ft.Text("Tap + to add your first task", size=13,
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
            # insert target at position 0 (top)
            list_column.controls.append(_build_insert_target(0))

            for idx, item in enumerate(state["items"]):
                # resolve linked goal title
                linked_title = None
                if item.linked_goal_id:
                    for g in state["goals"]:
                        if g.id == item.linked_goal_id:
                            linked_title = g.title
                            break

                # draggable card
                card = TaskListCard(
                    item=item,
                    is_next=(idx == 0),
                    linked_goal_title=linked_title,
                    on_complete=handle_complete,
                    on_delete=handle_delete,
                    on_edit=handle_edit,
                )

                # wrap in drag/drop for reorder
                draggable_card = ft.LongPressDraggable(
                    content=card,
                    group="task_list",
                    data=str(idx),
                    content_when_dragging=ft.Container(
                        height=60, bgcolor=SURFACE, border_radius=12,
                        border=ft.Border.all(1, TEAL),
                        opacity=0.3,
                    ),
                    content_feedback=ft.Container(
                        content=ft.Text(item.title, size=14, color=TEXT_PRIMARY),
                        bgcolor=CARD_BG, border_radius=12, padding=16,
                        border=ft.Border.all(2, TEAL),
                        width=300, opacity=0.9,
                        shadow=ft.BoxShadow(
                            blur_radius=20, color=f"{TEAL}40",
                            spread_radius=2,
                        ),
                    ),
                )

                # drag target wrapping the card
                drag_target = ft.DragTarget(
                    content=draggable_card,
                    group="task_list",
                    data=str(idx),
                    on_accept=lambda e, target_idx=idx: handle_drag_accept(e, target_idx),
                )

                list_column.controls.append(
                    ft.Container(content=drag_target, margin=ft.Margin.only(bottom=2))
                )

                # insert target after each card
                list_column.controls.append(_build_insert_target(idx + 1))

        page.update()

    # ── insert targets ──

    def _build_insert_target(position: int):
        """thin tappable line between cards to insert at a specific position."""
        line = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(expand=True, height=1.5, bgcolor=f"{TEAL}30"),
                    ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED, size=14, color=f"{TEAL}50"),
                    ft.Container(expand=True, height=1.5, bgcolor=f"{TEAL}30"),
                ],
                spacing=4,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(vertical=4, horizontal=8),
            opacity=0.0,
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
            on_hover=lambda e: _on_insert_hover(e, line),
            on_click=lambda e: show_add_dialog(position),
            height=20,
        )
        return line

    def _on_insert_hover(e, container):
        container.opacity = 1.0 if e.data == "true" else 0.0
        try:
            container.update()
        except Exception:
            pass

    # ── drag reorder ──

    def handle_drag_accept(e, target_idx):
        """handle a drag reorder: move dragged item to target position."""
        src_idx = int(e.src_id)

        async def do_reorder():
            items = state["items"]
            if src_idx == target_idx or src_idx < 0 or src_idx >= len(items):
                return
            item = items.pop(src_idx)
            # adjust target index if source was before target
            adj_target = target_idx if src_idx > target_idx else target_idx - 1
            adj_target = max(0, min(adj_target, len(items)))
            items.insert(adj_target, item)
            for idx, it in enumerate(items):
                it.position = idx
            await save_task_list(page, items)
            await refresh_list()

        page.run_task(do_reorder)

    # ── complete ──

    def handle_complete(item_id):
        """show confirmation then complete the item."""
        async def show_confirm():
            item = None
            for it in state["items"]:
                if it.id == item_id:
                    item = it
                    break
            if not item:
                return

            # tag chips for dialog
            tag_row = ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(tag, size=10, color=TAG_COLORS.get(tag, MUTED)),
                        bgcolor=f"{TAG_COLORS.get(tag, MUTED)}18",
                        border_radius=4,
                        padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                    )
                    for tag in item.tags
                ],
                spacing=4, wrap=True,
            ) if item.tags else ft.Container()

            def close(e=None):
                page.pop_dialog()

            def confirm(e=None):
                page.pop_dialog()
                page.run_task(do_complete, item_id)

            dlg = ft.AlertDialog(
                title=ft.Text("Complete this task?", size=16, weight=ft.FontWeight.BOLD),
                content=ft.Column([
                    ft.Text(f'"{item.title}"', size=14, color=TEXT_PRIMARY, italic=True),
                    ft.Container(height=4),
                    tag_row,
                ], spacing=4, tight=True),
                actions=[
                    ft.TextButton("Cancel", on_click=close),
                    ft.FilledButton("Complete ✓", bgcolor=TEAL, color=BG, on_click=confirm),
                ],
            )
            page.show_dialog(dlg)

        page.run_task(show_confirm)

    async def do_complete(item_id):
        await complete_task_item(page, item_id)
        await refresh_list()

    # ── delete ──

    def handle_delete(item_id):
        """show confirmation then delete."""
        async def show_confirm():
            item = None
            for it in state["items"]:
                if it.id == item_id:
                    item = it
                    break
            if not item:
                return

            def close(e=None):
                page.pop_dialog()

            def confirm(e=None):
                page.pop_dialog()
                page.run_task(do_delete, item_id)

            dlg = ft.AlertDialog(
                title=ft.Text("Delete this task?", size=16, weight=ft.FontWeight.BOLD),
                content=ft.Text(f'"{item.title}"', size=14, color=TEXT_PRIMARY),
                actions=[
                    ft.TextButton("Cancel", on_click=close),
                    ft.FilledButton("Delete", bgcolor=RED, color="white", on_click=confirm),
                ],
            )
            page.show_dialog(dlg)

        page.run_task(show_confirm)

    async def do_delete(item_id):
        await delete_task_item(page, item_id)
        await refresh_list()

    # ── edit ──

    def handle_edit(item_id):
        """open edit dialog for an existing item."""
        async def show_edit():
            item = None
            for it in state["items"]:
                if it.id == item_id:
                    item = it
                    break
            if not item:
                return
            _show_item_dialog(
                edit_item=item,
                insert_position=item.position,
            )

        page.run_task(show_edit)

    # ── add dialog ──

    def show_add_dialog(position: int = None):
        """open the add-item dialog."""
        if position is None:
            position = len(state["items"])
        _show_item_dialog(edit_item=None, insert_position=position)

    def _show_item_dialog(edit_item: Optional[TaskItem], insert_position: int):
        """shared dialog for add/edit. if edit_item is None, it's a new item."""
        is_editing = edit_item is not None

        title_field = ft.TextField(
            hint_text="What do you need to do?",
            value=edit_item.title if is_editing else "",
            border_radius=8, bgcolor=SURFACE,
            border_color=SURFACE, focused_border_color=TEAL,
            cursor_color=TEAL,
            hint_style=ft.TextStyle(color=TEXT_MUTED),
            text_style=ft.TextStyle(color=TEXT_PRIMARY, size=15),
            autofocus=True,
        )

        desc_field = ft.TextField(
            hint_text="Description (optional)",
            value=edit_item.description if is_editing else "",
            border_radius=8, bgcolor=SURFACE,
            border_color=SURFACE, focused_border_color=TEAL,
            cursor_color=TEAL,
            hint_style=ft.TextStyle(color=TEXT_MUTED, size=13),
            text_style=ft.TextStyle(color=TEXT_SECONDARY, size=13),
            multiline=True, min_lines=1, max_lines=3,
        )

        # tag selection state
        all_tags = list(DEFAULT_TAGS)
        for ct in state["custom_tags"]:
            if ct not in all_tags:
                all_tags.append(ct)
        selected_tags = set(edit_item.tags if is_editing else [])

        tag_chips_container = ft.Row(spacing=6, wrap=True)
        custom_tag_field = ft.TextField(
            hint_text="+ custom tag",
            border_radius=6, bgcolor=SURFACE,
            border_color="transparent", focused_border_color=TEAL,
            cursor_color=TEAL,
            hint_style=ft.TextStyle(color=TEXT_MUTED, size=11),
            text_style=ft.TextStyle(color=TEXT_PRIMARY, size=11),
            content_padding=ft.Padding.symmetric(horizontal=8, vertical=4),
            width=100,
        )

        def _refresh_tag_chips():
            tag_chips_container.controls.clear()
            for tag in all_tags:
                is_selected = tag in selected_tags
                color = TAG_COLORS.get(tag, MUTED)
                chip = ft.Container(
                    content=ft.Text(
                        tag, size=11, color=color if is_selected else TEXT_MUTED,
                        weight=ft.FontWeight.W_600 if is_selected else ft.FontWeight.NORMAL,
                    ),
                    bgcolor=f"{color}25" if is_selected else "transparent",
                    border=ft.Border.all(1, color if is_selected else SURFACE),
                    border_radius=6,
                    padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                    on_click=lambda e, t=tag: _toggle_tag(t),
                )
                tag_chips_container.controls.append(chip)

            # add custom tag button
            def add_custom_tag(e):
                new_tag = custom_tag_field.value.strip().lower()
                if new_tag and new_tag not in all_tags:
                    all_tags.append(new_tag)
                    selected_tags.add(new_tag)
                    # save custom tag
                    if new_tag not in state["custom_tags"]:
                        state["custom_tags"].append(new_tag)
                        page.run_task(save_custom_tags, page, state["custom_tags"])
                elif new_tag in all_tags:
                    selected_tags.add(new_tag)
                custom_tag_field.value = ""
                _refresh_tag_chips()
                page.update()

            custom_tag_field.on_submit = add_custom_tag
            tag_chips_container.controls.append(custom_tag_field)

        def _toggle_tag(tag):
            if tag in selected_tags:
                selected_tags.discard(tag)
            else:
                selected_tags.add(tag)
            _refresh_tag_chips()
            page.update()

        _refresh_tag_chips()

        # goal linker dropdown
        goal_options = [ft.dropdown.Option(key="", text="None")]
        for g in state["goals"]:
            label = g.title if len(g.title) <= 30 else g.title[:30] + "..."
            goal_options.append(ft.dropdown.Option(key=g.id, text=label))

        goal_dropdown = ft.Dropdown(
            options=goal_options,
            value=edit_item.linked_goal_id or "" if is_editing else "",
            border_radius=8, bgcolor=SURFACE,
            border_color=SURFACE, focused_border_color=TEAL,
            color=TEXT_PRIMARY, text_size=13,
            label="Link to Goal (optional)",
            label_style=ft.TextStyle(color=TEXT_MUTED, size=12),
        )

        # position display
        pos_text = ft.Text(
            f"Position: #{insert_position + 1} in list"
            if not is_editing else f"Position: #{edit_item.position + 1}",
            size=11, color=TEXT_MUTED, italic=True,
        )

        def close(e=None):
            page.pop_dialog()

        def save(e=None):
            title = title_field.value.strip()
            if not title:
                return

            if is_editing:
                edit_item.title = title
                edit_item.description = desc_field.value.strip()
                edit_item.tags = list(selected_tags)
                edit_item.linked_goal_id = goal_dropdown.value or None
                page.pop_dialog()
                page.run_task(do_save_existing, edit_item)
            else:
                new_item = TaskItem(
                    title=title,
                    description=desc_field.value.strip(),
                    tags=list(selected_tags),
                    linked_goal_id=goal_dropdown.value or None,
                    position=insert_position,
                    created_at=utc_now(),
                )
                page.pop_dialog()
                page.run_task(do_save_new, new_item)

        dlg = ft.AlertDialog(
            title=ft.Text(
                "Edit Task" if is_editing else "Add to Task List",
                size=18, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY,
            ),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        title_field,
                        desc_field,
                        ft.Container(height=4),
                        ft.Text("Tags", size=12, color=TEXT_SECONDARY),
                        tag_chips_container,
                        ft.Container(height=4),
                        goal_dropdown,
                        ft.Container(height=4),
                        pos_text,
                    ],
                    spacing=8,
                    tight=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=400,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close,
                              style=ft.ButtonStyle(color=TEXT_SECONDARY)),
                ft.FilledButton(
                    "Save" if is_editing else "Add ✓",
                    bgcolor=TEAL, color=BG, on_click=save,
                ),
            ],
        )
        page.show_dialog(dlg)

    async def do_save_new(item):
        await save_task_item(page, item)
        await refresh_list()

    async def do_save_existing(item):
        await save_task_item(page, item)
        await refresh_list()

    # ── header ──

    header = ft.Row(
        controls=[
            ft.Column(
                controls=[
                    ft.Text("Priority Tasks", size=28, weight=ft.FontWeight.BOLD,
                            color=TEXT_PRIMARY),
                    ft.Text("Pull your next task when you need to refocus",
                            size=13, color=TEXT_SECONDARY),
                ],
                spacing=2,
            ),
            ft.Container(expand=True),
            ft.FloatingActionButton(
                icon=ft.Icons.ADD_ROUNDED,
                bgcolor=TEAL, foreground_color=BG,
                mini=True,
                on_click=lambda e: show_add_dialog(),
            ),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ── DMN context note ──

    dmn_note = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, size=14, color=TEXT_MUTED),
                ft.Text(
                    "Designed to tackle a faulty DMN or low-quality environmental input. "
                    "For focused goals and nested tasks, use the Planner tab.",
                    size=11, color=TEXT_MUTED, italic=True, expand=True,
                ),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
        bgcolor=SURFACE,
        border_radius=8,
        padding=ft.Padding.symmetric(horizontal=12, vertical=8),
    )

    # ── stats bar ──

    stats_container = ft.Container()

    async def update_stats():
        total = len(state["items"])
        stats_container.content = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.FORMAT_LIST_NUMBERED_ROUNDED, color=TEAL, size=16),
                            ft.Text(f"{total} task{'s' if total != 1 else ''}", size=13,
                                    color=TEXT_SECONDARY),
                        ],
                        spacing=4,
                    ),
                ),
            ],
            spacing=16,
        )

    # ── initial load ──

    async def initial_load():
        await refresh_list()
        await update_stats()

    page.run_task(initial_load)

    # ── layout ──

    return ft.Column(
        controls=[
            header,
            dmn_note,
            ft.Container(content=stats_container, padding=ft.Padding.symmetric(vertical=4)),
            list_column,
        ],
        spacing=12,
        expand=True,
    )
