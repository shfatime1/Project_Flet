import csv
import flet as ft
import flet.canvas as cv

from views.theme import palette
from views.sidebar import page_shell, show_snack


EXPERIMENTS = [
    "ResNet50-v2-Baseline",
    "ResNet50-v2-LR-0.001",
    "ResNet50-v2-Augmented",
    "BERT-Base-SST2",
    "YOLOv8-Custom",
]

METRICS_DATA = [
    ("Accuracy",  "93.4%", "96.2%", "91.8%", True),
    ("Loss",      "0.12",  "0.08",  "0.15",  False),
    ("F1 Score",  "0.92",  "0.95",  "0.89",  True),
    ("Recall",    "0.91",  "0.94",  "0.88",  True),
]

HYPERPARAM_DATA = [
    ("Learning Rate",    "0.0001",          "0.001",           "0.0005"),
    ("Batch Size",       "32",              "32",              "64"),
    ("Optimizer",        "Adam",            "Adam",            "SGD"),
    ("Epochs",           "50",              "50",              "100"),
    ("Weight Decay",     "1e-4",            "1e-4",            "1e-5"),
    ("Base Dataset",     "ImageNet-2023-v1","ImageNet-2023-v1","ImageNet-v2-Full"),
    ("GPU Architecture", "NVIDIA A100",     "NVIDIA A100",     "NVIDIA H100"),
]


def compare_experiments_view(page: ft.Page, params, basket) -> ft.View:
    p = palette(page)
    go_to = basket["go_to"]

    # Bumping refresh counter
    refresh_count = {"v": 0}

    # ── Top buttons ────────────────────────────────────────────────────────
    def export_report(_e):
        try:
            with open("comparison_report.csv", "w", newline="", encoding="utf-8") as fp:
                w = csv.writer(fp)
                w.writerow(["Metric", "EXP 1", "EXP 2", "EXP 3", "Higher Better"])
                for m in METRICS_DATA:
                    w.writerow([m[0], m[1], m[2], m[3], "Yes" if m[4] else "No"])
                w.writerow([])
                w.writerow(["Hyperparameter", "EXP 1 (EXP-402)", "EXP 2 (EXP-405)", "EXP 3 (EXP-408)"])
                for r in HYPERPARAM_DATA:
                    w.writerow(list(r))
            show_snack(page, "comparison_report.csv saved.", p["GREEN"])
        except Exception as ex:
            show_snack(page, f"Export error: {ex}", "#EF4444")

    def share_view(_e):
        try:
            page.set_clipboard("https://aimodel.io/compare?ids=EXP-402,EXP-405,EXP-408")
            show_snack(page, "Link copied to clipboard.", p["GREEN"])
        except Exception:
            show_snack(page, "Share link: aimodel.io/compare?ids=...", p["GREEN"])

    def recalc(_e):
        refresh_count["v"] += 1
        recalc_btn.content = ft.Row(spacing=6, controls=[
            ft.Icon(ft.Icons.REFRESH, size=16, color="#FFFFFF"),
            ft.Text(f"Recalculated ({refresh_count['v']})", size=14,
                    color="#FFFFFF", weight=ft.FontWeight.W_600),
        ])
        page.update()
        show_snack(page, "Recalculated.", p["GREEN"])

    def add_baseline(_e):
        show_snack(page, "EXP 2 added to baseline.", p["GREEN"])

    def promote(_e):
        show_snack(page, "Model promoted to staging.", p["GREEN"])

    recalc_btn = ft.FilledButton(
        "Recalculate", icon=ft.Icons.REFRESH,
        style=ft.ButtonStyle(bgcolor={"": p["GREEN"]}, color={"": "#FFFFFF"}),
        on_click=recalc,
    )

    # ── Selectors ─────────────────────────────────────────────────────────
    def exp_selector(label, value):
        return ft.Column([
            ft.Row([
                ft.Text(label, size=11, color=p["MUTED"], weight=ft.FontWeight.W_600),
                ft.Container(
                    content=ft.Text("Completed", size=11, color=p["GREEN"],
                                    weight=ft.FontWeight.W_600),
                    bgcolor=p["GREEN_LIGHT"], border_radius=4,
                    padding=ft.Padding(left=6, right=6, top=2, bottom=2)),
            ], spacing=8),
            ft.Dropdown(
                value=value, text_size=13, border_radius=8,
                border_color=p["BORDER"], focused_border_color=p["GREEN"],
                color=p["TEXT"], bgcolor=p["INPUT_BG"],
                content_padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                options=[ft.DropdownOption(e) for e in EXPERIMENTS],
                on_select=lambda _e: show_snack(page, "Experiment selection updated.", p["GREEN"]),
            ),
        ], spacing=4, expand=True)

    selector_row = ft.Container(
        bgcolor=p["SURFACE"], border=ft.Border.all(1, p["BORDER"]),
        border_radius=12, padding=16,
        content=ft.Row([
            exp_selector("EXPERIMENT 1", "ResNet50-v2-Baseline"),
            exp_selector("EXPERIMENT 2", "ResNet50-v2-LR-0.001"),
            exp_selector("EXPERIMENT 3", "ResNet50-v2-Augmented"),
        ], spacing=16),
    )

    # ── Metric row ──────────────────────────────────────────────────────────
    def _metric_row(name, v1, v2, v3, higher_better):
        vals = [v1, v2, v3]
        try:
            nums = [float(x.strip("%")) for x in vals]
            best_idx = nums.index(max(nums) if higher_better else min(nums))
        except Exception:
            best_idx = 1

        def cell(val, idx):
            is_best = (idx == best_idx)
            return ft.Container(
                content=ft.Row([
                    ft.Text(val, size=14,
                            color=p["GREEN"] if is_best else p["TEXT"],
                            weight=ft.FontWeight.BOLD if is_best
                                                     else ft.FontWeight.W_500),
                    ft.Icon(ft.Icons.WORKSPACE_PREMIUM, size=12,
                            color=p["GREEN"]) if is_best else ft.Container(),
                ], spacing=4),
                expand=True,
                bgcolor=p["GREEN_SOFT"] if is_best else p["SURFACE"],
                padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                border_radius=6,
            )

        return ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.SHOW_CHART if higher_better
                            else ft.Icons.REMOVE_CIRCLE_OUTLINE,
                            size=14, color=p["GREEN"] if higher_better else p["RED"]),
                    ft.Text(name, size=13, color=p["TEXT"],
                            weight=ft.FontWeight.W_500),
                ], spacing=6, width=130),
                cell(v1, 0), cell(v2, 1), cell(v3, 2),
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=4, right=4, top=6, bottom=6),
            border=ft.Border(bottom=ft.BorderSide(1, p["BORDER"])),
        )

    metrics_section = ft.Container(
        bgcolor=p["SURFACE"], border=ft.Border.all(1, p["BORDER"]),
        border_radius=12, padding=16,
        content=ft.Column([
            ft.Text("Key Performance Metrics", size=15,
                    weight=ft.FontWeight.BOLD, color=p["TEXT"]),
            ft.Text("Direct numerical comparison of final evaluation results.",
                    size=12, color=p["MUTED"]),
            ft.Container(height=4),
            ft.Container(
                content=ft.Row([
                    ft.Container(width=138),
                    ft.Text("EXP 1", size=12, color=p["MUTED"],
                            weight=ft.FontWeight.W_600, expand=True),
                    ft.Text("EXP 2", size=12, color=p["MUTED"],
                            weight=ft.FontWeight.W_600, expand=True),
                    ft.Text("EXP 3", size=12, color=p["MUTED"],
                            weight=ft.FontWeight.W_600, expand=True),
                ], spacing=8),
                bgcolor=p["ROW_ALT"], border_radius=6,
                padding=ft.Padding(left=4, right=4, top=8, bottom=8),
            ),
            ft.Column([_metric_row(*m) for m in METRICS_DATA], spacing=0),
        ], spacing=8),
    )

    # ── Chart ───────────────────────────────────────────────────────────────
    def _accuracy_curves_chart():
        exp1 = [(30,185),(65,165),(100,140),(140,112),(185,88),(230,68),
                (275,54),(320,44),(365,38),(410,34)]
        exp2 = [(30,190),(65,168),(100,138),(140,106),(185,79),(230,56),
                (275,40),(320,28),(365,22),(410,18)]
        exp3 = [(30,180),(65,162),(100,144),(140,118),(185,96),(230,78),
                (275,64),(320,54),(365,48),(410,44)]

        shapes = []
        for pts, color in [(exp1, p["RED"]), (exp2, p["GREEN"]),
                           (exp3, "#374151" if p["BG"] != "#0F172A" else "#94A3B8")]:
            for i in range(len(pts) - 1):
                shapes.append(cv.Line(pts[i][0], pts[i][1],
                                       pts[i+1][0], pts[i+1][1],
                                       ft.Paint(color=color, stroke_width=2.5)))
            for x, y in pts:
                shapes.append(cv.Circle(x, y, 4,
                                         ft.Paint(color=color,
                                                  style=ft.PaintingStyle.FILL)))
        for y in [40, 80, 120, 160, 200]:
            shapes.append(cv.Line(20, y, 430, y,
                                   ft.Paint(color=p["BORDER"], stroke_width=1)))
        return cv.Canvas(shapes=shapes, width=450, height=220)

    chart_section = ft.Container(
        bgcolor=p["SURFACE"], border=ft.Border.all(1, p["BORDER"]),
        border_radius=12, padding=16, expand=True,
        content=ft.Column([
            ft.Row([
                ft.Text("Accuracy Over Time", size=15,
                        weight=ft.FontWeight.BOLD, color=p["TEXT"], expand=True),
                ft.Container(
                    content=ft.Text("Val Accuracy", size=11, color=p["GREEN"],
                                    weight=ft.FontWeight.W_600),
                    bgcolor=p["GREEN_LIGHT"], border_radius=4,
                    padding=ft.Padding(left=8, right=8, top=3, bottom=3)),
                ft.Container(
                    content=ft.Text("Accuracy", size=11, color=p["TEXT"],
                                    weight=ft.FontWeight.W_600),
                    border=ft.Border.all(1, p["BORDER"]), border_radius=4,
                    padding=ft.Padding(left=8, right=8, top=3, bottom=3)),
            ]),
            ft.Text("Comparing validation accuracy convergence across epochs.",
                    size=12, color=p["MUTED"]),
            ft.Container(height=6),
            _accuracy_curves_chart(),
            ft.Text("Epochs", size=11, color=p["MUTED"],
                    text_align=ft.TextAlign.CENTER),
            ft.Row([
                ft.Row([ft.Container(width=10, height=3, bgcolor=p["RED"]),
                        ft.Text("ResNet50-v2-Baseline", size=11, color=p["TEXT"])],
                       spacing=6),
                ft.Row([ft.Container(width=10, height=3, bgcolor=p["GREEN"]),
                        ft.Text("ResNet50-v2-LR-0.001", size=11, color=p["TEXT"])],
                       spacing=6),
                ft.Row([ft.Container(width=10, height=3, bgcolor=p["MUTED"]),
                        ft.Text("ResNet50-v2-Augmented", size=11, color=p["TEXT"])],
                       spacing=6),
            ], spacing=20, alignment=ft.MainAxisAlignment.CENTER),
        ], spacing=8),
    )

    top_row = ft.Row([metrics_section, chart_section], spacing=16,
                     vertical_alignment=ft.CrossAxisAlignment.START)

    # ── Hyperparams ─────────────────────────────────────────────────────────
    def _hyperparam_row(param, v1, v2, v3, last=False):
        def cell(val, highlight=False):
            return ft.Container(
                content=ft.Text(val, size=13,
                                color=p["BLUE"] if highlight else p["TEXT"],
                                weight=ft.FontWeight.W_600 if highlight
                                                          else ft.FontWeight.W_400),
                expand=True,
            )
        return ft.Container(
            content=ft.Row([
                ft.Text(param, size=13, color=p["TEXT"], width=160),
                cell(v1), cell(v2), cell(v3, v3 != v1),
            ], spacing=8),
            padding=ft.Padding(left=4, right=4, top=11, bottom=11),
            border=ft.Border(bottom=ft.BorderSide(0 if last else 1, p["BORDER"])),
        )

    hyperparam_section = ft.Container(
        bgcolor=p["SURFACE"], border=ft.Border.all(1, p["BORDER"]),
        border_radius=12, padding=16,
        content=ft.Column([
            ft.Text("Configuration & Hyperparameters", size=15,
                    weight=ft.FontWeight.BOLD, color=p["TEXT"]),
            ft.Text("Comparison of training parameters and environmental settings.",
                    size=12, color=p["MUTED"]),
            ft.Container(height=4),
            ft.Container(
                content=ft.Row([
                    ft.Container(width=168),
                    ft.Text("Experiment 1 (EXP-402)", size=12, color=p["MUTED"],
                            weight=ft.FontWeight.W_600, expand=True),
                    ft.Text("Experiment 2 (EXP-405)", size=12, color=p["MUTED"],
                            weight=ft.FontWeight.W_600, expand=True),
                    ft.Text("Experiment 3 (EXP-408)", size=12, color=p["MUTED"],
                            weight=ft.FontWeight.W_600, expand=True),
                ], spacing=8),
                bgcolor=p["ROW_ALT"], border_radius=6,
                padding=ft.Padding(left=4, right=4, top=8, bottom=8),
            ),
            ft.Column([
                _hyperparam_row(*row, last=(i == len(HYPERPARAM_DATA) - 1))
                for i, row in enumerate(HYPERPARAM_DATA)
            ], spacing=0),
        ], spacing=8),
    )

    rec_banner = ft.Container(
        bgcolor=p["SURFACE"], border=ft.Border.all(1, p["BORDER"]),
        border_radius=12, padding=16,
        content=ft.Row([
            ft.Container(
                content=ft.Icon(ft.Icons.TRENDING_UP, size=20, color=p["GREEN"]),
                bgcolor=p["GREEN_LIGHT"], border_radius=8, padding=8),
            ft.Column([
                ft.Text("Comparison Recommendation", size=13,
                        weight=ft.FontWeight.BOLD, color=p["TEXT"]),
                ft.Text("Experiment 2 shows 3.2% higher accuracy with 30% faster convergence.",
                        size=12, color=p["MUTED"]),
            ], spacing=2, expand=True),
            ft.OutlinedButton("Add to Baseline",
                style=ft.ButtonStyle(color={"": p["TEXT"]},
                                     side={"": ft.BorderSide(1, p["BORDER"])}),
                on_click=add_baseline),
            ft.FilledButton("Promote Model to Staging",
                style=ft.ButtonStyle(bgcolor={"": p["GREEN"]}, color={"": "#FFFFFF"}),
                on_click=promote),
        ], spacing=14, vertical_alignment=ft.CrossAxisAlignment.CENTER),
    )

    main_content = ft.Container(
        expand=True, padding=28, bgcolor=p["BG"],
        content=ft.Column([
            ft.Row([
                ft.TextButton("< METRICS ANALYSIS",
                              style=ft.ButtonStyle(color={"": p["MUTED"]}),
                              on_click=lambda e: go_to("/metrics")),
            ]),
            ft.Row([
                ft.Column([
                    ft.Text("Compare Experiments", size=26,
                            weight=ft.FontWeight.BOLD, color=p["TEXT"]),
                    ft.Text("Analyzing and bench-marking performance metrics across training runs.",
                            size=13, color=p["MUTED"]),
                ], expand=True),
                ft.OutlinedButton("Export Report", icon=ft.Icons.DOWNLOAD,
                    style=ft.ButtonStyle(color={"": p["TEXT"]},
                                         side={"": ft.BorderSide(1, p["BORDER"])}),
                    on_click=export_report),
                ft.OutlinedButton("Share View", icon=ft.Icons.SHARE,
                    style=ft.ButtonStyle(color={"": p["TEXT"]},
                                         side={"": ft.BorderSide(1, p["BORDER"])}),
                    on_click=share_view),
                recalc_btn,
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            selector_row,
            top_row,
            hyperparam_section,
            rec_banner,
        ], spacing=16, scroll=ft.ScrollMode.AUTO, expand=True),
    )

    return page_shell(page, go_to, "metrics", main_content,
                      route="/compare-experiments")
