import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import state as state_module
from src.state import State, DWELL_DEFAULT, DWELL_MIN, DWELL_MAX


class StateTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self._orig_dir = state_module.SETTINGS_DIR
        self._orig_file = state_module.SETTINGS_FILE
        state_module.SETTINGS_DIR = Path(self.tmpdir)
        state_module.SETTINGS_FILE = Path(self.tmpdir) / "settings.json"

    def tearDown(self):
        state_module.SETTINGS_DIR = self._orig_dir
        state_module.SETTINGS_FILE = self._orig_file

    def test_defaults(self):
        s = State()
        self.assertEqual(s.dwell_seconds, DWELL_DEFAULT)
        self.assertTrue(s.auto_click_enabled)
        self.assertFalse(s.autostart_enabled)
        self.assertEqual(s.window_corner, "top-right")

    def test_dwell_clamping(self):
        s = State()
        s.set_dwell(0.1)
        self.assertEqual(s.dwell_seconds, DWELL_MIN)
        s.set_dwell(99.0)
        self.assertEqual(s.dwell_seconds, DWELL_MAX)
        s.set_dwell(1.5)
        self.assertAlmostEqual(s.dwell_seconds, 1.5)

    def test_save_and_load_roundtrip(self):
        s = State()
        s.set_dwell(2.0)
        s.toggle_auto_click()
        s.set_corner("bottom-left")
        s.set_autostart(True)
        loaded = State.load()
        self.assertAlmostEqual(loaded.dwell_seconds, 2.0)
        self.assertFalse(loaded.auto_click_enabled)
        self.assertEqual(loaded.window_corner, "bottom-left")
        self.assertTrue(loaded.autostart_enabled)

    def test_invalid_corner_falls_back(self):
        s = State.from_dict({"window_corner": "nowhere"})
        self.assertEqual(s.window_corner, "top-right")

    def test_compact_mode_migrates_to_view_mode(self):
        # Old settings.json stored compact_mode: true. New schema uses view_mode.
        s = State.from_dict({"compact_mode": True})
        self.assertEqual(s.view_mode, "compact")
        s = State.from_dict({"compact_mode": False})
        self.assertEqual(s.view_mode, "full")

    def test_watch_mode_persistence_falls_back_on_load(self):
        # Persisting "watch" across restarts would leave the user staring at
        # a paused 90x90 widget with no warning — load() must coerce back to
        # the pre-watch view and re-enable auto-click.
        s = State.from_dict({
            "view_mode": "watch",
            "pre_watch_view_mode": "compact",
            "auto_click_enabled": False,
        })
        self.assertEqual(s.view_mode, "compact")
        self.assertTrue(s.auto_click_enabled)

    def test_enter_exit_watch_mode(self):
        s = State()
        s.view_mode = "compact"
        s.enter_watch_mode()
        self.assertEqual(s.view_mode, "watch")
        self.assertFalse(s.auto_click_enabled)
        self.assertEqual(s.pre_watch_view_mode, "compact")
        s.exit_watch_mode()
        self.assertEqual(s.view_mode, "compact")
        self.assertTrue(s.auto_click_enabled)

    def test_corrupted_json_returns_defaults(self):
        state_module.SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        state_module.SETTINGS_FILE.write_text("{not valid json", encoding="utf-8")
        s = State.load()
        self.assertEqual(s.dwell_seconds, DWELL_DEFAULT)

    def test_subscribers_called(self):
        s = State()
        events = []
        s.subscribe(lambda st: events.append(st.dwell_seconds))
        s.set_dwell(1.2)
        s.toggle_auto_click()
        self.assertEqual(len(events), 2)


if __name__ == "__main__":
    unittest.main()
