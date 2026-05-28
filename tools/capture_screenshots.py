"""Capture screenshots of the app window for the tutorial website.

Renders the app in each language and in pause/running states, then uses
Win32 PrintWindow to grab a pixel-accurate window capture into a PNG.
"""
import ctypes
import sys
import time
from ctypes import wintypes
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tempfile
from PIL import Image

# Redirect persistence to a throwaway dir BEFORE importing the app so the
# user's real %APPDATA%\DavidMouse\settings.json is never touched.
from src import state as _state_module
_TMP_SETTINGS_DIR = Path(tempfile.mkdtemp(prefix="dm-shots-"))
_state_module.SETTINGS_DIR = _TMP_SETTINGS_DIR
_state_module.SETTINGS_FILE = _TMP_SETTINGS_DIR / "settings.json"

from src.app import App
from src.state import SETTINGS_FILE


OUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "screenshots"


def _capture_hwnd(hwnd: int) -> Image.Image:
    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32

    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    width = rect.right - rect.left
    height = rect.bottom - rect.top

    hwnd_dc = user32.GetWindowDC(hwnd)
    mem_dc = gdi32.CreateCompatibleDC(hwnd_dc)
    bitmap = gdi32.CreateCompatibleBitmap(hwnd_dc, width, height)
    gdi32.SelectObject(mem_dc, bitmap)

    PW_RENDERFULLCONTENT = 0x00000002
    user32.PrintWindow(hwnd, mem_dc, PW_RENDERFULLCONTENT)

    BI_RGB = 0

    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [
            ("biSize", wintypes.DWORD),
            ("biWidth", wintypes.LONG),
            ("biHeight", wintypes.LONG),
            ("biPlanes", wintypes.WORD),
            ("biBitCount", wintypes.WORD),
            ("biCompression", wintypes.DWORD),
            ("biSizeImage", wintypes.DWORD),
            ("biXPelsPerMeter", wintypes.LONG),
            ("biYPelsPerMeter", wintypes.LONG),
            ("biClrUsed", wintypes.DWORD),
            ("biClrImportant", wintypes.DWORD),
        ]

    bmi = BITMAPINFOHEADER()
    bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.biWidth = width
    bmi.biHeight = -height  # top-down
    bmi.biPlanes = 1
    bmi.biBitCount = 32
    bmi.biCompression = BI_RGB

    buf_len = width * height * 4
    buffer = (ctypes.c_ubyte * buf_len)()
    gdi32.GetDIBits(mem_dc, bitmap, 0, height, buffer, ctypes.byref(bmi), 0)

    img = Image.frombuffer("RGBA", (width, height), buffer, "raw", "BGRA", 0, 1)

    gdi32.DeleteObject(bitmap)
    gdi32.DeleteDC(mem_dc)
    user32.ReleaseDC(hwnd, hwnd_dc)

    return img.convert("RGB")


def render_and_capture(out_path: Path, lang: str, paused: bool = False, countdown_key: str = None, compact: bool = False):
    if SETTINGS_FILE.exists():
        SETTINGS_FILE.unlink()

    app = App()
    app.state.set_lang(lang)
    if compact:
        app.state.toggle_compact()
    if paused:
        app.state.toggle_auto_click()

    if countdown_key:
        app.ui.start_countdown(countdown_key, 2.5, fire=lambda: None)

    def grab_and_close():
        app.ui.root.update_idletasks()
        app.ui.root.update()
        hwnd = app.ui.root.winfo_id()
        # Walk up to the toplevel window so we grab decorations too.
        user32 = ctypes.windll.user32
        GA_ROOT = 2
        try:
            hwnd = user32.GetAncestor(hwnd, GA_ROOT)
        except Exception:
            pass

        try:
            img = _capture_hwnd(hwnd)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(out_path)
            print(f"saved: {out_path}  ({img.size[0]}x{img.size[1]})")
        except Exception as exc:
            print(f"capture failed: {exc}")
        finally:
            app.ui.root.destroy()

    app.ui.root.after(450, grab_and_close)
    app.clicker.start()
    try:
        app.ui.run()
    finally:
        app.clicker.stop()


def main():
    SHOTS = [
        ("ui-zh-running.png", "zh-TW", False, None, False),
        ("ui-zh-paused.png", "zh-TW", True, None, False),
        ("ui-zh-countdown.png", "zh-TW", False, "countdown_left", False),
        ("ui-zh-compact-running.png", "zh-TW", False, None, True),
        ("ui-zh-compact-paused.png", "zh-TW", True, None, True),
        ("ui-en-running.png", "en", False, None, False),
        ("ui-en-paused.png", "en", True, None, False),
        ("ui-en-countdown.png", "en", False, "countdown_left", False),
        ("ui-en-compact-running.png", "en", False, None, True),
    ]
    for name, lang, paused, cd, compact in SHOTS:
        render_and_capture(OUT_DIR / name, lang, paused=paused, countdown_key=cd, compact=compact)
        time.sleep(0.2)


if __name__ == "__main__":
    main()
