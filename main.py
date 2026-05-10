import flet as ft
import inspect

from views.login import login_view
from views.dashboard import dashboard_view
from views.experiments import experiments_view
from views.registration import registration_view
from views.experiment_details import experiment_details_view
from views.training_monitor import training_monitor_view
from views.metrics import metrics_view
from views.compare_experiments import compare_experiments_view
from views.reports import reports_view
from views.manage_user import manage_user_view
from views.manage_dataset import manage_dataset_view
from views.manage_model import manage_model_view


# ── Routes that require login ──────────────────────────────────────────────
PROTECTED = {
    "/dashboard",
    "/experiments",
    "/experiment-details",
    "/training-monitor",
    "/metrics",
    "/compare-experiments",
    "/reports",
    "/manage-users",
    "/manage-datasets",
    "/manage-models",
}

# ── Routes only Admin can access ───────────────────────────────────────────
ADMIN_ONLY = {
    "/manage-users",
    "/manage-datasets",
    "/manage-models",
}

# ── Routes where whole page scrolls (no sidebar) ──────────────────────────
SCROLLABLE = {"/", "/registration"}

# ── Alias map ─────────────────────────────────────────────────────────────
ALIASES = {
    "dashboard":           "/dashboard",
    "experiments":         "/experiments",
    "experiment_details":  "/experiment-details",
    "experiment-details":  "/experiment-details",
    "training_monitor":    "/training-monitor",
    "training-monitor":    "/training-monitor",
    "metrics":             "/metrics",
    "compare_experiments": "/compare-experiments",
    "compare-experiments": "/compare-experiments",
    "reports":             "/reports",
    "manage_users":        "/manage-users",
    "manage-users":        "/manage-users",
    "manage_user":         "/manage-users",
    "manage_datasets":     "/manage-datasets",
    "manage-datasets":     "/manage-datasets",
    "manage_dataset":      "/manage-datasets",
    "manage_models":       "/manage-models",
    "manage-models":       "/manage-models",
    "manage_model":        "/manage-models",
    "login":               "/",
    "registration":        "/registration",
}


def _normalise(route: str) -> str:
    return ALIASES.get(route, route)


try:
    from views.theme import BG
except Exception:
    BG = "#F1F5F9"


def main(page: ft.Page) -> None:
    page.title = "AI Model Training Log"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0
    page.window.width  = 1280
    page.window.height = 800

    page.data = {}

    def is_logged_in() -> bool:
        return bool(page.data.get("is_logged_in"))

    def get_role() -> str:
        if isinstance(page.data, dict):
            return (page.data.get("role") or "DATA SCIENTIST").upper()
        return "DATA SCIENTIST"

    def _call_view(view_obj, params, handlers):
        if inspect.isclass(view_obj):
            instance = view_obj(navigate=handlers["go_to"], page=page)
            ctrl = instance.build()
            return ft.View(
                route="",
                controls=[ctrl],
                bgcolor=getattr(ctrl, "bgcolor", BG),
                padding=0, spacing=0,
            )
        else:
            return view_obj(page, params, handlers)

    def _render(view: ft.View) -> None:
        page.controls.clear()
        for ctrl in view.controls:
            page.controls.append(ctrl)
        if view.bgcolor:
            page.bgcolor = view.bgcolor
            try:
                page.window.bgcolor = view.bgcolor
            except Exception:
                pass

    def go_to(route: str) -> None:
        route = _normalise(route)

        # Auth guard
        if route in PROTECTED and not is_logged_in():
            route = "/"

        # Role guard — non-admin tries to reach admin-only page
        if route in ADMIN_ONLY and get_role() != "ADMIN":
            from views.sidebar import _show_snack
            from views.theme import palette
            p = palette(page)
            _show_snack(page, "⛔ Access denied: Admin only.", "#EF4444")
            route = "/dashboard"

        page.scroll = ft.ScrollMode.AUTO if route in SCROLLABLE else None

        params:   dict = {}
        handlers: dict = {"go_to": go_to}

        ROUTES = {
            "/":                    login_view,
            "/registration":        registration_view,
            "/dashboard":           dashboard_view,
            "/experiments":         experiments_view,
            "/experiment-details":  experiment_details_view,
            "/training-monitor":    training_monitor_view,
            "/metrics":             metrics_view,
            "/compare-experiments": compare_experiments_view,
            "/reports":             reports_view,
            "/manage-users":        manage_user_view,
            "/manage-datasets":     manage_dataset_view,
            "/manage-models":       manage_model_view,
        }

        view_obj = ROUTES.get(route, login_view)
        view     = _call_view(view_obj, params, handlers)

        _render(view)
        page.update()

    page.go           = go_to   # type: ignore
    page.push_route   = go_to   # type: ignore

    go_to("/")


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")