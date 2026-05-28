import json
import os
import tempfile
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Callable, List


SETTINGS_DIR = Path(os.environ.get("APPDATA", str(Path.home()))) / "DavidMouse"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"

DWELL_MIN = 0.5
DWELL_MAX = 3.0
DWELL_DEFAULT = 1.0

VALID_CORNERS = ("top-left", "top-right", "bottom-left", "bottom-right")
VALID_LANGS = ("zh-TW", "en", "ja", "ko")
DEFAULT_LANG = "zh-TW"

# View modes:
#   "full"    — every control visible (260x470)
#   "compact" — just PAUSE + corner arrows (220x180)
#   "watch"   — tiny recovery-only widget (e.g. 90x90), auto-click paused.
#               Designed for "watching/singing YouTube" without the window
#               blocking the video, while head-mouse jitter can't trigger any
#               accidental clicks.
VALID_VIEW_MODES = ("full", "compact", "watch")


@dataclass
class State:
    dwell_seconds: float = DWELL_DEFAULT
    auto_click_enabled: bool = True
    autostart_enabled: bool = False
    window_corner: str = "top-right"
    lang: str = DEFAULT_LANG
    view_mode: str = "full"
    # Where to return to when leaving watch mode. Tracked so a user who entered
    # watch from compact returns to compact, not full.
    pre_watch_view_mode: str = "full"

    _listeners: List[Callable[["State"], None]] = field(
        default_factory=list, repr=False, compare=False
    )

    @property
    def compact_mode(self) -> bool:
        # Back-compat for tests / external readers that still ask in boolean.
        return self.view_mode == "compact"

    def to_dict(self) -> dict:
        return {
            "dwell_seconds": self.dwell_seconds,
            "auto_click_enabled": self.auto_click_enabled,
            "autostart_enabled": self.autostart_enabled,
            "window_corner": self.window_corner,
            "lang": self.lang,
            "view_mode": self.view_mode,
            "pre_watch_view_mode": self.pre_watch_view_mode,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "State":
        # Migrate old `compact_mode` bool → new `view_mode` enum.
        view_mode = data.get("view_mode")
        if view_mode is None:
            view_mode = "compact" if data.get("compact_mode") else "full"
        view_mode = _validate_view_mode(view_mode)

        pre_watch = _validate_view_mode(data.get("pre_watch_view_mode", "full"))
        if pre_watch == "watch":
            pre_watch = "full"

        # Booting up directly into "watch" is unfriendly — auto-click would be
        # off and only a tiny recovery widget would be visible. Fall back to
        # the user's pre-watch mode and re-enable auto-click so the next launch
        # starts in a usable state.
        auto = bool(data.get("auto_click_enabled", True))
        if view_mode == "watch":
            view_mode = pre_watch
            auto = True

        return cls(
            dwell_seconds=_clamp_dwell(data.get("dwell_seconds", DWELL_DEFAULT)),
            auto_click_enabled=auto,
            autostart_enabled=bool(data.get("autostart_enabled", False)),
            window_corner=_validate_corner(data.get("window_corner", "top-right")),
            lang=_validate_lang(data.get("lang", DEFAULT_LANG)),
            view_mode=view_mode,
            pre_watch_view_mode=pre_watch,
        )

    def subscribe(self, callback: Callable[["State"], None]) -> None:
        self._listeners.append(callback)

    def _notify(self) -> None:
        for cb in self._listeners:
            cb(self)

    def set_dwell(self, value: float) -> None:
        self.dwell_seconds = _clamp_dwell(value)
        self.save()
        self._notify()

    def toggle_auto_click(self) -> None:
        self.auto_click_enabled = not self.auto_click_enabled
        self.save()
        self._notify()

    def set_autostart(self, enabled: bool) -> None:
        self.autostart_enabled = bool(enabled)
        self.save()
        self._notify()

    def set_corner(self, corner: str) -> None:
        self.window_corner = _validate_corner(corner)
        self.save()
        self._notify()

    def set_lang(self, lang: str) -> None:
        self.lang = _validate_lang(lang)
        self.save()
        self._notify()

    def set_view_mode(self, mode: str) -> None:
        self.view_mode = _validate_view_mode(mode)
        self.save()
        self._notify()

    def toggle_compact(self) -> None:
        # Toggles between full and compact only. Watch mode has its own entry
        # and exit so the user always knows how to escape it.
        self.view_mode = "full" if self.view_mode == "compact" else "compact"
        self.save()
        self._notify()

    def enter_watch_mode(self) -> None:
        """Atomic transition for the 'Watch Mode' button: remember the current
        view as the return target, pause auto-click, and switch to the tiny
        recovery-only widget."""
        if self.view_mode != "watch":
            self.pre_watch_view_mode = self.view_mode
        self.view_mode = "watch"
        self.auto_click_enabled = False
        self.save()
        self._notify()

    def exit_watch_mode(self) -> None:
        """Atomic exit for the recovery button: re-enable auto-click and return
        to whichever mode we were in before."""
        target = self.pre_watch_view_mode if self.pre_watch_view_mode != "watch" else "full"
        self.view_mode = target
        self.auto_click_enabled = True
        self.save()
        self._notify()

    def save(self) -> None:
        SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(dir=str(SETTINGS_DIR), prefix=".settings-", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=2)
            os.replace(tmp_path, SETTINGS_FILE)
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    @classmethod
    def load(cls) -> "State":
        if not SETTINGS_FILE.exists():
            return cls()
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except (json.JSONDecodeError, OSError):
            return cls()


def _clamp_dwell(value: float) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return DWELL_DEFAULT
    return max(DWELL_MIN, min(DWELL_MAX, v))


def _validate_corner(corner: str) -> str:
    return corner if corner in VALID_CORNERS else "top-right"


def _validate_lang(lang: str) -> str:
    return lang if lang in VALID_LANGS else DEFAULT_LANG


def _validate_view_mode(mode: str) -> str:
    return mode if mode in VALID_VIEW_MODES else "full"
