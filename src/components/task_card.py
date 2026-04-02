"""Task card component for Stride."""

import flet as ft

TEAL = "#00D9A6"
CARD_BG = "#141927"
TEXT_PRIMARY = "#E0E0E0"


def TaskCard(task: dict, on_toggle, on_delete):
    """Create a task card with checkbox, title, and delete button."""
    is_done = task.get("is_executed", False)

    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Checkbox(
                    value=is_done,
                    active_color=TEAL,
                    check_color="#0B0F1A",
                    on_change=lambda e: on_toggle(task["id"], e.control.value),
                ),
                ft.Text(
                    task["title"],
                    size=16,
                    color=TEAL if is_done else TEXT_PRIMARY,
                    weight=ft.FontWeight.W_500,
                    decoration=ft.TextDecoration.LINE_THROUGH if is_done else None,
                    expand=True,
                ),
                ft.IconButton(
                    icon=ft.Icons.CLOSE_ROUNDED,
                    icon_color="#5A6478",
                    icon_size=18,
                    on_click=lambda e: on_delete(task["id"]),
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=CARD_BG,
        border_radius=12,
        padding=ft.Padding.symmetric(horizontal=12, vertical=4),
        border=ft.Border.all(1, TEAL if is_done else "#1E2436"),
        animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        margin=ft.Margin.only(bottom=6),
    )
