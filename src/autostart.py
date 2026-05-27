"""Manage Windows autostart by creating/removing a .lnk in the Startup folder.

Avoids touching the Windows registry per project constraints.
"""
import os
import sys
from pathlib import Path


SHORTCUT_NAME = "HeadMouseHelper.lnk"


def _startup_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        return Path.home() / "Startup"
    return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def _shortcut_path() -> Path:
    return _startup_dir() / SHORTCUT_NAME


def is_enabled() -> bool:
    return _shortcut_path().exists()


def _target_command() -> tuple[str, str]:
    """Return (target, arguments) for the shortcut.

    If running from a frozen exe (PyInstaller), point at the exe directly.
    Otherwise launch via pythonw.exe + the main module.
    """
    if getattr(sys, "frozen", False):
        return sys.executable, ""

    pythonw = Path(sys.executable).with_name("pythonw.exe")
    interp = str(pythonw) if pythonw.exists() else sys.executable

    project_root = Path(__file__).resolve().parent.parent
    return interp, f'-m src.main'


def enable() -> bool:
    if sys.platform != "win32":
        return False

    try:
        import pythoncom
        from win32com.client import Dispatch
    except ImportError:
        return _enable_via_powershell()

    target, args = _target_command()
    startup = _startup_dir()
    startup.mkdir(parents=True, exist_ok=True)

    pythoncom.CoInitialize()
    try:
        shell = Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(str(_shortcut_path()))
        shortcut.TargetPath = target
        shortcut.Arguments = args
        shortcut.WorkingDirectory = str(Path(__file__).resolve().parent.parent)
        shortcut.IconLocation = target
        shortcut.Save()
    finally:
        pythoncom.CoUninitialize()

    return True


def _enable_via_powershell() -> bool:
    import subprocess

    target, args = _target_command()
    startup = _startup_dir()
    startup.mkdir(parents=True, exist_ok=True)

    work_dir = str(Path(__file__).resolve().parent.parent)
    lnk = str(_shortcut_path())

    ps = (
        f"$s=(New-Object -ComObject WScript.Shell).CreateShortcut('{lnk}');"
        f"$s.TargetPath='{target}';"
        f"$s.Arguments='{args}';"
        f"$s.WorkingDirectory='{work_dir}';"
        f"$s.Save()"
    )

    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
            check=True,
            capture_output=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def disable() -> bool:
    lnk = _shortcut_path()
    if lnk.exists():
        try:
            lnk.unlink()
            return True
        except OSError:
            return False
    return True


def sync(enabled: bool) -> bool:
    return enable() if enabled else disable()
