"""stride - plan. execute. improve."""

import flet as ft

from views.planner import build_planner
from views.task_list import build_task_list
from views.task_list_analytics import build_task_list_analytics
from constants.design import BG, TEAL, SURFACE


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

    # build views lazily to avoid loading all at startup
    views = {"planner": None, "task_list": None, "analytics": None}

    def get_view(name):
        if views[name] is None:
            if name == "planner":
                views[name] = build_planner(page)
            elif name == "task_list":
                views[name] = build_task_list(page)
            elif name == "analytics":
                views[name] = build_task_list_analytics(page)
        return views[name]

    content = ft.Container(
        content=get_view("planner"),
        expand=True,
        padding=ft.Padding.only(top=12, left=16, right=16, bottom=0),
    )

    def on_nav_change(e):
        idx = e.control.selected_index
        if idx == 0:
            content.content = get_view("planner")
        elif idx == 1:
            # rebuild task list each time to get fresh data
            views["task_list"] = build_task_list(page)
            content.content = views["task_list"]
        else:
            # rebuild analytics each time to get fresh data
            views["analytics"] = build_task_list_analytics(page)
            content.content = views["analytics"]
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
                icon=ft.Icons.FORMAT_LIST_NUMBERED_ROUNDED,
                selected_icon=ft.Icons.FORMAT_LIST_NUMBERED_ROUNDED,
                label="Tasks",
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
