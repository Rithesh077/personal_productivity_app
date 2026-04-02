"""Stride — Plan. Execute. Improve."""

import flet as ft

from views.planner import build_planner
from views.analytics import build_analytics

# Design tokens
NAVY = "#0B0F1A"
TEAL = "#00D9A6"
SURFACE = "#141927"


def main(page: ft.Page):
    page.title = "Stride"
    page.bgcolor = NAVY
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=TEAL,
            on_primary=NAVY,
            surface=NAVY,
            on_surface="#E0E0E0",
        ),
    )

    # Build the planner (persists across navigation)
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
            # Rebuild analytics each time for fresh data
            content.content = build_analytics(page)
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
