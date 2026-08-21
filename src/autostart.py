"""管理 David Mouse 的開機自動啟動。

兩種模式，優先順序如下：

1. **工作排程器（Task Scheduler）**：登入時觸發、以「最高可用權限」執行。
   這是唯一能讓程式開機就自動取得系統管理員權限的方式，而且不會跳 UAC。
   建立這種工作本身需要系統管理員權限，所以只有在目前這個 process 已經
   是系統管理員時才做得到。
2. **啟動資料夾捷徑（.lnk）**：沒有系統管理員權限時的退路。程式會自動啟動，
   但是以一般權限執行。

註：Windows 的「啟動」資料夾**沒辦法**啟動需要提權的程式，就算把捷徑勾了
「以系統管理員身分執行」，UAC 也會直接擋掉、程式不會跑起來。這就是為什麼
要走工作排程器。

依專案限制，全程不寫 Windows 登錄檔（registry）。
"""
import ctypes
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape


SHORTCUT_NAME = "DavidMouse.lnk"
# 舊檔名，disable() 時一併清掉，避免改名後在啟動資料夾留下孤兒捷徑。
LEGACY_SHORTCUT_NAMES = ("HeadMouseHelper.lnk",)

TASK_NAME = "DavidMouse"
# 登入後延遲幾秒再啟動，讓桌面先載入完成，避免視窗被其他程式蓋掉。
TASK_LOGON_DELAY = "PT15S"

# 模式代號
MODE_NONE = "none"
MODE_TASK = "task"
MODE_SHORTCUT = "shortcut"

_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)


# --------------------------------------------------------------------------
# 共用工具
# --------------------------------------------------------------------------
def is_admin() -> bool:
    """目前的 process 是不是以系統管理員身分執行。"""
    if sys.platform != "win32":
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def _run(args: list[str]) -> subprocess.CompletedProcess:
    """執行外部指令，不彈出主控台視窗（本程式是 --noconsole 打包）。"""
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=_NO_WINDOW,
    )


def _target_command() -> tuple[str, str]:
    """回傳 (執行檔, 參數)。

    打包成 exe（PyInstaller）時直接指向 exe；
    原始碼執行時用 pythonw.exe 跑 src.main。
    """
    if getattr(sys, "frozen", False):
        return sys.executable, ""

    pythonw = Path(sys.executable).with_name("pythonw.exe")
    interp = str(pythonw) if pythonw.exists() else sys.executable
    return interp, "-m src.main"


def _work_dir() -> str:
    if getattr(sys, "frozen", False):
        return str(Path(sys.executable).resolve().parent)
    return str(Path(__file__).resolve().parent.parent)


def _account_name() -> str:
    """目前使用者的帳號全名（DOMAIN\\user），寫進工作排程的 XML。"""
    domain = os.environ.get("USERDOMAIN") or os.environ.get("COMPUTERNAME") or ""
    user = os.environ.get("USERNAME") or ""
    return f"{domain}\\{user}" if domain else user


# --------------------------------------------------------------------------
# 模式一：工作排程器（以系統管理員權限自動啟動）
# --------------------------------------------------------------------------
def _task_xml() -> str:
    target, args = _target_command()
    account = escape(_account_name())

    arguments = f"      <Arguments>{escape(args)}</Arguments>\n" if args else ""

    return (
        '<?xml version="1.0" encoding="UTF-16"?>\n'
        '<Task version="1.2" '
        'xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">\n'
        "  <RegistrationInfo>\n"
        "    <Description>David Mouse 大衛滑鼠：登入時以系統管理員權限自動啟動。"
        "</Description>\n"
        "  </RegistrationInfo>\n"
        "  <Triggers>\n"
        "    <LogonTrigger>\n"
        "      <Enabled>true</Enabled>\n"
        f"      <UserId>{account}</UserId>\n"
        f"      <Delay>{TASK_LOGON_DELAY}</Delay>\n"
        "    </LogonTrigger>\n"
        "  </Triggers>\n"
        "  <Principals>\n"
        '    <Principal id="Author">\n'
        f"      <UserId>{account}</UserId>\n"
        "      <LogonType>InteractiveToken</LogonType>\n"
        "      <RunLevel>HighestAvailable</RunLevel>\n"
        "    </Principal>\n"
        "  </Principals>\n"
        "  <Settings>\n"
        "    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>\n"
        # 筆電使用者很重要：預設值會讓工作在電池模式下不啟動、插頭一拔就被停掉。
        "    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>\n"
        "    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>\n"
        "    <AllowHardTerminate>true</AllowHardTerminate>\n"
        "    <StartWhenAvailable>false</StartWhenAvailable>\n"
        "    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>\n"
        "    <IdleSettings>\n"
        "      <StopOnIdleEnd>false</StopOnIdleEnd>\n"
        "      <RestartOnIdle>false</RestartOnIdle>\n"
        "    </IdleSettings>\n"
        "    <AllowStartOnDemand>true</AllowStartOnDemand>\n"
        "    <Enabled>true</Enabled>\n"
        "    <Hidden>false</Hidden>\n"
        "    <RunOnlyIfIdle>false</RunOnlyIfIdle>\n"
        "    <WakeToRun>false</WakeToRun>\n"
        # PT0S＝不限制執行時間，預設的三天上限會把長時間開機的程式砍掉。
        "    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>\n"
        "    <Priority>7</Priority>\n"
        "  </Settings>\n"
        '  <Actions Context="Author">\n'
        "    <Exec>\n"
        f"      <Command>{escape(target)}</Command>\n"
        f"{arguments}"
        f"      <WorkingDirectory>{escape(_work_dir())}</WorkingDirectory>\n"
        "    </Exec>\n"
        "  </Actions>\n"
        "</Task>\n"
    )


def task_exists() -> bool:
    if sys.platform != "win32":
        return False
    try:
        return _run(["schtasks", "/Query", "/TN", TASK_NAME]).returncode == 0
    except OSError:
        return False


def _enable_task() -> bool:
    """建立（或覆寫）登入時以最高權限執行的排程工作。需要系統管理員權限。"""
    if sys.platform != "win32":
        return False

    tmp = Path(tempfile.gettempdir()) / f"{TASK_NAME}-task.xml"
    try:
        # schtasks /XML 只吃 Unicode（UTF-16）檔案，寫成 UTF-8 會被判為格式錯誤。
        tmp.write_text(_task_xml(), encoding="utf-16")
        result = _run(["schtasks", "/Create", "/TN", TASK_NAME, "/XML", str(tmp), "/F"])
        return result.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass


def _disable_task() -> bool:
    if sys.platform != "win32":
        return True
    if not task_exists():
        return True
    try:
        return _run(["schtasks", "/Delete", "/TN", TASK_NAME, "/F"]).returncode == 0
    except OSError:
        return False


# --------------------------------------------------------------------------
# 模式二：啟動資料夾捷徑（一般權限的退路）
# --------------------------------------------------------------------------
def _startup_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        return Path.home() / "Startup"
    return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def _shortcut_path() -> Path:
    return _startup_dir() / SHORTCUT_NAME


def shortcut_exists() -> bool:
    return _shortcut_path().exists()


def _enable_shortcut() -> bool:
    if sys.platform != "win32":
        return False

    try:
        import pythoncom
        from win32com.client import Dispatch
    except ImportError:
        return _enable_shortcut_via_powershell()

    target, args = _target_command()
    startup = _startup_dir()
    startup.mkdir(parents=True, exist_ok=True)

    pythoncom.CoInitialize()
    try:
        shell = Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(str(_shortcut_path()))
        shortcut.TargetPath = target
        shortcut.Arguments = args
        shortcut.WorkingDirectory = _work_dir()
        shortcut.IconLocation = target
        shortcut.Save()
    finally:
        pythoncom.CoUninitialize()

    return True


def _enable_shortcut_via_powershell() -> bool:
    target, args = _target_command()
    startup = _startup_dir()
    startup.mkdir(parents=True, exist_ok=True)

    lnk = str(_shortcut_path())

    ps = (
        f"$s=(New-Object -ComObject WScript.Shell).CreateShortcut('{lnk}');"
        f"$s.TargetPath='{target}';"
        f"$s.Arguments='{args}';"
        f"$s.WorkingDirectory='{_work_dir()}';"
        f"$s.Save()"
    )

    try:
        result = _run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps])
        return result.returncode == 0
    except OSError:
        return False


def _disable_shortcut() -> bool:
    ok = True
    targets = [_shortcut_path()] + [_startup_dir() / name for name in LEGACY_SHORTCUT_NAMES]
    for lnk in targets:
        if not lnk.exists():
            continue
        try:
            lnk.unlink()
        except OSError:
            ok = False
    return ok


# --------------------------------------------------------------------------
# 對外介面
# --------------------------------------------------------------------------
def current_mode() -> str:
    """目前的自動啟動狀態：MODE_TASK / MODE_SHORTCUT / MODE_NONE。"""
    if task_exists():
        return MODE_TASK
    if shortcut_exists():
        return MODE_SHORTCUT
    return MODE_NONE


def is_enabled() -> bool:
    return current_mode() != MODE_NONE


def is_admin_autostart() -> bool:
    """自動啟動是否會以系統管理員權限執行。"""
    return current_mode() == MODE_TASK


def enable() -> bool:
    """開啟自動啟動。有系統管理員權限就用排程工作，否則退回啟動資料夾捷徑。"""
    if sys.platform != "win32":
        return False

    if is_admin() and _enable_task():
        # 兩種都在會啟動兩份，排程工作建好就把捷徑清掉。
        _disable_shortcut()
        return True

    _disable_task()
    return _enable_shortcut()


def disable() -> bool:
    task_ok = _disable_task()
    lnk_ok = _disable_shortcut()
    return task_ok and lnk_ok


def sync(enabled: bool) -> bool:
    return enable() if enabled else disable()
