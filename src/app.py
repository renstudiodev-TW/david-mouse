from src import autostart, win32_input
from src.clicker import Clicker
from src.state import State
from src.ui import UI


# How long the user has to move their cursor to the target after dwell-clicking
# an action button (L / R / Double). Head-mouse users need plenty of time.
ACTION_COUNTDOWN_S = 2.5
# Pause the auto-clicker slightly longer than the countdown so the dwell
# engine doesn't fire an extra click at the destination.
ACTION_PAUSE_PAD_S = 0.7


class App:
    def __init__(self):
        self.state = State.load()
        self.clicker = Clicker(self.state, is_over_resume_zone=self._is_over_pause_button)
        self.ui = UI(
            state=self.state,
            on_left_click=self._do_left_click,
            on_double_click=self._do_double_click,
            on_right_click=self._do_right_click,
            on_toggle_auto=self._toggle_auto,
            on_move_corner=self._move_corner,
            on_dwell_change=self.state.set_dwell,
            on_autostart_change=self._set_autostart,
            on_lang_change=self.state.set_lang,
            on_toggle_compact=self.state.toggle_compact,
            on_enter_watch=self.state.enter_watch_mode,
            on_exit_watch=self.state.exit_watch_mode,
            on_dictation=self._do_dictation,
        )
        # 設定檔可能跟實際狀況不同步（例如使用者手動刪了排程工作），以系統現況為準。
        self._sync_autostart_ui()
        if self.state.autostart_enabled != autostart.is_enabled():
            self.state.set_autostart(autostart.is_enabled())

    def _is_over_pause_button(self, x: int, y: int) -> bool:
        try:
            btn = self.ui.pause_btn
            bx = btn.winfo_rootx()
            by = btn.winfo_rooty()
            bw = btn.winfo_width()
            bh = btn.winfo_height()
            return bx <= x <= bx + bw and by <= y <= by + bh
        except Exception:
            return False

    def _arm_action(self, label_key: str, fn) -> None:
        self.clicker.temporary_pause(ACTION_COUNTDOWN_S + ACTION_PAUSE_PAD_S)
        self.ui.start_countdown(label_key, ACTION_COUNTDOWN_S, fire=fn)

    def _do_left_click(self) -> None:
        self._arm_action("countdown_left", win32_input.left_click)

    def _do_double_click(self) -> None:
        self._arm_action("countdown_double", win32_input.double_click)

    def _do_right_click(self) -> None:
        self._arm_action("countdown_right", win32_input.right_click)

    def _do_dictation(self) -> None:
        self._arm_action("countdown_dictation", win32_input.dictation)

    def _toggle_auto(self) -> None:
        self.state.toggle_auto_click()

    def _move_corner(self, corner: str) -> None:
        self.state.set_corner(corner)
        self.ui.move_to_corner(corner)

    def _set_autostart(self, enabled: bool) -> None:
        ok = autostart.sync(enabled)
        self.state.set_autostart(enabled if ok else autostart.is_enabled())
        self._sync_autostart_ui()

    def _sync_autostart_ui(self) -> None:
        """把「自動啟動是不是系統管理員模式」告訴 UI，讓按鈕文字能區分。"""
        self.ui.set_autostart_admin(autostart.is_admin_autostart())

    def run(self) -> None:
        self.clicker.start()
        try:
            self.ui.run()
        finally:
            self.clicker.stop()
