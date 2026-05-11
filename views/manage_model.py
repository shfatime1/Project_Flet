import flet as ft
from views.theme import palette
from views.sidebar import page_shell, show_snack
from api import client as api


LIFECYCLE_OPTIONS = ["In Training", "Completed", "Stopped", "Deprecated", "Failed", "Running"]


def manage_model_view(page: ft.Page, params, basket) -> ft.View:
    p = palette(page)
    go_to = basket["go_to"]

    models_data = api.get_models()
    search_q    = {"v": (page.data.get("search_query", "") if isinstance(page.data, dict) else "") or ""}

    rows_col   = ft.Column(spacing=0)
    showing_tx = ft.Text("", size=12, color=p["MUTED"], expand=True)
    total_text = ft.Text(str(len(models_data)), size=24,
                         weight=ft.FontWeight.BOLD, color=p["TEXT"])

    STATUS_CFG = {
        "Completed":  (p["GREEN"], p["GREEN_LIGHT"]),
        "Running":    (p["BLUE"],  p["BLUE_LIGHT"]),
        "Stopped":    (p["GRAY"],  p["ROW_ALT"]),
        "Failed":     (p["RED"],   p["RED_LIGHT"]),
        "In Training":(p["BLUE"],  p["BLUE_LIGHT"]),
        "Deprecated": (p["GRAY"],  p["ROW_ALT"]),
    }

    def _status_badge(status):
        color, bg = STATUS_CFG.get(status, (p["GRAY"], p["ROW_ALT"]))
        return ft.Container(
            content=ft.Text(status, size=11, color=color, weight=ft.FontWeight.W_600),
            bgcolor=bg, border_radius=6,
            padding=ft.Padding(left=8, right=8, top=3, bottom=3))

    def _close(dlg):
        dlg.open = False
        page.update()

    def open_form(existing=None):
        is_edit = existing is not None
        name_f = ft.TextField(
            value=(existing or {}).get("name", ""),
            hint_text="e.g. ResNet50-Object-Detection",
            border_color=p["BORDER"], border_radius=8, text_size=13, height=44,
            color=p["TEXT"], bgcolor=p["INPUT_BG"],
            content_padding=ft.Padding(left=12, right=12, top=10, bottom=10))
        ver_f = ft.TextField(
            value=(existing or {}).get("version", ""),
            hint_text="e.g. v1.0.0",
            border_color=p["BORDER"], border_radius=8, text_size=13, height=44,
            color=p["TEXT"], bgcolor=p["INPUT_BG"],
            content_padding=ft.Padding(left=12, right=12, top=10, bottom=10))
        status_dd = ft.Dropdown(
            options=[ft.DropdownOption(s) for s in LIFECYCLE_OPTIONS],
            value=(existing or {}).get("status", "In Training"),
            border_color=p["BORDER"], border_radius=8, text_size=13, height=44,
            color=p["TEXT"], bgcolor=p["INPUT_BG"],
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6))
        notes_f = ft.TextField(
            value=(existing or {}).get("notes", ""),
            hint_text="Describe what this model version does...",
            border_color=p["BORDER"], border_radius=8, text_size=13,
            multiline=True, min_lines=3, max_lines=4,
            color=p["TEXT"], bgcolor=p["INPUT_BG"],
            content_padding=ft.Padding(left=12, right=12, top=10, bottom=10))

        def save(_e):
            n = (name_f.value or "").strip()
            if not n:
                name_f.error_text = "Name is required"
                page.update()
                return
            v  = (ver_f.value or "").strip() or "v1.0.0"
            s  = status_dd.value or "In Training"
            nt = (notes_f.value or "").strip()
            try:
                if is_edit:
                    api.update_model(existing["mod_id"], n, v, s, nt)
                    show_snack(page, "Model updated.", p["GREEN"])
                else:
                    api.create_model(n, v, s, nt)
                    show_snack(page, "Model registered.", p["GREEN"])
            except Exception as ex:
                show_snack(page, f"API error: {ex}", "#EF4444")
                return
            _close(dlg)
            _reload()

        body = ft.Column(spacing=16, controls=[
            ft.Row([
                ft.Column([ft.Text("MODEL NAME", size=11, color=p["MUTED"],
                                   weight=ft.FontWeight.W_600), name_f],
                         spacing=4, expand=True),
                ft.Column([ft.Text("VERSION", size=11, color=p["MUTED"],
                                   weight=ft.FontWeight.W_600), ver_f],
                         spacing=4, expand=True),
            ], spacing=12),
            ft.Column([ft.Text("LIFECYCLE STATUS", size=11, color=p["MUTED"],
                               weight=ft.FontWeight.W_600), status_dd], spacing=4),
            ft.Column([ft.Text("RELEASE NOTES", size=11, color=p["MUTED"],
                               weight=ft.FontWeight.W_600), notes_f], spacing=4),
        ])
        if is_edit:
            body.controls.append(
                ft.Container(
                    border=ft.Border(top=ft.BorderSide(1, p["BORDER"])),
                    padding=ft.Padding(left=0, right=0, top=10, bottom=0),
                    content=ft.Row([
                        ft.Column([ft.Text("SOURCE DATASET", size=10, color=p["MUTED"],
                                           weight=ft.FontWeight.W_600),
                                   ft.Text(f"↗ {existing.get('dataset') or 'N/A'}",
                                           size=12, color=p["GREEN"])],
                                  spacing=2, expand=True),
                        ft.Column([ft.Text("ORIGINATING EXPERIMENT", size=10, color=p["MUTED"],
                                           weight=ft.FontWeight.W_600),
                                   ft.Text(f"↗ {existing.get('experiment') or 'N/A'}",
                                           size=12, color=p["GREEN"])],
                                  spacing=2, expand=True),
                    ])))

        title    = "Edit Model Details" if is_edit else "Register New Model"
        subtitle = (f"Update metadata for {existing['name']}." if is_edit
                    else "Add a model to the central registry.")

        dlg = ft.AlertDialog(
            modal=True, bgcolor=p["SURFACE"],
            title=ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.HUB_OUTLINED, size=20, color=p["GREEN"]),
                    bgcolor=p["GREEN_LIGHT"], border_radius=10, padding=8),
                ft.Column([
                    ft.Text(title, size=16, color=p["TEXT"], weight=ft.FontWeight.W_700),
                    ft.Text(subtitle, size=12, color=p["MUTED"]),
                ], spacing=2),
            ], spacing=12),
            content=ft.Container(width=560, content=body),
            actions=[
                ft.TextButton("Cancel" if not is_edit else "Discard Changes",
                              style=ft.ButtonStyle(color={"": p["MUTED"]}),
                              on_click=lambda e: _close(dlg)),
                ft.FilledButton("Save & Publish Version" if is_edit else "Register Model",
                              style=ft.ButtonStyle(bgcolor={"": p["GREEN"]},
                                                   color={"": "#FFFFFF"}),
                              on_click=save),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def confirm_delete(m):
        def do_delete(_e):
            api.delete_model(m["mod_id"])
            _close(dlg)
            _reload()
            show_snack(page, f"{m['name']} deleted.", p["RED"])
        dlg = ft.AlertDialog(
            modal=True, bgcolor=p["SURFACE"],
            title=ft.Text("Delete Model", color=p["TEXT"], weight=ft.FontWeight.BOLD),
            content=ft.Text(f"\"{m['name']}\" will be deleted. Continue?", color=p["TEXT"]),
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

    def _row(m, idx=0):
        row_bg = p["ROW_ALT"] if idx % 2 == 1 else p["SURFACE"]  # alternating row colors
        return ft.Container(
            on_click=lambda e, mm=m: open_form(mm), ink=True,
            padding=ft.Padding(left=16, right=16, top=14, bottom=14),
            border=ft.Border(bottom=ft.BorderSide(1, p["BORDER"])),
            bgcolor=row_bg,
            content=ft.Row(spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                ft.Column([
                    ft.Text(m["name"], size=13, color=p["TEXT"], weight=ft.FontWeight.W_600),
                    ft.Text(m["mod_id"], size=11, color=p["MUTED"]),
                ], spacing=2, expand=3),
                ft.Container(
                    content=ft.Text(m["version"], size=11, color=p["GREEN"],
                                    weight=ft.FontWeight.W_600),
                    bgcolor=p["GREEN_LIGHT"], border_radius=4,
                    padding=ft.Padding(left=7, right=7, top=3, bottom=3), expand=1),
                ft.Container(content=_status_badge(m["status"]), expand=1),
                ft.TextButton(f"↗ {m['dataset'] or '—'}",
                    style=ft.ButtonStyle(color={"": p["GREEN"]}), expand=2),
                ft.TextButton(f"↗ {m['experiment'] or '—'}",
                    style=ft.ButtonStyle(color={"": p["GREEN"]}), expand=2),
                ft.Text(m["created_at"], size=12, color=p["MUTED"], expand=2),
                ft.Row(width=80, spacing=0, controls=[
                    ft.IconButton(ft.Icons.EDIT_OUTLINED,
                        icon_color=p["GRAY"], icon_size=18, tooltip="Edit",
                        on_click=lambda e, mm=m: open_form(mm)),
                    ft.IconButton(ft.Icons.DELETE_OUTLINE,
                        icon_color=p["RED"], icon_size=18, tooltip="Delete",
                        on_click=lambda e, mm=m: confirm_delete(mm)),
                ]),
            ]),
        )

    def _filtered():
        q = (search_q["v"] or "").lower().strip()
        items = list(models_data)
        if q:
            items = [m for m in items
                     if q in " ".join(str(m.get(k) or "")
                                      for k in ("name","mod_id","version",
                                                "status","dataset","experiment","notes")).lower()]
        return items

    def _rebuild_rows():
        items = _filtered()
        rows_col.controls.clear()
        for idx, m in enumerate(items):
            rows_col.controls.append(_row(m, idx))
        showing_tx.value = f"Showing 1-{len(items)} of {len(models_data)} models"
        total_text.value = str(len(models_data))
        try:
            page.update()
        except Exception:
            pass

    def _reload():
        nonlocal models_data
        models_data = api.get_models()
        _rebuild_rows()

    if isinstance(page.data, dict):
        def header_cb(value: str):
            search_q["v"] = value or ""
            search_input.value = value or ""
            try:
                search_input.update()
            except Exception:
                pass
            _rebuild_rows()
        page.data["on_header_search"] = header_cb

    def on_search_change(e):
        search_q["v"] = e.control.value or ""
        _rebuild_rows()

    search_input = ft.TextField(
        value=search_q["v"],
        hint_text="Search by name, version, or experiment...",
        hint_style=ft.TextStyle(color=p["MUTED"], size=13),
        border=ft.InputBorder.NONE, height=36, text_size=13, expand=True,
        color=p["TEXT"], bgcolor="transparent",
        content_padding=ft.Padding(left=6, right=6, top=0, bottom=0),
        on_change=on_search_change,
    )

    search_bar = ft.Container(
        expand=True, height=40,
        border=ft.Border.all(1, p["BORDER"]), border_radius=8,
        bgcolor=p["INPUT_BG"], padding=ft.Padding(left=10, right=0, top=0, bottom=0),
        content=ft.Row([
            ft.Icon(ft.Icons.SEARCH, size=16, color=p["GRAY"]),
            search_input,
        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
    )

    tbl_header = ft.Container(
        bgcolor=p["ROW_ALT"],
        padding=ft.Padding(left=16, right=16, top=10, bottom=10),
        border=ft.Border(bottom=ft.BorderSide(1, p["BORDER"])),
        content=ft.Row(spacing=8, controls=[
            ft.Text("Model Name",     size=12, color=p["GRAY"], weight=ft.FontWeight.W_600, expand=3),
            ft.Text("Version",        size=12, color=p["GRAY"], weight=ft.FontWeight.W_600, expand=1),
            ft.Text("Status",         size=12, color=p["GRAY"], weight=ft.FontWeight.W_600, expand=1),
            ft.Text("Source Dataset", size=12, color=p["GRAY"], weight=ft.FontWeight.W_600, expand=2),
            ft.Text("Experiment",     size=12, color=p["GRAY"], weight=ft.FontWeight.W_600, expand=2),
            ft.Text("Created At",     size=12, color=p["GRAY"], weight=ft.FontWeight.W_600, expand=2),
            ft.Text("Actions",        size=12, color=p["GRAY"], weight=ft.FontWeight.W_600, width=80),
        ]),
    )

    table_card = ft.Container(
        bgcolor=p["SURFACE"], border=ft.Border.all(1, p["BORDER"]),
        border_radius=12, clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Column(spacing=0, controls=[
            ft.Container(
                padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                border=ft.Border(bottom=ft.BorderSide(1, p["BORDER"])),
                content=ft.Row([
                    search_bar,
                    ft.TextButton("↗ View Full Registry",
                                  style=ft.ButtonStyle(color={"": p["GREEN"]}),
                                  on_click=lambda e: show_snack(page, "Full registry opened.", p["GREEN"])),
                ], spacing=10),
            ),
            tbl_header,
            rows_col,
            ft.Container(
                padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                border=ft.Border(top=ft.BorderSide(1, p["BORDER"])),
                content=ft.Row(spacing=8, controls=[
                    showing_tx,
                    ft.OutlinedButton("Previous", disabled=True,
                        style=ft.ButtonStyle(color={"": p["GRAY"]},
                                             side={"": ft.BorderSide(1, p["BORDER"])})),
                    ft.ElevatedButton("Next",
                        style=ft.ButtonStyle(bgcolor={"": p["GREEN"]},
                                             color={"": "#FFFFFF"},
                                             shape={"": ft.RoundedRectangleBorder(radius=8)},
                                             elevation={"": 0})),
                ]),
            ),
        ]),
    )

    _rebuild_rows()

    def _stat(icon, label, value, sub, sub_color=None):
        return ft.Container(
            expand=True, bgcolor=p["SURFACE"],
            border=ft.Border.all(1, p["BORDER"]), border_radius=12, padding=18,
            content=ft.Column([
                ft.Row([ft.Icon(icon, size=18, color=p["GREEN"]), ft.Container(expand=True)]),
                ft.Container(height=6),
                ft.Text(value, size=24, weight=ft.FontWeight.BOLD, color=p["TEXT"]),
                ft.Text(label, size=12, color=p["GRAY"]),
                ft.Text(sub, size=11, color=sub_color or p["GRAY"], weight=ft.FontWeight.W_500),
            ], spacing=4),
        )

    stats = ft.Row([
        ft.Container(
            expand=True, bgcolor=p["SURFACE"],
            border=ft.Border.all(1, p["BORDER"]), border_radius=12, padding=18,
            content=ft.Column([
                ft.Row([ft.Icon(ft.Icons.HUB_OUTLINED, size=18, color=p["GREEN"]),
                        ft.Container(expand=True)]),
                ft.Container(height=6),
                total_text,
                ft.Text("Total Models", size=12, color=p["GRAY"]),
                ft.Text("↑ 8% this month", size=11, color=p["GREEN"], weight=ft.FontWeight.W_500),
            ], spacing=4),
        ),
        _stat(ft.Icons.PLAY_CIRCLE_OUTLINE, "Active Trainings", "12", "Stable"),
        _stat(ft.Icons.CHECK_CIRCLE_OUTLINE, "Deployed Models", "18",
              "↑ 5% this month", sub_color=p["GREEN"]),
        _stat(ft.Icons.ERROR_OUTLINE, "Model Failures", "8",
              "↑ 14% improvement", sub_color=p["GREEN"]),
    ], spacing=16)

    def confirm_delete_all_models(_e):
        def do_delete(__e):
            try:
                api.delete_all_models()
                show_snack(page, "All models deleted.", p["RED"])
            except Exception as ex:
                show_snack(page, f"Error: {ex}", "#EF4444")
            dlg.open = False
            _reload()
            page.update()
        dlg = ft.AlertDialog(
            modal=True, bgcolor=p["SURFACE"],
            title=ft.Text("Delete All Models", color=p["TEXT"], weight=ft.FontWeight.BOLD),
            content=ft.Text("Are you sure you want to delete ALL models? This cannot be undone.",
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

    page_title = ft.Row(
        vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=10,
        controls=[
            ft.Column(expand=True, controls=[
                ft.Text("Manage Models", size=28, weight=ft.FontWeight.BOLD, color=p["TEXT"]),
                ft.Text("Central registry for all trained and deployed model versions.",
                        size=13, color=p["GRAY"]),
            ]),
            ft.OutlinedButton("↗ View Full Registry",
                style=ft.ButtonStyle(color={"": p["TEXT"]},
                                     side={"": ft.BorderSide(1, p["BORDER"])}),
                on_click=lambda e: show_snack(page, "Full registry opened.", p["GREEN"])),
            ft.OutlinedButton(
                "Delete All",
                icon=ft.Icons.DELETE_SWEEP_OUTLINED,
                style=ft.ButtonStyle(color={"": p["RED"]},
                                     side={"": ft.BorderSide(1, p["RED"])}),
                on_click=confirm_delete_all_models,
            ),
            ft.ElevatedButton("+ Register New Model",
                on_click=lambda e: open_form(None),
                style=ft.ButtonStyle(
                    bgcolor={"": p["GREEN"]}, color={"": "#FFFFFF"},
                    shape={"": ft.RoundedRectangleBorder(radius=8)},
                    elevation={"": 0},
                    padding={"": ft.Padding(left=16, right=16, top=12, bottom=12)})),
        ],
    )

    main_content = ft.Container(
        expand=True, bgcolor=p["BG"],
        padding=ft.Padding(left=30, right=30, top=30, bottom=30),
        content=ft.Column(
            expand=True, spacing=16, scroll=ft.ScrollMode.AUTO,
            controls=[page_title, ft.Divider(height=1, color=p["BORDER"]), stats, table_card],
        ),
    )

    return page_shell(page, go_to, "manage-models", main_content, route="/manage-models")
