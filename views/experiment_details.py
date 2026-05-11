import base64
import flet as ft
from datetime import datetime

from views.theme import palette
from views.sidebar import page_shell, show_snack


DEFAULT_METRICS = [
    ("Accuracy",  "0.942", "2 mins ago",  [0.45,0.62,0.74,0.83,0.89,0.92,0.94]),
    ("Loss",      "0.041", "2 mins ago",  [0.92,0.74,0.58,0.41,0.28,0.18,0.10]),
    ("F1 Score",  "0.928", "5 mins ago",  [0.40,0.58,0.70,0.80,0.87,0.91,0.93]),
    ("Precision", "0.951", "2 mins ago",  [0.50,0.65,0.76,0.85,0.91,0.93,0.95]),
    ("Recall",    "0.905", "10 mins ago", [0.38,0.55,0.68,0.78,0.85,0.89,0.91]),
]

DEFAULT_HYPERPARAMS = [
    ("Learning Rate",    "0.001"),
    ("Batch Size",       "64"),
    ("Optimizer",        "Adam"),
    ("Epochs",           "50"),
    ("Weight Decay",     "1e-4"),
    ("Base Dataset",     "MedScan-Alpha-2024"),
    ("GPU Architecture", "NVIDIA A100"),
    ("Seed",             "42"),
]


def _make_line_svg(values, color, width=80, height=32):
    n = len(values)
    if n < 2:
        return ""
    pad = 3
    w, h = width - pad * 2, height - pad * 2
    pts = " ".join(
        f"{pad+(i/(n-1))*w:.1f},{pad+(1-v)*h:.1f}"
        for i, v in enumerate(values)
    )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">'
        f'<polyline points="{pts}" fill="none" stroke="{color}" '
        f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        f'</svg>'
    )
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def _make_chart_svg(values, color, width=300, height=100):
    n = len(values)
    if n < 2:
        return ""
    pad = 12
    w, h = width - pad * 2, height - pad * 2
    pts = " ".join(
        f"{pad+(i/(n-1))*w:.1f},{pad+(1-v)*h:.1f}"
        for i, v in enumerate(values)
    )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">'
        f'<polyline points="{pts}" fill="none" stroke="{color}" '
        f'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
        f'</svg>'
    )
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def _sparkline_img(values, color):
    if not values or max(values) == min(values):
        norm = [0.5] * len(values) if values else [0.5, 0.5]
    else:
        mn, mx = min(values), max(values)
        norm = [(v - mn) / (mx - mn) for v in values]
    return ft.Image(
        src=_make_line_svg(norm, color),
        width=80, height=32, fit=ft.BoxFit.FILL,
    )


def _line_chart_widget(values, color, title, p):
    epochs = ["E1", "E5", "E10", "E20", "E30", "E40", "E50"]
    if not values:
        return ft.Container()
    if max(values) == min(values):
        norm = [0.5] * len(values)
    else:
        mn, mx = min(values), max(values)
        norm = [(v - mn) / (mx - mn) for v in values]
    return ft.Column([
        ft.Text(title, size=10, color=p["GRAY"], weight=ft.FontWeight.W_600),
        ft.Image(src=_make_chart_svg(norm, color), width=300, height=100,
                 fit=ft.BoxFit.FILL),
        ft.Row([ft.Container(ft.Text(e, size=9, color=p["GRAY"]), expand=True)
                for e in epochs], spacing=0),
    ], expand=True, spacing=4)


# ── View ────────────────────────────────────────────────────────────────────
def experiment_details_view(page: ft.Page, params, basket) -> ft.View:
    p = palette(page)
    nav = basket.get("go_to", page.push_route)

    data = page.data if isinstance(page.data, dict) else {}
    exp = data.get("selected_experiment", {})
    hyperparams = data.get("selected_hyperparams", DEFAULT_HYPERPARAMS)

    raw_metrics = data.get("selected_metrics")
    if raw_metrics:
        metrics = []
        for m in raw_metrics:
            name, value, updated = m[0], m[1], m[2]
            rising = m[3] if len(m) > 3 else True
            try:
                v = float((value or "0").replace("%", "").replace(",", "."))
                if v > 1.5:  # if % or 0–100 scale
                    v = v / 100
            except Exception:
                v = 0.5
            if rising:
                trend = [0.40, 0.55, 0.68, 0.78, 0.87, 0.93, max(0.0, min(1.0, v))]
            else:
                trend = [0.92, 0.80, 0.68, 0.55, 0.42, 0.30, max(0.0, min(1.0, v))]
            metrics.append((name, value, updated, trend))
    else:
        metrics = DEFAULT_METRICS

    exp_name    = exp.get("name", "Exp-ResNet50-ImageNet-FineTune")
    exp_desc    = exp.get("desc",
                          "Fine-tuning ResNet50 on specialised medical imagery dataset")
    exp_owner   = exp.get("owner", "Alex Rivera")
    exp_created = (exp.get("created", "May 15, 2024 • 10:45 AM") or "").replace("\n", " ")
    exp_status  = exp.get("status", "Running")
    exp_dataset = next((v for k, v in hyperparams if "Dataset" in k),
                       "MedScan-Alpha-2024")

    if exp_status == "Running":
        status_color = p["GREEN"]
        status_bg = p["GREEN_LIGHT"]
    elif exp_status == "Failed":
        status_color = p["RED"]
        status_bg = p["RED_LIGHT"]
    else:
        status_color = p["GRAY"]
        status_bg = p["GRAY_SOFT"]

    # ── Buttons ─────────────────────────────────────────────────────────────
    def do_clone(_e):
        try:
            from views.experiments import _insert, _next_id, _load
            _load()  # ensure table exists / seed
            new_id = _next_id()
            new_name = f"{exp_name} (Clone)"
            _insert(
                new_id, new_name, exp_owner,
                exp.get("model", "v1.0.0"),
                datetime.now().strftime("%Y-%m-%d\n%H:%M"),
                "Running", exp_desc,
            )
            show_snack(page, f"Cloned: {new_id}", p["GREEN"])
            nav("/experiments")
        except Exception as ex:
            show_snack(page, f"Clone error: {ex}", "#EF4444")

    def do_stop(_e):
        nav("/training-monitor")

    def do_report(_e):
        try:
            from views.reports import _insert_report
            _insert_report(
                f"{exp_name} - Auto Report",
                "PDF",
                exp.get("id", "EXP-AUTO"),
                exp_owner,
                "Final",
            )
            show_snack(page, "Report created.", p["GREEN"])
        except Exception as ex:
            show_snack(page, f"Error: {ex}", "#EF4444")
        nav("/reports")

    # ── Header card ──────────────────────────────────────────────────────────
    header_card = ft.Container(
        bgcolor=p["SURFACE"], border=ft.Border.all(1, p["BORDER"]),
        border_radius=12, padding=20,
        content=ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.SCIENCE_OUTLINED,
                                    color=p["GREEN"], size=20),
                    bgcolor=p["GREEN_LIGHT"], border_radius=8, padding=8),
                ft.Column([
                    ft.Text(exp_name, size=17, weight=ft.FontWeight.BOLD,
                            color=p["TEXT"]),
                    ft.Text(exp_desc, size=12, color=p["GRAY"]),
                ], spacing=2, expand=True),
                ft.OutlinedButton("Clone", icon=ft.Icons.COPY_OUTLINED,
                    style=ft.ButtonStyle(color={"": p["TEXT"]},
                                         side={"": ft.BorderSide(1, p["BORDER"])}),
                    on_click=do_clone),
                ft.OutlinedButton("Stop Training",
                    icon=ft.Icons.STOP_CIRCLE_OUTLINED,
                    style=ft.ButtonStyle(color={"": p["RED"]},
                                         side={"": ft.BorderSide(1, p["RED"])}),
                    on_click=do_stop),
                ft.FilledButton("Generate Report",
                    icon=ft.Icons.DESCRIPTION_OUTLINED,
                    style=ft.ButtonStyle(bgcolor={"": p["GREEN"]},
                                         color={"": "#FFFFFF"}),
                    on_click=do_report),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            ft.Divider(height=1, color=p["BORDER"]),
            ft.Row([
                ft.Column([
                    ft.Text("DATASET", size=10, color=p["GRAY"],
                            weight=ft.FontWeight.W_600),
                    ft.Text(exp_dataset, size=12, color=p["TEXT"])
                ], spacing=2),
                ft.Column([
                    ft.Text("CREATED BY", size=10, color=p["GRAY"],
                            weight=ft.FontWeight.W_600),
                    ft.Text(exp_owner, size=12, color=p["TEXT"])
                ], spacing=2),
                ft.Column([
                    ft.Text("CREATED AT", size=10, color=p["GRAY"],
                            weight=ft.FontWeight.W_600),
                    ft.Text(exp_created, size=12, color=p["TEXT"])
                ], spacing=2),
                ft.Column([
                    ft.Text("CURRENT STATUS", size=10, color=p["GRAY"],
                            weight=ft.FontWeight.W_600),
                    ft.Container(
                        content=ft.Text(exp_status, size=11,
                                        color=status_color,
                                        weight=ft.FontWeight.W_600),
                        bgcolor=status_bg,
                        border_radius=4,
                        padding=ft.Padding(left=8, right=8, top=2, bottom=2),
                    ),
                ], spacing=2),
                ft.Text("Last auto-refresh: 14:52:01", size=11,
                        color=p["GRAY"], expand=True,
                        text_align=ft.TextAlign.RIGHT),
            ], spacing=30),
        ], spacing=14),
    )

    # ── Performance Metrics tab ──────────────────────────────────────────────
    def _performance_metrics_tab():
        def _metric_row(name, value, updated, trend_values):
            rising = trend_values[-1] >= trend_values[0]
            color = p["GREEN"] if rising else p["RED"]
            return ft.Container(
                content=ft.Row([
                    ft.Text(name, size=13, color=p["TEXT"],
                            weight=ft.FontWeight.W_500, width=110),
                    ft.Text(value, size=13, color=color,
                            weight=ft.FontWeight.BOLD, width=80),
                    ft.Text(updated, size=12, color=p["GRAY"], expand=True),
                    _sparkline_img(trend_values, color),
                    ft.TextButton("Compare",
                        style=ft.ButtonStyle(color={"": p["GREEN"]}),
                        on_click=lambda e: nav("/compare-experiments")),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.Padding(left=4, right=4, top=12, bottom=12),
                border=ft.Border(bottom=ft.BorderSide(1, p["BORDER"])),
            )

        header = ft.Container(
            content=ft.Row([
                ft.Text("Metric Name",   size=12, color=p["GRAY"],
                        weight=ft.FontWeight.W_600, width=110),
                ft.Text("Current Value", size=12, color=p["GRAY"],
                        weight=ft.FontWeight.W_600, width=80),
                ft.Text("Last Updated",  size=12, color=p["GRAY"],
                        weight=ft.FontWeight.W_600, expand=True),
                ft.Text("Trend",         size=12, color=p["GRAY"],
                        weight=ft.FontWeight.W_600, width=84),
                ft.Text("Actions",       size=12, color=p["GRAY"],
                        weight=ft.FontWeight.W_600, width=90),
            ]),
            bgcolor=p["ROW_ALT"],
            padding=ft.Padding(left=4, right=4, top=10, bottom=10),
            border_radius=ft.BorderRadius(top_left=8, top_right=8,
                                           bottom_left=0, bottom_right=0),
        )

        acc_vals  = next((m[3] for m in metrics
                          if "ccuracy" in m[0] or "MAE" in m[0] or "Reward" in m[0]),
                         None)
        loss_vals = next((m[3] for m in metrics if "oss" in m[0]), None)

        charts = []
        if acc_vals:
            charts.append(_line_chart_widget(acc_vals, p["GREEN"], "PRIMARY ACCURACY CURVE", p))
        if loss_vals:
            charts.append(_line_chart_widget(loss_vals, p["RED"], "LOSS DECAY CURVE", p))

        return ft.Column([
            ft.Text("Real-time Metrics Tracking", size=16,
                    weight=ft.FontWeight.BOLD, color=p["TEXT"]),
            ft.Text("Visualising performance trends.",
                    size=12, color=p["GRAY"]),
            ft.Container(height=6),
            header,
            ft.Column([_metric_row(*m) for m in metrics], spacing=0),
            ft.Container(height=16),
            ft.Row(charts, spacing=24) if charts else ft.Container(),
        ], spacing=4)

    def _hyperparameters_tab():
        def _row(key, val):
            return ft.Container(
                content=ft.Row([
                    ft.Text(key, size=13, color=p["GRAY"], width=200),
                    ft.Text(val, size=13, color=p["TEXT"],
                            weight=ft.FontWeight.W_500),
                ]),
                padding=ft.Padding(left=0, right=0, top=11, bottom=11),
                border=ft.Border(bottom=ft.BorderSide(1, p["BORDER"])),
            )
        return ft.Column([
            ft.Text("Hyperparameters", size=16, weight=ft.FontWeight.BOLD,
                    color=p["TEXT"]),
            ft.Container(height=8),
            ft.Column([_row(k, v) for k, v in hyperparams], spacing=0),
        ])

    def _produced_models_tab():
        return ft.Column([
            ft.Text("Produced Models", size=16, weight=ft.FontWeight.BOLD,
                    color=p["TEXT"]),
            ft.Container(height=12),
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.INBOX_OUTLINED, size=40,
                            color=p["GRAY_LIGHT"]),
                    ft.Text("No models produced yet.", size=14,
                            color=p["GRAY"], weight=ft.FontWeight.W_500),
                    ft.Text("Models will appear here once training checkpoints are saved.",
                            size=12, color=p["GRAY_LIGHT"]),
                ], spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.Alignment(0, 0), height=180,
            ),
        ])

    selected_tab = {"v": 2}
    tab_labels = ["Produced Models", "Hyperparameters", "Performance Metrics"]

    def get_content(idx):
        if idx == 0: return _produced_models_tab()
        if idx == 1: return _hyperparameters_tab()
        return _performance_metrics_tab()

    content_area = ft.Container(content=get_content(selected_tab["v"]),
                                padding=20)
    tab_buttons = []

    def make_tab_btn(idx, label):
        def on_click(_e, i=idx):
            selected_tab["v"] = i
            for j, b in enumerate(tab_buttons):
                active = (j == i)
                b.border = ft.Border(bottom=ft.BorderSide(
                    2, p["GREEN"] if active else "transparent"))
                b.content.controls[0].color = p["GREEN"] if active else p["GRAY"]
                b.content.controls[0].weight = (ft.FontWeight.W_600
                                                if active else ft.FontWeight.W_400)
            content_area.content = get_content(i)
            page.update()

        active = (idx == selected_tab["v"])
        return ft.Container(
            content=ft.Row([ft.Text(label, size=13,
                color=p["GREEN"] if active else p["GRAY"],
                weight=ft.FontWeight.W_600 if active else ft.FontWeight.W_400)]),
            padding=ft.Padding(left=16, right=16, top=12, bottom=12),
            border=ft.Border(bottom=ft.BorderSide(
                2, p["GREEN"] if active else "transparent")),
            on_click=on_click, ink=True,
        )

    for i, lbl in enumerate(tab_labels):
        tab_buttons.append(make_tab_btn(i, lbl))

    tab_bar = ft.Container(
        content=ft.Row(tab_buttons + [ft.Container(expand=True)], spacing=0),
        border=ft.Border(bottom=ft.BorderSide(1, p["BORDER"])),
    )
    tab_card = ft.Container(
        bgcolor=p["SURFACE"], border=ft.Border.all(1, p["BORDER"]),
        border_radius=12,
        content=ft.Column([tab_bar, content_area], spacing=0),
    )

    main_content = ft.Container(
        expand=True, bgcolor=p["BG"], padding=30,
        content=ft.Column([
            ft.Row([
                ft.TextButton("Experiments",
                              style=ft.ButtonStyle(color={"": p["GREEN"]}),
                              on_click=lambda e: nav("/experiments")),
                ft.Text(" › ", color=p["GRAY"], size=13),
                ft.Text(exp_name, color=p["GRAY"], size=13),
            ], spacing=2),
            header_card,
            tab_card,
        ], spacing=16, scroll=ft.ScrollMode.AUTO, expand=True),
    )

    return page_shell(page, nav, "experiments", main_content,
                      route="/experiment-details")
