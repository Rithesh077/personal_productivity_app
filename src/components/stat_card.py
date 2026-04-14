"""stat card component."""

import flet as ft
from constants.design import CARD_BG, TEXT_SECONDARY, SURFACE


def StatCard(label: str, value: str, icon, color: str):
    """metric card with icon, value, and label."""
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
                    color=TEXT_SECONDARY,
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
        border=ft.Border.all(1, SURFACE),
    )
