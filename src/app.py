from src import autostart, win32_input
from src.clicker import Clicker
from src.state import State
from src.ui import UI


class App:
    def __init__(self):
        self.state = State.load()
        self.clicker = Clicker(self.state, is_over_app_window=self._is_over_window)
        self.ui = UI(
            state=self.state,
            on_left_click=self._do_left_click,
            on_double_click=self._do_double_click,
            on_right_click=self._do_right_click,
            on_toggle_auto=self._toggle_auto,
            on_move_corner=self._move_corner,
            on_dwell_change=self.state.set_dwell,
            on_autostart_change=self._set_autostart,
        )

    def _is_over_window(self, x: int, y: int) -> bool:
        try:
            root = self.ui.root
            wx = root.winfo_rootx()
            wy = root.winfo_rooty()
            ww = root.winfo_width()
            wh = root.winfo_height()
            return wx <= x <= wx + ww and wy <= y <= wy + wh
        except Exception:
            return False

    def _do_left_click(self) -> None:
        self.ui.schedule(win32_input.left_click, delay_ms=120)

    def _do_double_click(self) -> None:
        self.ui.schedule(win32_input.double_click, delay_ms=120)

    def _do_right_click(self) -> None:
        self.ui.schedule(win32_input.right_click, delay_ms=120)

    def _toggle_auto(self) -> None:
        self.state.toggle_auto_click()

    def _move_corner(self, corner: str) -> None:
        self.state.set_corner(corner)
        self.ui.move_to_corner(corner)

    def _set_autostart(self, enabled: bool) -> None:
        ok = autostart.sync(enabled)
        self.state.set_autostart(enabled if ok else autostart.is_enabled())

    def run(self) -> None:
        self.clicker.start()
        try:
            self.ui.run()
        finally:
            self.clicker.stop()
