"""One-off: capture the new Watch Mode (90x90) widget to a PNG.

Used by the FB-post banner build, not part of the regular screenshot set.
"""
import ctypes
import sys
import tempfile
from ctypes import wintypes
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image

from src import state as _state_module
_TMP = Path(tempfile.mkdtemp(prefix="dm-watch-shot-"))
_state_module.SETTINGS_DIR = _TMP
_state_module.SETTINGS_FILE = _TMP / "settings.json"

from src.app import App

OUT = Path(__file__).resolve().parent.parent / "docs" / "screenshots" / "zh-TW" / "ui-watch.png"


def _capture_hwnd(hwnd: int) -> Image.Image:
    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    w, h = rect.right - rect.left, rect.bottom - rect.top
    hwnd_dc = user32.GetWindowDC(hwnd)
    mem_dc = gdi32.CreateCompatibleDC(hwnd_dc)
    bitmap = gdi32.CreateCompatibleBitmap(hwnd_dc, w, h)
    gdi32.SelectObject(mem_dc, bitmap)
    user32.PrintWindow(hwnd, mem_dc, 0x00000002)

    class BI(ctypes.Structure):
        _fields_ = [("biSize", wintypes.DWORD), ("biWidth", wintypes.LONG),
                    ("biHeight", wintypes.LONG), ("biPlanes", wintypes.WORD),
                    ("biBitCount", wintypes.WORD), ("biCompression", wintypes.DWORD),
                    ("biSizeImage", wintypes.DWORD), ("biXPelsPerMeter", wintypes.LONG),
                    ("biYPelsPerMeter", wintypes.LONG), ("biClrUsed", wintypes.DWORD),
                    ("biClrImportant", wintypes.DWORD)]
    bmi = BI()
    bmi.biSize = ctypes.sizeof(BI)
    bmi.biWidth = w
    bmi.biHeight = -h
    bmi.biPlanes = 1
    bmi.biBitCount = 32
    bmi.biCompression = 0
    buf = (ctypes.c_ubyte * (w * h * 4))()
    gdi32.GetDIBits(mem_dc, bitmap, 0, h, buf, ctypes.byref(bmi), 0)
    img = Image.frombuffer("RGBA", (w, h), buf, "raw", "BGRA", 0, 1)
    gdi32.DeleteObject(bitmap)
    gdi32.DeleteDC(mem_dc)
    user32.ReleaseDC(hwnd, hwnd_dc)
    return img.convert("RGB")


def main():
    app = App()
    app.state.set_lang("zh-TW")
    app.state.enter_watch_mode()

    def grab():
        app.ui.root.update_idletasks()
        app.ui.root.update()
        hwnd = app.ui.root.winfo_id()
        user32 = ctypes.windll.user32
        try:
            hwnd = user32.GetAncestor(hwnd, 2)
        except Exception:
            pass
        try:
            img = _capture_hwnd(hwnd)
            OUT.parent.mkdir(parents=True, exist_ok=True)
            img.save(OUT)
            print(f"saved: {OUT}  ({img.size})")
        finally:
            app.ui.root.destroy()

    app.ui.root.after(500, grab)
    app.clicker.start()
    try:
        app.ui.run()
    finally:
        app.clicker.stop()


if __name__ == "__main__":
    main()
