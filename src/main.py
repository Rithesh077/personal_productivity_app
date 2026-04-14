"""stride - plan. execute. improve."""

import flet as ft

from views.planner import build_planner
from constants.design import BG, TEAL, SURFACE, TEXT_PRIMARY, TEXT_MUTED, CARD_BG


def _build_coming_soon():
    """placeholder for analytics tab."""
    return ft.Column(
        controls=[
            ft.Container(expand=True),
            ft.Column(
                controls=[
                    ft.Icon(ft.Icons.INSIGHTS_ROUNDED, color=TEXT_MUTED, size=64),
                    ft.Container(height=16),
                    ft.Text("Analytics", size=24, weight=ft.FontWeight.BOLD,
                            color=TEXT_PRIMARY, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=8),
                    ft.Text("Coming soon", size=16, color=TEXT_MUTED,
                            text_align=ft.TextAlign.CENTER),
                    ft.Text("Track your follow-through rate, on-time %, and more.",
                            size=13, color=TEXT_MUTED, text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            ft.Container(expand=True),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )


def main(page: ft.Page):
    page.title = "Stride"
    page.bgcolor = BG
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=TEAL,
            on_primary=BG,
            surface=BG,
            on_surface="#E0E0E0",
        ),
    )

    planner = build_planner(page)

    content = ft.Container(
        content=planner,
        expand=True,
        padding=ft.Padding.only(top=12, left=16, right=16, bottom=0),
    )

    def on_nav_change(e):
        idx = e.control.selected_index
        if idx == 0:
            content.content = planner
        else:
            content.content = _build_coming_soon()
        page.update()

    page.navigation_bar = ft.NavigationBar(
        bgcolor=SURFACE,
        indicator_color=TEAL,
        selected_index=0,
        on_change=on_nav_change,
        height=65,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.CHECKLIST_ROUNDED,
                selected_icon=ft.Icons.CHECKLIST_ROUNDED,
                label="Planner",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.INSIGHTS_ROUNDED,
                selected_icon=ft.Icons.INSIGHTS_ROUNDED,
                label="Analytics",
            ),
        ],
    )

    page.add(
        ft.SafeArea(
            expand=True,
            content=content,
        )
    )


ft.run(main)
