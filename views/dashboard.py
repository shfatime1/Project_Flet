"""
dashboard.py - System Overview. SQLite əvəzinə API client istifadə edir.
"""

import csv
import flet as ft

from views.theme import palette
from views.sidebar import page_shell, show_snack
from api import client as api


def _experiments_for_dashboard():
    default = [
        ("ResNet50-ImageNet-FineTune",     "Dr. Sarah Chen",  "ResNet50v2", "2023-10-24 14:20", "Running"),
        ("BERT-Base-SST2-Classifier",      "Marcus Thorne",   "BERT-Base",  "2023-10-24 12:15", "Completed"),
        ("YOLOv8-Custom-Safety-Detection", "Dr. Sarah Chen",  "YOLOv8n",    "2023-10-23 18:45", "Failed"),
        ("GPT2-Small-WikiText-LM",         "Elena Rodriguez", "GPT2-S",     "2023-10-23 10:30", "Completed"),
        ("LSTM-Stock-Prediction-v4",       "Marcus Thorne",   "LSTM-TS",    "2023-10-22 16:00", "Stopped"),
    ]
    try:
        rows = api.get_experiments()
        if not rows:
            return default
        out = []
        for r in rows[:5]:
            out.append((r["name"], r["owner"], r["model"],
                        (r["created"] or "").replace("\n", " "), r["status"]))
        return out
    except Exception:
        return default


def dashboard_view(page: ft.Page, params, basket) -> ft.View:
    p = palette(page)
    go_to = basket["go_to"]

    page.title = "AI Model Training Dashboard"

    _username = "User"
    if isinstance(page.data, dict):
        _username = (page.data.get("username") or page.data.get("user_email") or "User")

    def metric_card(title, value, badge, status, icon,
                    icon_color=None, icon_bg=None, icon_border=None):
        icon_color  = icon_color  or p["MUTED"]
        icon_bg     = icon_bg     or p["SURFACE"]
        icon_border = icon_border or p["BORDER"]
        if status == "green":
            badge_bg, badge_fg = p["GREEN_LIGHT"], p["GREEN_DARK"]
        elif status == "blue":
            badge_bg, badge_fg = p["BLUE_LIGHT"], p["BLUE"]
        elif status == "red":
            badge_bg, badge_fg = p["RED_LIGHT"], p["RED"]
        else:
            badge_bg, badge_fg = p["GRAY_SOFT"], p["MUTED"]
        return ft.Container(
            expand=True, bgcolor=p["SURFACE"], border_radius=14,
            border=ft.Border.all(1, p["BORDER"]),
            padding=ft.Padding(left=18, right=18, top=18, bottom=18),
            content=ft.Column(spacing=12, controls=[
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                    ft.Container(width=34, height=34, border_radius=10,
                                 border=ft.Border.all(1, icon_border),
                                 bgcolor=icon_bg, alignment=ft.Alignment(0, 0),
                                 content=ft.Icon(icon, size=16, color=icon_color)),
                    ft.Container(padding=ft.Padding(left=8, right=8, top=3, bottom=3),
                                 border_radius=20, bgcolor=badge_bg,
                                 content=ft.Text(badge, size=12, color=badge_fg,
                                                 weight=ft.FontWeight.W_600)),
                ]),
                ft.Text(title, size=13, color=p["MUTED"]),
                ft.Text(value, size=30, color=p["TEXT"], weight=ft.FontWeight.W_700),
            ]),
        )

    def status_badge(label):
        if label == "Running":
            bg, fg = p["GRAY_SOFT"], p["TEXT"]; dot = "#9CA3AF"
        elif label == "Completed":
            bg, fg = p["BLUE_LIGHT"], p["BLUE"]; dot = p["BLUE"]
        elif label == "Failed":
            bg, fg = p["RED_LIGHT"], p["RED"]; dot = p["RED"]
        else:
            bg, fg = p["GRAY_SOFT"], p["MUTED"]; dot = "#9CA3AF"
        return ft.Container(
            padding=ft.Padding(left=10, right=10, top=4, bottom=4),
            border_radius=16, bgcolor=bg,
            content=ft.Row(spacing=6, controls=[
                ft.Container(width=6, height=6, border_radius=3, bgcolor=dot),
                ft.Text(label, size=12, color=fg, weight=ft.FontWeight.W_600),
            ]),
        )

    def experiment_row(name, owner, model, created, status, last=False):
        def open_details(_e=None):
            if not isinstance(page.data, dict):
                page.data = {}
            page.data["selected_experiment"] = {
                "id": "EXP-AUTO", "name": name, "owner": owner,
                "model": model, "created": created, "status": status, "desc": "",
            }
            go_to("/experiment-details")

        return ft.Container(
            padding=ft.Padding(left=16, right=16, top=12, bottom=12),
            border=ft.Border(bottom=ft.BorderSide(0 if last else 1, p["BORDER"])),
            on_click=open_details, ink=True,
            content=ft.Row(controls=[
                ft.Container(expand=2, content=ft.Column(spacing=2, controls=[
                    ft.Text(name,  size=13, color=p["TEXT"], weight=ft.FontWeight.W_600),
                    ft.Text(owner, size=12, color=p["MUTED"]),
                ])),
                ft.Container(expand=1, content=ft.Container(
                    padding=ft.Padding(left=8, right=8, top=3, bottom=3),
                    border_radius=8, bgcolor=p["GRAY_SOFT"],
                    content=ft.Text(model, size=11, color=p["MUTED"]))),
                ft.Container(expand=1, content=ft.Text(created, size=12, color=p["MUTED"])),
                ft.Container(expand=1, content=status_badge(status)),
                ft.Container(width=70, content=ft.TextButton(
                    content=ft.Text("View", size=13, color=p["GREEN_DARK"],
                                    weight=ft.FontWeight.W_600),
                    on_click=open_details)),
            ]),
        )

    def view_logs(_e):    go_to("/training-monitor")
    def quick_create(_e): go_to("/experiments")
    def quick_users(_e):  go_to("/manage-users")
    def quick_deploy(_e): go_to("/manage-models")

    def export_data(_e):
        try:
            with open("dashboard_export.csv", "w", newline="", encoding="utf-8") as fp:
                w = csv.writer(fp)
                w.writerow(["Experiment","Owner","Model","Created","Status"])
                for row in _experiments_for_dashboard():
                    w.writerow(row)
            show_snack(page, "dashboard_export.csv saved.", p["GREEN"])
        except Exception as ex:
            show_snack(page, f"Error during export: {ex}", "#EF4444")

    rows = _experiments_for_dashboard()
    table_rows = [experiment_row(*rows[i], last=(i == len(rows)-1)) for i in range(len(rows))]

    experiments_table = ft.Container(
        bgcolor=p["SURFACE"], border=ft.Border.all(1, p["BORDER"]),
        border_radius=14, clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Column(spacing=0, controls=[
            ft.Container(
                bgcolor=p["ROW_ALT"],
                border=ft.Border(bottom=ft.BorderSide(1, p["BORDER"])),
                padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                content=ft.Row(controls=[
                    ft.Container(expand=2, content=ft.Text("Experiment Name", size=13, color=p["MUTED"], weight=ft.FontWeight.W_600)),
                    ft.Container(expand=1, content=ft.Text("Linked Model",    size=13, color=p["MUTED"], weight=ft.FontWeight.W_600)),
                    ft.Container(expand=1, content=ft.Text("Created At",      size=13, color=p["MUTED"], weight=ft.FontWeight.W_600)),
                    ft.Container(expand=1, content=ft.Text("Status",          size=13, color=p["MUTED"], weight=ft.FontWeight.W_600)),
                    ft.Container(width=70, content=ft.Text("Actions",         size=13, color=p["MUTED"], weight=ft.FontWeight.W_600)),
                ]),
            ),
            *table_rows,
        ]),
    )

    def quick_link(label, icon, on_click):
        return ft.Container(
            border=ft.Border.all(1, p["BORDER"]), border_radius=10,
            padding=ft.Padding(left=14, right=14, top=10, bottom=10),
            on_click=on_click, ink=True,
            content=ft.Row(spacing=10, controls=[
                ft.Icon(icon, size=17, color=p["MUTED"]),
                ft.Text(label, size=13, color=p["TEXT"]),
            ]),
        )

    def metric_line(name, model, value, age, last=False):
        return ft.Container(
            border=ft.Border(bottom=ft.BorderSide(0 if last else 1, p["BORDER"])),
            padding=ft.Padding(left=2, right=2, top=10, bottom=10),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(spacing=2, controls=[
                        ft.Text(name,  size=14, color=p["TEXT"], weight=ft.FontWeight.W_600),
                        ft.Text(model, size=12, color=p["MUTED"]),
                    ]),
                    ft.Column(spacing=2, horizontal_alignment=ft.CrossAxisAlignment.END, controls=[
                        ft.Text(value, size=14, color=p["GREEN_DARK"], weight=ft.FontWeight.W_700),
                        ft.Text(age, size=11, color=p["MUTED"]),
                    ]),
                ],
            ),
        )

    refresh_count = {"v": 0}
    refresh_text  = ft.Text("Refresh Stream", size=13, color=p["MUTED"])

    def refresh_metrics(_e):
        refresh_count["v"] += 1
        refresh_text.value = f"Refreshed ✓  ({refresh_count['v']})"
        page.update()
        show_snack(page, "Metrics refreshed.", p["GREEN"])

    right_panel = ft.Container(width=320, content=ft.Column(spacing=16, controls=[
        ft.Container(
            border=ft.Border.all(1, p["BORDER"]), border_radius=14,
            bgcolor=p["SURFACE"], padding=ft.Padding(left=16, right=16, top=16, bottom=16),
            content=ft.Column(spacing=12, controls=[
                ft.Text("Quick Actions", size=18, color=p["TEXT"], weight=ft.FontWeight.W_700),
                ft.Text("Common tasks based on your role.", size=13, color=p["MUTED"]),
                ft.ElevatedButton("+  Create New Experiment",
                    style=ft.ButtonStyle(bgcolor={"": p["GREEN"]}, color={"": "#FFFFFF"},
                                         shape={"": ft.RoundedRectangleBorder(radius=10)},
                                         elevation={"": 0}),
                    height=42, width=280, on_click=quick_create),
                quick_link("Manage System Users", ft.Icons.PEOPLE_OUTLINE, quick_users),
                quick_link("Deployment Portal",   ft.Icons.OPEN_IN_NEW,    quick_deploy),
            ]),
        ),
        ft.Container(
            border=ft.Border.all(1, p["BORDER"]), border_radius=14,
            bgcolor=p["SURFACE"], padding=ft.Padding(left=16, right=16, top=16, bottom=16),
            content=ft.Column(spacing=6, controls=[
                ft.Text("Latest Metrics", size=18, color=p["TEXT"], weight=ft.FontWeight.W_700),
                ft.Text("Real-time updates from active runs.", size=13, color=p["MUTED"]),
                metric_line("Accuracy",  "RESNET50V2", "94.2%", "2 mins ago"),
                metric_line("Loss",      "BERT-BASE",  "0.124", "5 mins ago"),
                metric_line("F1-Score",  "RESNET50V2", "0.89",  "12 mins ago"),
                metric_line("Precision", "GPT2-S",     "0.91",  "20 mins ago"),
                metric_line("Recall",    "YOLOV8N",    "0.88",  "45 mins ago", True),
                ft.Container(padding=ft.Padding(left=0,right=0,top=8,bottom=0),
                             alignment=ft.Alignment(0,0), ink=True,
                             on_click=refresh_metrics, content=refresh_text),
            ]),
        ),
    ]))

    main_area = ft.Container(
        expand=True, padding=ft.Padding(left=20, right=20, top=20, bottom=20), bgcolor=p["BG"],
        content=ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=18, controls=[
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                   vertical_alignment=ft.CrossAxisAlignment.END, controls=[
                ft.Column(spacing=4, controls=[
                    ft.Text("System Overview", size=26, color=p["TEXT"], weight=ft.FontWeight.W_700),
                    ft.Text(f"Welcome back, {_username}. Here's what happened with your models today.",
                            size=13, color=p["MUTED"]),
                ]),
                ft.Row(spacing=10, controls=[
                    ft.OutlinedButton("View Logs", icon=ft.Icons.VISIBILITY_OUTLINED,
                        style=ft.ButtonStyle(color={"": p["TEXT"]},
                                             shape={"": ft.RoundedRectangleBorder(radius=10)},
                                             side={"": ft.BorderSide(1, p["BORDER"])}),
                        on_click=view_logs),
                    ft.ElevatedButton("Export Data", icon=ft.Icons.NORTH_EAST,
                        style=ft.ButtonStyle(bgcolor={"": p["GREEN"]}, color={"": "#FFFFFF"},
                                             shape={"": ft.RoundedRectangleBorder(radius=10)},
                                             elevation={"": 0}),
                        on_click=export_data),
                ]),
            ]),
            ft.Row(spacing=14, controls=[
                metric_card("Total Experiments","1,284","+12%","green",
                    ft.Icons.DESCRIPTION_OUTLINED,
                    icon_color=p["GREEN"],icon_bg=p["GREEN_SOFT"],icon_border=p["GREEN_LIGHT"]),
                metric_card("Active Trainings","12","Stable","blue",
                    ft.Icons.SHOW_CHART,
                    icon_color=p["BLUE"],icon_bg=p["BLUE_LIGHT"],icon_border=p["BLUE_LIGHT"]),
                metric_card("Completed Models","842","+5%","green",
                    ft.Icons.CHECK_CIRCLE_OUTLINE,
                    icon_color=p["TEXT"],icon_bg=p["SURFACE"],icon_border=p["BORDER"]),
                metric_card("Failed Runs","24","-2%","red",
                    ft.Icons.CANCEL_OUTLINED,
                    icon_color=p["RED"],icon_bg=p["RED_LIGHT"],icon_border=p["RED_LIGHT"]),
            ]),
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                ft.Column(spacing=4, controls=[
                    ft.Text("Recent Experiments", size=20, color=p["TEXT"], weight=ft.FontWeight.W_700),
                    ft.Text("Last 5 training runs across all active models.", size=13, color=p["MUTED"]),
                ]),
                ft.TextButton(content=ft.Text("View All Experiments", size=14,
                                              color=p["GREEN_DARK"], weight=ft.FontWeight.W_700),
                              on_click=lambda _e: go_to("/experiments")),
            ]),
            ft.Row(spacing=16, vertical_alignment=ft.CrossAxisAlignment.START, controls=[
                ft.Container(expand=True, content=experiments_table),
                right_panel,
            ]),
        ]),
    )

    return page_shell(page, go_to, "dashboard", main_area, route="/dashboard")
