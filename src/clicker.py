"""Dwell-time auto-click engine.

Runs a background thread that polls the cursor position, measures how long it
has stayed within a tolerance radius, and triggers a left-click via SendInput
when the dwell time threshold is reached.

Polling (not low-level hook) keeps the impl simple and avoids antivirus
false positives. CPU cost is negligible at 30 Hz.

The dwell click intentionally fires anywhere on screen — INCLUDING over the
app's own UI. This is required so head-mouse users can dwell-click the PAUSE
button to escape the YouTube auto-click trap.
"""
import threading
import time
from typing import Callable, Optional

from src import win32_input
from src.state import State


POLL_HZ = 30
MOVE_TOLERANCE_PX = 25  # head-mouse users jitter; 25px ~= a fingertip diameter


class Clicker:
    def __init__(
        self,
        state: State,
        is_over_resume_zone: Optional[Callable[[int, int], bool]] = None,
    ):
        self.state = state
        # When auto-click is paused, dwell-click still works but ONLY inside
        # this zone — typically the PAUSE/RESUME button rect — otherwise a
        # head-mouse user would have no way to re-enable auto-click.
        self.is_over_resume_zone = is_over_resume_zone or (lambda x, y: False)
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._last_pos: Optional[tuple[int, int]] = None
        self._dwell_started_at: Optional[float] = None
        self._cooldown_until: float = 0.0
        self._paused_until: float = 0.0

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True, name="dwell-clicker")
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def temporary_pause(self, seconds: float) -> None:
        """Pause the auto-clicker for a short window. Used while the user is
        in the middle of a manual action countdown so they don't get a
        double-click at the destination."""
        self._paused_until = time.monotonic() + max(0.0, seconds)
        self._last_pos = None
        self._dwell_started_at = None

    def _loop(self) -> None:
        period = 1.0 / POLL_HZ
        while not self._stop_event.is_set():
            try:
                self._tick()
            except Exception:
                pass
            time.sleep(period)

    def _tick(self) -> None:
        now = time.monotonic()
        if now < self._cooldown_until or now < self._paused_until:
            return

        x, y = win32_input.get_cursor_pos()

        if not self.state.auto_click_enabled:
            # Paused: only respond to dwell when cursor is over the resume zone
            # (the big PAUSE button). Otherwise a head-mouse user could never
            # un-pause.
            if not self.is_over_resume_zone(x, y):
                self._last_pos = None
                self._dwell_started_at = None
                return

        if self._last_pos is None:
            self._last_pos = (x, y)
            self._dwell_started_at = now
            return

        dx = x - self._last_pos[0]
        dy = y - self._last_pos[1]
        moved = (dx * dx + dy * dy) > (MOVE_TOLERANCE_PX * MOVE_TOLERANCE_PX)

        if moved:
            self._last_pos = (x, y)
            self._dwell_started_at = now
            return

        if self._dwell_started_at is None:
            return

        elapsed = now - self._dwell_started_at
        if elapsed >= self.state.dwell_seconds:
            win32_input.left_click()
            self._cooldown_until = now + (self.state.dwell_seconds * 1.5)
            self._dwell_started_at = None
            self._last_pos = None
