"""analytics view - planned vs executed dashboard."""

import flet as ft

from services.storage import load_goals
from components.stat_card import StatCard
from components.analytics_charts import (
    build_horizontal_bar_chart,
    build_pie_chart_text,
    build_status_distribution_chart,
    build_completion_by_level_chart,
)
from utils.time_utils import (
    is_past_deadline,
    was_completed_before_deadline,
    was_same_day_execution,
)
from utils.color_utils import get_performance_color, get_on_time_color, get_same_day_color
from utils.math_utils import safe_percentage
from constants.design import (
    TEAL, AMBER, RED, PURPLE, MUTED, CARD_BG, SURFACE,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, CHART_MIN_HEIGHT,
    TITLE_TRUNCATE_CHART, TITLE_TRUNCATE_PROGRESS, TITLE_TRUNCATE_HISTORY,
)


def build_analytics(page: ft.Page):
    """build the analytics view with planned vs executed metrics."""

    # loading state
    stats_row = ft.Row(
        controls=[
            StatCard("Active", "--", ft.Icons.FLAG_ROUNDED, TEAL),
            StatCard("Completed", "--", ft.Icons.CHECK_CIRCLE_ROUNDED, AMBER),
            StatCard("Overdue", "--", ft.Icons.WARNING_ROUNDED, MUTED),
        ],
        spacing=10, wrap=True,
    )

    metrics_cards_row = ft.Row(
        controls=[
            StatCard("Completion Rate", "--", ft.Icons.TRENDING_UP_ROUNDED, TEAL),
            StatCard("On-Time %", "--", ft.Icons.EVENT_NOTE_ROUNDED, TEAL),
            StatCard("Same-Day %", "--", ft.Icons.FLASH_ON_ROUNDED, PURPLE),
        ],
        spacing=10, wrap=True,
    )

    chart_selector = ft.Dropdown(
        width=400,
        options=[
            ft.dropdown.Option("Completion by Level"),
            ft.dropdown.Option("Status Distribution"),
            ft.dropdown.Option("On-Time Analysis"),
            ft.dropdown.Option("Same-Day Execution"),
            ft.dropdown.Option("Recent Goals Progress"),
        ],
        value="Completion by Level",
        bgcolor=CARD_BG, border_color=SURFACE, color=TEXT_PRIMARY,
    )

    chart_container = ft.Container(
        content=ft.Text("Loading chart...", color=TEXT_MUTED),
        padding=20, bgcolor=CARD_BG, border_radius=12,
    )

    planned_vs_executed_section = ft.Container(
        content=ft.Text("Loading...", color=TEXT_MUTED), padding=20,
    )

    progress_chart_section = ft.Container(
        content=ft.Text("Loading...", color=TEXT_MUTED), padding=20,
    )

    completion_history_section = ft.Container()

    async def do_load_analytics():
        try:
            goals = await load_goals(page)

            # basic stats
            total_goals = len(goals)
            completed_goals = sum(1 for g in goals if g.is_completed)
            active_goals = total_goals - completed_goals
            overdue_goals = sum(
                1 for g in goals if not g.is_completed and is_past_deadline(g.deadline)
            )

            stats_row.controls = [
                StatCard("Active", str(active_goals), ft.Icons.FLAG_ROUNDED, TEAL),
                StatCard("Completed", str(completed_goals), ft.Icons.CHECK_CIRCLE_ROUNDED, AMBER),
                StatCard("Overdue", str(overdue_goals), ft.Icons.WARNING_ROUNDED,
                         RED if overdue_goals > 0 else MUTED),
            ]

            # planned vs executed stats
            goal_stats = {"total": 0, "completed": 0, "on_time": 0, "same_day": 0,
                          "custom_deadline_count": 0, "default_deadline_count": 0}
            task_stats = {"total": 0, "completed": 0, "on_time": 0, "same_day": 0,
                          "custom_deadline_count": 0, "default_deadline_count": 0}
            subtask_stats = {"total": 0, "completed": 0, "on_time": 0, "same_day": 0,
                             "custom_deadline_count": 0, "default_deadline_count": 0}

            for goal in goals:
                has_custom = getattr(goal, 'has_custom_deadline', False)

                goal_stats["total"] += 1
                if has_custom:
                    goal_stats["custom_deadline_count"] += 1
                else:
                    goal_stats["default_deadline_count"] += 1

                if goal.is_completed:
                    goal_stats["completed"] += 1
                    if has_custom:
                        if was_completed_before_deadline(goal.completed_at, goal.deadline):
                            goal_stats["on_time"] += 1
                    else:
                        if was_same_day_execution(goal.created_at, goal.completed_at):
                            goal_stats["same_day"] += 1

                for task in goal.tasks:
                    task_stats["total"] += 1
                    if has_custom:
                        task_stats["custom_deadline_count"] += 1
                    else:
                        task_stats["default_deadline_count"] += 1

                    if task.is_completed:
                        task_stats["completed"] += 1
                        if has_custom:
                            if was_completed_before_deadline(task.completed_at, goal.deadline):
                                task_stats["on_time"] += 1
                        else:
                            if was_same_day_execution(task.created_at, task.completed_at):
                                task_stats["same_day"] += 1

                    for subtask in task.sub_tasks:
                        subtask_stats["total"] += 1
                        if has_custom:
                            subtask_stats["custom_deadline_count"] += 1
                        else:
                            subtask_stats["default_deadline_count"] += 1

                        if subtask.is_completed:
                            subtask_stats["completed"] += 1
                            if has_custom:
                                if was_completed_before_deadline(subtask.completed_at, goal.deadline):
                                    subtask_stats["on_time"] += 1
                            else:
                                if was_same_day_execution(subtask.created_at, subtask.completed_at):
                                    subtask_stats["same_day"] += 1

            calc_pct = safe_percentage

            # overall metrics
            overall_completion_pct = calc_pct(goal_stats["completed"], goal_stats["total"])
            overall_on_time_pct = calc_pct(goal_stats["on_time"], goal_stats["custom_deadline_count"])
            overall_same_day_pct = calc_pct(goal_stats["same_day"], goal_stats["default_deadline_count"])

            metrics_cards_row.controls = [
                StatCard(
                    "Completion Rate", f"{overall_completion_pct}%",
                    ft.Icons.TRENDING_UP_ROUNDED,
                    get_performance_color(overall_completion_pct),
                ),
                StatCard(
                    "On-Time %", f"{overall_on_time_pct}%",
                    ft.Icons.EVENT_NOTE_ROUNDED,
                    get_on_time_color(overall_on_time_pct),
                ) if goal_stats["custom_deadline_count"] > 0 else StatCard(
                    "On-Time %", "--", ft.Icons.EVENT_NOTE_ROUNDED, MUTED,
                ),
                StatCard(
                    "Same-Day %", f"{overall_same_day_pct}%",
                    ft.Icons.FLASH_ON_ROUNDED,
                    get_same_day_color(overall_same_day_pct),
                ) if goal_stats["default_deadline_count"] > 0 else StatCard(
                    "Same-Day %", "--", ft.Icons.FLASH_ON_ROUNDED, MUTED,
                ),
            ]

            # cache sorted goal lists
            recent_goals_sorted = sorted(goals, key=lambda g: g.created_at, reverse=True)[:5]

            # chart rendering
            def render_chart(chart_type):
                if chart_type == "Completion by Level":
                    return build_completion_by_level_chart(goal_stats, task_stats, subtask_stats)
                elif chart_type == "Status Distribution":
                    return build_status_distribution_chart({
                        "active": active_goals, "completed": completed_goals, "overdue": overdue_goals,
                    })
                elif chart_type == "On-Time Analysis":
                    on_time = goal_stats["on_time"]
                    late = goal_stats["completed"] - on_time
                    return build_pie_chart_text([
                        {"label": "On-Time", "value": on_time, "color": TEAL},
                        {"label": "Late", "value": late, "color": RED},
                    ], "Goals On-Time vs Late")
                elif chart_type == "Same-Day Execution":
                    same_day = goal_stats["same_day"]
                    not_same_day = goal_stats["completed"] - same_day
                    return build_pie_chart_text([
                        {"label": "Same-Day", "value": same_day, "color": PURPLE},
                        {"label": "Multi-Day", "value": not_same_day, "color": MUTED},
                    ], "Same-Day vs Multi-Day Completion")
                elif chart_type == "Recent Goals Progress":
                    data = [
                        {
                            "label": g.title[:TITLE_TRUNCATE_CHART] + "..." if len(g.title) > TITLE_TRUNCATE_CHART else g.title,
                            "completed": int(g.completion_percentage()),
                            "total": 100,
                            "color": TEAL if g.is_completed else (
                                RED if is_past_deadline(g.deadline) and not g.is_completed else AMBER
                            ),
                        }
                        for g in recent_goals_sorted
                    ]
                    return build_horizontal_bar_chart(data)
                return ft.Text("Invalid chart type", color=TEXT_MUTED)

            def on_chart_selector_change(e):
                chart_container.content = render_chart(chart_selector.value)
                page.update()

            chart_selector.on_change = on_chart_selector_change
            chart_container.content = render_chart("Completion by Level")

            # detailed breakdown section
            def build_pve_row(label, stats, color):
                """planned vs executed row for one level."""
                completion_pct = calc_pct(stats["completed"], stats["total"])
                on_time_pct = calc_pct(stats["on_time"], stats["custom_deadline_count"])
                same_day_pct = calc_pct(stats["same_day"], stats["default_deadline_count"])

                metrics = [
                    _metric_box("Completion", f"{completion_pct}%",
                                TEAL if completion_pct >= 80 else AMBER if completion_pct >= 50 else MUTED),
                ]

                if on_time_pct > 0 and stats["custom_deadline_count"] > 0:
                    metrics.append(_metric_box(
                        f"On-Time ({stats['custom_deadline_count']})",
                        f"{on_time_pct}%",
                        TEAL if on_time_pct >= 80 else AMBER if on_time_pct >= 50 else RED,
                    ))

                if same_day_pct > 0 and stats["default_deadline_count"] > 0:
                    metrics.append(_metric_box(
                        f"Same-Day ({stats['default_deadline_count']})",
                        f"{same_day_pct}%",
                        TEAL if same_day_pct >= 50 else MUTED,
                    ))

                return ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.CIRCLE, color=color, size=12),
                                    ft.Text(label, size=14, weight=ft.FontWeight.W_600, color=TEXT_PRIMARY),
                                    ft.Container(expand=True),
                                    ft.Text(f"{stats['completed']}/{stats['total']}",
                                            size=13, color=TEXT_SECONDARY),
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Container(height=8),
                            ft.Row(controls=metrics, spacing=8),
                        ],
                        spacing=0,
                    ),
                    bgcolor=SURFACE, border_radius=12, padding=12,
                )

            if total_goals > 0:
                planned_vs_executed_section.content = ft.Column(
                    controls=[
                        ft.Text("Detailed Breakdown", size=16,
                                weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ft.Text("On-Time = custom deadline met | Same-Day = completed day created",
                                size=11, color=TEXT_MUTED),
                        ft.Container(height=8),
                        build_pve_row("Goals", goal_stats, TEAL),
                        ft.Container(height=6),
                        build_pve_row("Tasks", task_stats, AMBER),
                        ft.Container(height=6),
                        build_pve_row("Sub-Tasks", subtask_stats, PURPLE),
                    ],
                    spacing=4,
                )
            else:
                planned_vs_executed_section.content = ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Detailed Breakdown", size=16,
                                    weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                            ft.Container(height=20),
                            ft.Text("Add some goals to see analytics", color=TEXT_MUTED),
                        ],
                    ),
                    bgcolor=CARD_BG, border_radius=12, padding=16,
                )

            # recent activity section
            recent_goals = sorted(goals, key=lambda g: g.created_at, reverse=True)[:5]

            progress_items = []
            for g in recent_goals:
                pct = g.completion_percentage()
                is_done = g.is_completed
                is_over = is_past_deadline(g.deadline) and not is_done

                if is_done:
                    color = TEAL
                elif is_over:
                    color = RED
                elif pct >= 50:
                    color = AMBER
                else:
                    color = MUTED

                progress_items.append(
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text(
                                            g.title[:20] + "..." if len(g.title) > 20 else g.title,
                                            size=13, color=TEXT_PRIMARY, expand=True,
                                        ),
                                        ft.Text(f"{pct}%", size=12, color=color,
                                                weight=ft.FontWeight.W_500),
                                    ],
                                ),
                                ft.ProgressBar(value=pct / 100, color=color, bgcolor=SURFACE),
                            ],
                            spacing=4,
                        ),
                        padding=ft.Padding.symmetric(vertical=4),
                    )
                )

            if progress_items:
                def legend_dot(color, label):
                    return ft.Row(
                        controls=[
                            ft.Container(width=8, height=8, bgcolor=color, border_radius=4),
                            ft.Text(label, size=10, color=TEXT_SECONDARY),
                        ],
                        spacing=4,
                    )

                progress_chart_section.content = ft.Column(
                    controls=[
                        ft.Text("Recent Goals Progress", size=14,
                                weight=ft.FontWeight.W_600, color=TEXT_SECONDARY),
                        ft.Container(height=4),
                        *progress_items,
                        ft.Container(height=8),
                        ft.Row(
                            controls=[
                                legend_dot(TEAL, "Done"),
                                legend_dot(AMBER, "In Progress"),
                                legend_dot(RED, "Overdue"),
                            ],
                            spacing=12,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ],
                    spacing=4,
                )
            else:
                progress_chart_section.content = ft.Column(
                    controls=[
                        ft.Text("Recent Goals Progress", size=14,
                                weight=ft.FontWeight.W_600, color=TEXT_SECONDARY),
                        ft.Container(height=20),
                        ft.Text("No goals yet", color=TEXT_MUTED),
                    ],
                )

            progress_chart_section.bgcolor = CARD_BG
            progress_chart_section.border_radius = 12
            progress_chart_section.padding = 12
            progress_chart_section.border = ft.Border.all(1, SURFACE)

            # completion history summary
            completed_list = [g for g in goals if g.is_completed]
            completed_list.sort(key=lambda g: g.completed_at or g.created_at, reverse=True)
            recent_completed = completed_list[:5]

            history_items = []
            for g in recent_completed:
                badges = []
                has_custom = getattr(g, 'has_custom_deadline', False)
                if has_custom:
                    on_time = was_completed_before_deadline(g.completed_at, g.deadline)
                    badges.append(_badge("On-Time", TEAL) if on_time else _badge("Late", RED))
                else:
                    same_day = was_same_day_execution(g.created_at, g.completed_at)
                    if same_day:
                        badges.append(_badge("Same-Day", PURPLE))

                history_items.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, color=TEAL, size=16),
                                ft.Text(
                                    g.title[:25] + "..." if len(g.title) > 25 else g.title,
                                    size=13, color=TEXT_PRIMARY, expand=True,
                                ),
                                *badges,
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=6,
                        ),
                        padding=ft.Padding.symmetric(vertical=6),
                    )
                )

            if history_items:
                completion_history_section.content = ft.Column(
                    controls=[
                        ft.Text("Recent Completions", size=14,
                                weight=ft.FontWeight.W_600, color=TEXT_SECONDARY),
                        ft.Container(height=4),
                        *history_items,
                    ],
                    spacing=0,
                )
                completion_history_section.bgcolor = CARD_BG
                completion_history_section.border_radius = 12
                completion_history_section.padding = 12
                completion_history_section.border = ft.Border.all(1, SURFACE)

            page.update()

        except Exception as e:
            planned_vs_executed_section.content = ft.Text(f"Error: {str(e)}", color=RED)
            page.update()

    page.run_task(do_load_analytics)

    return ft.Column(
        controls=[
            ft.Text("Analytics", size=28, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            ft.Text("Planned vs Executed - All Time", size=13, color=TEXT_SECONDARY),
            ft.Container(height=8),
            stats_row,
            ft.Container(height=12),
            ft.Text("Overall Performance", size=16, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            ft.Container(height=4),
            metrics_cards_row,
            ft.Container(height=16),
            ft.Text("Analytics Charts", size=16, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            ft.Container(height=8),
            ft.Row(
                controls=[ft.Text("View:", size=12, color=TEXT_SECONDARY), chart_selector],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Container(height=8),
            chart_container,
            ft.Container(height=16),
            planned_vs_executed_section,
            ft.Container(height=12),
            progress_chart_section,
            ft.Container(height=12),
            completion_history_section,
        ],
        spacing=4,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


def _metric_box(label, value, color):
    """small metric display box."""
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(value, size=18, weight=ft.FontWeight.BOLD, color=color),
                ft.Text(label, size=10, color=TEXT_MUTED),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        expand=True,
        alignment=ft.Alignment(0, 0),
        padding=8,
        bgcolor=CARD_BG,
        border_radius=8,
    )


def _badge(text, color):
    """small status badge."""
    return ft.Container(
        content=ft.Text(text, size=9, color=color, weight=ft.FontWeight.W_500),
        bgcolor=f"{color}20",
        border_radius=4,
        padding=ft.Padding.symmetric(horizontal=6, vertical=2),
    )
