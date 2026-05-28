from src.win32_input import get_screen_size


WINDOW_W = 260
WINDOW_H = 470
COMPACT_W = 220
COMPACT_H = 180
MARGIN = 12


def _window_size(compact: bool) -> tuple[int, int]:
    return (COMPACT_W, COMPACT_H) if compact else (WINDOW_W, WINDOW_H)


def corner_position(corner: str, compact: bool = False) -> tuple[int, int]:
    screen_w, screen_h = get_screen_size()
    w, h = _window_size(compact)

    if corner == "top-left":
        return MARGIN, MARGIN
    if corner == "top-right":
        return screen_w - w - MARGIN, MARGIN
    if corner == "bottom-left":
        return MARGIN, screen_h - h - MARGIN - 40
    if corner == "bottom-right":
        return screen_w - w - MARGIN, screen_h - h - MARGIN - 40

    return MARGIN, MARGIN


def geometry_string(corner: str, compact: bool = False) -> str:
    x, y = corner_position(corner, compact)
    w, h = _window_size(compact)
    return f"{w}x{h}+{x}+{y}"
