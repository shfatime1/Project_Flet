"""
metrics.py - Real-time metric logs.
• Each log can be clicked - the chart on the right updates.
• Live search filtering.
• Export CSV writes a file.
"""

import csv
import flet as ft
import flet.canvas as cv

from views.theme import palette
from views.sidebar import page_shell, show_snack


# ── Test data ───────────────────────────────────────────────────────────
LOGS = [
    # (name, value, trend, model_id, model_name, rising_or_None, time, history)
    ("Validation Accuracy", "0.942", "RISING",  "M-702", "ResNet-50-v2",     True,
     "14:32:10",
     [(0,0.10),(10,0.28),(20,0.45),(30,0.59),(40,0.71),(50,0.79),(60,0.85),
      (70,0.89),(80,0.91),(90,0.93),(100,0.942)]),
    ("Training Loss",       "0.124", "FALLING",  "M-702", "ResNet-50-v2",     False,
     "14:31:55",
     [(0,2.45),(10,1.98),(20,1.45),(30,1.12),(40,0.85),(50,0.62),(60,0.43),
      (70,0.30),(80,0.21),(90,0.15),(100,0.124)]),
    ("F1 Score",            "0.891", "STABLE",   "M-698", "EfficientNet-B0",  None,
     "14:30:22",
     [(0,0.80),(10,0.83),(20,0.85),(30,0.87),(40,0.88),(50,0.89),(60,0.89),
      (70,0.89),(80,0.89),(90,0.891),(100,0.891)]),
    ("Recall",              "0.875", "RISING",   "M-702", "ResNet-50-v2",     True,
     "14:28:45",
     [(0,0.20),(10,0.35),(20,0.48),(30,0.59),(40,0.68),(50,0.74),(60,0.79),
      (70,0.83),(80,0.85),(90,0.87),(100,0.875)]),
    ("Precision",           "0.912", "STABLE",   "M-698", "EfficientNet-B0",  None,
     "14:25:12",
     [(0,0.85),(10,0.87),(20,0.89),(30,0.90),(40,0.905),(50,0.910),(60,0.911),
      (70,0.912),(80,0.912),(90,0.912),(100,0.912)]),
    ("Mean IoU",            "0.756", "FALLING",  "M-654", "UNet-v3",          False,
     "14:20:01",
     [(0,0.92),(10,0.88),(20,0.84),(30,0.81),(40,0.79),(50,0.77),(60,0.765),
      (70,0.76),(80,0.758),(90,0.756),(100,0.756)]),
    ("Validation Accuracy", "0.938", "RISING",   "M-702", "ResNet-50-v2",     True,
     "14:15:30",
     [(0,0.12),(10,0.30),(20,0.46),(30,0.58),(40,0.69),(50,0.78),(60,0.84),
      (70,0.88),(80,0.91),(90,0.93),(100,0.938)]),
    ("Training Loss",       "0.131", "FALLING",  "M-702", "ResNet-50-v2",     False,
     "14:10:22",
     [(0,2.50),(10,2.05),(20,1.50),(30,1.18),(40,0.90),(50,0.65),(60,0.45),
      (70,0.32),(80,0.22),(90,0.16),(100,0.131)]),
]


def metrics_view(page: ft.Page, params, basket) -> ft.View:
    p = palette(page)
    go_to = basket["go_to"]

    # ── State ───────────────────────────────────────────────────────────────
    selected = {"v": 0}  # cari log indeksi
    search_q   = {"v": (page.data.get("search_query", "") if isinstance(page.data, dict) else "") or ""}
    date_filter = {"v": "All Time"}   # Last 24h | Last 7 Days | Last 30 Days | All Time
    filtered_idx = list(range(len(LOGS)))  # filtered log indices

    # Map each log to a "minutes ago" bucket using its index as a proxy
    # LOGS[0] = most recent (14:32), LOGS[-1] = oldest (14:10)
    # We treat index 0-1 as last 24h, 0-3 as last 7 days, 0-5 as last 30 days, all = all
    _DATE_IDX_MAP = {
        "Last 24h":   set(range(0, 2)),
        "Last 7 Days": set(range(0, 4)),
        "Last 30 Days": set(range(0, 6)),
        "All Time":    set(range(len(LOGS))),
    }

    # ── Helper ──────────────────────────────────────────────────────────────
    def _val_color(rising):
        if rising is True:  return p["GREEN"]
        if rising is False: return p["RED"]
        return p["MUTED"]

    def _trend(t):
        if t == "RISING":
            return ft.Text("↑ RISING",  size=11, color=p["GREEN"], weight=ft.FontWeight.W_600)
        if t == "FALLING":
            return ft.Text("↓ FALLING", size=11, color=p["RED"],   weight=ft.FontWeight.W_600)
        return ft.Text("→ STABLE",      size=11, color=p["MUTED"], weight=ft.FontWeight.W_600)

    # ── Chart canvas ────────────────────────────────────────────────────────
    chart_canvas = cv.Canvas(shapes=[], width=440, height=210)
    chart_title  = ft.Text("Validation Accuracy", size=16,
                           weight=ft.FontWeight.BOLD, color=p["TEXT"])
    chart_value  = ft.Text("0.942", size=22, color=p["GREEN"],
                           weight=ft.FontWeight.BOLD)
    chart_subtitle = ft.Text("Showing history for ResNet-50-v2",
                             size=12, color=p["MUTED"])
    min_text  = ft.Text("0.10", size=18, weight=ft.FontWeight.BOLD, color=p["TEXT"])
    max_text  = ft.Text("0.94", size=18, weight=ft.FontWeight.BOLD, color=p["GREEN"])
    stab_text = ft.Text("High", size=16, weight=ft.FontWeight.BOLD, color=p["TEXT"])

    def _draw_chart(idx):
        log = LOGS[idx]
        name, value, trend, mid, mname, rising, ts, history = log

        chart_title.value = name
        chart_value.value = value
        chart_value.color = _val_color(rising)
        chart_subtitle.value = f"Showing history for {mname}"

        xs = [pt[0] for pt in history]
        ys = [pt[1] for pt in history]
        if not ys:
            chart_canvas.shapes = []
            min_text.value = "—"
            max_text.value = "—"
            return

        mn, mx = min(ys), max(ys)
        rng = (mx - mn) if mx != mn else 1e-9

        # Fill canvas (440x210) in px
        W, H = 440, 210
        pad_l, pad_r = 20, 20
        pad_t, pad_b = 20, 30
        pw = W - pad_l - pad_r
        ph = H - pad_t - pad_b

        x_min, x_max = min(xs), max(xs)
        x_range = (x_max - x_min) if x_max != x_min else 1

        pts = []
        for x, y in history:
            px = pad_l + ((x - x_min) / x_range) * pw
            py = pad_t + (1 - (y - mn) / rng) * ph
            pts.append((px, py))

        color = _val_color(rising) if rising is not None else p["MUTED"]
        shapes = []

        # Grid lines
        for k in range(5):
            gy = pad_t + (k / 4) * ph
            shapes.append(cv.Line(pad_l, gy, W - pad_r, gy,
                                   ft.Paint(color=p["BORDER"], stroke_width=1)))

        # Polylines
        for i in range(len(pts) - 1):
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
            shapes.append(cv.Line(x1, y1, x2, y2,
                                   ft.Paint(color=color, stroke_width=2.5)))
        # Points
        for x, y in pts:
            shapes.append(cv.Circle(x, y, 4,
                                     ft.Paint(color=color,
                                              style=ft.PaintingStyle.FILL)))

        chart_canvas.shapes = shapes

        # Stat panels
        min_text.value = f"{mn:.3f}"
        max_text.value = f"{mx:.3f}"
        max_text.color = color
        # Determine stability based on the log's trend
        if trend == "STABLE":
            stab_text.value = "High"
        elif trend == "RISING":
            stab_text.value = "Improving"
        else:
            stab_text.value = "Declining"

    # ── Log list ────────────────────────────────────────────────────────
    log_items_col = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, height=400)
    entries_text = ft.Text("8 entries", size=11, color=p["MUTED"])

    def _make_log_item(real_idx):
        name, value, trend, mid, mname, rising, ts, _ = LOGS[real_idx]
        is_sel = (selected["v"] == real_idx)
        bg  = p["GREEN_SOFT"] if is_sel else p["SURFACE"]
        bdc = p["GREEN"]      if is_sel else p["BORDER"]

        def on_click(_e, idx=real_idx):
            selected["v"] = idx
            _draw_chart(idx)
            _rebuild_logs()

        return ft.Container(
            on_click=on_click, ink=True,
            content=ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Text(name, size=13, color=p["TEXT"],
                                weight=ft.FontWeight.W_600, expand=True),
                        ft.Row([
                            ft.Icon(ft.Icons.ACCESS_TIME, size=11, color=p["MUTED"]),
                            ft.Text(ts, size=11, color=p["MUTED"]),
                        ], spacing=3,
                           vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ], spacing=1, expand=True),
                    ft.Column([
                        ft.Text(value, size=14, color=_val_color(rising),
                                weight=ft.FontWeight.BOLD),
                        _trend(trend),
                    ], spacing=1,
                       horizontal_alignment=ft.CrossAxisAlignment.END),
                ]),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.MEMORY_OUTLINED, size=11, color=p["MUTED"]),
                        ft.Text(f"{mid}  ·  {mname}", size=11, color=p["MUTED"]),
                    ], spacing=4,
                       vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=p["ROW_ALT"], border_radius=4,
                    padding=ft.Padding(left=6, right=6, top=3, bottom=3),
                ),
            ], spacing=6),
            bgcolor=bg, border=ft.Border.all(1, bdc),
            border_radius=8, padding=12,
        )

    def _apply_filter():
        q      = (search_q["v"] or "").lower().strip()
        d_set  = _DATE_IDX_MAP.get(date_filter["v"], set(range(len(LOGS))))
        out = []
        for i, log in enumerate(LOGS):
            if i not in d_set:
                continue
            name, value, trend, mid, mname, *_ = log
            hay = f"{name} {value} {trend} {mid} {mname}".lower()
            if q and q not in hay:
                continue
            out.append(i)
        return out

    def _rebuild_logs():
        idxs = _apply_filter()
        log_items_col.controls.clear()
        for i in idxs:
            log_items_col.controls.append(_make_log_item(i))
        entries_text.value = f"{len(idxs)} entries"
        try:
            page.update()
        except Exception:
            pass

    # ── Initial chart ─────────────────────────────────────────────────────────
    _draw_chart(0)
    _rebuild_logs()

    # ── Filter bar (search + Compare + Export) ──────────────────────────────
    def on_search_change(e):
        search_q["v"] = e.control.value or ""
        _rebuild_logs()

    if isinstance(page.data, dict):
        def header_cb(value: str):
            search_q["v"] = value or ""
            search_input.value = value or ""
            try:
                search_input.update()
            except Exception:
                pass
            _rebuild_logs()
        page.data["on_header_search"] = header_cb

    search_input = ft.TextField(
        value=search_q["v"],
        hint_text="Search metric logs...",
        hint_style=ft.TextStyle(color=p["MUTED"], size=13),
        border=ft.InputBorder.NONE, height=36, text_size=13, expand=True,
        color=p["TEXT"],
        bgcolor="transparent",
        content_padding=ft.Padding(left=6, right=6, top=0, bottom=0),
        on_change=on_search_change,
    )

    def export_csv(_e):
        try:
            with open("metrics_export.csv", "w", newline="", encoding="utf-8") as fp:
                w = csv.writer(fp)
                w.writerow(["Metric", "Value", "Trend", "Model ID", "Model", "Time"])
                for i in _apply_filter():
                    name, value, trend, mid, mname, _, ts, _ = LOGS[i]
                    w.writerow([name, value, trend, mid, mname, ts])
            show_snack(page, "metrics_export.csv saved.", p["GREEN"])
        except Exception as ex:
            show_snack(page, f"Export error: {ex}", "#EF4444")

    date_label = ft.Text("All Time", size=13, color=p["TEXT"])

    filter_bar = ft.Row([
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.SEARCH, size=16, color=p["MUTED"]),
                search_input,
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            border=ft.Border.all(1, p["BORDER"]), border_radius=8,
            padding=ft.Padding(left=10, right=0, top=0, bottom=0),
            height=40, bgcolor=p["INPUT_BG"], expand=True,
        ),
        ft.Container(
            bgcolor=p["INPUT_BG"],
            border=ft.Border.all(1, p["BORDER"]),
            border_radius=8,
            padding=ft.Padding(left=10, right=6, top=4, bottom=4),
            content=ft.PopupMenuButton(
                tooltip="",
                content=ft.Row([
                    ft.Icon(ft.Icons.CALENDAR_TODAY, size=14, color=p["MUTED"]),
                    date_label,
                    ft.Icon(ft.Icons.ARROW_DROP_DOWN, size=18, color=p["MUTED"]),
                ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                items=[
                    ft.PopupMenuItem(
                        content=ft.Text(opt, size=13),
                        on_click=lambda e, o=opt: (
                            date_filter.__setitem__("v", o),
                            setattr(date_label, "value", o),
                            date_label.update(),
                            _rebuild_logs(),
                        ),
                    )
                    for opt in ["Last 24h", "Last 7 Days", "Last 30 Days", "All Time"]
                ],
            ),
        ),
        ft.IconButton(ft.Icons.FILTER_LIST, icon_color=p["MUTED"],
                      tooltip="Filters",
                      on_click=lambda _e: show_snack(page, "Filter panel.", p["GREEN"])),
        ft.Container(expand=True),
        ft.OutlinedButton("Compare Experiments", icon=ft.Icons.COMPARE_ARROWS,
            style=ft.ButtonStyle(color={"": p["GREEN"]},
                                 side={"": ft.BorderSide(1, p["GREEN"])}),
            on_click=lambda e: go_to("/compare-experiments")),
        ft.FilledButton("Export CSV", icon=ft.Icons.DOWNLOAD,
            style=ft.ButtonStyle(bgcolor={"": p["GREEN"]}, color={"": "#FFFFFF"}),
            on_click=export_csv),
    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    # ── Log panel ──────────────────────────────────────────────────────────
    log_panel = ft.Container(
        bgcolor=p["SURFACE"], border=ft.Border.all(1, p["BORDER"]),
        border_radius=12, padding=16, width=340,
        content=ft.Column([
            ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.SHOW_CHART, size=14, color=p["GREEN"]),
                    ft.Text("Latest Logs", size=14, weight=ft.FontWeight.BOLD,
                            color=p["TEXT"]),
                ], spacing=6, expand=True),
                ft.Container(
                    content=entries_text,
                    bgcolor=p["ROW_ALT"], border_radius=10,
                    padding=ft.Padding(left=8, right=8, top=3, bottom=3)),
            ]),
            log_items_col,
            ft.TextButton("View More Logs →",
                          style=ft.ButtonStyle(color={"": p["GREEN"]}),
                          on_click=lambda _e: show_snack(page, "Viewing all logs.", p["GREEN"])),
        ], spacing=10),
    )

    # ── Chart panel ────────────────────────────────────────────────────────
    chart_panel = ft.Container(
        bgcolor=p["SURFACE"], border=ft.Border.all(1, p["BORDER"]),
        border_radius=12, padding=20, expand=True,
        content=ft.Column([
            ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.TRENDING_UP, size=16, color=p["GREEN"]),
                    chart_title,
                ], spacing=6, expand=True),
                chart_value,
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            chart_subtitle,
            ft.Container(height=6),
            chart_canvas,
            ft.Row([
                ft.Container(width=10, height=10, bgcolor=p["GREEN"], border_radius=5),
                ft.Text("Metric Value", size=12, color=p["TEXT"]),
            ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(height=1, color=p["BORDER"]),
            ft.Row([
                ft.Column([
                    ft.Text("MIN VALUE", size=10, color=p["MUTED"],
                            weight=ft.FontWeight.W_600),
                    min_text,
                ], expand=True,
                   horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(width=1, bgcolor=p["BORDER"], height=40),
                ft.Column([
                    ft.Text("MAX VALUE", size=10, color=p["MUTED"],
                            weight=ft.FontWeight.W_600),
                    max_text,
                ], expand=True,
                   horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(width=1, bgcolor=p["BORDER"], height=40),
                ft.Column([
                    ft.Text("STABILITY", size=10, color=p["MUTED"],
                            weight=ft.FontWeight.W_600),
                    ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=16,
                                color=p["GREEN"]),
                        stab_text,
                    ], spacing=4,
                       vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ], expand=True,
                   horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ]),
        ], spacing=8),
    )

    main_content = ft.Container(
        expand=True, padding=28, bgcolor=p["BG"],
        content=ft.Column([
            ft.Row([ft.Column([
                ft.Text("Performance Metrics", size=26,
                        weight=ft.FontWeight.BOLD, color=p["TEXT"]),
                ft.Text("Monitor and analyze model training outputs in real-time.",
                        size=13, color=p["MUTED"]),
            ], expand=True)]),
            ft.Divider(height=1, color=p["BORDER"]),
            filter_bar,
            ft.Row([log_panel, chart_panel], spacing=16,
                   vertical_alignment=ft.CrossAxisAlignment.START, expand=True),
        ], spacing=16, scroll=ft.ScrollMode.AUTO, expand=True),
    )

    return page_shell(page, go_to, "metrics", main_content, route="/metrics")