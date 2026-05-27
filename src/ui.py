"""Tkinter UI: 4 large buttons + dwell scale + corner arrows + autostart checkbox.

High contrast, large click targets for head-mouse users (>= 60x60 px).
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable

from src.corners import WINDOW_W, WINDOW_H, geometry_string
from src.state import State, DWELL_MIN, DWELL_MAX


COLOR_BG = "#1e1e1e"
COLOR_FG = "#ffffff"
COLOR_PAUSED = "#d63838"
COLOR_RUNNING = "#3aa64a"
COLOR_BTN_BG = "#2d2d2d"
COLOR_BTN_ACTIVE = "#454545"
COLOR_ACCENT = "#2383e2"

FONT_LARGE = ("Segoe UI", 12, "bold")
FONT_MEDIUM = ("Segoe UI", 10, "bold")
FONT_SMALL = ("Segoe UI", 9)
FONT_HUGE = ("Segoe UI", 14, "bold")


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
    ):
        self.state = state
        self.on_left_click = on_left_click
        self.on_double_click = on_double_click
        self.on_right_click = on_right_click
        self.on_toggle_auto = on_toggle_auto
        self.on_move_corner = on_move_corner
        self.on_dwell_change = on_dwell_change
        self.on_autostart_change = on_autostart_change

        self.root = tk.Tk()
        self.root.title("HeadMouse Helper")
        self.root.geometry(geometry_string(state.window_corner))
        self.root.attributes("-topmost", True)
        self.root.configure(bg=COLOR_BG)
        self.root.minsize(WINDOW_W, WINDOW_H)
        self.root.resizable(False, False)

        self._dwell_var = tk.DoubleVar(value=state.dwell_seconds)
        self._autostart_var = tk.BooleanVar(value=state.autostart_enabled)

        self._build_widgets()
        state.subscribe(self._on_state_change)
        self._on_state_change(state)

    def _build_widgets(self) -> None:
        # Corner arrows row (top)
        top = tk.Frame(self.root, bg=COLOR_BG)
        top.pack(fill="x", padx=4, pady=2)
        tk.Button(
            top, text="↖", font=FONT_MEDIUM, width=2, height=1,
            bg=COLOR_BTN_BG, fg=COLOR_FG, activebackground=COLOR_BTN_ACTIVE,
            relief="flat", bd=0, command=lambda: self.on_move_corner("top-left"),
        ).pack(side="left")
        tk.Label(top, text="", bg=COLOR_BG).pack(side="left", expand=True)
        tk.Button(
            top, text="↗", font=FONT_MEDIUM, width=2, height=1,
            bg=COLOR_BTN_BG, fg=COLOR_FG, activebackground=COLOR_BTN_ACTIVE,
            relief="flat", bd=0, command=lambda: self.on_move_corner("top-right"),
        ).pack(side="right")

        # PAUSE / RESUME big button
        self.pause_btn = tk.Button(
            self.root,
            text="",
            font=FONT_HUGE,
            fg=COLOR_FG,
            bg=COLOR_RUNNING,
            activebackground=COLOR_RUNNING,
            relief="flat",
            bd=0,
            height=2,
            command=self.on_toggle_auto,
        )
        self.pause_btn.pack(fill="x", padx=10, pady=(6, 8))

        # Click buttons row 1: Left, Right
        row1 = tk.Frame(self.root, bg=COLOR_BG)
        row1.pack(fill="x", padx=10, pady=2)
        self._make_action_btn(row1, "◐ Left", self.on_left_click).pack(side="left", expand=True, fill="x", padx=(0, 4))
        self._make_action_btn(row1, "◑ Right", self.on_right_click).pack(side="right", expand=True, fill="x", padx=(4, 0))

        # Click button row 2: Double click
        row2 = tk.Frame(self.root, bg=COLOR_BG)
        row2.pack(fill="x", padx=10, pady=2)
        self._make_action_btn(row2, "◐◐ Double", self.on_double_click).pack(fill="x")

        # Dwell time controls
        dwell_frame = tk.Frame(self.root, bg=COLOR_BG)
        dwell_frame.pack(fill="x", padx=10, pady=(10, 2))
        self.dwell_label = tk.Label(
            dwell_frame, text="", font=FONT_MEDIUM, fg=COLOR_FG, bg=COLOR_BG, anchor="w",
        )
        self.dwell_label.pack(fill="x")
        self.dwell_scale = tk.Scale(
            self.root,
            from_=DWELL_MIN,
            to=DWELL_MAX,
            resolution=0.1,
            orient="horizontal",
            variable=self._dwell_var,
            bg=COLOR_BG,
            fg=COLOR_FG,
            troughcolor=COLOR_BTN_BG,
            activebackground=COLOR_ACCENT,
            highlightthickness=0,
            bd=0,
            showvalue=False,
            length=WINDOW_W - 24,
            command=self._on_scale,
        )
        self.dwell_scale.pack(fill="x", padx=10)

        # Autostart checkbox
        self.autostart_check = tk.Checkbutton(
            self.root,
            text="Start with Windows",
            variable=self._autostart_var,
            command=self._on_autostart,
            bg=COLOR_BG,
            fg=COLOR_FG,
            activebackground=COLOR_BG,
            activeforeground=COLOR_FG,
            selectcolor=COLOR_BTN_BG,
            font=FONT_SMALL,
        )
        self.autostart_check.pack(anchor="w", padx=10, pady=(6, 2))

        # Corner arrows row (bottom)
        bottom = tk.Frame(self.root, bg=COLOR_BG)
        bottom.pack(fill="x", side="bottom", padx=4, pady=2)
        tk.Button(
            bottom, text="↙", font=FONT_MEDIUM, width=2, height=1,
            bg=COLOR_BTN_BG, fg=COLOR_FG, activebackground=COLOR_BTN_ACTIVE,
            relief="flat", bd=0, command=lambda: self.on_move_corner("bottom-left"),
        ).pack(side="left")
        tk.Label(bottom, text="", bg=COLOR_BG).pack(side="left", expand=True)
        tk.Button(
            bottom, text="↘", font=FONT_MEDIUM, width=2, height=1,
            bg=COLOR_BTN_BG, fg=COLOR_FG, activebackground=COLOR_BTN_ACTIVE,
            relief="flat", bd=0, command=lambda: self.on_move_corner("bottom-right"),
        ).pack(side="right")

    def _make_action_btn(self, parent, label: str, cmd: Callable[[], None]) -> tk.Button:
        return tk.Button(
            parent,
            text=label,
            font=FONT_LARGE,
            fg=COLOR_FG,
            bg=COLOR_BTN_BG,
            activebackground=COLOR_BTN_ACTIVE,
            relief="flat",
            bd=0,
            height=2,
            command=cmd,
        )

    def _on_scale(self, value: str) -> None:
        try:
            v = float(value)
        except ValueError:
            return
        self.on_dwell_change(v)

    def _on_autostart(self) -> None:
        self.on_autostart_change(bool(self._autostart_var.get()))

    def _on_state_change(self, state: State) -> None:
        if state.auto_click_enabled:
            self.pause_btn.configure(text="● AUTO-CLICK ON", bg=COLOR_RUNNING, activebackground=COLOR_RUNNING)
        else:
            self.pause_btn.configure(text="⏸ PAUSED", bg=COLOR_PAUSED, activebackground=COLOR_PAUSED)

        self.dwell_label.configure(text=f"Dwell time: {state.dwell_seconds:.1f} s")

        if self._autostart_var.get() != state.autostart_enabled:
            self._autostart_var.set(state.autostart_enabled)

        if abs(self._dwell_var.get() - state.dwell_seconds) > 0.01:
            self._dwell_var.set(state.dwell_seconds)

    def move_to_corner(self, corner: str) -> None:
        self.root.geometry(geometry_string(corner))

    def run(self) -> None:
        self.root.mainloop()

    def schedule(self, fn: Callable[[], None], delay_ms: int = 0) -> None:
        self.root.after(delay_ms, fn)
