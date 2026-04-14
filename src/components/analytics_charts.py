"""analytics chart components."""

import flet as ft

from constants.design import (
    TEAL, AMBER, PURPLE, CARD_BG, SURFACE,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    BAR_HEIGHT_SMALL, BAR_HEIGHT_LARGE, LABEL_WIDTH, PERCENTAGE_WIDTH, COLOR_BOX_SIZE,
)
from utils.math_utils import safe_percentage


def _build_legend_item(label: str, value: int, color: str, pct: int) -> ft.Container:
    """single legend item with label, value, and percentage."""
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    width=COLOR_BOX_SIZE,
                    height=COLOR_BOX_SIZE,
                    bgcolor=color,
                    border_radius=2,
                ),
                ft.Text(
                    f"{label}",
                    size=12,
                    color=TEXT_PRIMARY,
                    width=120,
                ),
                ft.Container(expand=True),
                ft.Text(
                    f"{value}",
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color=color,
                    width=40,
                ),
                ft.Text(
                    f"{pct}%",
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color=color,
                    width=50,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.symmetric(horizontal=0, vertical=8),
    )


def _build_stacked_bar_segment(value: int, total: int, color: str, min_height: int = 24) -> ft.Container:
    """single segment for a stacked bar chart."""
    pct = (value / total * 100) if total > 0 else 0
    expand_amount = int(pct) if pct >= 1 else 0
    return ft.Container(
        expand=expand_amount,
        height=min_height,
        bgcolor=color,
    )


def build_horizontal_bar_chart(data: list[dict]):
    """horizontal bar chart showing completion rates by level.

    data: [{"label": str, "completed": int, "total": int, "color": str}]
    """
    items = []
    for item in data:
        label = item["label"]
        completed = item["completed"]
        total = item["total"]
        color = item["color"]
        pct = safe_percentage(completed, total)

        bar = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(label, size=13, weight=ft.FontWeight.W_600,
                                    color=TEXT_PRIMARY, width=LABEL_WIDTH),
                            ft.Container(expand=True),
                            ft.Text(f"{completed}/{total}", size=12, color=TEXT_SECONDARY),
                            ft.Text(f"{pct}%", size=13, weight=ft.FontWeight.BOLD,
                                    color=color, width=PERCENTAGE_WIDTH),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(height=6),
                    ft.ProgressBar(value=pct / 100, color=color, bgcolor=SURFACE, height=8),
                ],
                spacing=0,
            ),
            padding=12,
            bgcolor=CARD_BG,
            border_radius=12,
        )
        items.append(bar)

    return ft.Column(controls=items, spacing=8)


def build_pie_chart_text(data: list[dict], title: str = ""):
    """text-based pie chart with stacked bar and legend.

    data: [{"label": str, "value": int, "color": str}]
    """
    total = sum(item["value"] for item in data)
    if total == 0:
        return ft.Column(controls=[ft.Text("No data", color=TEXT_MUTED, size=12)])

    data_with_pct = [
        {**item, "pct": safe_percentage(item["value"], total)}
        for item in data
    ]

    legend_items = [
        _build_legend_item(item["label"], item["value"], item["color"], item["pct"])
        for item in data_with_pct
    ]

    segments = [
        _build_stacked_bar_segment(item["value"], total, item["color"], BAR_HEIGHT_SMALL)
        for item in data_with_pct
    ]

    stacked_bar = ft.Row(controls=segments, spacing=0, height=BAR_HEIGHT_SMALL)

    controls = []
    if title:
        controls.append(ft.Text(title, size=14, weight=ft.FontWeight.W_600, color=TEXT_SECONDARY))
        controls.append(ft.Container(height=8))

    controls.extend([
        stacked_bar,
        ft.Container(height=12),
        ft.Column(controls=legend_items, spacing=0),
    ])

    return ft.Column(controls=controls, spacing=0)


def build_status_distribution_chart(stats: dict):
    """status distribution: active / completed / overdue.

    stats: {"active": int, "completed": int, "overdue": int}
    """
    from constants.design import RED

    active = stats.get("active", 0)
    completed = stats.get("completed", 0)
    overdue = stats.get("overdue", 0)
    total = active + completed + overdue

    if total == 0:
        return ft.Column(controls=[ft.Text("No goals", color=TEXT_MUTED, size=12)])

    segment_configs = [
        ("completed", completed, TEAL),
        ("active", active, AMBER),
        ("overdue", overdue, RED),
    ]

    segments = [
        _build_stacked_bar_segment(count, total, color, BAR_HEIGHT_LARGE)
        for label, count, color in segment_configs
        if count > 0
    ]

    stacked_bar = ft.Row(controls=segments, spacing=2, height=BAR_HEIGHT_LARGE)

    legend_items = []
    for label, count, color in segment_configs:
        if count > 0:
            pct = safe_percentage(count, total)
            legend_items.append(_build_legend_item(label.capitalize(), count, color, pct))

    return ft.Column(
        controls=[stacked_bar, ft.Container(height=12), *legend_items],
        spacing=0,
    )


def build_completion_by_level_chart(goal_stats: dict, task_stats: dict, subtask_stats: dict):
    """completion rates across goal/task/subtask levels."""
    data = [
        {"label": "Goals", "completed": goal_stats.get("completed", 0),
         "total": goal_stats.get("total", 0), "color": TEAL},
        {"label": "Tasks", "completed": task_stats.get("completed", 0),
         "total": task_stats.get("total", 0), "color": AMBER},
        {"label": "Sub-Tasks", "completed": subtask_stats.get("completed", 0),
         "total": subtask_stats.get("total", 0), "color": PURPLE},
    ]
    return build_horizontal_bar_chart(data)
