"""
training_monitor.py - Real-time training console.
Stop Training and Clear Console buttons functional.
Light/dark theme is supported.
"""

import flet as ft

from views.theme import palette
from views.sidebar import page_shell, show_snack


CONSOLE_LINES = [
    ("[14:00:01]", "INFO", "Initialising training environment..."),
    ("[14:00:05]", "INFO", "Loading dataset: ImageNet-Subset-2023 (1.2 TB)"),
    ("[14:00:15]", "INFO", "Hyperparameters synced: lr=0.001, batch_size=64, optimizer=Adam"),
    ("[14:01:00]", "INFO", "Epoch [1/50] started."),
    ("[14:05:22]", "INFO", "Step [100/704] – loss: 2.4512 – accuracy: 0.1245"),
    ("[14:10:45]", "INFO", "Step [200/704] – loss: 1.9842 – accuracy: 0.2841"),
    ("[14:20:30]", "INFO", "Step [300/704] – loss: 1.4522 – accuracy: 0.4512"),
    ("[14:25:55]", "INFO", "Step [400/704] – loss: 1.1205 – accuracy: 0.5892"),
    ("[14:31:15]", "INFO", "Step [500/704] – loss: 0.9845 – accuracy: 0.6421"),
    ("[14:36:40]", "INFO", "Step [600/704] – loss: 0.8241 – accuracy: 0.7102"),
    ("[14:42:05]", "INFO", "Step [700/704] – loss: 0.7512 – accuracy: 0.7485"),
    ("[14:45:10]", "INFO", "Checkpoint saved: /models/resnet50_v2/checkpoints/epoch_1.pt"),
]


def training_monitor_view(page: ft.Page, params, basket) -> ft.View:
    p = palette(page)
    nav = basket.get("go_to", page.push_route)

    is_training = {"v": True}
    cleared = {"v": False}

    # Console rows
    def make_console_rows():
        if cleared["v"]:
            return [ft.Row([
                ft.Text("Console cleared.", size=11, color="#94A3B8",
                        font_family="monospace", expand=True,
                        text_align=ft.TextAlign.CENTER),
            ])]
        return [
            ft.Row([
                ft.Text(ts,  size=11, color="#6EE7B7", font_family="monospace", width=90),
                ft.Text(lvl, size=11, color="#86EFAC", font_family="monospace", width=40),
                ft.Text(msg, size=11, color="#D1FAE5", font_family="monospace",
                        expand=True, selectable=True),
            ], spacing=6)
            for ts, lvl, msg in CONSOLE_LINES
        ]

    console_inner = ft.Column(make_console_rows(), spacing=3,
                              scroll=ft.ScrollMode.AUTO)

    # ── Top buttons ────────────────────────────────────────────────────────
    status_pill = ft.Container(
        content=ft.Text("Running", size=11, color=p["GREEN"],
                        weight=ft.FontWeight.W_600),
        bgcolor=p["GREEN_LIGHT"], border_radius=4,
        padding=ft.Padding(left=8, right=8, top=3, bottom=3),
    )
    streaming_pill = ft.Container(
        content=ft.Text("● STREAMING LIVE", size=10,
                        color=p["GREEN"], weight=ft.FontWeight.W_600),
        border=ft.Border.all(1, p["GREEN"]), border_radius=4,
        padding=ft.Padding(left=6, right=6, top=2, bottom=2),
    )
    stop_btn = ft.FilledButton(
        "Stop Training", icon=ft.Icons.STOP_ROUNDED,
        style=ft.ButtonStyle(bgcolor={"": p["RED"]}, color={"": "#FFFFFF"}),
    )

    def stop_clicked(_e):
        is_training["v"] = False
        # Visual update
        status_pill.content.value = "Stopped"
        status_pill.content.color = p["MUTED"]
        status_pill.bgcolor = p["GRAY_SOFT"]
        streaming_pill.content.value = "● STOPPED"
        streaming_pill.content.color = p["MUTED"]
        streaming_pill.border = ft.Border.all(1, p["MUTED"])
        stop_btn.content = ft.Row(spacing=6, controls=[
            ft.Icon(ft.Icons.STOP_ROUNDED, size=16, color="#FFFFFF"),
            ft.Text("Training Stopped", size=14, color="#FFFFFF",
                    weight=ft.FontWeight.W_600),
        ])
        stop_btn.disabled = True
        page.update()
        show_snack(page, "Training stopped.", p["RED"])

    stop_btn.on_click = stop_clicked

    def clear_console(_e):
        cleared["v"] = True
        console_inner.controls.clear()
        console_inner.controls.extend(make_console_rows())
        page.update()
        show_snack(page, "Console cleared.", p["GREEN"])

    # ── Progress card ───────────────────────────────────────────────────────
    progress_card = ft.Container(
        bgcolor=p["SURFACE"], border=ft.Border.all(1, p["BORDER"]),
        border_radius=12, padding=20,
        content=ft.Row([
            ft.Column([
                ft.Row([
                    ft.Text("ResNet-50 Fine-Tuning", size=16,
                            weight=ft.FontWeight.BOLD, color=p["TEXT"]),
                    status_pill,
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Text("Experiment ID: EXP-2023-904-B", size=12, color=p["GRAY"]),
                ft.Container(height=10),
                ft.Row([
                    ft.Text("Overall Progress", size=12, color=p["GRAY"], expand=True),
                    ft.Text("Epoch 18 / 50", size=12, color=p["TEXT"]),
                ]),
                ft.ProgressBar(value=0.64, color=p["GREEN"], bgcolor=p["BORDER"],
                               height=8, border_radius=4),
                ft.Row([
                    ft.Text("Current Phase: Optimisation Phase 2",
                            size=11, color=p["GRAY"], expand=True),
                    ft.Text("Est. Remaining: 4 h 12 m", size=11, color=p["GRAY"]),
                ]),
            ], spacing=6, expand=True),
            ft.Container(width=1, bgcolor=p["BORDER"], height=100),
            ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.CALENDAR_TODAY_OUTLINED, size=14, color=p["GRAY"]),
                    ft.Column([
                        ft.Text("STARTED AT", size=10, color=p["GRAY"],
                                weight=ft.FontWeight.W_600),
                        ft.Text("Nov 24, 2023  14:00:01", size=12, color=p["TEXT"]),
                    ], spacing=1),
                ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Row([
                    ft.Icon(ft.Icons.TIMER_OUTLINED, size=14, color=p["GRAY"]),
                    ft.Column([
                        ft.Text("ELAPSED TIME", size=10, color=p["GRAY"],
                                weight=ft.FontWeight.W_600),
                        ft.Text("01 h 45 m 22 s", size=12, color=p["TEXT"]),
                    ], spacing=1),
                ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Row([
                    ft.Icon(ft.Icons.STORAGE_OUTLINED, size=14, color=p["GRAY"]),
                    ft.Column([
                        ft.Text("DATASET", size=10, color=p["GRAY"],
                                weight=ft.FontWeight.W_600),
                        ft.Text("ImageNet-Subset-2023", size=12, color=p["TEXT"]),
                    ], spacing=1),
                ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.TextButton(
                    "Go to Experiment Details  ↗",
                    style=ft.ButtonStyle(color={"": p["GREEN"]}),
                    on_click=lambda e: nav("/experiment-details"),
                ),
            ], spacing=10, width=210),
        ], spacing=20),
    )

    # ── Stat row ────────────────────────────────────────────────────────────
    def _stat_card(label, value, sub, badge_text=None, badge_color=None):
        badge = ft.Container()
        if badge_text:
            badge = ft.Container(
                content=ft.Text(badge_text, size=10, color="#FFFFFF",
                                weight=ft.FontWeight.W_700),
                bgcolor=badge_color or p["ORANGE"],
                border_radius=4,
                padding=ft.Padding(left=6, right=6, top=2, bottom=2),
            )
        return ft.Container(
            bgcolor=p["SURFACE"], border=ft.Border.all(1, p["BORDER"]),
            border_radius=12, padding=18, expand=True,
            content=ft.Column([
                ft.Text(label, size=10, color=p["GRAY"], weight=ft.FontWeight.W_600),
                ft.Row([
                    ft.Text(value, size=22, weight=ft.FontWeight.BOLD, color=p["TEXT"]),
                    ft.Text(sub, size=11, color=p["GRAY"]) if sub else ft.Container(),
                    badge,
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
            ], spacing=4),
        )

    stat_row = ft.Row([
        _stat_card("GPU UTILIZATION",     "88.4%",  "Tesla V100 (Node-04)"),
        _stat_card("CURRENT LOSS",        "0.6942", "-0.0571 vs prev epoch",
                   "IMPROVEMENT", p["GREEN"]),
        _stat_card("VALIDATION ACCURACY", "78.12%", "+2.1% from start",
                   "DEGRADATION", p["RED"]),
    ], spacing=12)

    # ── Console ─────────────────────────────────────────────────────────────
    console_card = ft.Container(
        bgcolor=p["CONSOLE_PANEL"], border_radius=12, padding=16,
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.TERMINAL_ROUNDED, size=16, color=p["GREEN"]),
                ft.Text("Training Console Output", size=14,
                        weight=ft.FontWeight.BOLD, color="#FFFFFF", expand=True),
                streaming_pill,
                ft.TextButton("Clear Console",
                              style=ft.ButtonStyle(color={"": p["GRAY"]}),
                              on_click=clear_console),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(
                content=console_inner,
                height=210, bgcolor=p["CONSOLE_BG"],
                border_radius=8, padding=12,
            ),
            ft.Row([
                ft.Row([
                    ft.Container(width=8, height=8, bgcolor=p["GREEN"], border_radius=4),
                    ft.Text("Node Connected: worker-gpu-04", size=11, color=p["GRAY"]),
                    ft.Text("⊙  Auto-scrolling enabled", size=11, color=p["GRAY"]),
                ], spacing=8),
                ft.Text("Log Size: 2.4 MB", size=11, color=p["GRAY"]),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ], spacing=10),
    )

    # ── Notice ──────────────────────────────────────────────────────────────
    env_notice = ft.Container(
        bgcolor=p["ORANGE_LIGHT"], border=ft.Border.all(1, "#FDE68A"),
        border_radius=10, padding=16,
        content=ft.Row([
            ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, size=18, color=p["ORANGE"]),
            ft.Column([
                ft.Text("Environmental Notice", size=13,
                        weight=ft.FontWeight.BOLD, color=p["TEXT"]),
                ft.Text("Training cluster is currently experiencing high demand. "
                        "Automatic checkpoints are being written to secondary storage. "
                        "GPU temperature is monitored; throttling will occur if "
                        "Node-04 exceeds 85 °C.",
                        size=12, color=p["TEXT"], expand=True),
            ], spacing=2, expand=True),
        ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.START),
    )

    main_content = ft.Container(
        expand=True, bgcolor=p["BG"], padding=30,
        content=ft.Column([
            ft.Row([
                ft.TextButton("Experiments",
                              style=ft.ButtonStyle(color={"": p["GREEN"]}),
                              on_click=lambda e: nav("/experiments")),
                ft.Text(" › ", color=p["GRAY"], size=13),
                ft.TextButton("Exp-ResNet50-ImageNet-FineTune",
                              style=ft.ButtonStyle(color={"": p["GREEN"]}),
                              on_click=lambda e: nav("/experiment-details")),
                ft.Text(" › ", color=p["GRAY"], size=13),
                ft.Text("Training Monitor", color=p["GRAY"], size=13),
            ], spacing=2),
            ft.Row([
                ft.Text("Training Monitor", size=28,
                        weight=ft.FontWeight.BOLD, color=p["TEXT"], expand=True),
                ft.OutlinedButton("View Metrics",
                    icon=ft.Icons.BAR_CHART_OUTLINED,
                    style=ft.ButtonStyle(color={"": p["TEXT"]},
                                         side={"": ft.BorderSide(1, p["BORDER"])}),
                    on_click=lambda e: nav("/metrics")),
                stop_btn,
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            ft.Divider(height=1, color=p["BORDER"]),
            progress_card,
            stat_row,
            console_card,
            env_notice,
        ], spacing=16, scroll=ft.ScrollMode.AUTO, expand=True),
    )

    return page_shell(page, nav, "experiments", main_content,
                      route="/training-monitor")
