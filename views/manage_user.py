"""
manage_user.py - User management. SQLite əvəzinə API client istifadə edir.
"""

import flet as ft
from datetime import datetime

from views.theme import palette
from views.sidebar import page_shell, show_snack
from api import client as api


AVATAR_COLORS = ["#6366F1", "#EC4899", "#F59E0B", "#10B981", "#3B82F6"]
ROLE_COLORS = {
    "Admin":          ("#FEF3C7", "#92400E"),
    "Data Scientist": ("#DBEAFE", "#1D4ED8"),
    "Viewer":         ("#F3F4F6", "#374151"),
}


def manage_user_view(page: ft.Page, params, basket) -> ft.View:
    p = palette(page)
    go_to = basket["go_to"]

    users_data = api.get_users()
    search_q   = {"v": (page.data.get("search_query", "") if isinstance(page.data, dict) else "") or ""}
    sort_order = {"v": "Newest First"}

    rows_col   = ft.Column(spacing=0)
    showing_tx = ft.Text("", size=12, color=p["MUTED"], expand=True)

    def _avatar(name, idx):
        return ft.Container(
            content=ft.Text((name or "?")[0].upper(), size=13, color="#FFFFFF",
                            weight=ft.FontWeight.BOLD),
            bgcolor=AVATAR_COLORS[idx % len(AVATAR_COLORS)],
            border_radius=18, width=36, height=36, alignment=ft.Alignment(0, 0))

    def _role_badge(role):
        bg, fg = ROLE_COLORS.get(role, ("#F3F4F6", "#374151"))
        return ft.Container(
            content=ft.Text(role, size=11, color=fg, weight=ft.FontWeight.W_600),
            bgcolor=bg, border_radius=6,
            padding=ft.Padding(left=8, right=8, top=3, bottom=3))

    def _status_dot(status):
        color = p["GREEN"] if status == "Active" else "#9CA3AF"
        return ft.Row([
            ft.Container(width=8, height=8, border_radius=4, bgcolor=color),
            ft.Text(status, size=12, color=p["TEXT"]),
        ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    def _close(dlg):
        dlg.open = False
        page.update()

    def open_user_form(existing=None):
        username_f = ft.TextField(
            value=(existing or {}).get("username", ""),
            hint_text="e.g. john.doe", text_size=13,
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            border_radius=8, border_color=p["BORDER"],
            focused_border_color=p["GREEN"],
            color=p["TEXT"], bgcolor=p["INPUT_BG"],
            content_padding=ft.Padding(left=12, right=12, top=10, bottom=10))
        email_f = ft.TextField(
            value=(existing or {}).get("email", ""),
            hint_text="john@example.com", text_size=13,
            prefix_icon=ft.Icons.MAIL_OUTLINE,
            border_radius=8, border_color=p["BORDER"],
            focused_border_color=p["GREEN"],
            color=p["TEXT"], bgcolor=p["INPUT_BG"],
            content_padding=ft.Padding(left=12, right=12, top=10, bottom=10))
        pwd_f = ft.TextField(
            password=True, can_reveal_password=True, text_size=13,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            border_radius=8, border_color=p["BORDER"],
            focused_border_color=p["GREEN"],
            color=p["TEXT"], bgcolor=p["INPUT_BG"],
            content_padding=ft.Padding(left=12, right=12, top=10, bottom=10),
            disabled=existing is not None,
            hint_text="(password unchanged)" if existing else "")
        role_dd = ft.Dropdown(
            value=(existing or {}).get("role", "Data Scientist"),
            text_size=13, border_radius=8,
            border_color=p["BORDER"], color=p["TEXT"], bgcolor=p["INPUT_BG"],
            content_padding=ft.Padding(left=12, right=12, top=8, bottom=8),
            options=[ft.DropdownOption(r) for r in ["Admin", "Data Scientist", "Viewer"]])
        status_sw = ft.Switch(
            value=((existing or {}).get("status", "Active") == "Active"),
            active_color=p["GREEN"])

        def save(_e):
            uname = (username_f.value or "").strip()
            email = (email_f.value or "").strip()
            if not uname or not email:
                show_snack(page, "Username and email are required.", "#EF4444")
                return
            try:
                if existing:
                    api.update_user(
                        existing["id"], uname, email,
                        role_dd.value or "Data Scientist",
                        "Active" if status_sw.value else "Inactive")
                    show_snack(page, "Updated.", p["GREEN"])
                else:
                    pwd = (pwd_f.value or "").strip() or "default1234"
                    api.create_user(uname, email, pwd, role_dd.value or "Data Scientist")
                    show_snack(page, "User created.", p["GREEN"])
            except Exception as ex:
                detail = str(ex)
                if "409" in detail or "already exists" in detail.lower():
                    show_snack(page, "This email already exists.", "#EF4444")
                else:
                    show_snack(page, f"API error: {detail}", "#EF4444")
                return
            _close(dlg)
            _reload()

        title = "Edit User" if existing else "Create New User"
        subtitle = ("Update an existing user." if existing
                    else "Register a new member to the training log system.")

        body = ft.Column(spacing=16, controls=[
            ft.Row([
                ft.Column([ft.Text("USERNAME", size=11, color=p["MUTED"],
                                   weight=ft.FontWeight.W_600), username_f],
                         spacing=4, expand=True),
                ft.Column([ft.Text("EMAIL ADDRESS", size=11, color=p["MUTED"],
                                   weight=ft.FontWeight.W_600), email_f],
                         spacing=4, expand=True),
            ], spacing=12),
            ft.Row([
                ft.Column([ft.Text("PASSWORD", size=11, color=p["MUTED"],
                                   weight=ft.FontWeight.W_600), pwd_f],
                         spacing=4, expand=True),
                ft.Column([ft.Text("ASSIGNED ROLE", size=11, color=p["MUTED"],
                                   weight=ft.FontWeight.W_600), role_dd],
                         spacing=4, expand=True),
            ], spacing=12),
            ft.Container(
                border=ft.Border.all(1, p["BORDER"]), border_radius=8,
                padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                content=ft.Row([
                    ft.Column([
                        ft.Text("Account Status", size=13, color=p["TEXT"],
                                weight=ft.FontWeight.W_600),
                        ft.Text("Immediately allow login upon creation",
                                size=12, color=p["MUTED"]),
                    ], spacing=2, expand=True),
                    status_sw,
                ]),
            ),
        ])

        dlg = ft.AlertDialog(
            modal=True, bgcolor=p["SURFACE"],
            title=ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.PERSON_ADD_OUTLINED, size=20, color=p["GREEN"]),
                    bgcolor=p["GREEN_LIGHT"], border_radius=10, padding=8),
                ft.Column([
                    ft.Text(title, size=16, color=p["TEXT"], weight=ft.FontWeight.W_700),
                    ft.Text(subtitle, size=12, color=p["MUTED"]),
                ], spacing=2),
            ], spacing=12),
            content=ft.Container(width=520, content=body),
            actions=[
                ft.TextButton("Cancel",
                              style=ft.ButtonStyle(color={"": p["MUTED"]}),
                              on_click=lambda e: _close(dlg)),
                ft.FilledButton("Save" if existing else "Create Account",
                              style=ft.ButtonStyle(bgcolor={"": p["GREEN"]},
                                                   color={"": "#FFFFFF"}),
                              on_click=save),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def confirm_delete(user):
        def do_delete(_e):
            api.delete_user(user["id"])
            _close(dlg)
            _reload()
            show_snack(page, f"{user['username']} deleted.", p["RED"])
        dlg = ft.AlertDialog(
            modal=True, bgcolor=p["SURFACE"],
            title=ft.Text("Delete User", color=p["TEXT"], weight=ft.FontWeight.BOLD),
            content=ft.Text(f"\"{user['username']}\" user? Are you sure?", color=p["TEXT"]),
            actions=[
                ft.TextButton("Cancel",
                              style=ft.ButtonStyle(color={"": p["MUTED"]}),
                              on_click=lambda e: _close(dlg)),
                ft.FilledButton("Delete",
                              style=ft.ButtonStyle(bgcolor={"": p["RED"]},
                                                   color={"": "#FFFFFF"}),
                              on_click=do_delete),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def deactivate_user(user):
        new_status = "Inactive" if user["status"] == "Active" else "Active"
        api.toggle_user_status(user["id"], new_status)
        _reload()
        show_snack(page, f"Status: {new_status}", p["GREEN"])

    def _user_row(i, u):
        row_bg = p["ROW_ALT"] if i % 2 == 1 else p["SURFACE"]  # alternating row colors
        return ft.Container(
            bgcolor=row_bg,
            content=ft.Row([
                ft.Row([_avatar(u["username"], i),
                        ft.Column([
                            ft.Text(u["username"] or "?", size=13, color=p["TEXT"],
                                    weight=ft.FontWeight.W_600),
                            ft.Text(f"ID: {u['id']}", size=11, color=p["MUTED"]),
                        ], spacing=1)],
                       spacing=10, expand=3,
                       vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Row([
                    ft.Icon(ft.Icons.MAIL_OUTLINE, size=13, color=p["MUTED"]),
                    ft.Text(u["email"] or "—", size=12, color=p["MUTED"]),
                ], spacing=6, expand=3),
                ft.Container(content=_role_badge(u["role"] or "Data Scientist"), expand=2),
                ft.Container(content=_status_dot(u["status"] or "Active"), expand=1),
                ft.Text(u["joined"] or "—", size=12, color=p["MUTED"], expand=2),
                ft.Container(width=60, alignment=ft.Alignment(1, 0),
                             content=ft.PopupMenuButton(
                                 icon=ft.Icons.MORE_VERT, icon_size=18, icon_color=p["MUTED"],
                                 items=[
                                     ft.PopupMenuItem(content=ft.Text("Edit"),
                                         icon=ft.Icons.EDIT_OUTLINED,
                                         on_click=lambda e, uu=u: open_user_form(uu)),
                                     ft.PopupMenuItem(
                                         content=ft.Text("Deactivate" if u["status"] == "Active" else "Activate"),
                                         icon=ft.Icons.BLOCK_OUTLINED,
                                         on_click=lambda e, uu=u: deactivate_user(uu)),
                                     ft.PopupMenuItem(content=ft.Text("Delete"),
                                         icon=ft.Icons.DELETE_OUTLINE,
                                         on_click=lambda e, uu=u: confirm_delete(uu)),
                                 ])),
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=20, right=20, top=12, bottom=12),
            border=ft.Border(bottom=ft.BorderSide(1, p["BORDER"])),
        )

    def _filtered():
        q = (search_q["v"] or "").lower().strip()
        items = list(users_data)
        if q:
            items = [u for u in items
                     if q in " ".join([str(u.get(k) or "")
                                       for k in ("username","email","role","status")]).lower()]
        if sort_order["v"] == "Newest First":
            items.sort(key=lambda u: u.get("joined") or "", reverse=True)
        elif sort_order["v"] == "Oldest First":
            items.sort(key=lambda u: u.get("joined") or "")
        return items

    def _rebuild_rows():
        items = _filtered()
        rows_col.controls.clear()
        for i, u in enumerate(items):
            rows_col.controls.append(_user_row(i, u))
        showing_tx.value = f"Showing {len(items)} of {len(users_data)} users"
        try:
            page.update()
        except Exception:
            pass

    def _reload():
        nonlocal users_data
        users_data = api.get_users()
        _rebuild_rows()

    if isinstance(page.data, dict):
        def header_cb(value: str):
            search_q["v"] = value or ""
            local_search.value = value or ""
            try:
                local_search.update()
            except Exception:
                pass
            _rebuild_rows()
        page.data["on_header_search"] = header_cb

    def on_local_search(e):
        search_q["v"] = e.control.value or ""
        _rebuild_rows()

    local_search = ft.TextField(
        value=search_q["v"],
        hint_text="Search users...", border=ft.InputBorder.NONE,
        height=34, text_size=13, expand=True,
        color=p["TEXT"], hint_style=ft.TextStyle(color=p["MUTED"]),
        bgcolor="transparent",
        content_padding=ft.Padding(left=8, right=8, top=0, bottom=0),
        on_change=on_local_search,
    )

    def on_sort_change(e):
        sort_order["v"] = e.control.value or "Newest First"
        _rebuild_rows()

    sort_dd = ft.Dropdown(
        value="Newest First", text_size=13, width=150, height=38,
        border_radius=8, border_color=p["BORDER"],
        color=p["TEXT"], bgcolor=p["INPUT_BG"],
        content_padding=ft.Padding(left=10, right=10, top=6, bottom=6),
        options=[ft.DropdownOption("Newest First"), ft.DropdownOption("Oldest First")],
        on_select=on_sort_change)

    def clear_filters(_e):
        search_q["v"] = ""
        sort_order["v"] = "Newest First"
        local_search.value = ""
        sort_dd.value = "Newest First"
        if isinstance(page.data, dict):
            page.data["search_query"] = ""
        _rebuild_rows()

    tbl_header = ft.Container(
        content=ft.Row([
            ft.Text("User",   size=12, color=p["MUTED"], weight=ft.FontWeight.W_600, expand=3),
            ft.Text("Email",  size=12, color=p["MUTED"], weight=ft.FontWeight.W_600, expand=3),
            ft.Text("Role",   size=12, color=p["MUTED"], weight=ft.FontWeight.W_600, expand=2),
            ft.Text("Status", size=12, color=p["MUTED"], weight=ft.FontWeight.W_600, expand=1),
            ft.Text("Joined", size=12, color=p["MUTED"], weight=ft.FontWeight.W_600, expand=2),
            ft.Text("Actions",size=12, color=p["MUTED"], weight=ft.FontWeight.W_600, width=60),
        ], spacing=8),
        bgcolor=p["ROW_ALT"],
        border_radius=ft.BorderRadius(top_left=10, top_right=10, bottom_left=0, bottom_right=0),
        padding=ft.Padding(left=20, right=20, top=11, bottom=11),
        border=ft.Border(bottom=ft.BorderSide(1, p["BORDER"])),
    )

    user_table = ft.Container(
        bgcolor=p["SURFACE"], border=ft.Border.all(1, p["BORDER"]),
        border_radius=12, clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.SEARCH, size=15, color=p["MUTED"]),
                            local_search,
                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        border=ft.Border.all(1, p["BORDER"]), border_radius=8,
                        padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                        height=38, bgcolor=p["INPUT_BG"], expand=True),
                    sort_dd,
                    ft.TextButton("Clear Filters",
                                  style=ft.ButtonStyle(color={"": p["MUTED"]}),
                                  on_click=clear_filters),
                ], spacing=10),
                padding=ft.Padding(left=20, right=20, top=12, bottom=12),
                border=ft.Border(bottom=ft.BorderSide(1, p["BORDER"])),
            ),
            tbl_header,
            rows_col,
            ft.Container(
                content=ft.Row([
                    showing_tx,
                    ft.OutlinedButton("Previous", disabled=True,
                        style=ft.ButtonStyle(color={"": p["MUTED"]},
                                             side={"": ft.BorderSide(1, p["BORDER"])})),
                    ft.OutlinedButton("Next",
                        style=ft.ButtonStyle(color={"": p["TEXT"]},
                                             side={"": ft.BorderSide(1, p["BORDER"])})),
                ], spacing=8),
                padding=ft.Padding(left=20, right=20, top=12, bottom=12),
                border=ft.Border(top=ft.BorderSide(1, p["BORDER"])),
            ),
        ], spacing=0),
    )

    _rebuild_rows()

    def confirm_delete_all(_e):
        def do_delete_all(__e):
            try:
                api.delete_all_users() if hasattr(api, "delete_all_users") else None
                # fallback: delete one by one
                for u in api.get_users():
                    api.delete_user(u["id"])
                show_snack(page, "All users deleted.", p["RED"])
            except Exception as ex:
                show_snack(page, f"Error: {ex}", "#EF4444")
            dlg.open = False
            _reload()
            page.update()

        dlg = ft.AlertDialog(
            modal=True, bgcolor=p["SURFACE"],
            title=ft.Text("Delete All Users", color=p["TEXT"], weight=ft.FontWeight.BOLD),
            content=ft.Text("Are you sure you want to delete ALL users? This cannot be undone.",
                            color=p["TEXT"]),
            actions=[
                ft.TextButton("Cancel",
                              style=ft.ButtonStyle(color={"": p["MUTED"]}),
                              on_click=lambda e: _close(dlg)),
                ft.FilledButton("Delete All",
                              style=ft.ButtonStyle(bgcolor={"": p["RED"]},
                                                   color={"": "#FFFFFF"}),
                              on_click=do_delete_all),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    main_content = ft.Container(
        expand=True, padding=28, bgcolor=p["BG"],
        content=ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("User Management", size=26, weight=ft.FontWeight.BOLD, color=p["TEXT"]),
                    ft.Text("Manage platform access, assign roles, and monitor user activity.",
                            size=13, color=p["MUTED"]),
                ], expand=True),
                ft.OutlinedButton(
                    "Delete All",
                    icon=ft.Icons.DELETE_SWEEP_OUTLINED,
                    style=ft.ButtonStyle(color={"": p["RED"]},
                                         side={"": ft.BorderSide(1, p["RED"])}),
                    on_click=confirm_delete_all,
                ),
                ft.FilledButton("+ Add New User",
                                style=ft.ButtonStyle(bgcolor={"": p["GREEN"]},
                                                     color={"": "#FFFFFF"}),
                                on_click=lambda e: open_user_form(None)),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Divider(height=1, color=p["BORDER"]),
            user_table,
        ], spacing=16, scroll=ft.ScrollMode.AUTO, expand=True),
    )

    return page_shell(page, go_to, "manage-users", main_content, route="/manage-users")
