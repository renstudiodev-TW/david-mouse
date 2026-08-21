# David Mouse / 大衛滑鼠

A free Windows tool that helps head-mouse users avoid accidental clicks while watching YouTube (and elsewhere). One big PAUSE button — that's it.

給頭控滑鼠使用者的免費小工具：一鍵暫停自動點擊，看 YouTube 不會再被誤觸暫停。

→ **[Full docs, screenshots, and download links — davidmouse.renstudio.tw](https://davidmouse.renstudio.tw)**

## For end users

Download the standalone Windows .exe (no Python needed) from the [latest Release](https://github.com/renstudiodev-TW/david-mouse/releases/latest) or from the [docs site](https://davidmouse.renstudio.tw).

### 開機自動以系統管理員權限啟動

有些程式（以及所有提權的視窗）會忽略模擬點擊，除非 David Mouse 自己也用系統管理員權限執行。要讓它開機就自動用管理員權限跑，在解壓縮後的資料夾裡雙擊 `setup-admin-autostart.bat`，同意一次 UAC 就好。之後每次登入 Windows 都會自動啟動，而且不會再跳 UAC。要取消就雙擊 `remove-admin-autostart.bat`。

Windows 的「啟動」資料夾做不到這件事。把捷徑勾「以系統管理員身分執行」再放進啟動資料夾，UAC 會直接擋掉、程式根本不會跑起來，所以改用工作排程器（Task Scheduler）。

App 裡的「開機自動啟動」按鈕也會自己判斷：如果目前這份程式是用系統管理員身分開的，按下去就會建立同一個排程工作，按鈕會顯示「開（管理員）」；否則退回一般權限的啟動資料夾捷徑。

## For developers

```bat
install.bat   :: one-time: auto-installs Python 3.12 if missing, then deps (per-user, no admin)
run.vbs       :: launch the app — silent, no console window (recommended)
run.bat       :: launch the app — shows a console window (alternative)
build.bat     :: build a standalone .exe via PyInstaller (output in dist\)
```

UI is available in 繁中 / English / 日本語 / 한국어, switchable from the language row.

## Tech stack

Python + Tkinter + ctypes (Win32) + pynput + PyInstaller. See `DESIGN.md` for full rationale.

## License

MIT
