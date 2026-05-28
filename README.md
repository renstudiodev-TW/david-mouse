# David Mouse / 大衛滑鼠

A free Windows tool that helps head-mouse users avoid accidental clicks while watching YouTube (and elsewhere). One big PAUSE button — that's it.

給頭控滑鼠使用者的免費小工具：一鍵暫停自動點擊，看 YouTube 不會再被誤觸暫停。

→ See full documentation site at [`docs/index.html`](docs/index.html) (中文) or [`docs/en/index.html`](docs/en/index.html) (English)

## Quick start

```bat
install.bat   :: auto-installs Python 3.12 if missing, then deps (per-user, no admin)
run.bat       :: launch the app
```

## Build a standalone .exe

```bat
pip install pyinstaller
build.bat
:: output in dist\david-mouse.exe
```

## Tech stack

Python + Tkinter + ctypes (Win32) + pynput + PyInstaller. See `DESIGN.md` for full rationale.

## License

MIT
