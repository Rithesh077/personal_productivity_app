"""Analytics view for Stride — goal completion dashboard."""

import flet as ft

from services.storage import load_goals
from components.stat_card import StatCard
from utils.time_utils import is_past_deadline

# Design tokens
TEAL = "#00D9A6"
AMBER = "#FFB547"
RED = "#FF5C5C"
MUTED = "#3A4157"
CARD_BG = "#141927"
TEXT_PRIMARY = "#E0E0E0"
TEXT_SECONDARY = "#8A92A6"


def build_analytics(page: ft.Page):
    """Build the analytics view. Returns a Column control."""

    # Placeholders that will be populated async
    chart_section = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Goal Progress", size=14, weight=ft.FontWeight.W_600,
                        color=TEXT_SECONDARY),
                ft.Container(height=4),
                ft.Container(
                    content=ft.ProgressRing(color=TEAL),
                    alignment=ft.Alignment(0, 0),
                    height=220,
                ),
            ],
        ),
        bgcolor=CARD_BG,
        border_radius=16,
        padding=ft.Padding.only(top=16, right=12, bottom=8, left=8),
        border=ft.Border.all(1, "#1E2436"),
    )

    legend = ft.Row(
        controls=[],
        spacing=16,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    stats_row = ft.Row(
        controls=[
            StatCard("Active", "—", ft.Icons.FLAG_ROUNDED, TEAL),
            StatCard("Completed", "—", ft.Icons.CHECK_CIRCLE_ROUNDED, AMBER),
            StatCard("Overdue", "—", ft.Icons.WARNING_ROUNDED, RED),
        ],
        spacing=10,
    )

    async def do_load_analytics():
        goals = await load_goals(page)

        # Calculate stats
        total = len(goals)
        completed = sum(1 for g in goals if g.is_completed)
        active = total - completed
        overdue = sum(1 for g in goals if not g.is_completed and is_past_deadline(g.deadline))

        # Build progress bars for recent goals
        recent_goals = sorted(goals, key=lambda g: g.created_at, reverse=True)[:7]

        bar_groups = []
        for i, g in enumerate(recent_goals):
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

            bar_groups.append(
                ft.BarChartGroup(
                    x=i,
                    bar_rods=[
                        ft.BarChartRod(
                            from_y=0,
                            to_y=pct if pct > 0 else 3,
                            width=28,
                            color=color,
                            border_radius=6,
                            tooltip=f"{g.title[:20]}...: {pct}%" if len(g.title) > 20
                            else f"{g.title}: {pct}%",
                        ),
                    ],
                )
            )

        bottom_labels = [
            ft.ChartAxisLabel(
                value=i,
                label=ft.Container(
                    content=ft.Text(
                        g.title[:8] + "..." if len(g.title) > 8 else g.title,
                        size=10,
                        color=TEXT_SECONDARY,
                    ),
                    padding=ft.Padding.only(top=4),
                ),
            )
            for i, g in enumerate(recent_goals)
        ]

        left_labels = [
            ft.ChartAxisLabel(value=v, label=ft.Text(
                f"{v}%", size=10, color="#3A4157"))
            for v in [0, 50, 100]
        ]

        if recent_goals:
            chart = ft.BarChart(
                bar_groups=bar_groups,
                bottom_axis=ft.ChartAxis(labels=bottom_labels, labels_size=40),
                left_axis=ft.ChartAxis(labels=left_labels, labels_size=40),
                max_y=105,
                bgcolor="transparent",
                border=ft.Border.all(0, "transparent"),
                horizontal_grid_lines=ft.ChartGridLines(
                    color="#1E2436", width=1, interval=25),
                animate=ft.Animation(600, ft.AnimationCurve.EASE_IN_OUT),
                height=220,
                expand=True,
            )
        else:
            chart = ft.Container(
                content=ft.Text("No goals yet", color=MUTED),
                alignment=ft.Alignment(0, 0),
                height=220,
            )

        chart_section.content = ft.Column(
            controls=[
                ft.Text("Recent Goals Progress", size=14, weight=ft.FontWeight.W_600,
                        color=TEXT_SECONDARY),
                ft.Container(height=4),
                chart,
            ],
        )

        # Legend
        def legend_dot(color, label):
            return ft.Row(
                controls=[
                    ft.Container(width=10, height=10,
                                 bgcolor=color, border_radius=5),
                    ft.Text(label, size=11, color=TEXT_SECONDARY),
                ],
                spacing=6,
            )

        legend.controls = [
            legend_dot(TEAL, "Done"),
            legend_dot(AMBER, "In Progress"),
            legend_dot(RED, "Overdue"),
            legend_dot(MUTED, "Just Started"),
        ]

        # Stat cards
        stats_row.controls = [
            StatCard("Active", str(active), ft.Icons.FLAG_ROUNDED, TEAL),
            StatCard("Done", str(completed), ft.Icons.CHECK_CIRCLE_ROUNDED, AMBER),
            StatCard(
                "Overdue", str(overdue),
                ft.Icons.WARNING_ROUNDED,
                RED if overdue > 0 else MUTED,
            ),
        ]

        page.update()

    # Kick off async load
    page.run_task(do_load_analytics)

    return ft.Column(
        controls=[
            ft.Text("Analytics", size=28,
                    weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            ft.Text("Your goal progress at a glance",
                    size=13, color=TEXT_SECONDARY),
            ft.Container(height=4),
            chart_section,
            ft.Container(height=4),
            legend,
            ft.Container(height=4),
            stats_row,
        ],
        spacing=8,
        expand=True,
    )
