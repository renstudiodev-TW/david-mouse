"""確保同一位使用者同時只會有一個 David Mouse 在跑。

為什麼需要：使用者很可能在程式已經縮在角落時又點一次桌面捷徑，或是排程工作
已經幫他開好了、他自己又開一次。跑出兩份的話，一份在自動點擊、另一份顯示
暫停中，畫面互相矛盾，對頭控使用者非常混亂。

做法是在設定資料夾放一個鎖檔，用作業系統層級的獨占鎖（`msvcrt.locking`）鎖住
第一個位元組。鎖由作業系統在程序結束時自動釋放，所以就算上次是當機收場，也不會
留下解不開的死鎖。

為什麼不用具名 Mutex：以系統管理員權限啟動的那一份（工作排程）跟使用者手動開的
那一份完整性等級不同，較低等級的程序不一定打得開高等級程序建立的核心物件，會誤判
成「沒有其他實例」。鎖檔放在使用者自己的 AppData 底下，兩種權限都存取得到。

例外：使用者刻意以系統管理員身分重開一份（例如某些遊戲視窗只認得系統管理員權限
送出的點擊，一般權限的 David Mouse 點不進去），這時新開的這份應該要接手，而不是
被舊的一般權限實例擋下來、只是把舊視窗叫到前面——那樣使用者永遠開不出他真正需要
的那份。做法是：搶鎖失敗時，如果目前這個 process 本身是系統管理員，就直接關掉舊
的那份程序再重新搶鎖。方向反過來（一般權限想接管系統管理員那份）不會發生，一般
權限本來就打不開系統管理員程序的控制代碼，維持原本「叫到前面就好」的行為。
"""
import ctypes
import os
import sys
from ctypes import wintypes
from pathlib import Path

from src import state


LOCK_FILENAME = "instance.lock"
PID_FILENAME = "instance.pid"

# 全域保留鎖檔的 fd。被垃圾回收關掉的話鎖會提早釋放，等於沒鎖。
_lock_fd = None

_PROCESS_TERMINATE = 0x0001
_SYNCHRONIZE = 0x00100000
_TERMINATE_WAIT_MS = 2000


def _lock_path() -> Path:
    return state.SETTINGS_DIR / LOCK_FILENAME


def _pid_path() -> Path:
    return state.SETTINGS_DIR / PID_FILENAME


def acquire() -> bool:
    """搶下單一實例的鎖。回傳 False 代表已經有另一份在跑（而且接手不了）。"""
    if sys.platform != "win32":
        return True

    if _try_acquire():
        return True

    if _take_over_from_lower_privilege():
        return _try_acquire()

    return False


def _try_acquire() -> bool:
    global _lock_fd

    try:
        state.SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(_lock_path()), os.O_RDWR | os.O_CREAT, 0o600)
    except OSError:
        # 連鎖檔都開不了就別擋使用者，寧可放行也不要讓程式打不開。
        return True

    try:
        import msvcrt

        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
    except OSError:
        os.close(fd)
        return False

    _lock_fd = fd
    _write_pid()
    return True


def _take_over_from_lower_privilege() -> bool:
    """目前這個 process 是系統管理員時，強制關掉舊的那份讓這份接手。"""
    from src.autostart import is_admin

    if not is_admin():
        return False

    pid = _read_pid()
    if pid <= 0 or pid == os.getpid():
        return False

    return _terminate_pid(pid)


def _terminate_pid(pid: int, timeout_ms: int = _TERMINATE_WAIT_MS) -> bool:
    """強制關閉指定 pid，並等到它真的結束再回傳，讓鎖檔確實釋放。"""
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.OpenProcess(_PROCESS_TERMINATE | _SYNCHRONIZE, False, pid)
    if not handle:
        # 開不到，可能程序早就不在了；當作已經結束，讓外層重試搶鎖。
        return True
    try:
        kernel32.TerminateProcess(handle, 0)
        kernel32.WaitForSingleObject(handle, timeout_ms)
        return True
    finally:
        kernel32.CloseHandle(handle)


def release() -> None:
    """釋放鎖並清掉 pid 檔。程序結束時作業系統也會自動釋放，這裡只是收乾淨。"""
    global _lock_fd

    if _lock_fd is None:
        return

    try:
        import msvcrt

        os.lseek(_lock_fd, 0, os.SEEK_SET)
        msvcrt.locking(_lock_fd, msvcrt.LK_UNLCK, 1)
    except OSError:
        pass

    try:
        os.close(_lock_fd)
    except OSError:
        pass
    _lock_fd = None

    try:
        _pid_path().unlink(missing_ok=True)
    except OSError:
        pass


def _write_pid() -> None:
    try:
        _pid_path().write_text(str(os.getpid()), encoding="ascii")
    except OSError:
        pass


def _read_pid() -> int:
    try:
        return int(_pid_path().read_text(encoding="ascii").strip())
    except (OSError, ValueError):
        return 0


# --------------------------------------------------------------------------
# 把已經在跑的那個視窗叫到前面來
# --------------------------------------------------------------------------
_SW_RESTORE = 9
_FLASHW_ALL = 0x00000003
_FLASHW_TIMERNOFG = 0x0000000C


class _FLASHWINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.UINT),
        ("hwnd", wintypes.HWND),
        ("dwFlags", wintypes.DWORD),
        ("uCount", wintypes.UINT),
        ("dwTimeout", wintypes.DWORD),
    ]


def _windows_of_pid(pid: int) -> list:
    """列出屬於某個程序、看得見而且有標題的最上層視窗。"""
    user32 = ctypes.windll.user32
    found = []

    enum_proc = ctypes.WINFUNCTYPE(
        wintypes.BOOL, wintypes.HWND, wintypes.LPARAM
    )

    def callback(hwnd, _lparam):
        owner = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
        if owner.value != pid:
            return True
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            found.append(hwnd)
        return True

    user32.EnumWindows(enum_proc(callback), 0)
    return found


def focus_existing() -> bool:
    """把先開的那份叫到最前面。找不到就安靜放棄，不要跳訊息框嚇到使用者。"""
    if sys.platform != "win32":
        return False

    pid = _read_pid()
    if pid <= 0:
        return False

    try:
        windows = _windows_of_pid(pid)
    except Exception:
        return False

    if not windows:
        return False

    user32 = ctypes.windll.user32
    hwnd = windows[0]
    try:
        user32.ShowWindow(hwnd, _SW_RESTORE)
        user32.SetForegroundWindow(hwnd)
        # 閃一下標題列，讓使用者知道程式其實已經開著了。
        info = _FLASHWINFO(
            cbSize=ctypes.sizeof(_FLASHWINFO),
            hwnd=hwnd,
            dwFlags=_FLASHW_ALL | _FLASHW_TIMERNOFG,
            uCount=3,
            dwTimeout=0,
        )
        user32.FlashWindowEx(ctypes.byref(info))
    except Exception:
        return False

    return True
