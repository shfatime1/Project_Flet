"""
sidebar.py – Shared shell for all authenticated pages.
Changes:
  - header shows real role badge from page.data["role"]
  - sidebar hides Manage Users/Datasets/Models for non-Admin roles
    (UML: only Admin can manage users, datasets, models)
  - Viewer sees only: Dashboard, Experiments, Metrics, Reports
  - Data Scientist sees: + Compare Experiments (no manage pages)
  - Admin sees everything
"""

import flet as ft

from views.theme import palette, is_dark, toggle_dark


def _show_snack(page: ft.Page, msg: str, color: str = "#22C55E") -> None:
    snack = ft.SnackBar(
        content=ft.Text(msg, color="#FFFFFF", size=13),
        bgcolor=color,
        duration=2200,
        behavior=ft.SnackBarBehavior.FLOATING,
        shape=ft.RoundedRectangleBorder(radius=10),
        margin=ft.Margin(left=24, right=24, bottom=24, top=0),
        open=True,
    )
    page.overlay.append(snack)
    page.update()


def _get_role(page: ft.Page) -> str:
    """Return uppercase role: ADMIN | DATA SCIENTIST | VIEWER"""
    if isinstance(page.data, dict):
        return (page.data.get("role") or "DATA SCIENTIST").upper()
    return "DATA SCIENTIST"


def sidebar_component(page: ft.Page, go_to, active: str) -> ft.Container:
    p    = palette(page)
    role = _get_role(page)

    def do_logout(_e=None):
        if isinstance(page.data, dict):
            keep_dark = page.data.get("dark_mode", False)
            page.data.clear()
            page.data["dark_mode"] = keep_dark
        go_to("/")

    def open_settings(_e=None):
        _show_snack(page, "Settings panel opened.", p["GREEN"])

    def nav_item(label, icon, key, route):
        is_active = (active == key)
        return ft.Container(
            border_radius=10,
            bgcolor=p["SIDEBAR_ACTIVE"] if is_active else "transparent",
            padding=ft.Padding(left=12, right=12, top=8, bottom=8),
            on_click=(lambda e, r=route: go_to(r)),
            ink=True,
            content=ft.Row(spacing=9, controls=[
                ft.Icon(icon, size=17,
                        color=p["GREEN_DARK"] if is_active else p["MUTED"]),
                ft.Text(label, size=13, expand=True,
                        color=p["GREEN_DARK"] if is_active else p["TEXT"],
                        weight=ft.FontWeight.W_600 if is_active
                               else ft.FontWeight.W_500),
                ft.Icon(ft.Icons.CHEVRON_RIGHT, size=16,
                        color=p["GREEN_DARK"] if is_active else "transparent"),
            ]),
        )

    # ── All possible nav items ────────────────────────────────────────────
    ALL_NAV = [
        ("Dashboard",          ft.Icons.DASHBOARD,            "dashboard",       "/dashboard",       ["ADMIN", "DATA SCIENTIST", "VIEWER"]),
        ("Experiments",        ft.Icons.TABLE_ROWS_OUTLINED,  "experiments",     "/experiments",     ["ADMIN", "DATA SCIENTIST", "VIEWER"]),
        ("Metrics",            ft.Icons.SHOW_CHART,           "metrics",         "/metrics",         ["ADMIN", "DATA SCIENTIST", "VIEWER"]),
        ("Reports",            ft.Icons.DESCRIPTION_OUTLINED, "reports",         "/reports",         ["ADMIN", "DATA SCIENTIST", "VIEWER"]),
        ("Manage Users",       ft.Icons.PEOPLE_OUTLINE,       "manage-users",    "/manage-users",    ["ADMIN"]),
        ("Manage Datasets",    ft.Icons.STORAGE_OUTLINED,     "manage-datasets", "/manage-datasets", ["ADMIN"]),
        ("Manage Models",      ft.Icons.HUB_OUTLINED,         "manage-models",   "/manage-models",   ["ADMIN"]),
    ]

    # Filter by role
    visible_nav = [
        (lbl, ico, key, route)
        for lbl, ico, key, route, allowed_roles in ALL_NAV
        if role in allowed_roles
    ]

    return ft.Container(
        width=220,
        bgcolor=p["SIDEBAR_BG"],
        border=ft.Border(right=ft.BorderSide(1, p["BORDER"])),
        content=ft.Column(expand=True, spacing=0, controls=[
            # Logo
            ft.Container(
                border=ft.Border(bottom=ft.BorderSide(1, p["BORDER"])),
                padding=ft.Padding(left=16, right=16, top=14, bottom=14),
                content=ft.Row(spacing=10,
                               vertical_alignment=ft.CrossAxisAlignment.CENTER,
                               controls=[
                    ft.Container(width=30, height=30, bgcolor=p["GREEN"], border_radius=8,
                                 alignment=ft.Alignment(0, 0),
                                 content=ft.Icon(ft.Icons.GRAPHIC_EQ, color="#FFFFFF", size=16)),
                    ft.Text("AI Model Training Log", size=12,
                            color=p["GREEN_DARK"], weight=ft.FontWeight.W_700),
                ]),
            ),
            # Nav items (filtered by role)
            ft.Container(
                padding=ft.Padding(left=8, right=8, top=14, bottom=8),
                content=ft.Column(spacing=2, controls=[
                    nav_item(lbl, ico, key, route)
                    for lbl, ico, key, route in visible_nav
                ]),
            ),
            ft.Container(expand=True),
            # Footer
            ft.Container(
                border=ft.Border(top=ft.BorderSide(1, p["BORDER"])),
                padding=ft.Padding(left=12, right=12, top=10, bottom=10),
                content=ft.Column(spacing=2, controls=[
                    ft.Container(
                        padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                        border_radius=8, ink=True, on_click=open_settings,
                        content=ft.Row(spacing=8, controls=[
                            ft.Icon(ft.Icons.SETTINGS_OUTLINED, size=16, color=p["MUTED"]),
                            ft.Text("Settings", size=13, color=p["MUTED"]),
                        ]),
                    ),
                    ft.Container(
                        padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                        border_radius=8, on_click=do_logout, ink=True,
                        content=ft.Row(spacing=8, controls=[
                            ft.Icon(ft.Icons.LOGOUT, size=16, color=p["RED"]),
                            ft.Text("Logout", size=13, color=p["RED"]),
                        ]),
                    ),
                ]),
            ),
        ]),
    )


def header_bar(page: ft.Page, go_to) -> ft.Container:
    p = palette(page)

    # ── Read real user info from page.data ────────────────────────────────
    display_name = "User"
    role_label   = "DATA SCIENTIST"
    if isinstance(page.data, dict):
        display_name = (page.data.get("username")
                        or page.data.get("user_email", "User"))
        role_label   = (page.data.get("role") or "DATA SCIENTIST").upper()

    # ── Role badge colour ─────────────────────────────────────────────────
    ROLE_COLORS = {
        "ADMIN":          ("#FEF3C7", "#92400E"),   # amber
        "DATA SCIENTIST": ("#DBEAFE", "#1D4ED8"),   # blue
        "VIEWER":         ("#F3F4F6", "#374151"),   # grey
    }
    badge_bg, badge_text = ROLE_COLORS.get(role_label, ("#DBEAFE", "#1D4ED8"))

    def change_theme(_e=None):
        toggle_dark(page)
        if not isinstance(page.data, dict):
            page.data = {}
        cur = page.data.get("current_route") or "/dashboard"
        if cur in ("/", "") and page.data.get("is_logged_in"):
            cur = "/dashboard"
        go_to(cur)

    def on_search_change(e):
        if not isinstance(page.data, dict):
            page.data = {}
        page.data["search_query"] = e.control.value or ""
        cb = page.data.get("on_header_search")
        if callable(cb):
            try:
                cb(e.control.value or "")
            except Exception:
                pass

    initial_query = ""
    if isinstance(page.data, dict):
        initial_query = page.data.get("search_query", "") or ""

    search_field = ft.TextField(
        value=initial_query,
        hint_text="Search experiments...",
        height=38, text_size=13,
        border_radius=10, filled=True, bgcolor=p["SEARCH_BG"],
        border_color=p["BORDER"], focused_border_color=p["GREEN"],
        prefix_icon=ft.Icons.SEARCH, color=p["TEXT"],
        hint_style=ft.TextStyle(color=p["MUTED"], size=13),
        content_padding=ft.Padding(left=12, right=12, top=8, bottom=8),
        on_change=on_search_change,
    )

    theme_icon = ft.Icons.LIGHT_MODE if is_dark(page) else ft.Icons.DARK_MODE
    theme_tip  = "Switch to light mode" if is_dark(page) else "Switch to dark mode"

    return ft.Container(
        bgcolor=p["SURFACE"],
        border=ft.Border(bottom=ft.BorderSide(1, p["BORDER"])),
        padding=ft.Padding(left=20, right=20, top=10, bottom=10),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(expand=True,
                             padding=ft.Padding(left=0, right=20, top=0, bottom=0),
                             content=search_field),
                ft.Row(spacing=10,
                       vertical_alignment=ft.CrossAxisAlignment.CENTER,
                       controls=[
                    ft.Column(spacing=2,
                              horizontal_alignment=ft.CrossAxisAlignment.END,
                              controls=[
                        ft.Text(display_name, size=13,
                                weight=ft.FontWeight.W_600, color=p["TEXT"]),
                        # ── Role badge ────────────────────────────────
                        ft.Container(
                            padding=ft.Padding(left=8, right=8, top=2, bottom=2),
                            border_radius=6,
                            bgcolor=badge_bg,
                            content=ft.Text(role_label, size=10,
                                            color=badge_text,
                                            weight=ft.FontWeight.W_700),
                        ),
                    ]),
                    ft.IconButton(icon=theme_icon, icon_color=p["MUTED"], icon_size=18,
                                  tooltip=theme_tip, on_click=change_theme),
                    ft.IconButton(icon=ft.Icons.NOTIFICATIONS_NONE,
                                  icon_color=p["MUTED"], icon_size=18,
                                  tooltip="Notifications",
                                  on_click=lambda e: _show_snack(
                                      page, "No new notifications.", p["GREEN"])),
                    ft.Container(width=32, height=32, border_radius=16,
                                 bgcolor=p["AVATAR_BG"], alignment=ft.Alignment(0, 0),
                                 content=ft.Icon(ft.Icons.PERSON,
                                                 color=p["AVATAR_ICON"], size=16)),
                ]),
            ],
        ),
    )


def footer_bar(page: ft.Page) -> ft.Container:
    p = palette(page)
    return ft.Container(
        bgcolor=p["SURFACE"],
        border=ft.Border(top=ft.BorderSide(1, p["BORDER"])),
        padding=ft.Padding(left=20, right=20, top=8, bottom=8),
        content=ft.Text("© 2026 AI Model Training Log System. All Rights Reserved.",
                        size=11, color=p["MUTED"], text_align=ft.TextAlign.CENTER),
        alignment=ft.Alignment(0, 0),
    )


def page_shell(page: ft.Page, go_to, active: str,
               content: ft.Control, route: str = "") -> ft.View:
    p = palette(page)

    final_route = route or f"/{active}"
    if not isinstance(page.data, dict):
        page.data = {}
    page.data["current_route"] = final_route

    sidebar = sidebar_component(page, go_to, active)
    header  = header_bar(page, go_to)
    footer  = footer_bar(page)

    body = ft.Row(expand=True, spacing=0, controls=[
        sidebar,
        ft.Column(expand=True, spacing=0, controls=[
            header,
            ft.Container(expand=True, content=content, bgcolor=p["BG"]),
            footer,
        ]),
    ])

    return ft.View(
        route=final_route,
        padding=0, spacing=0, bgcolor=p["BG"],
        controls=[body],
    )


# ── Helpers re-exported ────────────────────────────────────────────────────
show_snack = _show_snack