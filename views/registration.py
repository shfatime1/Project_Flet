import flet as ft
from views.theme import palette, is_dark, toggle_dark
from api.client import create_user as api_create_user


def _input_block(label_text, field, color):
    return ft.Column(
        spacing=8,
        controls=[
            ft.Text(label_text, size=14, weight=ft.FontWeight.W_600, color=color),
            field,
        ],
    )


def registration_view(page: ft.Page, params, basket) -> ft.View:
    p = palette(page)

    page.title = "Register"
    page.bgcolor = p["BG"]
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO

    GREEN      = "#22C55E"
    GREEN_DARK = "#16A34A"
    GREEN_LINE = "#86EFAC"

    message_box = ft.Container(
        width=380, bgcolor="#ECFDF3",
        border=ft.Border.all(1, "#86EFAC"), border_radius=10,
        padding=ft.Padding(left=12, right=12, top=10, bottom=10),
        visible=False,
        content=ft.Row(spacing=10, controls=[
            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=GREEN_DARK, size=18),
            ft.Text("Done", size=13, color=GREEN_DARK),
        ]),
    )

    username_input = ft.TextField(
        width=380, height=44, border_radius=10, border_color=p["BORDER"],
        focused_border_color=GREEN, cursor_color=GREEN,
        prefix_icon=ft.Icons.PERSON_OUTLINE, text_size=14, color=p["TEXT"],
        bgcolor=p["INPUT_BG"],
        content_padding=ft.Padding(left=12, right=12, top=10, bottom=10),
    )
    email_input = ft.TextField(
        width=380, height=44, border_radius=10, border_color=p["BORDER"],
        focused_border_color=GREEN, cursor_color=GREEN,
        prefix_icon=ft.Icons.MAIL_OUTLINE, text_size=14, color=p["TEXT"],
        bgcolor=p["INPUT_BG"], hint_text="example@gmail.com",
        content_padding=ft.Padding(left=12, right=12, top=10, bottom=10),
    )
    password_input = ft.TextField(
        width=380, height=44, password=True, can_reveal_password=True,
        border_radius=10, border_color=p["BORDER"],
        focused_border_color=GREEN, cursor_color=GREEN,
        prefix_icon=ft.Icons.LOCK_OUTLINE, text_size=14, color=p["TEXT"],
        bgcolor=p["INPUT_BG"],
        content_padding=ft.Padding(left=12, right=12, top=10, bottom=10),
    )

    role_dropdown = ft.Dropdown(
        width=380, border_radius=10, border_color=p["BORDER"],
        focused_border_color=GREEN, color=p["TEXT"], bgcolor=p["INPUT_BG"],
        text_size=14, value="Data Scientist",
        content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
        options=[
            ft.dropdown.Option("Data Scientist"),
            ft.dropdown.Option("Viewer"),
            ft.dropdown.Option("Admin"),
        ],
    )

    def change_theme(_e):
        toggle_dark(page)
        basket["go_to"]("/registration")

    theme_button = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE if is_dark(page) else ft.Icons.DARK_MODE,
        icon_color=p["MUTED"], on_click=change_theme,
    )

    def _show_err(msg: str):
        message_box.bgcolor = "#FEE2E2"
        message_box.border  = ft.Border.all(1, "#FCA5A5")
        message_box.content.controls[0].name  = ft.Icons.ERROR_OUTLINE
        message_box.content.controls[0].color = "#DC2626"
        message_box.content.controls[1].value = msg
        message_box.content.controls[1].color = "#DC2626"
        message_box.visible = True

    # ── Register — uses API ────────────────────────────────────────────────
    def register(_e):
        username = (username_input.value or "").strip()
        email    = (email_input.value or "").strip().lower()
        password = password_input.value or ""
        role     = role_dropdown.value or "Data Scientist"

        errors = []
        if len(username) < 2:
            errors.append(f"username: must be at least 2 characters (got '{username}')")
        if not email:
            errors.append("email: must not be empty")
        elif not email.endswith("@gmail.com"):
            errors.append(f"email: '{email}' — must end with @gmail.com")
        if len(password) < 6:
            errors.append("password: must be at least 6 characters long")

        if errors:
            if any("username" in e for e in errors):
                username_input.border_color = "#DC2626"
                username_input.error_text   = "Min 2 characters"
            else:
                username_input.border_color = p["BORDER"]
                username_input.error_text   = None
            if any("email" in e for e in errors):
                email_input.border_color = "#DC2626"
                email_input.error_text   = "Must be @gmail.com"
            else:
                email_input.border_color = p["BORDER"]
                email_input.error_text   = None
            if any("password" in e for e in errors):
                password_input.border_color = "#DC2626"
                password_input.error_text   = "Min 6 characters"
            else:
                password_input.border_color = p["BORDER"]
                password_input.error_text   = None
            _show_err(errors[0])
            page.update()
            return

        for f in [username_input, email_input, password_input]:
            f.border_color = p["BORDER"]
            f.error_text   = None

        try:
            api_create_user(username, email, password, role)
            username_input.value = ""
            email_input.value    = ""
            password_input.value = ""
            role_dropdown.value  = "Data Scientist"
            message_box.bgcolor = "#ECFDF3"
            message_box.border  = ft.Border.all(1, "#86EFAC")
            message_box.content.controls[0].name  = ft.Icons.CHECK_CIRCLE_OUTLINE
            message_box.content.controls[0].color = GREEN_DARK
            message_box.content.controls[1].value = f"User created as: {role}"
            message_box.content.controls[1].color = GREEN_DARK
            message_box.visible = True
        except Exception as ex:
            detail = str(ex)
            if "409" in detail or "already exists" in detail.lower():
                _show_err("This email already exists.")
            else:
                _show_err(f"API error: {detail}")

        page.update()

    top_line = ft.Container(height=3, bgcolor=GREEN_LINE, border_radius=3)

    logo = ft.Image(
        src="image.png", width=82, height=82, fit=ft.BoxFit.CONTAIN,
        error_content=ft.Container(
            width=82, height=82, bgcolor="#ECFDF3",
            border_radius=41, alignment=ft.Alignment(0, 0),
            content=ft.Icon(ft.Icons.PERSON_ADD_ALT_1, color=GREEN, size=36),
        ),
    )

    title_block = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8,
        controls=[
            logo,
            ft.Text("Create Account", size=26, weight=ft.FontWeight.W_700, color=p["TEXT"]),
            ft.Text("Register to continue", size=14, color=p["MUTED"]),
        ],
    )

    card = ft.Container(
        width=440, bgcolor=p["SURFACE"],
        border=ft.Border.all(1, p["BORDER"]), border_radius=18,
        shadow=ft.BoxShadow(blur_radius=18, spread_radius=0,
                            color="#14000000", offset=ft.Offset(0, 5)),
        content=ft.Column(spacing=0, controls=[
            top_line,
            ft.Container(
                padding=ft.Padding(left=32, top=30, right=32, bottom=24),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=18,
                    controls=[
                        ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=6, controls=[
                                ft.Text("Sign Up", size=22, weight=ft.FontWeight.W_700, color=p["TEXT"]),
                                ft.Text("Create your account", size=14, color=p["MUTED"],
                                        text_align=ft.TextAlign.CENTER),
                            ],
                        ),
                        message_box,
                        _input_block("Username", username_input, p["TEXT"]),
                        _input_block("Email",    email_input,    p["TEXT"]),
                        _input_block("Password", password_input, p["TEXT"]),
                        ft.Column(spacing=8, controls=[
                            ft.Text("Role", size=14, weight=ft.FontWeight.W_600, color=p["TEXT"]),
                            role_dropdown,
                        ]),
                        ft.ElevatedButton(
                            on_click=register, width=380, height=46,
                            style=ft.ButtonStyle(
                                bgcolor={"": GREEN}, color={"": "#FFFFFF"},
                                shape={"": ft.RoundedRectangleBorder(radius=10)},
                                elevation={"": 0},
                            ),
                            content=ft.Text("Register", size=15, weight=ft.FontWeight.W_600),
                        ),
                        ft.TextButton(
                            content=ft.Text("Back to Sign In", size=13, color=GREEN_DARK,
                                            weight=ft.FontWeight.W_600),
                            on_click=lambda _: basket["go_to"]("/"),
                        ),
                    ],
                ),
            ),
        ]),
    )

    body = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=26,
        controls=[
            ft.Row(alignment=ft.MainAxisAlignment.END, controls=[theme_button]),
            title_block, card,
        ],
    )

    container = ft.Container(
        expand=True, alignment=ft.Alignment(0, 0),
        padding=24, content=body, bgcolor=p["BG"],
    )

    return ft.View(
        route="/registration",
        padding=0, spacing=0, bgcolor=p["BG"],
        controls=[container],
    )
