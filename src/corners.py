from src.win32_input import get_screen_size


WINDOW_W = 260
WINDOW_H = 400
MARGIN = 12


def corner_position(corner: str) -> tuple[int, int]:
    screen_w, screen_h = get_screen_size()

    if corner == "top-left":
        return MARGIN, MARGIN
    if corner == "top-right":
        return screen_w - WINDOW_W - MARGIN, MARGIN
    if corner == "bottom-left":
        return MARGIN, screen_h - WINDOW_H - MARGIN - 40
    if corner == "bottom-right":
        return screen_w - WINDOW_W - MARGIN, screen_h - WINDOW_H - MARGIN - 40

    return MARGIN, MARGIN


def geometry_string(corner: str) -> str:
    x, y = corner_position(corner)
    return f"{WINDOW_W}x{WINDOW_H}+{x}+{y}"
