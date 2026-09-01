import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import autostart, single_instance, state as state_module


@unittest.skipUnless(sys.platform == "win32", "單一實例鎖只在 Windows 上生效")
class SingleInstanceTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self._orig_dir = state_module.SETTINGS_DIR
        state_module.SETTINGS_DIR = Path(self.tmpdir)
        single_instance._lock_fd = None

    def tearDown(self):
        single_instance.release()
        state_module.SETTINGS_DIR = self._orig_dir
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_first_acquire_succeeds(self):
        self.assertTrue(single_instance.acquire())
        self.assertTrue((Path(self.tmpdir) / "instance.lock").exists())

    def test_second_acquire_is_blocked(self):
        self.assertTrue(single_instance.acquire())
        # 第二次等同另一個程序來搶鎖，必須被擋下來。
        self.assertFalse(single_instance.acquire())

    def test_release_allows_reacquire(self):
        self.assertTrue(single_instance.acquire())
        single_instance.release()
        self.assertTrue(single_instance.acquire())

    def test_pid_file_roundtrip(self):
        single_instance.acquire()
        self.assertEqual(single_instance._read_pid(), os.getpid())
        single_instance.release()
        self.assertFalse((Path(self.tmpdir) / "instance.pid").exists())
        self.assertEqual(single_instance._read_pid(), 0)

    def test_focus_existing_without_pid_file_is_safe(self):
        # 沒有 pid 檔時不可以爆掉，只要回 False。
        self.assertFalse(single_instance.focus_existing())

    def test_admin_takes_over_from_normal_privilege_instance(self):
        # 重現曾經回報的 bug：一般權限已經在跑，使用者改用系統管理員身分重開
        # （例如某些遊戲視窗只吃管理員權限送出的點擊），這份必須接手成功，
        # 不能被舊的一般權限實例擋下來。
        holder_script = Path(self.tmpdir) / "holder.py"
        repo_root = Path(__file__).resolve().parent.parent
        holder_script.write_text(
            "import sys, time\n"
            f"sys.path.insert(0, {str(repo_root)!r})\n"
            "from src import single_instance, state as state_module\n"
            "from pathlib import Path\n"
            f"state_module.SETTINGS_DIR = Path({self.tmpdir!r})\n"
            "print('acquired:', single_instance.acquire(), flush=True)\n"
            "time.sleep(30)\n",
            encoding="utf-8",
        )
        holder = subprocess.Popen(
            [sys.executable, str(holder_script)], stdout=subprocess.PIPE, text=True
        )
        try:
            self.assertEqual(holder.stdout.readline().strip(), "acquired: True")
            time.sleep(0.3)
            self.assertEqual(single_instance._read_pid(), holder.pid)

            orig_is_admin = autostart.is_admin
            autostart.is_admin = lambda: True
            try:
                self.assertTrue(single_instance.acquire())
            finally:
                autostart.is_admin = orig_is_admin

            self.assertIsNotNone(holder.wait(timeout=2))
        finally:
            if holder.poll() is None:
                holder.kill()


if __name__ == "__main__":
    unittest.main()
