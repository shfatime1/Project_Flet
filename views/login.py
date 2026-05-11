import flet as ft
from api.client import login as api_login
from views.theme import palette, is_dark, toggle_dark


def _input_block(label_text: str, field: ft.TextField, color: str) -> ft.Control:
    return ft.Column(
        spacing=8,
        controls=[
            ft.Text(label_text, size=14, weight=ft.FontWeight.W_600, color=color),
            field,
        ],
    )


def login_view(page: ft.Page, params, basket) -> ft.View:
    p = palette(page)

    page.title = "AI Model Training Log"
    page.bgcolor = p["BG"]
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO

    GREEN      = "#22C55E"
    GREEN_DARK = "#16A34A"
    GREEN_LINE = "#86EFAC"

    def show_error(msg: str) -> None:
        snack = ft.SnackBar(
            content=ft.Row(spacing=10, controls=[
                ft.Icon(ft.Icons.ERROR_OUTLINE, color="#FFFFFF", size=18),
                ft.Text(msg, size=13, color="#FFFFFF"),
            ]),
            bgcolor="#D66969", duration=2500,
            behavior=ft.SnackBarBehavior.FLOATING,
            shape=ft.RoundedRectangleBorder(radius=10),
            margin=ft.Margin(left=24, right=24, bottom=24, top=0),
            open=True,
        )
        page.overlay.append(snack)
        page.update()

    email_input = ft.TextField(
        width=380, height=44,
        border_radius=10, border_color=p["BORDER"],
        focused_border_color=GREEN, cursor_color=GREEN,
        prefix_icon=ft.Icons.MAIL_OUTLINE, text_size=14,
        color=p["TEXT"],
        hint_text="name@company.com",
        hint_style=ft.TextStyle(color=p["MUTED"]),
        bgcolor=p["INPUT_BG"],
        content_padding=ft.Padding(left=12, right=12, top=10, bottom=10),
    )

    password_input = ft.TextField(
        width=380, height=44, password=True, can_reveal_password=True,
        border_radius=10, border_color=p["BORDER"],
        focused_border_color=GREEN, cursor_color=GREEN,
        prefix_icon=ft.Icons.LOCK_OUTLINE, text_size=14,
        color=p["TEXT"],
        hint_text="••••••••",
        hint_style=ft.TextStyle(color=p["MUTED"]),
        bgcolor=p["INPUT_BG"],
        content_padding=ft.Padding(left=12, right=12, top=10, bottom=10),
    )

    # ── Forgot Password dialog ────────────────────────────────────────────
    reset_email_field = ft.TextField(
        width=340,
        hint_text="Enter your email address",
        prefix_icon=ft.Icons.MAIL_OUTLINE,
        border_radius=10, border_color=p["BORDER"],
        focused_border_color=GREEN, cursor_color=GREEN,
        bgcolor=p["INPUT_BG"], color=p["TEXT"],
        hint_style=ft.TextStyle(color=p["MUTED"]),
        content_padding=ft.Padding(left=12, right=12, top=10, bottom=10),
    )

    def close_reset_dialog(_e=None):
        reset_dialog.open = False
        page.update()

    def send_reset(_e):
        addr = (reset_email_field.value or "").strip()
        if not addr:
            reset_email_field.error_text = "Please enter your email."
            page.update()
            return
        reset_email_field.error_text = None
        reset_dialog.open = False
        page.update()
        snack = ft.SnackBar(
            content=ft.Row(spacing=10, controls=[
                ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color="#FFFFFF", size=18),
                ft.Text(f"Reset link sent to {addr}", size=13, color="#FFFFFF"),
            ]),
            bgcolor=GREEN, duration=3000,
            behavior=ft.SnackBarBehavior.FLOATING,
            shape=ft.RoundedRectangleBorder(radius=10),
            margin=ft.Margin(left=24, right=24, bottom=24, top=0),
            open=True,
        )
        page.overlay.append(snack)
        page.update()

    reset_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Reset Password", size=18, weight=ft.FontWeight.W_700, color=p["TEXT"]),
        content=ft.Container(
            width=360,
            content=ft.Column(spacing=12, tight=True, controls=[
                ft.Text(
                    "Enter the email linked to your account and we'll send you a reset link.",
                    size=13, color=p["MUTED"],
                ),
                reset_email_field,
            ]),
        ),
        actions=[
            ft.TextButton("Cancel",
                style=ft.ButtonStyle(color={"": p["MUTED"]}),
                on_click=close_reset_dialog),
            ft.ElevatedButton(
                "Send Reset Link",
                style=ft.ButtonStyle(
                    bgcolor={"": GREEN}, color={"": "#FFFFFF"},
                    shape={"": ft.RoundedRectangleBorder(radius=10)},
                    elevation={"": 0},
                ),
                on_click=send_reset),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        bgcolor=p["SURFACE"],
    )
    page.overlay.append(reset_dialog)

    def open_forgot(_e):
        reset_email_field.value = ""
        reset_email_field.error_text = None
        reset_dialog.open = True
        page.update()

    forgot_btn = ft.Row(
        alignment=ft.MainAxisAlignment.END,
        controls=[
            ft.TextButton(
                content=ft.Text("Forgot Password?", size=13, color=GREEN_DARK,
                                weight=ft.FontWeight.W_600),
                on_click=open_forgot,
            ),
        ],
    )

    remember_checked = {"v": False}
    remember_box = ft.Checkbox(
        label="Remember this device for 30 days",
        value=False, active_color=GREEN, check_color="#FFFFFF",
        label_style=ft.TextStyle(size=13, color=p["TEXT"]),
    )
    def on_remember_change(e):
        remember_checked["v"] = remember_box.value
    remember_box.on_change = on_remember_change

    def change_theme(_e):
        toggle_dark(page)
        basket["go_to"]("/")

    theme_button = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE if is_dark(page) else ft.Icons.DARK_MODE,
        icon_color=p["MUTED"],
        on_click=change_theme,
    )

    # ── Login handler — now uses API ──────────────────────────────────────
    def handle_login(_e):
        email    = (email_input.value or "").strip()
        password = password_input.value or ""

        if not email or not password.strip():
            show_error("Please enter your email/username and password.")
            return

        try:
            row = api_login(email, password)
        except Exception:
            show_error("Email or password is incorrect.")
            return

        if not isinstance(page.data, dict):
            page.data = {}
        page.data["is_logged_in"] = True
        page.data["username"]     = row.get("username") or row.get("email", "").split("@")[0]
        page.data["user_email"]   = row.get("email", "")
        page.data["role"]         = (row.get("role") or "Data Scientist").upper()
        page.data["search_query"] = ""
        page.data["remember"]     = remember_checked["v"]

        basket["go_to"]("/dashboard")

    # ── Card layout ───────────────────────────────────────────────────────
    top_line = ft.Container(height=3, bgcolor=GREEN_LINE, border_radius=3)

    logo = ft.Image(
        src="image.png", width=82, height=82, fit=ft.BoxFit.CONTAIN,
        error_content=ft.Container(
            width=82, height=82, bgcolor="#ECFDF3",
            border_radius=41, alignment=ft.Alignment(0, 0),
            content=ft.Icon(ft.Icons.GRAPHIC_EQ, color=GREEN, size=36),
        ),
    )

    title_block = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=8,
        controls=[
            logo,
            ft.Text("AI Model Training Log", size=26, weight=ft.FontWeight.W_700, color=p["TEXT"]),
            ft.Text("Streamlining the ML development lifecycle", size=14, color=p["MUTED"]),
        ],
    )

    card = ft.Container(
        width=440, bgcolor=p["SURFACE"],
        border=ft.Border.all(1, p["BORDER"]),
        border_radius=18,
        shadow=ft.BoxShadow(blur_radius=18, spread_radius=0,
                            color="#14000000", offset=ft.Offset(0, 5)),
        content=ft.Column(spacing=0, controls=[
            top_line,
            ft.Container(
                padding=ft.Padding(left=32, top=30, right=32, bottom=24),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=18, controls=[
                        ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=6, controls=[
                                ft.Text("Sign In", size=22, weight=ft.FontWeight.W_700, color=p["TEXT"]),
                                ft.Text("Enter your credentials to access the dashboard",
                                        size=14, color=p["MUTED"], text_align=ft.TextAlign.CENTER),
                            ],
                        ),
                        _input_block("Email Address", email_input, p["TEXT"]),
                        ft.Column(spacing=6, controls=[
                            ft.Text("Password", size=14, weight=ft.FontWeight.W_600, color=p["TEXT"]),
                            password_input,
                            forgot_btn,
                        ]),
                        remember_box,
                        ft.ElevatedButton(
                            on_click=handle_login,
                            width=380, height=46,
                            style=ft.ButtonStyle(
                                bgcolor={"": GREEN}, color={"": "#FFFFFF"},
                                shape={"": ft.RoundedRectangleBorder(radius=10)},
                                elevation={"": 0},
                            ),
                            content=ft.Text("Sign In  →", size=15, weight=ft.FontWeight.W_600),
                        ),
                        ft.TextButton(
                            content=ft.Text("Create new account", size=13, color=GREEN_DARK,
                                            weight=ft.FontWeight.W_600),
                            on_click=lambda _: basket["go_to"]("/registration"),
                        ),
                    ],
                ),
            ),
        ]),
    )

    body = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=26,
        controls=[
            ft.Row(alignment=ft.MainAxisAlignment.END, controls=[theme_button]),
            title_block,
            card,
        ],
    )

    container = ft.Container(
        expand=True, alignment=ft.Alignment(0, 0),
        padding=24, content=body, bgcolor=p["BG"],
    )

    return ft.View(
        route="/",
        padding=0, spacing=0,
        bgcolor=p["BG"],
        controls=[container],
    )
