"""
manage_dataset.py - Dataset management. SQLite əvəzinə API client istifadə edir.
"""

import flet as ft
from datetime import datetime

from views.theme import palette
from views.sidebar import page_shell, show_snack
from api import client as api


PROVIDER_COLORS = {
    "AWS S3 (US-East-1)":          ("#FEF3C7", "#92400E"),
    "AWS S3 (US-West-2)":          ("#FEF3C7", "#92400E"),
    "GCP Bucket (Europe-West)":    ("#DBEAFE", "#1D4ED8"),
    "Azure Blob Storage":          ("#EDE9FE", "#5B21B6"),
    "On-Premise NAS (Hospital A)": ("#F3F4F6", "#374151"),
}
PROVIDERS = list(PROVIDER_COLORS.keys())


def manage_dataset_view(page: ft.Page, params, basket) -> ft.View:
    p = palette(page)
    go_to = basket["go_to"]

    datasets = api.get_datasets()
    search_q = {"v": (page.data.get("search_query", "") if isinstance(page.data, dict) else "") or ""}

    rows_col = ft.Column(spacing=0)
    showing_tx = ft.Text("", size=12, color=p["MUTED"], expand=True)
    inv_count_text = ft.Text(str(len(datasets)), size=22,
                             weight=ft.FontWeight.BOLD, color=p["TEXT"])

    def _provider_badge(prov):
        bg, fg = PROVIDER_COLORS.get(prov, ("#F3F4F6", "#374151"))
        return ft.Container(
            content=ft.Text(prov, size=11, color=fg, weight=ft.FontWeight.W_600),
            bgcolor=bg, border_radius=6,
            padding=ft.Padding(left=8, right=8, top=3, bottom=3))

    def stat_card(label, value_widget, sub, icon):
        return ft.Container(
            expand=True, bgcolor=p["SURFACE"],
            border=ft.Border.all(1, p["BORDER"]), border_radius=12, padding=16,
            content=ft.Row([
                ft.Container(content=ft.Icon(icon, size=20, color=p["GREEN"]),
                             bgcolor=p["GREEN_LIGHT"], border_radius=10, padding=10),
                ft.Column([
                    ft.Text(label, size=12, color=p["MUTED"]),
                    value_widget,
                    ft.Text(sub, size=11, color=p["MUTED"]),
                ], spacing=2),
            ], spacing=14, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        )

    def _close(dlg):
        dlg.open = False
        page.update()

    def open_form(existing=None):
        name_f = ft.TextField(value=(existing or {}).get("name", ""),
                               hint_text="ImageNet-1K-Sub",
                               border_color=p["BORDER"], border_radius=8,
                               text_size=13, height=44,
                               color=p["TEXT"], bgcolor=p["INPUT_BG"],
                               content_padding=ft.Padding(left=12, right=12, top=10, bottom=10))
        desc_f = ft.TextField(value=(existing or {}).get("description", ""),
                               hint_text="Short description...", border_color=p["BORDER"],
                               border_radius=8, text_size=13, multiline=True,
                               min_lines=2, max_lines=4,
                               color=p["TEXT"], bgcolor=p["INPUT_BG"],
                               content_padding=ft.Padding(left=12, right=12, top=10, bottom=10))
        provider_dd = ft.Dropdown(
            value=(existing or {}).get("provider", PROVIDERS[0]),
            options=[ft.DropdownOption(pp) for pp in PROVIDERS],
            border_color=p["BORDER"], border_radius=8, text_size=13, height=44,
            color=p["TEXT"], bgcolor=p["INPUT_BG"],
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6))
        size_f = ft.TextField(value=(existing or {}).get("size", ""),
                               hint_text="e.g. 12.4 GB",
                               border_color=p["BORDER"], border_radius=8,
                               text_size=13, height=44,
                               color=p["TEXT"], bgcolor=p["INPUT_BG"],
                               content_padding=ft.Padding(left=12, right=12, top=10, bottom=10))

        def save(_e):
            n = (name_f.value or "").strip()
            if not n:
                show_snack(page, "Name is required.", "#EF4444")
                return
            try:
                if existing:
                    api.update_dataset(existing["id"], n,
                                       (desc_f.value or "").strip(),
                                       provider_dd.value or PROVIDERS[0],
                                       (size_f.value or "—").strip() or "—")
                    show_snack(page, "Dataset updated.", p["GREEN"])
                else:
                    api.create_dataset(n, (desc_f.value or "").strip(),
                                       provider_dd.value or PROVIDERS[0],
                                       (size_f.value or "—").strip() or "—")
                    show_snack(page, "Dataset added.", p["GREEN"])
            except Exception as ex:
                show_snack(page, f"API error: {ex}", "#EF4444")
                return
            _close(dlg)
            _reload()

        body = ft.Column(spacing=14, controls=[
            ft.Column([ft.Text("DATASET NAME", size=11, color=p["MUTED"],
                               weight=ft.FontWeight.W_600), name_f], spacing=4),
            ft.Column([ft.Text("DESCRIPTION", size=11, color=p["MUTED"],
                               weight=ft.FontWeight.W_600), desc_f], spacing=4),
            ft.Row([
                ft.Column([ft.Text("PROVIDER", size=11, color=p["MUTED"],
                                   weight=ft.FontWeight.W_600), provider_dd],
                         spacing=4, expand=True),
                ft.Column([ft.Text("SIZE", size=11, color=p["MUTED"],
                                   weight=ft.FontWeight.W_600), size_f],
                         spacing=4, expand=True),
            ], spacing=12),
        ])

        dlg = ft.AlertDialog(
            modal=True, bgcolor=p["SURFACE"],
            title=ft.Text("Edit Dataset" if existing else "Add Dataset",
                          color=p["TEXT"], weight=ft.FontWeight.BOLD),
            content=ft.Container(width=520, content=body),
            actions=[
                ft.TextButton("Cancel",
                              style=ft.ButtonStyle(color={"": p["MUTED"]}),
                              on_click=lambda e: _close(dlg)),
                ft.FilledButton("Save",
                              style=ft.ButtonStyle(bgcolor={"": p["GREEN"]},
                                                   color={"": "#FFFFFF"}),
                              on_click=save),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def open_view(d):
        body = ft.Column(spacing=10, controls=[
            ft.Row([ft.Icon(ft.Icons.STORAGE_OUTLINED, size=20, color=p["GREEN"]),
                    ft.Text(d["name"], size=16, color=p["TEXT"],
                            weight=ft.FontWeight.W_700, expand=True)], spacing=10),
            ft.Divider(height=1, color=p["BORDER"]),
            ft.Row([ft.Text("Description:", color=p["MUTED"], size=13, width=120),
                    ft.Text(d["description"] or "—", color=p["TEXT"], size=13, expand=True)]),
            ft.Row([ft.Text("Provider:", color=p["MUTED"], size=13, width=120),
                    _provider_badge(d["provider"])]),
            ft.Row([ft.Text("Size:", color=p["MUTED"], size=13, width=120),
                    ft.Text(d["size"] or "—", color=p["TEXT"], size=13)]),
            ft.Row([ft.Text("Created at:", color=p["MUTED"], size=13, width=120),
                    ft.Text(d["created"] or "—", color=p["TEXT"], size=13)]),
        ])
        dlg = ft.AlertDialog(
            modal=True, bgcolor=p["SURFACE"],
            title=ft.Text("Dataset Details", color=p["TEXT"], weight=ft.FontWeight.BOLD),
            content=ft.Container(width=480, content=body),
            actions=[ft.TextButton("Close",
                                   style=ft.ButtonStyle(color={"": p["MUTED"]}),
                                   on_click=lambda e: _close(dlg))],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def confirm_delete(d):
        def do_delete(_e):
            api.delete_dataset(d["id"])
            _close(dlg)
            _reload()
            show_snack(page, f"{d['name']} deleted.", p["RED"])
        dlg = ft.AlertDialog(
            modal=True, bgcolor=p["SURFACE"],
            title=ft.Text("Delete Dataset", color=p["TEXT"], weight=ft.FontWeight.BOLD),
            content=ft.Text(f"\"{d['name']}\" will be deleted. Continue?", color=p["TEXT"]),
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

    def _ds_row(d, idx=0):
        row_bg = p["ROW_ALT"] if idx % 2 == 1 else p["SURFACE"]  # alternating row colors
        return ft.Container(
            bgcolor=row_bg,
            content=ft.Row([
                ft.Column([
                    ft.Text(d["name"], size=13, color=p["TEXT"], weight=ft.FontWeight.W_600),
                    ft.Text(d["description"] or "—", size=11, color=p["MUTED"]),
                ], spacing=2, expand=3),
                ft.Container(content=_provider_badge(d["provider"] or "—"), expand=2),
                ft.Text(d["size"] or "—", size=13, color=p["TEXT"], expand=1),
                ft.Text(d["created"] or "—", size=12, color=p["MUTED"], expand=2),
                ft.Container(width=50, alignment=ft.Alignment(1, 0),
                             content=ft.PopupMenuButton(
                                 icon=ft.Icons.MORE_VERT, icon_size=18, icon_color=p["MUTED"],
                                 items=[
                                     ft.PopupMenuItem(content=ft.Text("View"),
                                         icon=ft.Icons.VISIBILITY_OUTLINED,
                                         on_click=lambda e, dd=d: open_view(dd)),
                                     ft.PopupMenuItem(content=ft.Text("Edit"),
                                         icon=ft.Icons.EDIT_OUTLINED,
                                         on_click=lambda e, dd=d: open_form(dd)),
                                     ft.PopupMenuItem(content=ft.Text("Delete"),
                                         icon=ft.Icons.DELETE_OUTLINE,
                                         on_click=lambda e, dd=d: confirm_delete(dd)),
                                 ])),
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=20, right=20, top=13, bottom=13),
            border=ft.Border(bottom=ft.BorderSide(1, p["BORDER"])),
        )

    provider_filter = {"v": "All Providers"}

    def _filtered():
        q = (search_q["v"] or "").lower().strip()
        items = list(datasets)
        if q:
            items = [d for d in items
                     if q in " ".join(str(d.get(k) or "")
                                      for k in ("name","description","provider","size")).lower()]
        if provider_filter["v"] != "All Providers":
            items = [d for d in items if d.get("provider") == provider_filter["v"]]
        return items

    def _rebuild_rows():
        items = _filtered()
        rows_col.controls.clear()
        for idx, d in enumerate(items):
            rows_col.controls.append(_ds_row(d, idx))
        showing_tx.value = f"Showing 1 to {len(items)} of {len(datasets)} entries"
        inv_count_text.value = str(len(datasets))
        try:
            page.update()
        except Exception:
            pass

    def _reload():
        nonlocal datasets
        datasets = api.get_datasets()
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
        hint_text="Search by name or source...",
        border=ft.InputBorder.NONE,
        height=34, text_size=13, expand=True,
        color=p["TEXT"], bgcolor="transparent",
        hint_style=ft.TextStyle(color=p["MUTED"]),
        content_padding=ft.Padding(left=8, right=8, top=0, bottom=0),
        on_change=on_local_search,
    )

    def on_filter_change(e):
        provider_filter["v"] = e.control.value or "All Providers"
        _rebuild_rows()

    filter_dd = ft.Dropdown(
        value="All Providers", text_size=13, width=210, height=38,
        border_radius=8, border_color=p["BORDER"],
        color=p["TEXT"], bgcolor=p["INPUT_BG"],
        content_padding=ft.Padding(left=10, right=10, top=6, bottom=6),
        options=[ft.DropdownOption("All Providers")] +
                [ft.DropdownOption(prov) for prov in PROVIDERS],
        on_select=on_filter_change,
    )

    tbl_header = ft.Container(
        content=ft.Row([
            ft.Text("Dataset Name",    size=12, color=p["MUTED"], weight=ft.FontWeight.W_600, expand=3),
            ft.Text("Source Provider", size=12, color=p["MUTED"], weight=ft.FontWeight.W_600, expand=2),
            ft.Text("Size",            size=12, color=p["MUTED"], weight=ft.FontWeight.W_600, expand=1),
            ft.Text("Created At",      size=12, color=p["MUTED"], weight=ft.FontWeight.W_600, expand=2),
            ft.Text("Actions",         size=12, color=p["MUTED"], weight=ft.FontWeight.W_600, width=50),
        ], spacing=8),
        bgcolor=p["ROW_ALT"],
        border_radius=ft.BorderRadius(top_left=10, top_right=10, bottom_left=0, bottom_right=0),
        padding=ft.Padding(left=20, right=20, top=11, bottom=11),
        border=ft.Border(bottom=ft.BorderSide(1, p["BORDER"])),
    )

    table = ft.Container(
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
                    filter_dd,
                    showing_tx,
                ], spacing=10),
                padding=ft.Padding(left=20, right=20, top=12, bottom=12),
                border=ft.Border(bottom=ft.BorderSide(1, p["BORDER"])),
            ),
            tbl_header,
            rows_col,
            ft.Container(
                content=ft.Row([
                    ft.Text(f"Total: {len(datasets)} datasets",
                            size=12, color=p["MUTED"], expand=True),
                    ft.OutlinedButton("Previous", disabled=True,
                        style=ft.ButtonStyle(color={"": p["MUTED"]},
                                             side={"": ft.BorderSide(1, p["BORDER"])})),
                    ft.Container(width=32, height=32, border_radius=16,
                                 bgcolor=p["GREEN"], alignment=ft.Alignment(0, 0),
                                 content=ft.Text("1", size=13, color="#FFFFFF",
                                                 weight=ft.FontWeight.W_600)),
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

    def _total_size():
        total_gb = 0.0
        for d in datasets:
            sz = (d.get("size") or "").upper().replace(" ", "")
            try:
                if sz.endswith("TB"):
                    total_gb += float(sz[:-2]) * 1024
                elif sz.endswith("GB"):
                    total_gb += float(sz[:-2])
                elif sz.endswith("MB"):
                    total_gb += float(sz[:-2]) / 1024
            except Exception:
                pass
        if total_gb >= 1024:
            return f"{total_gb / 1024:.2f} TB"
        return f"{total_gb:.2f} GB"

    def confirm_delete_all_datasets(_e):
        def do_delete(__e):
            try:
                api.delete_all_datasets()
                show_snack(page, "All datasets deleted.", p["RED"])
            except Exception as ex:
                show_snack(page, f"Error: {ex}", "#EF4444")
            dlg.open = False
            _reload()
            page.update()
        dlg = ft.AlertDialog(
            modal=True, bgcolor=p["SURFACE"],
            title=ft.Text("Delete All Datasets", color=p["TEXT"], weight=ft.FontWeight.BOLD),
            content=ft.Text("Are you sure you want to delete ALL datasets? This cannot be undone.",
                            color=p["TEXT"]),
            actions=[
                ft.TextButton("Cancel",
                              style=ft.ButtonStyle(color={"": p["MUTED"]}),
                              on_click=lambda e: _close(dlg)),
                ft.FilledButton("Delete All",
                              style=ft.ButtonStyle(bgcolor={"": p["RED"]},
                                                   color={"": "#FFFFFF"}),
                              on_click=do_delete),
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
                    ft.Text("Manage Datasets", size=26, weight=ft.FontWeight.BOLD, color=p["TEXT"]),
                    ft.Text("Maintain and configure the global inventory of datasets for training.",
                            size=13, color=p["MUTED"]),
                ], expand=True),
                ft.OutlinedButton(
                    "Delete All",
                    icon=ft.Icons.DELETE_SWEEP_OUTLINED,
                    style=ft.ButtonStyle(color={"": p["RED"]},
                                         side={"": ft.BorderSide(1, p["RED"])}),
                    on_click=confirm_delete_all_datasets,
                ),
                ft.FilledButton("+ Add Dataset",
                                style=ft.ButtonStyle(bgcolor={"": p["GREEN"]},
                                                     color={"": "#FFFFFF"}),
                                on_click=lambda e: open_form(None)),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Row([
                stat_card("Total Inventory", inv_count_text,
                          "Active registered datasets", ft.Icons.STORAGE_OUTLINED),
                stat_card("Total Storage",
                          ft.Text(_total_size(), size=22, weight=ft.FontWeight.BOLD, color=p["TEXT"]),
                          "Aggregated cloud & local size", ft.Icons.CLOUD_OUTLINED),
                stat_card("Recent Additions",
                          ft.Text(str(min(2, len(datasets))), size=22,
                                  weight=ft.FontWeight.BOLD, color=p["TEXT"]),
                          "Added in the last 30 days",
                          ft.Icons.CALENDAR_TODAY_OUTLINED),
            ], spacing=14),
            table,
        ], spacing=16, scroll=ft.ScrollMode.AUTO, expand=True),
    )

    return page_shell(page, go_to, "manage-datasets", main_content, route="/manage-datasets")
