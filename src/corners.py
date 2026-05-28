from src.win32_input import get_screen_size


WINDOW_W = 260
WINDOW_H = 470
COMPACT_W = 220
COMPACT_H = 180
# Watch mode: smallest viable square the head-mouse user can still dwell on
# while a YouTube video plays full-screen behind it. 90px ≥ the 60x60 minimum
# tap target plus padding for the high-contrast border.
WATCH_W = 90
WATCH_H = 90
MARGIN = 12


def _window_size(view_mode: str) -> tuple[int, int]:
    if view_mode == "watch":
        return (WATCH_W, WATCH_H)
    if view_mode == "compact":
        return (COMPACT_W, COMPACT_H)
    return (WINDOW_W, WINDOW_H)


def corner_position(corner: str, view_mode: str = "full") -> tuple[int, int]:
    screen_w, screen_h = get_screen_size()
    w, h = _window_size(view_mode)

    if corner == "top-left":
        return MARGIN, MARGIN
    if corner == "top-right":
        return screen_w - w - MARGIN, MARGIN
    if corner == "bottom-left":
        return MARGIN, screen_h - h - MARGIN - 40
    if corner == "bottom-right":
        return screen_w - w - MARGIN, screen_h - h - MARGIN - 40

    return MARGIN, MARGIN


def geometry_string(corner: str, view_mode: str = "full") -> str:
    x, y = corner_position(corner, view_mode)
    w, h = _window_size(view_mode)
    return f"{w}x{h}+{x}+{y}"
