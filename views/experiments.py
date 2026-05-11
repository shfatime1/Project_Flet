import flet as ft
from datetime import datetime

from views.theme import palette
from views.sidebar import page_shell, show_snack
from api import client as api


EXP_HYPERPARAMS = {
    "EXP-8802": [("Learning Rate","0.001"),("Batch Size","64"),("Optimizer","Adam"),("Epochs","50"),("Weight Decay","1e-4"),("Base Dataset","MedScan-Alpha-2024"),("GPU Architecture","NVIDIA A100"),("Seed","42")],
    "EXP-8795": [("Learning Rate","2e-5"),("Batch Size","32"),("Optimizer","AdamW"),("Epochs","10"),("Weight Decay","0.01"),("Base Dataset","SST-2"),("GPU Architecture","NVIDIA V100"),("Seed","123")],
    "EXP-8782": [("Learning Rate","0.01"),("Batch Size","16"),("Optimizer","SGD"),("Epochs","100"),("Weight Decay","5e-4"),("Base Dataset","COCO-2023"),("GPU Architecture","NVIDIA RTX 4090"),("Seed","7")],
    "EXP-8777": [("Learning Rate","0.0005"),("Batch Size","128"),("Optimizer","RMSprop"),("Epochs","200"),("Weight Decay","1e-5"),("Base Dataset","Yahoo Finance"),("GPU Architecture","NVIDIA A100"),("Seed","99")],
    "EXP-8761": [("Learning Rate","0.001"),("Batch Size","64"),("Optimizer","Adam"),("Epochs","500"),("Weight Decay","0"),("Base Dataset","OpenAI Gym"),("GPU Architecture","CPU"),("Seed","0")],
}

EXP_METRICS = {
    "EXP-8802": [("Accuracy","0.942","2 mins ago",True),("Loss","0.041","2 mins ago",False),("F1 Score","0.928","5 mins ago",True),("Precision","0.951","2 mins ago",True),("Recall","0.905","10 mins ago",True)],
    "EXP-8795": [("Accuracy","0.934","1 min ago",True),("Loss","0.120","1 min ago",False),("F1 Score","0.912","3 mins ago",True),("Precision","0.928","2 mins ago",True),("Recall","0.897","8 mins ago",True)],
    "EXP-8782": [("mAP@50","0.612","Last epoch",False),("Loss","0.891","Last epoch",False),("Precision","0.743","Last epoch",False),("Recall","0.581","Last epoch",False),("F1 Score","0.651","Last epoch",False)],
    "EXP-8777": [("MAE","0.0412","Final",True),("RMSE","0.0638","Final",True),("R²","0.8821","Final",True),("MAPE","3.24%","Final",True),("Loss","0.0023","Final",False)],
    "EXP-8761": [("Avg Reward","487.2","Ep 500",True),("Loss","0.0081","Ep 500",False),("Epsilon","0.05","Ep 500",True),("Success Rate","96.8%","Ep 500",True),("Q-Value","23.4","Ep 500",True)],
}


def experiments_view(page: ft.Page, params, basket) -> ft.View:
    p = palette(page)
    go_to = basket["go_to"]

    _role = "DATA SCIENTIST"
    if isinstance(page.data, dict):
        _role = (page.data.get("role") or "DATA SCIENTIST").upper()
    _is_viewer = (_role == "VIEWER")

    all_data = api.get_experiments()
    if not isinstance(page.data, dict):
        page.data = {}
    page.data["experiments"] = all_data

    wizard_step   = {"v": 1}
    editing_index = {"v": None}
    search_query  = {"v": page.data.get("search_query", "") or ""}
    status_filter = {"v": "All Status"}

    def _status_badge(label):
        if label == "Completed":
            bg, fg = p["GREEN"], "#FFFFFF"
        elif label == "Failed":
            bg, fg = p["RED"], "#FFFFFF"
        elif label == "Running":
            bg, fg = p["GRAY_SOFT"], p["TEXT"]
        else:
            bg, fg = p["GRAY_SOFT"], p["MUTED"]
        return ft.Container(
            padding=ft.Padding(left=12, right=12, top=4, bottom=4),
            border_radius=16, bgcolor=bg,
            content=ft.Text(label, size=12, color=fg, weight=ft.FontWeight.W_600))

    def _model_badge(v):
        return ft.Container(
            padding=ft.Padding(left=10, right=10, top=4, bottom=4),
            border_radius=8, bgcolor=p["GREEN_SOFT"],
            content=ft.Text(v, size=11, color=p["GREEN_DARK"], weight=ft.FontWeight.W_600))

    def _avatar(name):
        colors = ["#6366F1","#EC4899","#F59E0B","#10B981","#3B82F6"]
        c = colors[sum(ord(x) for x in name) % len(colors)]
        return ft.Container(width=28, height=28, border_radius=14, bgcolor=c,
                            alignment=ft.Alignment(0,0),
                            content=ft.Text(name[0].upper(), size=12, color="#FFFFFF",
                                            weight=ft.FontWeight.W_600))

    def open_details(exp):
        def handler(_e=None):
            page.data["selected_experiment"]  = exp
            page.data["selected_hyperparams"] = EXP_HYPERPARAMS.get(
                exp["id"], list(EXP_HYPERPARAMS.values())[0])
            page.data["selected_metrics"]     = EXP_METRICS.get(
                exp["id"], list(EXP_METRICS.values())[0])
            go_to("/experiment-details")
        return handler

    table_col = ft.Column(spacing=0)
    count_txt = ft.Text("", size=13, color=p["MUTED"])
    total_txt = ft.Text("", size=13, color=p["MUTED"])

    def _filtered():
        q  = search_query["v"].lower().strip()
        sf = status_filter["v"]
        out = []
        for ex in all_data:
            if sf != "All Status" and ex["status"] != sf:
                continue
            if q and not any(q in (ex.get(k) or "").lower()
                             for k in ("name","id","model","owner","desc")):
                continue
            out.append(ex)
        return out

    def _make_row(exp, last=False, idx=0):
        row_bg = p["ROW_ALT"] if idx % 2 == 1 else p["SURFACE"]  # alternating row colors
        return ft.Container(
            bgcolor=row_bg,
            padding=ft.Padding(left=20, right=20, top=12, bottom=12),
            border=ft.Border(bottom=ft.BorderSide(0 if last else 1, p["BORDER"])),
            on_click=open_details(exp), ink=True,
            content=ft.Row(vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                ft.Container(expand=3, content=ft.Column(spacing=2, controls=[
                    ft.Text(exp["name"], size=13, color=p["TEXT"], weight=ft.FontWeight.W_600),
                    ft.Text(exp["id"],   size=11, color=p["MUTED"]),
                ])),
                ft.Container(expand=2, content=ft.Row(spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[_avatar(exp["owner"]),
                              ft.Text(exp["owner"], size=13, color=p["TEXT"])])),
                ft.Container(expand=2, content=ft.Text(
                    (exp["created"] or "").replace("\n"," "), size=12, color=p["MUTED"])),
                ft.Container(expand=2, content=_model_badge(exp["model"])),
                ft.Container(expand=2, content=_status_badge(exp["status"])),
                ft.Container(width=48, alignment=ft.Alignment(1,0),
                    content=ft.PopupMenuButton(
                        icon=ft.Icons.MORE_VERT, icon_size=18, icon_color=p["MUTED"],
                        items=[
                            ft.PopupMenuItem(
                                content=ft.Text("View Details"),
                                icon=ft.Icons.VISIBILITY_OUTLINED,
                                on_click=lambda e, ex=exp: open_details(ex)()),
                            *( [] if _is_viewer else [
                                ft.PopupMenuItem(
                                    content=ft.Text("Edit"),
                                    icon=ft.Icons.EDIT_OUTLINED,
                                    on_click=_make_edit_handler(exp)),
                                ft.PopupMenuItem(
                                    content=ft.Text("Delete"),
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    on_click=_make_del_handler(exp["id"])),
                            ]),
                        ])),
            ]),
        )

    def _rebuild():
        visible = _filtered()
        table_col.controls.clear()
        for i, ex in enumerate(visible):
            table_col.controls.append(_make_row(ex, last=(i == len(visible)-1), idx=i))
        n = len(visible)
        count_txt.value = f"Showing 1-{n} of {n} experiments"
        total_txt.value = f"{len(all_data)} Total"
        try:
            page.update()
        except Exception:
            pass

    def _reload_and_rebuild():
        all_data.clear()
        all_data.extend(api.get_experiments())
        _rebuild()

    def _make_edit_handler(exp):
        def h(_e):
            try:
                idx = next(i for i, x in enumerate(all_data) if x["id"] == exp["id"])
            except StopIteration:
                return
            editing_index["v"] = idx
            wizard_step["v"]   = 1
            dlg_name.value     = exp["name"];  dlg_name.error_text  = None
            dlg_name.border_color = p["BORDER"]
            dlg_desc.value     = exp.get("desc","")
            dlg_owner.value    = exp["owner"]; dlg_owner.error_text = None
            dlg_owner.border_color = p["BORDER"]
            dlg_model.value    = exp["model"]; dlg_model.error_text = None
            dlg_model.border_color = p["BORDER"]
            dlg_status.value   = exp["status"]
            _sync_wizard()
            modal_bg.visible = True
            page.update()
        return h

    def _make_del_handler(exp_id):
        def h(_e):
            api.delete_experiment(exp_id)
            _reload_and_rebuild()
            show_snack(page, f"{exp_id} deleted.", p["RED"])
        return h

    _tf = dict(text_size=13, border_radius=8, border_color=p["BORDER"],
               focused_border_color=p["GREEN"], color=p["TEXT"],
               bgcolor=p["INPUT_BG"],
               content_padding=ft.Padding(left=14, right=14, top=12, bottom=12))

    dlg_name   = ft.TextField(hint_text="e.g. ResNet50_Standard_Epoch100", **_tf)
    dlg_desc   = ft.TextField(
        hint_text="Describe the hypothesis, model architecture changes, or goals...",
        min_lines=4, max_lines=6, multiline=True,
        text_size=13, border_radius=8, border_color=p["BORDER"],
        focused_border_color=p["GREEN"], color=p["TEXT"], bgcolor=p["INPUT_BG"],
        content_padding=ft.Padding(left=14, right=14, top=14, bottom=14))
    dlg_owner  = ft.TextField(hint_text="Owner name", **_tf)
    dlg_model  = ft.TextField(hint_text="e.g. v1.0.0", **_tf)
    dlg_status = ft.Dropdown(
        value="Running", text_size=13, border_radius=8,
        border_color=p["BORDER"], focused_border_color=p["GREEN"], color=p["TEXT"],
        bgcolor=p["INPUT_BG"],
        content_padding=ft.Padding(left=14, right=14, top=8, bottom=8),
        options=[ft.DropdownOption(s) for s in ["Running","Completed","Failed","Stopped"]])

    step_lbl   = ft.Text("Step 1 of 3", size=12, color="#FFFFFF", weight=ft.FontWeight.W_600)
    step_badge = ft.Container(
        padding=ft.Padding(left=10, right=10, top=4, bottom=4),
        border_radius=12, bgcolor=p["GREEN"], content=step_lbl)
    prog_inner = ft.Container(
        bgcolor=p["GREEN"], border_radius=2, height=4,
        alignment=ft.Alignment(-1,0), width=160)
    prog_bar   = ft.Container(height=4, border_radius=2, bgcolor="#E5E7EB", content=prog_inner)

    s1 = ft.Column(spacing=14, visible=True, controls=[
        ft.Text("Experiment Name", size=14, color=p["TEXT"], weight=ft.FontWeight.W_600), dlg_name,
        ft.Text("Unique identifier for this training run.", size=12, color=p["MUTED"]),
        ft.Text("Description", size=14, color=p["TEXT"], weight=ft.FontWeight.W_600), dlg_desc,
    ])
    s2 = ft.Column(spacing=14, visible=False, controls=[
        ft.Text("Owner", size=14, color=p["TEXT"], weight=ft.FontWeight.W_600), dlg_owner,
        ft.Text("Linked Model Version", size=14, color=p["TEXT"], weight=ft.FontWeight.W_600), dlg_model,
    ])
    s3 = ft.Column(spacing=14, visible=False, controls=[
        ft.Text("Status", size=14, color=p["TEXT"], weight=ft.FontWeight.W_600), dlg_status,
        ft.Container(height=24),
    ])

    cont_text = ft.Text("Continue", size=14, color="#FFFFFF", weight=ft.FontWeight.W_600)
    cont_icon = ft.Icon(ft.Icons.CHEVRON_RIGHT, size=18, color="#FFFFFF")

    def _sync_wizard():
        sv = wizard_step["v"]
        step_lbl.value = f"Step {sv} of 3"
        s1.visible = (sv == 1); s2.visible = (sv == 2); s3.visible = (sv == 3)
        prog_inner.width = int(160 * sv / 3)
        cont_text.value = "Save" if sv == 3 else "Continue"
        cont_icon.name  = ft.Icons.CHECK if sv == 3 else ft.Icons.CHEVRON_RIGHT

    def _v1():
        if not (dlg_name.value or "").strip():
            dlg_name.error_text = "Name is required"
            dlg_name.border_color = p["RED"]
            page.update()
            return False
        dlg_name.error_text = None
        dlg_name.border_color = p["BORDER"]
        return True

    def _v2():
        ok = True
        for f, msg in [(dlg_owner,"Owner required"),(dlg_model,"Model required")]:
            if not (f.value or "").strip():
                f.error_text = msg; f.border_color = p["RED"]; ok = False
            else:
                f.error_text = None; f.border_color = p["BORDER"]
        if not ok:
            page.update()
        return ok

    def on_continue(_e):
        sv = wizard_step["v"]
        if sv == 1:
            if not _v1(): return
            wizard_step["v"] = 2
        elif sv == 2:
            if not _v2(): return
            wizard_step["v"] = 3
        else:
            nm = (dlg_name.value or "").strip()
            ow = (dlg_owner.value or "").strip()
            md = (dlg_model.value or "").strip()
            st = dlg_status.value or "Running"
            dc = (dlg_desc.value or "").strip()
            ei = editing_index["v"]
            try:
                if ei is not None and ei >= 0:
                    api.update_experiment(all_data[ei]["id"], nm, ow, md, st, dc)
                else:
                    next_id = api.get_next_experiment_id()
                    api.create_experiment(
                        next_id, nm, ow, md,
                        datetime.now().strftime("%Y-%m-%d\n%H:%M"), st, dc)
            except Exception as ex:
                show_snack(page, f"API error: {ex}", "#EF4444")
                return
            editing_index["v"] = None
            modal_bg.visible = False
            _reload_and_rebuild()
            show_snack(page, "Experiment saved.", p["GREEN"])
            return
        _sync_wizard()
        page.update()

    def on_draft(_e):
        if not _v1(): return
        nm = (dlg_name.value or "").strip()
        ei = editing_index["v"]
        owner_default = "Unknown"
        if isinstance(page.data, dict):
            owner_default = page.data.get("username") or owner_default
        try:
            if ei is not None and ei >= 0:
                api.update_experiment(all_data[ei]["id"], nm,
                    (dlg_owner.value or owner_default).strip(),
                    (dlg_model.value or "v1.0.0").strip(),
                    "Running", (dlg_desc.value or "").strip())
            else:
                next_id = api.get_next_experiment_id()
                api.create_experiment(
                    next_id, nm, owner_default, "v1.0.0",
                    datetime.now().strftime("%Y-%m-%d\n%H:%M"), "Running", "")
        except Exception as ex:
            show_snack(page, f"API error: {ex}", "#EF4444")
            return
        editing_index["v"] = None
        modal_bg.visible = False
        _reload_and_rebuild()
        show_snack(page, "Draft saved.", p["GREEN"])

    def close_dlg(_e=None):
        modal_bg.visible = False
        page.update()

    def open_create(_e):
        editing_index["v"] = -1
        wizard_step["v"] = 1
        for f in [dlg_name, dlg_desc, dlg_owner, dlg_model]:
            f.value = ""; f.error_text = None; f.border_color = p["BORDER"]
        dlg_status.value = "Running"
        _sync_wizard()
        modal_bg.visible = True
        page.update()

    dialog_card = ft.Container(
        width=500, bgcolor=p["SURFACE"], border_radius=16,
        shadow=ft.BoxShadow(blur_radius=50, spread_radius=2,
                            color="#00000060", offset=ft.Offset(0,10)),
        content=ft.Column(tight=True, spacing=0, controls=[
            ft.Container(padding=ft.Padding(left=28, right=28, top=28, bottom=28),
                content=ft.Column(tight=True, spacing=18, controls=[
                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                        ft.Text("Create New Experiment", size=18, color=p["TEXT"],
                                weight=ft.FontWeight.W_700),
                        ft.Row(spacing=8, controls=[
                            step_badge,
                            ft.IconButton(icon=ft.Icons.CLOSE, icon_size=18,
                                          icon_color=p["MUTED"], on_click=close_dlg),
                        ]),
                    ]),
                    prog_bar, s1, s2, s3,
                ])),
            ft.Container(
                padding=ft.Padding(left=28, right=28, top=14, bottom=14),
                border=ft.Border(top=ft.BorderSide(1, p["BORDER"])),
                content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                    ft.TextButton("Cancel", on_click=close_dlg,
                                  style=ft.ButtonStyle(color={"": p["MUTED"]})),
                    ft.Row(spacing=10, controls=[
                        ft.TextButton(
                            content=ft.Row(spacing=6, controls=[
                                ft.Icon(ft.Icons.BOOKMARK_BORDER, size=16, color=p["GREEN_DARK"]),
                                ft.Text("Save Draft", size=14, color=p["GREEN_DARK"],
                                        weight=ft.FontWeight.W_600),
                            ]), on_click=on_draft),
                        ft.ElevatedButton(
                            content=ft.Row(spacing=4, controls=[cont_text, cont_icon]),
                            style=ft.ButtonStyle(
                                bgcolor={"": p["GREEN"]}, color={"": "#FFFFFF"},
                                shape={"": ft.RoundedRectangleBorder(radius=10)},
                                elevation={"": 0},
                                padding={"": ft.Padding(left=20, right=20, top=10, bottom=10)}),
                            on_click=on_continue),
                    ]),
                ])),
        ]),
    )

    modal_bg = ft.Container(
        visible=False, expand=True, bgcolor="#00000055", alignment=ft.Alignment(0, 0),
        content=dialog_card,
    )
    dialog_card.on_click = lambda e: None

    def on_search(e):
        search_query["v"] = e.control.value or ""
        _rebuild()

    def on_status_change(e):
        status_filter["v"] = e.control.value or "All Status"
        _rebuild()

    def on_reset(_e):
        search_query["v"] = ""
        status_filter["v"] = "All Status"
        search_field.value = ""
        status_dd.value = "All Status"
        if isinstance(page.data, dict):
            page.data["search_query"] = ""
        _rebuild()

    search_field = ft.TextField(
        value=search_query["v"],
        hint_text="Search by name, ID or model...",
        width=240, height=38, text_size=13, border_radius=8,
        border_color=p["BORDER"], focused_border_color=p["GREEN"],
        prefix_icon=ft.Icons.SEARCH, color=p["TEXT"], bgcolor=p["INPUT_BG"],
        hint_style=ft.TextStyle(color=p["MUTED"]),
        content_padding=ft.Padding(left=10, right=10, top=8, bottom=8),
        on_change=on_search,
    )

    status_dd = ft.Dropdown(
        value="All Status", width=160, text_size=13,
        border_radius=8, border_color=p["BORDER"], color=p["TEXT"], bgcolor=p["INPUT_BG"],
        options=[ft.DropdownOption(s) for s in ["All Status","Running","Completed","Failed","Stopped"]],
        on_select=on_status_change,
    )

    def header_cb(value: str):
        search_query["v"] = value or ""
        search_field.value = value or ""
        try:
            search_field.update()
        except Exception:
            pass
        _rebuild()

    page.data["on_header_search"] = header_cb

    filter_bar = ft.Container(
        bgcolor=p["SURFACE"], border=ft.Border.all(1, p["BORDER"]), border_radius=14,
        padding=ft.Padding(left=20, right=20, top=14, bottom=14),
        content=ft.Row(spacing=16, vertical_alignment=ft.CrossAxisAlignment.END, controls=[
            ft.Column(spacing=4, controls=[
                ft.Text("Search", size=12, color=p["MUTED"], weight=ft.FontWeight.W_600),
                search_field,
            ]),
            ft.Column(spacing=4, controls=[
                ft.Text("Status", size=12, color=p["MUTED"], weight=ft.FontWeight.W_600),
                status_dd,
            ]),
            ft.Column(spacing=4, controls=[
                ft.Text("Date Range", size=12, color=p["MUTED"], weight=ft.FontWeight.W_600),
                ft.Container(height=38, border_radius=8, border=ft.Border.all(1, p["BORDER"]),
                    padding=ft.Padding(left=12, right=12, top=6, bottom=6),
                    content=ft.Row(spacing=8, controls=[
                        ft.Icon(ft.Icons.CALENDAR_TODAY, size=13, color=p["MUTED"]),
                        ft.Text("Oct 1, 2023 – Oct 24, 2023", size=13, color=p["TEXT"]),
                    ])),
            ]),
            ft.Container(height=38, border_radius=8, border=ft.Border.all(1, p["BORDER"]),
                padding=ft.Padding(left=12, right=12, top=6, bottom=6),
                content=ft.Row(spacing=8, controls=[
                    ft.Icon(ft.Icons.FILTER_LIST, size=15, color=p["MUTED"]),
                    ft.Text("More Filters", size=13, color=p["TEXT"]),
                ])),
            ft.TextButton("Reset", style=ft.ButtonStyle(color={"": p["MUTED"]}), on_click=on_reset),
        ]),
    )

    table_header = ft.Container(
        bgcolor=p["ROW_ALT"],
        border=ft.Border(bottom=ft.BorderSide(1, p["BORDER"])),
        padding=ft.Padding(left=20, right=20, top=11, bottom=11),
        content=ft.Row(vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
            ft.Container(expand=3, content=ft.Text("Experiment Name", size=12, color=p["MUTED"], weight=ft.FontWeight.W_600)),
            ft.Container(expand=2, content=ft.Text("Created By",      size=12, color=p["MUTED"], weight=ft.FontWeight.W_600)),
            ft.Container(expand=2, content=ft.Text("Created At",      size=12, color=p["MUTED"], weight=ft.FontWeight.W_600)),
            ft.Container(expand=2, content=ft.Text("Linked Model",    size=12, color=p["MUTED"], weight=ft.FontWeight.W_600)),
            ft.Container(expand=2, content=ft.Text("Status",          size=12, color=p["MUTED"], weight=ft.FontWeight.W_600)),
            ft.Container(width=48, content=ft.Text("Actions",         size=12, color=p["MUTED"], weight=ft.FontWeight.W_600)),
        ]),
    )

    experiments_table = ft.Container(
        bgcolor=p["SURFACE"], border=ft.Border.all(1, p["BORDER"]),
        border_radius=14, clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Column(spacing=0, controls=[table_header, table_col]),
    )

    _rebuild()

    pagination = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            count_txt,
            ft.Row(spacing=4, controls=[
                ft.Text("< Previous", size=13, color=p["MUTED"]),
                *[ft.Container(width=30, height=30, border_radius=15,
                               bgcolor=p["GREEN"] if i == 1 else "transparent",
                               alignment=ft.Alignment(0,0),
                               content=ft.Text(str(i), size=13,
                                               color="#FFFFFF" if i == 1 else p["MUTED"],
                                               weight=ft.FontWeight.W_600))
                  for i in [1, 2, 3]],
                ft.Text("Next >", size=13, color=p["MUTED"]),
            ]),
        ],
    )

    promo = ft.Container(
        bgcolor=p["SURFACE"], border=ft.Border.all(1, p["BORDER"]), border_radius=14,
        padding=ft.Padding(left=40, right=40, top=26, bottom=26),
        alignment=ft.Alignment(0,0),
        content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10, controls=[
            ft.Container(width=42, height=42, border_radius=21, bgcolor=p["GREEN_SOFT"],
                         alignment=ft.Alignment(0,0),
                         content=ft.Icon(ft.Icons.ADD, color=p["GREEN"], size=20)),
            ft.Text("Scale your research", size=17, color=p["TEXT"], weight=ft.FontWeight.W_700),
            ft.Text("Need to run batch experiments? Use our API or CLI tool to submit\n"
                    "multiple training jobs directly to the cluster.",
                    size=13, color=p["MUTED"], text_align=ft.TextAlign.CENTER),
            ft.TextButton("View API Documentation",
                          style=ft.ButtonStyle(color={"": p["GREEN_DARK"]}),
                          on_click=lambda _e: show_snack(page, "API documentation opened.", p["GREEN"])),
        ]),
    )

    main_area = ft.Container(
        expand=True, padding=ft.Padding(left=28, right=28, top=28, bottom=28),
        bgcolor=p["BG"],
        content=ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=20, controls=[
            ft.Row(spacing=6, controls=[
                ft.Text("Home",        size=12, color=p["MUTED"]),
                ft.Text(">",           size=12, color=p["MUTED"]),
                ft.Text("Experiments", size=12, color=p["TEXT"], weight=ft.FontWeight.W_600),
            ]),
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                   vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                ft.Row(spacing=14, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                    ft.Text("Experiments", size=28, color=p["TEXT"], weight=ft.FontWeight.W_700),
                    ft.Container(padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                                 border_radius=12, bgcolor=p["GRAY_SOFT"], content=total_txt),
                ]),
                *([] if _is_viewer else [
                    ft.OutlinedButton(
                        "Delete All",
                        icon=ft.Icons.DELETE_SWEEP_OUTLINED,
                        style=ft.ButtonStyle(color={"": p["RED"]},
                                             side={"": ft.BorderSide(1, p["RED"])}),
                        on_click=lambda _e: _confirm_delete_all_exp(),
                    ),
                    ft.ElevatedButton(
                        content=ft.Row(spacing=6, controls=[
                            ft.Icon(ft.Icons.ADD, size=18, color="#FFFFFF"),
                            ft.Text("Create Experiment", size=14, color="#FFFFFF",
                                    weight=ft.FontWeight.W_600),
                        ]),
                        style=ft.ButtonStyle(
                            bgcolor={"": p["GREEN"]}, color={"": "#FFFFFF"},
                            shape={"": ft.RoundedRectangleBorder(radius=10)},
                            elevation={"": 0},
                            padding={"": ft.Padding(left=20, right=20, top=12, bottom=12)}),
                        on_click=open_create),
                ]),
            ]),
            filter_bar,
            experiments_table,
            pagination,
            promo,
        ]),
    )

    def _confirm_delete_all_exp():
        def do_delete(_e):
            try:
                api.delete_all_experiments()
                show_snack(page, "All experiments deleted.", p["RED"])
            except Exception as ex:
                show_snack(page, f"Error: {ex}", "#EF4444")
            dlg.open = False
            _reload_and_rebuild()
            page.update()
        dlg = ft.AlertDialog(
            modal=True, bgcolor=p["SURFACE"],
            title=ft.Text("Delete All Experiments", color=p["TEXT"], weight=ft.FontWeight.BOLD),
            content=ft.Text("Are you sure you want to delete ALL experiments? This cannot be undone.",
                            color=p["TEXT"]),
            actions=[
                ft.TextButton("Cancel",
                              style=ft.ButtonStyle(color={"": p["MUTED"]}),
                              on_click=lambda e: _close_dlg(dlg)),
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

    def _close_dlg(dlg):
        dlg.open = False
        page.update()

    layout_with_modal = ft.Stack(controls=[
        ft.Container(content=main_area, expand=True),
        modal_bg,
    ], expand=True)

    return page_shell(page, go_to, "experiments", layout_with_modal, route="/experiments")
