# David Mouse / 大衛滑鼠

A free Windows tool that helps head-mouse users avoid accidental clicks while watching YouTube (and elsewhere). One big PAUSE button — that's it.

給頭控滑鼠使用者的免費小工具：一鍵暫停自動點擊，看 YouTube 不會再被誤觸暫停。

→ **[Full docs, screenshots, and download links — davidmouse.renstudio.tw](https://davidmouse.renstudio.tw)**

## For end users

Download the standalone Windows .exe (no Python needed) from the [latest Release](https://github.com/renstudiodev-TW/david-mouse/releases/latest) or from the [docs site](https://davidmouse.renstudio.tw).

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
