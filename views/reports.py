import csv
import flet as ft
from datetime import datetime

from views.theme import palette
from views.sidebar import page_shell, show_snack
from api import client as api


AVATAR_COLORS = {
    "Jordan Smith": ("#DBEAFE", "#1D4ED8"),
    "Sarah Chen":   ("#FCE7F3", "#BE185D"),
    "Marcus Vogt":  ("#FEF3C7", "#92400E"),
}


def reports_view(page: ft.Page, params, basket) -> ft.View:
    p = palette(page)
    go_to = basket["go_to"]

    _role = (page.data.get("role") or "") if isinstance(page.data, dict) else ""
    _is_admin = _role.upper() == "ADMIN"

    reports_data = api.get_reports()
    search_q   = {"v": page.data.get("search_query", "") if isinstance(page.data, dict) else ""}
    fmt_filter  = {"v": "All"}
    date_filter = {"v": "All"}

    rows_col = ft.Column(spacing=0)
    total_text = ft.Text(f"Total Reports: {len(reports_data)}",
                         size=13, color=p["TEXT"], weight=ft.FontWeight.W_600, expand=True)
    showing_text = ft.Text(f"Showing {len(reports_data)} of {len(reports_data)} reports",
                           size=12, color=p["MUTED"], expand=True)

    def _initials(name):
        parts = name.split()
        return (parts[0][0] + parts[-1][0]).upper() if len(parts) >= 2 else name[:2].upper()

    def _avatar(name):
        bg, fg = AVATAR_COLORS.get(name, ("#F3F4F6", "#374151"))
        return ft.Container(
            content=ft.Text(_initials(name), size=12, color=fg, weight=ft.FontWeight.BOLD),
            bgcolor=bg, border_radius=20, width=32, height=32, alignment=ft.Alignment(0, 0))

    def _fmt_icon(fmt):
        icon  = ft.Icons.PICTURE_AS_PDF_OUTLINED if fmt == "PDF" else ft.Icons.CODE_OUTLINED
        color = p["RED"] if fmt == "PDF" else p["BLUE"]
        return ft.Icon(icon, size=18, color=color)

    def _status_badge(status):
        if status == "Final":
            return ft.Container(
                content=ft.Text("Final", size=11, color=p["GREEN"], weight=ft.FontWeight.W_600),
                bgcolor=p["GREEN_LIGHT"], border_radius=6,
                padding=ft.Padding(left=8, right=8, top=3, bottom=3))
        return ft.Container(
            content=ft.Text("Draft", size=11, color=p["MUTED"], weight=ft.FontWeight.W_600),
            bgcolor=p["ROW_ALT"], border=ft.Border.all(1, p["BORDER"]), border_radius=6,
            padding=ft.Padding(left=8, right=8, top=3, bottom=3))

    def _close(dlg):
        dlg.open = False
        page.update()

    def show_view_dialog(rid, title, fmt, experiment, creator, date, status):
        body = ft.Column([
            ft.Row([_fmt_icon(fmt),
                    ft.Text(title, size=16, color=p["TEXT"], weight=ft.FontWeight.W_700, expand=True)],
                   spacing=10),
            ft.Divider(height=1, color=p["BORDER"]),
            ft.Row([ft.Text("Experiment:", color=p["MUTED"], size=13, width=100),
                    ft.Text(experiment, color=p["TEXT"], size=13)]),
            ft.Row([ft.Text("Format:", color=p["MUTED"], size=13, width=100),
                    ft.Text(fmt, color=p["TEXT"], size=13)]),
            ft.Row([ft.Text("Created by:", color=p["MUTED"], size=13, width=100),
                    ft.Text(creator, color=p["TEXT"], size=13)]),
            ft.Row([ft.Text("Date:", color=p["MUTED"], size=13, width=100),
                    ft.Text(date, color=p["TEXT"], size=13)]),
            ft.Row([ft.Text("Status:", color=p["MUTED"], size=13, width=100),
                    _status_badge(status)]),
        ], spacing=10, tight=True)
        dlg = ft.AlertDialog(
            modal=True, bgcolor=p["SURFACE"],
            title=ft.Text("Report Details", color=p["TEXT"], weight=ft.FontWeight.BOLD),
            content=ft.Container(width=460, content=body),
            actions=[ft.TextButton("Close",
                                   style=ft.ButtonStyle(color={"": p["MUTED"]}),
                                   on_click=lambda e: _close(dlg))],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def show_edit_dialog(rid, title, fmt, experiment, status):
        title_f = ft.TextField(value=title, color=p["TEXT"], bgcolor=p["INPUT_BG"],
                                border_color=p["BORDER"], border_radius=8, text_size=13, height=44,
                                content_padding=ft.Padding(left=12, right=12, top=10, bottom=10))
        fmt_dd = ft.Dropdown(
            options=[ft.DropdownOption("PDF"), ft.DropdownOption("HTML")],
            value=fmt, color=p["TEXT"], bgcolor=p["INPUT_BG"],
            border_color=p["BORDER"], border_radius=8, text_size=13, height=44,
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6))
        exp_f = ft.TextField(value=experiment, color=p["TEXT"], bgcolor=p["INPUT_BG"],
                              border_color=p["BORDER"], border_radius=8, text_size=13, height=44,
                              content_padding=ft.Padding(left=12, right=12, top=10, bottom=10))
        status_dd = ft.Dropdown(
            options=[ft.DropdownOption("Draft"), ft.DropdownOption("Final")],
            value=status, color=p["TEXT"], bgcolor=p["INPUT_BG"],
            border_color=p["BORDER"], border_radius=8, text_size=13, height=44,
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6))

        def save(_e):
            try:
                api.update_report(rid,
                                  (title_f.value or "").strip() or title,
                                  fmt_dd.value or fmt,
                                  (exp_f.value or "").strip() or experiment,
                                  status_dd.value or status)
            except Exception as ex:
                show_snack(page, f"API error: {ex}", "#EF4444")
                return
            _close(dlg)
            _reload()
            show_snack(page, "Report updated.", p["GREEN"])

        body = ft.Column([
            ft.Text("Title",      size=12, color=p["MUTED"], weight=ft.FontWeight.W_600), title_f,
            ft.Text("Format",     size=12, color=p["MUTED"], weight=ft.FontWeight.W_600), fmt_dd,
            ft.Text("Experiment", size=12, color=p["MUTED"], weight=ft.FontWeight.W_600), exp_f,
            ft.Text("Status",     size=12, color=p["MUTED"], weight=ft.FontWeight.W_600), status_dd,
        ], spacing=6, tight=True)
        dlg = ft.AlertDialog(
            modal=True, bgcolor=p["SURFACE"],
            title=ft.Text("Edit Report", color=p["TEXT"], weight=ft.FontWeight.BOLD),
            content=ft.Container(width=460, content=body),
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

    def confirm_delete(rid, title):
        def do_delete(_e):
            api.delete_report(rid)
            _close(dlg)
            _reload()
            show_snack(page, f"{title} deleted.", p["RED"])
        dlg = ft.AlertDialog(
            modal=True, bgcolor=p["SURFACE"],
            title=ft.Text("Delete Report", color=p["TEXT"], weight=ft.FontWeight.BOLD),
            content=ft.Text(f"\"{title}\" report? Are you sure?", color=p["TEXT"]),
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

    def open_generate(_e):
        title_f = ft.TextField(hint_text="e.g. Q4 ResNet-50 Training Summary",
                                color=p["TEXT"], bgcolor=p["INPUT_BG"],
                                border_color=p["BORDER"], border_radius=8, text_size=13, height=44,
                                content_padding=ft.Padding(left=12, right=12, top=10, bottom=10))
        exp_dd  = ft.Dropdown(
            options=[ft.DropdownOption(f"EXP-{x}") for x in [902, 884, 905, 772, 651]],
            value="EXP-902", color=p["TEXT"], bgcolor=p["INPUT_BG"],
            border_color=p["BORDER"], border_radius=8, text_size=13, height=44,
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6))
        fmt_g   = ft.RadioGroup(content=ft.Row([
            ft.Radio(value="PDF", label="PDF"),
            ft.Radio(value="HTML", label="HTML"),
        ]), value="PDF")

        def do_create(_e):
            title = (title_f.value or "").strip()
            if not title:
                title_f.error_text = "Title is required"
                page.update()
                return
            creator = "Sarah Chen"
            if isinstance(page.data, dict):
                creator = page.data.get("username") or creator
            try:
                api.create_report(title, fmt_g.value or "PDF",
                                  exp_dd.value or "EXP-902", creator, "Draft")
            except Exception as ex:
                show_snack(page, f"API error: {ex}", "#EF4444")
                return
            _close(dlg)
            _reload()
            show_snack(page, "Report created.", p["GREEN"])

        dlg = ft.AlertDialog(
            modal=True, bgcolor=p["SURFACE"],
            title=ft.Text("Generate New Report", color=p["TEXT"], weight=ft.FontWeight.BOLD),
            content=ft.Container(width=420, content=ft.Column([
                ft.Text("Fill in the details to generate a new experiment report.",
                        size=13, color=p["MUTED"]),
                ft.Container(height=4),
                ft.Text("Report Title", size=13, color=p["TEXT"], weight=ft.FontWeight.W_500),
                title_f,
                ft.Text("Experiment", size=13, color=p["TEXT"], weight=ft.FontWeight.W_500),
                exp_dd,
                ft.Text("Format", size=13, color=p["TEXT"], weight=ft.FontWeight.W_500),
                fmt_g,
            ], spacing=10, tight=True)),
            actions=[
                ft.TextButton("Cancel",
                              style=ft.ButtonStyle(color={"": p["MUTED"]}),
                              on_click=lambda e: _close(dlg)),
                ft.FilledButton("Generate",
                              style=ft.ButtonStyle(bgcolor={"": p["GREEN"]},
                                                   color={"": "#FFFFFF"}),
                              on_click=do_create),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def open_workflows(_e):
        dlg = ft.AlertDialog(
            modal=True, bgcolor=p["SURFACE"],
            title=ft.Text("Automated Workflows", color=p["TEXT"], weight=ft.FontWeight.BOLD),
            content=ft.Container(width=480, content=ft.Column([
                ft.Text("These reports are generated automatically:", size=13, color=p["MUTED"]),
                ft.Container(height=4),
                ft.Container(
                    bgcolor=p["ROW_ALT"], border_radius=8, padding=12,
                    content=ft.Column([
                        ft.Row([ft.Icon(ft.Icons.SCHEDULE, size=16, color=p["GREEN"]),
                                ft.Text("Every Monday at 09:00", color=p["TEXT"], size=13)], spacing=8),
                        ft.Row([ft.Icon(ft.Icons.SCIENCE_OUTLINED, size=16, color=p["GREEN"]),
                                ft.Text("PDFs for completed experiments", color=p["TEXT"], size=13)], spacing=8),
                        ft.Row([ft.Icon(ft.Icons.MAIL_OUTLINE, size=16, color=p["GREEN"]),
                                ft.Text("Email sent to: team@aimodel.io", color=p["TEXT"], size=13)], spacing=8),
                    ], spacing=6),
                ),
            ], spacing=10, tight=True)),
            actions=[
                ft.FilledButton("Got it",
                              style=ft.ButtonStyle(bgcolor={"": p["GREEN"]}, color={"": "#FFFFFF"}),
                              on_click=lambda e: _close(dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def batch_download(_e):
        try:
            with open("reports_batch.csv", "w", newline="", encoding="utf-8") as fp:
                w = csv.writer(fp)
                w.writerow(["ID","Title","Format","Experiment","Creator","Date","Status"])
                for r in reports_data:
                    w.writerow([r.get("id"),r.get("title"),r.get("format"),
                                r.get("experiment"),r.get("creator"),
                                r.get("created_at"),r.get("status")])
            show_snack(page, f"{len(reports_data)} reports downloaded → reports_batch.csv", p["GREEN"])
        except Exception as ex:
            show_snack(page, f"Download error: {ex}", "#EF4444")

    def _row(r, idx=0):
        rid      = r["id"]
        title    = r["title"]
        fmt      = r["format"]
        exp_id   = r["experiment"]
        creator  = r["creator"]
        date     = r["created_at"]
        status   = r["status"]
        row_bg   = p["ROW_ALT"] if idx % 2 == 1 else p["SURFACE"]  # alternating row colors
        actions_menu = ft.PopupMenuButton(
            icon=ft.Icons.MORE_VERT_ROUNDED, icon_size=18, icon_color=p["MUTED"],
            items=[
                ft.PopupMenuItem(content=ft.Text("View"), icon=ft.Icons.VISIBILITY_OUTLINED,
                                 on_click=lambda e: show_view_dialog(rid,title,fmt,exp_id,creator,date,status)),
                ft.PopupMenuItem(content=ft.Text("Edit"), icon=ft.Icons.EDIT_OUTLINED,
                                 on_click=lambda e: show_edit_dialog(rid,title,fmt,exp_id,status)),
                ft.PopupMenuItem(content=ft.Text("Delete"), icon=ft.Icons.DELETE_OUTLINE,
                                 on_click=lambda e: confirm_delete(rid,title)),
            ])
        return ft.Container(
            bgcolor=row_bg,
            content=ft.Row([
                _fmt_icon(fmt),
                ft.Column([
                    ft.Text(title, size=13, color=p["TEXT"], weight=ft.FontWeight.W_500),
                    ft.Text(f"Format: {fmt}", size=11, color=p["MUTED"]),
                ], spacing=2, expand=3),
                ft.Container(
                    content=ft.Text(exp_id, size=11, color=p["TEXT"], weight=ft.FontWeight.W_600),
                    bgcolor=p["ROW_ALT"], border=ft.Border.all(1, p["BORDER"]),
                    border_radius=4, padding=ft.Padding(left=6, right=6, top=3, bottom=3), expand=1),
                ft.Row([_avatar(creator), ft.Text(creator, size=13, color=p["TEXT"])],
                       spacing=8, expand=2),
                ft.Text(date, size=12, color=p["MUTED"], expand=2),
                ft.Container(content=_status_badge(status), expand=1),
                ft.Row([
                    ft.IconButton(ft.Icons.VISIBILITY_OUTLINED,
                                  icon_color=p["MUTED"], icon_size=18, tooltip="View",
                                  on_click=lambda e: show_view_dialog(rid,title,fmt,exp_id,creator,date,status)),
                    actions_menu,
                ], width=80),
            ], spacing=8),
            padding=ft.Padding(left=16, right=16, top=12, bottom=12),
            border=ft.Border(bottom=ft.BorderSide(1, p["BORDER"])),
        )

    def _filtered():
        q    = (search_q["v"] or "").lower().strip()
        fmt  = fmt_filter["v"]
        days = date_filter["v"]
        out  = []
        cutoff = None
        if days == "30 Days":
            from datetime import timedelta
            cutoff = datetime.now() - timedelta(days=30)
        for r in reports_data:
            if fmt != "All" and r.get("format") != fmt:
                continue
            if cutoff:
                try:
                    dt = datetime.strptime(r.get("created_at","")[:16], "%Y-%m-%d %H:%M")
                    if dt < cutoff:
                        continue
                except Exception:
                    pass
            if q:
                hay = " ".join(str(r.get(k,"")) for k in ("title","format","experiment","creator","status")).lower()
                if q not in hay:
                    continue
            out.append(r)
        return out

    GREEN = p["GREEN"]

    def _make_fmt_btn(label):
        return ft.Container(
            data=label,
            content=ft.Text(label, size=12, color=GREEN if fmt_filter["v"] == label else p["TEXT"]),
            border=ft.Border.all(1, GREEN if fmt_filter["v"] == label else p["BORDER"]),
            border_radius=6,
            padding=ft.Padding(left=10, right=10, top=5, bottom=5),
            on_click=lambda e, lbl=label: _set_fmt(lbl),
        )

    def _make_date_btn(label):
        return ft.Container(
            data=label,
            content=ft.Text(label, size=12, color=GREEN if date_filter["v"] == label else p["TEXT"]),
            border=ft.Border.all(1, GREEN if date_filter["v"] == label else p["BORDER"]),
            border_radius=6,
            padding=ft.Padding(left=10, right=10, top=5, bottom=5),
            on_click=lambda e, lbl=label: _set_date(lbl),
        )

    fmt_btn_row  = ft.Row(spacing=4, controls=[_make_fmt_btn("All"), _make_fmt_btn("PDF"), _make_fmt_btn("HTML")])
    date_btn_row = ft.Row(spacing=4, controls=[_make_date_btn("All"), _make_date_btn("30 Days")])

    def _refresh_btn_styles():
        for c in fmt_btn_row.controls:
            active = fmt_filter["v"] == c.data
            c.content.color = GREEN if active else p["TEXT"]
            c.border = ft.Border.all(1, GREEN if active else p["BORDER"])
        for c in date_btn_row.controls:
            active = date_filter["v"] == c.data
            c.content.color = GREEN if active else p["TEXT"]
            c.border = ft.Border.all(1, GREEN if active else p["BORDER"])

    def _set_fmt(label):
        fmt_filter["v"] = label
        _refresh_btn_styles()
        _rebuild_rows()

    def _set_date(label):
        date_filter["v"] = label
        _refresh_btn_styles()
        _rebuild_rows()

    def _rebuild_rows():
        items = _filtered()
        rows_col.controls.clear()
        for idx, r in enumerate(items):
            rows_col.controls.append(_row(r, idx))
        total_text.value   = f"Total Reports: {len(reports_data)}"
        showing_text.value = f"Showing {len(items)} of {len(reports_data)} reports"
        try:
            page.update()
        except Exception:
            pass

    def _reload():
        nonlocal reports_data
        reports_data = api.get_reports()
        _rebuild_rows()

    if isinstance(page.data, dict):
        def header_cb(value: str):
            search_q["v"] = value or ""
            _rebuild_rows()
        page.data["on_header_search"] = header_cb

    _rebuild_rows()

    tbl_header = ft.Container(
        content=ft.Row([
            ft.Container(width=28),
            ft.Text("Report Title", size=12, color=p["MUTED"], weight=ft.FontWeight.W_600, expand=3),
            ft.Text("Experiment",   size=12, color=p["MUTED"], weight=ft.FontWeight.W_600, expand=1),
            ft.Text("Created By",   size=12, color=p["MUTED"], weight=ft.FontWeight.W_600, expand=2),
            ft.Text("Date",         size=12, color=p["MUTED"], weight=ft.FontWeight.W_600, expand=2),
            ft.Text("Status",       size=12, color=p["MUTED"], weight=ft.FontWeight.W_600, expand=1),
            ft.Text("Actions",      size=12, color=p["MUTED"], weight=ft.FontWeight.W_600, width=80),
        ], spacing=8),
        bgcolor=p["ROW_ALT"],
        border_radius=ft.BorderRadius(top_left=10, top_right=10, bottom_left=0, bottom_right=0),
        padding=ft.Padding(left=16, right=16, top=10, bottom=10),
        border=ft.Border(bottom=ft.BorderSide(1, p["BORDER"])),
    )

    table = ft.Container(
        bgcolor=p["SURFACE"], border=ft.Border.all(1, p["BORDER"]), border_radius=12,
        content=ft.Column([
            ft.Container(
                content=ft.Row([total_text, fmt_btn_row, date_btn_row], spacing=8),
                padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                border=ft.Border(bottom=ft.BorderSide(1, p["BORDER"])),
            ),
            tbl_header,
            rows_col,
            ft.Container(
                content=ft.Row([
                    showing_text,
                    ft.OutlinedButton("Previous", disabled=True,
                        style=ft.ButtonStyle(color={"": p["MUTED"]},
                                             side={"": ft.BorderSide(1, p["BORDER"])})),
                    ft.OutlinedButton("Next", disabled=True,
                        style=ft.ButtonStyle(color={"": p["MUTED"]},
                                             side={"": ft.BorderSide(1, p["BORDER"])})),
                ], spacing=8),
                padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                border=ft.Border(top=ft.BorderSide(1, p["BORDER"])),
            ),
        ], spacing=0),
    )

    auto_banner = ft.Container(
        bgcolor=p["SURFACE"], border=ft.Border.all(1, p["BORDER"]),
        border_radius=12, padding=30,
        content=ft.Column([
            ft.Container(
                content=ft.Icon(ft.Icons.DESCRIPTION_OUTLINED, size=28, color=p["GREEN"]),
                bgcolor=p["GREEN_LIGHT"], border_radius=20, padding=8),
            ft.Text("Automated Report Generation", size=15, weight=ft.FontWeight.BOLD, color=p["TEXT"]),
            ft.Text("You can set up automated reporting for recurring experiments.", size=12, color=p["MUTED"]),
            ft.OutlinedButton("View Automated Workflows",
                              style=ft.ButtonStyle(color={"": p["TEXT"]},
                                                   side={"": ft.BorderSide(1, p["BORDER"])}),
                              on_click=open_workflows),
        ], spacing=10),
    )

    def confirm_delete_all_reports(_e):
        def do_delete(__e):
            try:
                api.delete_all_reports()
                show_snack(page, "All reports deleted.", p["RED"])
            except Exception as ex:
                show_snack(page, f"Error: {ex}", "#EF4444")
            dlg.open = False
            _reload()
            page.update()
        dlg = ft.AlertDialog(
            modal=True, bgcolor=p["SURFACE"],
            title=ft.Text("Delete All Reports", color=p["TEXT"], weight=ft.FontWeight.BOLD),
            content=ft.Text("Are you sure you want to delete ALL reports? This cannot be undone.",
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
                    ft.Text("Experiment Reports", size=26, weight=ft.FontWeight.BOLD, color=p["TEXT"]),
                    ft.Text("Manage and review performance summaries for completed training cycles.",
                            size=13, color=p["MUTED"]),
                ], expand=True),
                ft.OutlinedButton("Batch Download", icon=ft.Icons.DOWNLOAD_OUTLINED,
                                  style=ft.ButtonStyle(color={"": p["TEXT"]},
                                                       side={"": ft.BorderSide(1, p["BORDER"])}),
                                  on_click=batch_download),
                ft.OutlinedButton(
                    "Delete All",
                    icon=ft.Icons.DELETE_SWEEP_OUTLINED,
                    visible=_is_admin,
                    style=ft.ButtonStyle(color={"": p["RED"]},
                                         side={"": ft.BorderSide(1, p["RED"])}),
                    on_click=confirm_delete_all_reports,
                ),
                ft.FilledButton("Generate Report", icon=ft.Icons.ADD_ROUNDED,
                                style=ft.ButtonStyle(bgcolor={"": p["GREEN"]}, color={"": "#FFFFFF"}),
                                on_click=open_generate),
            ]),
            ft.Divider(height=1, color=p["BORDER"]),
            table,
            auto_banner,
        ], spacing=16, scroll=ft.ScrollMode.AUTO),
    )

    return page_shell(page, go_to, "reports", main_content, route="/reports")
