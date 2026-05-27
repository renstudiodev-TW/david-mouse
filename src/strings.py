"""i18n string tables for HeadMouse Helper.

Add new keys here. Two languages: zh-TW (default) and en.
"""
from typing import Dict


STRINGS: Dict[str, Dict[str, str]] = {
    "zh-TW": {
        "app_title": "HeadMouse Helper 頭控滑鼠助手",
        "auto_on": "● 自動點擊中",
        "auto_paused": "⏸ 已暫停",
        "btn_left": "◐ 左鍵",
        "btn_right": "◑ 右鍵",
        "btn_double": "◐◐ 雙擊",
        "dwell_label": "停留時間：{value} 秒",
        "autostart": "開機自動啟動",
        "lang_label": "語言",
        "countdown_left": "{n} 秒後左鍵點擊",
        "countdown_right": "{n} 秒後右鍵點擊",
        "countdown_double": "{n} 秒後雙擊",
        "countdown_fire": "點擊！",
        "move_now": "移動游標到目標",
    },
    "en": {
        "app_title": "HeadMouse Helper",
        "auto_on": "● AUTO-CLICK ON",
        "auto_paused": "⏸ PAUSED",
        "btn_left": "◐ Left",
        "btn_right": "◑ Right",
        "btn_double": "◐◐ Double",
        "dwell_label": "Dwell time: {value} s",
        "autostart": "Start with Windows",
        "lang_label": "Language",
        "countdown_left": "Left click in {n}s",
        "countdown_right": "Right click in {n}s",
        "countdown_double": "Double click in {n}s",
        "countdown_fire": "Click!",
        "move_now": "Move cursor to target",
    },
}


SUPPORTED_LANGS = tuple(STRINGS.keys())
LANG_DISPLAY = {"zh-TW": "中文", "en": "English"}


def t(lang: str, key: str, **kwargs) -> str:
    """Translate a string key. Falls back to zh-TW, then to the key itself."""
    table = STRINGS.get(lang) or STRINGS["zh-TW"]
    value = table.get(key) or STRINGS["zh-TW"].get(key) or key
    if kwargs:
        try:
            return value.format(**kwargs)
        except (KeyError, IndexError):
            return value
    return value
