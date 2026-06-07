"""task list analytics view — completion history and stats."""

import flet as ft

from services.storage import (
    load_completed_task_items, load_task_list,
    clear_completed_task_items, load_goals,
)
from components.stat_card import StatCard
from constants.design import (
    TEAL, AMBER, RED, PURPLE, MUTED, GREEN, CARD_BG, SURFACE, BG,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    TAG_COLORS,
)
from utils.time_utils import relative_time, utc_to_local
from utils.math_utils import safe_percentage


def build_task_list_analytics(page: ft.Page):
    """analytics for the priority tasks list — completed items history."""

    stats_row = ft.Row(
        controls=[
            StatCard("Active", "--", ft.Icons.FORMAT_LIST_NUMBERED_ROUNDED, TEAL),
            StatCard("Completed", "--", ft.Icons.CHECK_CIRCLE_ROUNDED, AMBER),
        ],
        spacing=10, wrap=True,
    )

    avg_time_card = ft.Container()
    tag_breakdown_section = ft.Container()
    history_section = ft.Container()
    show_all_state = {"showing_all": False}

    async def do_load_analytics():
        try:
            active_items = await load_task_list(page)
            completed_items = await load_completed_task_items(page)
            goals = await load_goals(page)

            # goal lookup for linked items
            goal_map = {g.id: g.title for g in goals}

            active_count = len(active_items)
            completed_count = len(completed_items)

            stats_row.controls = [
                StatCard("Active", str(active_count),
                         ft.Icons.FORMAT_LIST_NUMBERED_ROUNDED, TEAL),
                StatCard("Completed", str(completed_count),
                         ft.Icons.CHECK_CIRCLE_ROUNDED, AMBER),
            ]

            # average time in list
            if completed_items:
                total_seconds = 0
                valid_count = 0
                for item in completed_items:
                    if item.created_at and item.completed_at:
                        try:
                            created = utc_to_local(item.created_at)
                            completed = utc_to_local(item.completed_at)
                            if created and completed:
                                diff = completed - created
                                total_seconds += diff.total_seconds()
                                valid_count += 1
                        except Exception:
                            pass

                if valid_count > 0:
                    avg_seconds = total_seconds / valid_count
                    avg_text = _format_duration(avg_seconds)
                    avg_time_card.content = ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text("Average Time in List", size=12,
                                        color=TEXT_SECONDARY, weight=ft.FontWeight.W_500),
                                ft.Text(avg_text, size=22, color=TEAL,
                                        weight=ft.FontWeight.BOLD),
                                ft.Text(f"across {valid_count} completed items",
                                        size=11, color=TEXT_MUTED),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=4,
                        ),
                        bgcolor=CARD_BG, border_radius=12, padding=16,
                        border=ft.Border.all(1, SURFACE),
                        alignment=ft.Alignment(0, 0),
                    )

            # tag breakdown
            tag_counts = {}
            for item in completed_items:
                for tag in item.tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

            if tag_counts:
                sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
                tag_items = []
                for tag, count in sorted_tags:
                    color = TAG_COLORS.get(tag, MUTED)
                    tag_items.append(
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Container(
                                        content=ft.Text(tag, size=11, color=color,
                                                        weight=ft.FontWeight.W_600),
                                        bgcolor=f"{color}18",
                                        border_radius=4,
                                        padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                    ),
                                    ft.Container(expand=True),
                                    ft.Text(f"{count}", size=14, color=color,
                                            weight=ft.FontWeight.BOLD),
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            padding=ft.Padding.symmetric(vertical=4),
                        )
                    )

                tag_breakdown_section.content = ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Completed by Tag", size=14,
                                    weight=ft.FontWeight.W_600, color=TEXT_SECONDARY),
                            ft.Container(height=4),
                            *tag_items,
                        ],
                        spacing=0,
                    ),
                    bgcolor=CARD_BG, border_radius=12, padding=12,
                    border=ft.Border.all(1, SURFACE),
                )

            # completed items history
            display_items = completed_items if show_all_state["showing_all"] else completed_items[:5]
            has_more = len(completed_items) > 5 and not show_all_state["showing_all"]

            if display_items:
                history_items = []
                for item in display_items:
                    # time in list
                    time_in_list = ""
                    if item.created_at and item.completed_at:
                        try:
                            created = utc_to_local(item.created_at)
                            completed = utc_to_local(item.completed_at)
                            if created and completed:
                                diff = completed - created
                                time_in_list = _format_duration(diff.total_seconds())
                        except Exception:
                            pass

                    # tag chips
                    tag_chips = []
                    for tag in item.tags:
                        color = TAG_COLORS.get(tag, MUTED)
                        tag_chips.append(
                            ft.Container(
                                content=ft.Text(tag, size=9, color=color),
                                bgcolor=f"{color}15",
                                border_radius=3,
                                padding=ft.Padding.symmetric(horizontal=5, vertical=1),
                            )
                        )

                    # goal link
                    goal_text = ft.Container()
                    if item.linked_goal_id and item.linked_goal_id in goal_map:
                        goal_name = goal_map[item.linked_goal_id]
                        goal_text = ft.Text(
                            f"→ {goal_name}" if len(goal_name) <= 20 else f"→ {goal_name[:20]}...",
                            size=10, color=TEXT_MUTED, italic=True,
                        )

                    # metadata row
                    meta_parts = []
                    if item.completed_at:
                        meta_parts.append(
                            ft.Text(f"completed {relative_time(item.completed_at)}",
                                    size=10, color=TEXT_MUTED)
                        )
                    if time_in_list:
                        meta_parts.append(ft.Text("·", size=10, color=TEXT_MUTED))
                        meta_parts.append(
                            ft.Text(f"in list for {time_in_list}",
                                    size=10, color=TEXT_MUTED)
                        )

                    history_items.append(
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED,
                                                    color=TEAL, size=16),
                                            ft.Text(
                                                item.title if len(item.title) <= 30
                                                else item.title[:30] + "...",
                                                size=13, color=TEXT_PRIMARY, expand=True,
                                            ),
                                        ],
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=8,
                                    ),
                                    ft.Row(controls=tag_chips, spacing=4) if tag_chips else ft.Container(),
                                    ft.Row(controls=meta_parts, spacing=4) if meta_parts else ft.Container(),
                                    goal_text,
                                ],
                                spacing=2,
                            ),
                            padding=ft.Padding.symmetric(vertical=6, horizontal=4),
                        )
                    )

                # show more button
                if has_more:
                    history_items.append(
                        ft.Container(
                            content=ft.TextButton(
                                f"Show all ({len(completed_items)} items)",
                                on_click=lambda e: _show_all(),
                                style=ft.ButtonStyle(color=TEAL),
                            ),
                            alignment=ft.Alignment(0, 0),
                            padding=ft.Padding.only(top=8),
                        )
                    )

                history_section.content = ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Completed Items", size=14,
                                    weight=ft.FontWeight.W_600, color=TEXT_SECONDARY),
                            ft.Container(height=4),
                            *history_items,
                        ],
                        spacing=0,
                    ),
                    bgcolor=CARD_BG, border_radius=12, padding=12,
                    border=ft.Border.all(1, SURFACE),
                )
            else:
                history_section.content = ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Completed Items", size=14,
                                    weight=ft.FontWeight.W_600, color=TEXT_SECONDARY),
                            ft.Container(height=20),
                            ft.Text("No completed items yet", color=TEXT_MUTED),
                        ],
                    ),
                    bgcolor=CARD_BG, border_radius=12, padding=16,
                    border=ft.Border.all(1, SURFACE),
                )

            page.update()

        except Exception as e:
            history_section.content = ft.Text(f"Error: {str(e)}", color=RED)
            page.update()

    def _show_all():
        show_all_state["showing_all"] = True
        page.run_task(do_load_analytics)

    def _handle_clear(e):
        """confirm then clear completed items."""
        def close(e=None):
            page.pop_dialog()

        def confirm(e=None):
            page.pop_dialog()
            page.run_task(do_clear)

        dlg = ft.AlertDialog(
            title=ft.Text("Clear completed items?", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Text(
                "This will permanently remove all completed items from history.",
                size=13, color=TEXT_SECONDARY,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close),
                ft.FilledButton("Clear All", bgcolor=RED, color="white", on_click=confirm),
            ],
        )
        page.show_dialog(dlg)

    async def do_clear():
        await clear_completed_task_items(page)
        show_all_state["showing_all"] = False
        await do_load_analytics()

    # initial load
    page.run_task(do_load_analytics)

    return ft.Column(
        controls=[
            ft.Text("Analytics", size=28, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            ft.Text("Priority Tasks List — Completion History", size=13, color=TEXT_SECONDARY),
            ft.Container(height=8),
            stats_row,
            ft.Container(height=12),
            avg_time_card,
            ft.Container(height=12),
            tag_breakdown_section,
            ft.Container(height=12),
            history_section,
            ft.Container(height=12),
            ft.Container(
                content=ft.TextButton(
                    "Clear completed items",
                    icon=ft.Icons.DELETE_SWEEP_ROUNDED,
                    on_click=_handle_clear,
                    style=ft.ButtonStyle(color=TEXT_MUTED),
                ),
                alignment=ft.Alignment(0, 0),
            ),
        ],
        spacing=4,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


def _format_duration(seconds: float) -> str:
    """format seconds into a human-readable duration."""
    if seconds < 60:
        return "< 1 min"
    minutes = int(seconds // 60)
    if minutes < 60:
        return f"{minutes} min{'s' if minutes != 1 else ''}"
    hours = int(minutes // 60)
    if hours < 24:
        remaining_mins = minutes % 60
        if remaining_mins > 0:
            return f"{hours}h {remaining_mins}m"
        return f"{hours} hour{'s' if hours != 1 else ''}"
    days = int(hours // 24)
    remaining_hours = hours % 24
    if remaining_hours > 0:
        return f"{days}d {remaining_hours}h"
    return f"{days} day{'s' if days != 1 else ''}"
