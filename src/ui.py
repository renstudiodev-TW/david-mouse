"""Tkinter UI: full mode (all controls) + compact mode (just PAUSE + expand).

High contrast, large click targets for head-mouse users.
"""
import tkinter as tk
import webbrowser
from typing import Callable, Optional

from src.corners import WINDOW_W, WINDOW_H, geometry_string
from src.state import State, DWELL_MIN, DWELL_MAX
from src.strings import t, LANG_DISPLAY, SUPPORTED_LANGS


COLOR_BG = "#1e1e1e"
COLOR_FG = "#ffffff"
COLOR_PAUSED = "#d63838"
COLOR_RUNNING = "#3aa64a"
COLOR_COUNTDOWN = "#f1c232"
COLOR_BTN_BG = "#2d2d2d"
COLOR_BTN_ACTIVE = "#454545"
COLOR_ACCENT = "#2383e2"
COLOR_AUTOSTART_ON = "#f1c232"
COLOR_AUTOSTART_OFF = "#3a3a3a"
COLOR_LINK = "#5aa9e6"
CREDIT_URL = "https://renstudio.tw"
CREDIT_TEXT = "dev by renstudio"

FONT_LARGE = ("Segoe UI", 11, "bold")
FONT_MEDIUM = ("Segoe UI", 10, "bold")
FONT_SMALL = ("Segoe UI", 9)
FONT_HUGE = ("Segoe UI", 13, "bold")
FONT_ARROW = ("Segoe UI", 14, "bold")


class UI:
    def __init__(
        self,
        state: State,
        on_left_click: Callable[[], None],
        on_double_click: Callable[[], None],
        on_right_click: Callable[[], None],
        on_toggle_auto: Callable[[], None],
        on_move_corner: Callable[[str], None],
        on_dwell_change: Callable[[float], None],
        on_autostart_change: Callable[[bool], None],
        on_lang_change: Callable[[str], None],
        on_toggle_compact: Callable[[], None],
    ):
        self.state = state
        self.on_left_click = on_left_click
        self.on_double_click = on_double_click
        self.on_right_click = on_right_click
        self.on_toggle_auto = on_toggle_auto
        self.on_move_corner = on_move_corner
        self.on_dwell_change = on_dwell_change
        self.on_autostart_change = on_autostart_change
        self.on_lang_change = on_lang_change
        self.on_toggle_compact = on_toggle_compact

        self.root = tk.Tk()
        self.root.geometry(geometry_string(state.window_corner, state.compact_mode))
        self.root.attributes("-topmost", True)
        self.root.configure(bg=COLOR_BG)
        self.root.resizable(False, False)

        self._dwell_var = tk.DoubleVar(value=state.dwell_seconds)
        self._autostart_var = tk.BooleanVar(value=state.autostart_enabled)

        self._countdown_job: Optional[str] = None
        self._countdown_label_key: Optional[str] = None
        self._countdown_remaining: float = 0.0
        self._countdown_fire: Optional[Callable[[], None]] = None

        self._current_mode_compact: Optional[bool] = None
        self.pause_btn: Optional[tk.Button] = None

        self._build_for_mode(state.compact_mode)
        state.subscribe(self._on_state_change)
        self._on_state_change(state)

    def _T(self, key: str, **kwargs) -> str:
        return t(self.state.lang, key, **kwargs)

    def _clear_root(self) -> None:
        for child in self.root.winfo_children():
            child.destroy()

    def _build_for_mode(self, compact: bool) -> None:
        self._clear_root()
        if compact:
            self._build_compact()
        else:
            self._build_full()
        self._current_mode_compact = compact
        self.root.geometry(geometry_string(self.state.window_corner, compact))

    # ------------------------------------------------------------------
    # Full layout
    # ------------------------------------------------------------------
    def _build_full(self) -> None:
        # Top row: corner arrows + compact toggle
        top = tk.Frame(self.root, bg=COLOR_BG)
        top.pack(fill="x", padx=4, pady=(4, 0))
        self.btn_tl = self._mk_arrow(top, "↖", lambda: self.on_move_corner("top-left"))
        self.btn_tl.pack(side="left", ipady=4)
        self.btn_compact = tk.Button(
            top, text="", font=FONT_SMALL,
            bg=COLOR_BTN_BG, fg=COLOR_FG, activebackground=COLOR_BTN_ACTIVE,
            relief="flat", bd=0, command=self.on_toggle_compact,
        )
        self.btn_compact.pack(side="left", padx=6, ipady=4, ipadx=4)
        tk.Label(top, text="", bg=COLOR_BG).pack(side="left", expand=True)
        self.btn_tr = self._mk_arrow(top, "↗", lambda: self.on_move_corner("top-right"))
        self.btn_tr.pack(side="right", ipady=4)

        # PAUSE / RESUME big button
        self.pause_btn = tk.Button(
            self.root, text="", font=FONT_HUGE,
            fg=COLOR_FG, bg=COLOR_RUNNING, activebackground=COLOR_RUNNING,
            relief="flat", bd=0, height=2,
            command=self.on_toggle_auto,
        )
        self.pause_btn.pack(fill="x", padx=10, pady=(8, 8))

        # Action buttons row 1
        row1 = tk.Frame(self.root, bg=COLOR_BG)
        row1.pack(fill="x", padx=10, pady=2)
        self.btn_left = self._mk_action(row1, "", self.on_left_click)
        self.btn_left.pack(side="left", expand=True, fill="x", padx=(0, 4))
        self.btn_right = self._mk_action(row1, "", self.on_right_click)
        self.btn_right.pack(side="right", expand=True, fill="x", padx=(4, 0))

        # Action button row 2
        row2 = tk.Frame(self.root, bg=COLOR_BG)
        row2.pack(fill="x", padx=10, pady=2)
        self.btn_double = self._mk_action(row2, "", self.on_double_click)
        self.btn_double.pack(fill="x")

        # Dwell time scale
        dwell_frame = tk.Frame(self.root, bg=COLOR_BG)
        dwell_frame.pack(fill="x", padx=10, pady=(10, 0))
        self.dwell_label = tk.Label(
            dwell_frame, text="", font=FONT_MEDIUM, fg=COLOR_FG, bg=COLOR_BG, anchor="w",
        )
        self.dwell_label.pack(fill="x")
        self.dwell_scale = tk.Scale(
            self.root,
            from_=DWELL_MIN, to=DWELL_MAX, resolution=0.1, orient="horizontal",
            variable=self._dwell_var,
            bg=COLOR_BG, fg=COLOR_FG, troughcolor=COLOR_BTN_BG,
            activebackground=COLOR_ACCENT,
            highlightthickness=0, bd=0, showvalue=False,
            sliderlength=28, width=18, length=WINDOW_W - 24,
            command=self._on_scale,
        )
        self.dwell_scale.pack(fill="x", padx=10)

        # Autostart toggle — highlighted, larger so it's hard to miss
        self.autostart_btn = tk.Button(
            self.root, text="", font=FONT_MEDIUM,
            fg=COLOR_FG, bg=COLOR_AUTOSTART_OFF, activebackground=COLOR_AUTOSTART_OFF,
            relief="flat", bd=0,
            command=self._toggle_autostart,
        )
        self.autostart_btn.pack(fill="x", padx=10, pady=(8, 4), ipady=8)

        # Language buttons — one box per language for direct selection
        lang_frame = tk.Frame(self.root, bg=COLOR_BG)
        lang_frame.pack(fill="x", padx=10, pady=(0, 4))
        self.lang_buttons: dict[str, tk.Button] = {}
        for code in SUPPORTED_LANGS:
            btn = tk.Button(
                lang_frame, text=LANG_DISPLAY[code], font=FONT_MEDIUM,
                fg=COLOR_FG, bg=COLOR_BTN_BG, activebackground=COLOR_BTN_ACTIVE,
                relief="flat", bd=0,
                command=lambda c=code: self.on_lang_change(c),
            )
            btn.pack(side="left", expand=True, fill="x", padx=2, ipady=4)
            self.lang_buttons[code] = btn

        # Credit link — sits at the very bottom, above the corner arrows row
        credit = tk.Label(
            self.root, text=CREDIT_TEXT, font=FONT_SMALL,
            fg=COLOR_LINK, bg=COLOR_BG, cursor="hand2",
        )
        credit.pack(side="bottom", pady=(0, 2))
        credit.bind("<Button-1>", lambda _e: webbrowser.open(CREDIT_URL))

        # Bottom corner arrows
        bottom = tk.Frame(self.root, bg=COLOR_BG)
        bottom.pack(fill="x", side="bottom", padx=4, pady=(4, 0))
        self.btn_bl = self._mk_arrow(bottom, "↙", lambda: self.on_move_corner("bottom-left"))
        self.btn_bl.pack(side="left", ipady=4)
        tk.Label(bottom, text="", bg=COLOR_BG).pack(side="left", expand=True)
        self.btn_br = self._mk_arrow(bottom, "↘", lambda: self.on_move_corner("bottom-right"))
        self.btn_br.pack(side="right", ipady=4)

    # ------------------------------------------------------------------
    # Compact layout — PAUSE button + 4 corner arrows + expand
    # ------------------------------------------------------------------
    def _build_compact(self) -> None:
        # Top row: ↖ arrow, expand button (mirrors compact button's slot in
        # full mode so the toggle lives in the same place either way), ↗ arrow
        top = tk.Frame(self.root, bg=COLOR_BG)
        top.pack(fill="x", padx=4, pady=(4, 0))
        self.btn_tl = self._mk_arrow(top, "↖", lambda: self.on_move_corner("top-left"))
        self.btn_tl.pack(side="left", ipady=4)
        self.btn_expand = tk.Button(
            top, text="", font=FONT_SMALL,
            fg=COLOR_FG, bg=COLOR_BTN_BG, activebackground=COLOR_BTN_ACTIVE,
            relief="flat", bd=0, command=self.on_toggle_compact,
        )
        self.btn_expand.pack(side="left", padx=6, ipady=4, ipadx=4)
        tk.Label(top, text="", bg=COLOR_BG).pack(side="left", expand=True)
        self.btn_tr = self._mk_arrow(top, "↗", lambda: self.on_move_corner("top-right"))
        self.btn_tr.pack(side="right", ipady=4)

        # Bottom corner arrows only — symmetric with the top row's arrows
        bottom = tk.Frame(self.root, bg=COLOR_BG)
        bottom.pack(fill="x", side="bottom", padx=4, pady=4)
        self.btn_bl = self._mk_arrow(bottom, "↙", lambda: self.on_move_corner("bottom-left"))
        self.btn_bl.pack(side="left", ipady=4)
        tk.Label(bottom, text="", bg=COLOR_BG).pack(side="left", expand=True)
        self.btn_br = self._mk_arrow(bottom, "↘", lambda: self.on_move_corner("bottom-right"))
        self.btn_br.pack(side="right", ipady=4)

        # PAUSE / RESUME big button fills the middle
        self.pause_btn = tk.Button(
            self.root, text="", font=FONT_HUGE,
            fg=COLOR_FG, bg=COLOR_RUNNING, activebackground=COLOR_RUNNING,
            relief="flat", bd=0,
            command=self.on_toggle_auto,
        )
        self.pause_btn.pack(fill="both", expand=True, padx=8, pady=4)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _mk_action(self, parent, label: str, cmd: Callable[[], None]) -> tk.Button:
        return tk.Button(
            parent, text=label, font=FONT_LARGE,
            fg=COLOR_FG, bg=COLOR_BTN_BG, activebackground=COLOR_BTN_ACTIVE,
            relief="flat", bd=0, height=2, command=cmd,
        )

    def _mk_arrow(self, parent, glyph: str, cmd: Callable[[], None]) -> tk.Button:
        return tk.Button(
            parent, text=glyph, font=FONT_ARROW, width=3, height=1,
            bg=COLOR_BTN_BG, fg=COLOR_FG, activebackground=COLOR_BTN_ACTIVE,
            relief="flat", bd=0, command=cmd,
        )

    def _on_scale(self, value: str) -> None:
        try:
            v = float(value)
        except ValueError:
            return
        self.on_dwell_change(v)

    def _toggle_autostart(self) -> None:
        new_val = not self._autostart_var.get()
        self._autostart_var.set(new_val)
        self.on_autostart_change(new_val)

    # ------------------------------------------------------------------
    # State binding
    # ------------------------------------------------------------------
    def _on_state_change(self, state: State) -> None:
        # If compact mode flipped, rebuild widget tree
        if self._current_mode_compact != state.compact_mode:
            self._build_for_mode(state.compact_mode)

        self.root.title(self._T("app_title"))

        if self._countdown_job is None and self.pause_btn is not None:
            if state.auto_click_enabled:
                self.pause_btn.configure(
                    text=self._T("auto_on"),
                    bg=COLOR_RUNNING, activebackground=COLOR_RUNNING, fg=COLOR_FG,
                )
            else:
                self.pause_btn.configure(
                    text=self._T("auto_paused"),
                    bg=COLOR_PAUSED, activebackground=COLOR_PAUSED, fg=COLOR_FG,
                )

        if state.compact_mode:
            if hasattr(self, "btn_expand"):
                self.btn_expand.configure(text=self._T("expand"))
            return

        # Full-mode-only widget updates below
        self.btn_left.configure(text=self._T("btn_left"))
        self.btn_right.configure(text=self._T("btn_right"))
        self.btn_double.configure(text=self._T("btn_double"))
        self.btn_compact.configure(text=self._T("compact"))

        self.dwell_label.configure(
            text=self._T("dwell_label", value=f"{state.dwell_seconds:.1f}")
        )

        if state.autostart_enabled:
            self.autostart_btn.configure(
                text=self._T("autostart_on"),
                bg=COLOR_AUTOSTART_ON, activebackground=COLOR_AUTOSTART_ON, fg="#1e1e1e",
            )
        else:
            self.autostart_btn.configure(
                text=self._T("autostart_off"),
                bg=COLOR_AUTOSTART_OFF, activebackground=COLOR_AUTOSTART_OFF, fg=COLOR_FG,
            )

        for code, btn in self.lang_buttons.items():
            if code == state.lang:
                btn.configure(bg=COLOR_ACCENT, activebackground=COLOR_ACCENT, fg=COLOR_FG)
            else:
                btn.configure(bg=COLOR_BTN_BG, activebackground=COLOR_BTN_ACTIVE, fg=COLOR_FG)

        if self._autostart_var.get() != state.autostart_enabled:
            self._autostart_var.set(state.autostart_enabled)

        if abs(self._dwell_var.get() - state.dwell_seconds) > 0.01:
            self._dwell_var.set(state.dwell_seconds)

    def move_to_corner(self, corner: str) -> None:
        self.root.geometry(geometry_string(corner, self.state.compact_mode))

    def start_countdown(self, label_key: str, total_s: float, fire: Callable[[], None]) -> None:
        if self._countdown_job is not None:
            try:
                self.root.after_cancel(self._countdown_job)
            except Exception:
                pass
            self._countdown_job = None

        self._countdown_label_key = label_key
        self._countdown_remaining = total_s
        self._countdown_fire = fire
        self._tick_countdown()

    def _tick_countdown(self) -> None:
        if self.pause_btn is None:
            return
        n = max(0, int(round(self._countdown_remaining)))
        if self._countdown_remaining > 0.05:
            text = self._T(self._countdown_label_key or "countdown_fire", n=n)
            self.pause_btn.configure(
                text=text + "\n" + self._T("move_now"),
                bg=COLOR_COUNTDOWN, activebackground=COLOR_COUNTDOWN, fg="#1e1e1e",
            )
            self._countdown_remaining -= 0.1
            self._countdown_job = self.root.after(100, self._tick_countdown)
        else:
            self.pause_btn.configure(
                text=self._T("countdown_fire"),
                bg=COLOR_ACCENT, activebackground=COLOR_ACCENT, fg=COLOR_FG,
            )
            if self._countdown_fire is not None:
                try:
                    self._countdown_fire()
                except Exception:
                    pass
            self._countdown_fire = None
            self._countdown_job = self.root.after(400, self._end_countdown)

    def _end_countdown(self) -> None:
        self._countdown_job = None
        self._countdown_label_key = None
        if self.pause_btn is not None:
            self.pause_btn.configure(fg=COLOR_FG)
        self._on_state_change(self.state)

    def run(self) -> None:
        self.root.mainloop()

    def schedule(self, fn: Callable[[], None], delay_ms: int = 0) -> None:
        self.root.after(delay_ms, fn)
