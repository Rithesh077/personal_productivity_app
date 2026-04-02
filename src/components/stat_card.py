"""Stat card component for Stride."""

import flet as ft

CARD_BG = "#141927"


def StatCard(label: str, value: str, icon, color: str):
    """Create a metric card with icon, value, and label."""
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(icon, color=color, size=22),
                ft.Text(
                    value,
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=color,
                ),
                ft.Text(
                    label,
                    size=11,
                    color="#8A92A6",
                    weight=ft.FontWeight.W_500,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        ),
        bgcolor=CARD_BG,
        border_radius=16,
        padding=ft.Padding.symmetric(horizontal=12, vertical=16),
        expand=True,
        border=ft.Border.all(1, "#1E2436"),
    )
