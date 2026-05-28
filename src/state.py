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


@dataclass
class State:
    dwell_seconds: float = DWELL_DEFAULT
    auto_click_enabled: bool = True
    autostart_enabled: bool = False
    window_corner: str = "top-right"
    lang: str = DEFAULT_LANG
    compact_mode: bool = False

    _listeners: List[Callable[["State"], None]] = field(
        default_factory=list, repr=False, compare=False
    )

    def to_dict(self) -> dict:
        return {
            "dwell_seconds": self.dwell_seconds,
            "auto_click_enabled": self.auto_click_enabled,
            "autostart_enabled": self.autostart_enabled,
            "window_corner": self.window_corner,
            "lang": self.lang,
            "compact_mode": self.compact_mode,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "State":
        return cls(
            dwell_seconds=_clamp_dwell(data.get("dwell_seconds", DWELL_DEFAULT)),
            auto_click_enabled=bool(data.get("auto_click_enabled", True)),
            autostart_enabled=bool(data.get("autostart_enabled", False)),
            window_corner=_validate_corner(data.get("window_corner", "top-right")),
            lang=_validate_lang(data.get("lang", DEFAULT_LANG)),
            compact_mode=bool(data.get("compact_mode", False)),
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

    def toggle_compact(self) -> None:
        self.compact_mode = not self.compact_mode
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
