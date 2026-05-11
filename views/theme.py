import flet as ft

# ── Private palettes ────────────────────────────────────────────────────────
_LIGHT = {
    "BG":             "#F6F7F9",
    "SURFACE":        "#FFFFFF",
    "SIDEBAR_BG":     "#F9FAFB",
    "SIDEBAR_ACTIVE": "#DCFCE7",
    "TEXT":           "#20242C",
    "DARK":           "#20242C",
    "MUTED":          "#6B7280",
    "GRAY":           "#6B7280",
    "GRAY_LIGHT":     "#9CA3AF",
    "BORDER":         "#D9DDE3",
    "ROW_ALT":        "#F9FAFB",
    "GREEN":          "#22C55E",
    "GREEN_DARK":     "#16A34A",
    "GREEN_LIGHT":    "#DCFCE7",
    "GREEN_SOFT":     "#ECFDF3",
    "BLUE":           "#3B82F6",
    "BLUE_LIGHT":     "#DBEAFE",
    "BLUE_SOFT":      "#DBEAFE",
    "RED":            "#EF4444",
    "RED_LIGHT":      "#FEE2E2",
    "RED_SOFT":       "#FEE2E2",
    "ORANGE":         "#F59E0B",
    "ORANGE_LIGHT":   "#FEF3C7",
    "GRAY_SOFT":      "#F3F4F6",
    "SEARCH_BG":      "#F8FAFC",
    "AVATAR_BG":      "#E2E8F0",
    "AVATAR_ICON":    "#475569",
    "WHITE":          "#FFFFFF",
    "INPUT_BG":       "#FFFFFF",
    "CONSOLE_BG":     "#0F172A",
    "CONSOLE_PANEL":  "#1E293B",
}

_DARK = {
    "BG":             "#0F172A",
    "SURFACE":        "#1E293B",
    "SIDEBAR_BG":     "#0B1220",
    "SIDEBAR_ACTIVE": "#14532D",
    "TEXT":           "#F1F5F9",
    "DARK":           "#F1F5F9",
    "MUTED":          "#94A3B8",
    "GRAY":           "#94A3B8",
    "GRAY_LIGHT":     "#64748B",
    "BORDER":         "#334155",
    "ROW_ALT":        "#1E293B",
    "GREEN":          "#22C55E",
    "GREEN_DARK":     "#4ADE80",
    "GREEN_LIGHT":    "#14532D",
    "GREEN_SOFT":     "#14532D",
    "BLUE":           "#60A5FA",
    "BLUE_LIGHT":     "#1E3A8A",
    "BLUE_SOFT":      "#1E3A8A",
    "RED":            "#F87171",
    "RED_LIGHT":      "#7F1D1D",
    "RED_SOFT":       "#7F1D1D",
    "ORANGE":         "#FBBF24",
    "ORANGE_LIGHT":   "#78350F",
    "GRAY_SOFT":      "#1E293B",
    "SEARCH_BG":      "#1E293B",
    "AVATAR_BG":      "#334155",
    "AVATAR_ICON":    "#E2E8F0",
    "WHITE":          "#1E293B",     # "surface" in dark mode
    "INPUT_BG":       "#1E293B",
    "CONSOLE_BG":     "#020617",
    "CONSOLE_PANEL":  "#0F172A",
}


def is_dark(page: ft.Page) -> bool:
    """Returns True if the current theme is dark."""
    if not isinstance(page.data, dict):
        return False
    return bool(page.data.get("dark_mode"))


def set_dark(page: ft.Page, value: bool) -> None:
    """Saves the theme and adjusts `page.theme_mode`."""
    if not isinstance(page.data, dict):
        page.data = {}
    page.data["dark_mode"] = bool(value)
    page.theme_mode = ft.ThemeMode.DARK if value else ft.ThemeMode.LIGHT


def toggle_dark(page: ft.Page) -> bool:
    """Toggles the theme; returns the new value."""
    new_value = not is_dark(page)
    set_dark(page, new_value)
    return new_value


def palette(page: ft.Page) -> dict:
    """Color dictionary for the current theme."""
    return _DARK if is_dark(page) else _LIGHT


# ── Backward compatibility module-level names (for legacy imports) ──────
BG          = _LIGHT["BG"]
WHITE       = _LIGHT["WHITE"]
DARK        = _LIGHT["DARK"]
GRAY        = _LIGHT["GRAY"]
GRAY_LIGHT  = _LIGHT["GRAY_LIGHT"]
BORDER      = _LIGHT["BORDER"]
ROW_ALT     = _LIGHT["ROW_ALT"]
GREEN       = _LIGHT["GREEN"]
GREEN_DARK  = _LIGHT["GREEN_DARK"]
GREEN_LIGHT = _LIGHT["GREEN_LIGHT"]
RED         = _LIGHT["RED"]
RED_LIGHT   = _LIGHT["RED_LIGHT"]
BLUE        = _LIGHT["BLUE"]
BLUE_LIGHT  = _LIGHT["BLUE_LIGHT"]
ORANGE      = _LIGHT["ORANGE"]
ORANGE_LIGHT= _LIGHT["ORANGE_LIGHT"]
SIDEBAR_BG  = _LIGHT["SIDEBAR_BG"]
SIDEBAR_ACTIVE = _LIGHT["SIDEBAR_ACTIVE"]
TEXT        = _LIGHT["TEXT"]
MUTED       = _LIGHT["MUTED"]
SURFACE     = _LIGHT["SURFACE"]
GRAY_SOFT   = _LIGHT["GRAY_SOFT"]
SEARCH_BG   = _LIGHT["SEARCH_BG"]
