"""i18n string tables for David Mouse.

Add new keys here. Supported: zh-TW (default), en, ja, ko.
"""
from typing import Dict


STRINGS: Dict[str, Dict[str, str]] = {
    "zh-TW": {
        "app_title": "David Mouse 大衛滑鼠",
        "auto_on": "● 自動點擊中",
        "auto_paused": "⏸ 已暫停\n停留此處可恢復",
        "btn_left": "◐ 左鍵",
        "btn_right": "◑ 右鍵",
        "btn_double": "◐◐ 雙擊",
        "dwell_label": "停留時間：{value} 秒",
        "autostart": "開機自動啟動",
        "autostart_on": "✔ 開機自動啟動：開",
        "autostart_off": "✘ 開機自動啟動：關",
        "lang_label": "語言",
        "countdown_left": "{n} 秒後左鍵點擊",
        "countdown_right": "{n} 秒後右鍵點擊",
        "countdown_double": "{n} 秒後雙擊",
        "countdown_fire": "點擊！",
        "move_now": "移動游標到目標",
        "compact": "🗗 精簡",
        "expand": "🗖 展開",
    },
    "en": {
        "app_title": "David Mouse",
        "auto_on": "● AUTO-CLICK ON",
        "auto_paused": "⏸ PAUSED\nDwell here to resume",
        "btn_left": "◐ Left",
        "btn_right": "◑ Right",
        "btn_double": "◐◐ Double",
        "dwell_label": "Dwell time: {value} s",
        "autostart": "Start with Windows",
        "autostart_on": "✔ Start with Windows: ON",
        "autostart_off": "✘ Start with Windows: OFF",
        "lang_label": "Language",
        "countdown_left": "Left click in {n}s",
        "countdown_right": "Right click in {n}s",
        "countdown_double": "Double click in {n}s",
        "countdown_fire": "Click!",
        "move_now": "Move cursor to target",
        "compact": "🗗 Compact",
        "expand": "🗖 Expand",
    },
    "ja": {
        "app_title": "David Mouse デビッドマウス",
        "auto_on": "● 自動クリック中",
        "auto_paused": "⏸ 一時停止\nここに留まると再開",
        "btn_left": "◐ 左クリック",
        "btn_right": "◑ 右クリック",
        "btn_double": "◐◐ ダブル",
        "dwell_label": "ホールド時間：{value} 秒",
        "autostart": "Windows起動時に開始",
        "autostart_on": "✔ 起動時に開始：ON",
        "autostart_off": "✘ 起動時に開始：OFF",
        "lang_label": "言語",
        "countdown_left": "{n} 秒後に左クリック",
        "countdown_right": "{n} 秒後に右クリック",
        "countdown_double": "{n} 秒後にダブル",
        "countdown_fire": "クリック！",
        "move_now": "カーソルを目標へ移動",
        "compact": "🗗 コンパクト",
        "expand": "🗖 展開",
    },
    "ko": {
        "app_title": "David Mouse 데이비드 마우스",
        "auto_on": "● 자동 클릭 중",
        "auto_paused": "⏸ 일시정지\n여기에 머무르면 재개",
        "btn_left": "◐ 왼쪽",
        "btn_right": "◑ 오른쪽",
        "btn_double": "◐◐ 더블",
        "dwell_label": "머무름 시간: {value} 초",
        "autostart": "Windows 시작 시 실행",
        "autostart_on": "✔ 시작 시 실행: 켜짐",
        "autostart_off": "✘ 시작 시 실행: 꺼짐",
        "lang_label": "언어",
        "countdown_left": "{n} 초 후 왼쪽 클릭",
        "countdown_right": "{n} 초 후 오른쪽 클릭",
        "countdown_double": "{n} 초 후 더블",
        "countdown_fire": "클릭!",
        "move_now": "커서를 목표로 이동",
        "compact": "🗗 축소",
        "expand": "🗖 확장",
    },
}


SUPPORTED_LANGS = tuple(STRINGS.keys())
LANG_DISPLAY = {
    "zh-TW": "繁中",
    "en": "EN",
    "ja": "JP",
    "ko": "KR",
}


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
