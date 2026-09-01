"""ctypes wrappers around Win32 SendInput / SetCursorPos / GetCursorPos.

Falls back to pynput on non-Windows platforms (only for dev/test ergonomics).
"""
import ctypes
import sys
import time
from ctypes import wintypes


_IS_WIN = sys.platform == "win32"

MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1

KEYEVENTF_KEYUP = 0x0002

VK_CONTROL = 0x11
# US 鍵盤配置下「/」鍵的虛擬鍵碼，當 VkKeyScanW 查不到時的備援。
VK_OEM_2_FALLBACK = 0xBF


if _IS_WIN:
    ULONG_PTR = ctypes.c_size_t

    class _MOUSEINPUT(ctypes.Structure):
        _fields_ = [
            ("dx", wintypes.LONG),
            ("dy", wintypes.LONG),
            ("mouseData", wintypes.DWORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ULONG_PTR),
        ]

    class _KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", wintypes.WORD),
            ("wScan", wintypes.WORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ULONG_PTR),
        ]

    class _HARDWAREINPUT(ctypes.Structure):
        _fields_ = [
            ("uMsg", wintypes.DWORD),
            ("wParamL", wintypes.WORD),
            ("wParamH", wintypes.WORD),
        ]

    class _INPUT_UNION(ctypes.Union):
        _fields_ = [
            ("mi", _MOUSEINPUT),
            ("ki", _KEYBDINPUT),
            ("hi", _HARDWAREINPUT),
        ]

    class _INPUT(ctypes.Structure):
        _anonymous_ = ("u",)
        _fields_ = [
            ("type", wintypes.DWORD),
            ("u", _INPUT_UNION),
        ]

    _user32 = ctypes.WinDLL("user32", use_last_error=True)
    _SendInput = _user32.SendInput
    _SendInput.argtypes = (wintypes.UINT, ctypes.POINTER(_INPUT), ctypes.c_int)
    _SendInput.restype = wintypes.UINT


def get_cursor_pos() -> tuple[int, int]:
    if _IS_WIN:
        pt = wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        return pt.x, pt.y
    return (0, 0)


def set_cursor_pos(x: int, y: int) -> None:
    if _IS_WIN:
        ctypes.windll.user32.SetCursorPos(int(x), int(y))


def _send_mouse_event(flags: int) -> None:
    if not _IS_WIN:
        return
    inp = _INPUT(type=INPUT_MOUSE)
    inp.mi = _MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=flags, time=0, dwExtraInfo=0)
    _SendInput(1, ctypes.byref(inp), ctypes.sizeof(_INPUT))


def left_click() -> None:
    _send_mouse_event(MOUSEEVENTF_LEFTDOWN)
    _send_mouse_event(MOUSEEVENTF_LEFTUP)


def right_click() -> None:
    _send_mouse_event(MOUSEEVENTF_RIGHTDOWN)
    _send_mouse_event(MOUSEEVENTF_RIGHTUP)


def double_click() -> None:
    left_click()
    time.sleep(0.05)
    left_click()


def _send_key_event(vk: int, flags: int = 0) -> None:
    if not _IS_WIN:
        return
    inp = _INPUT(type=INPUT_KEYBOARD)
    inp.ki = _KEYBDINPUT(wVk=vk, wScan=0, dwFlags=flags, time=0, dwExtraInfo=0)
    _SendInput(1, ctypes.byref(inp), ctypes.sizeof(_INPUT))


def _vk_for_char(ch: str) -> int:
    """用目前的鍵盤配置查字元對應的虛擬鍵碼，查不到就回 0。"""
    if not _IS_WIN:
        return 0
    res = ctypes.windll.user32.VkKeyScanW(ord(ch))
    if res == -1:
        return 0
    return res & 0xFF


def ctrl_slash() -> None:
    """送出 Ctrl+/ 組合鍵，用來觸發 ChatGPT 桌面版的語音聽寫快捷鍵。

    鍵盤事件只會送到目前有焦點的視窗，不會跟著游標位置跑，所以呼叫前一定
    要先用 left_click() 在目標視窗（例如 ChatGPT 輸入框）點一下取得焦點，
    否則這個組合鍵會送到剛才按下 David Mouse 按鈕、目前仍持有焦點的
    David Mouse 視窗本身，而不是使用者真正想要的目標視窗。見 dictation()。
    """
    if not _IS_WIN:
        return
    vk_slash = _vk_for_char("/") or VK_OEM_2_FALLBACK
    _send_key_event(VK_CONTROL)
    _send_key_event(vk_slash)
    _send_key_event(vk_slash, KEYEVENTF_KEYUP)
    _send_key_event(VK_CONTROL, KEYEVENTF_KEYUP)


def dictation() -> None:
    """先在目前游標位置點一下左鍵取得焦點（跟 left_click 按鈕一樣，倒數期間
    使用者會把游標移到 ChatGPT 輸入框），再送出 Ctrl+/ 觸發語音聽寫。
    """
    left_click()
    time.sleep(0.05)
    ctrl_slash()


def get_screen_size() -> tuple[int, int]:
    if _IS_WIN:
        SM_CXSCREEN = 0
        SM_CYSCREEN = 1
        w = ctypes.windll.user32.GetSystemMetrics(SM_CXSCREEN)
        h = ctypes.windll.user32.GetSystemMetrics(SM_CYSCREEN)
        return int(w), int(h)
    return (1920, 1080)
