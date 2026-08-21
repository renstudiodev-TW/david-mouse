# David Mouse — 設計文件

## 1. 技術選型

**最終選擇：Python 3.11+ / Tkinter / ctypes (Win32 API) / pynput / PyInstaller**

### 為什麼選這個 stack

向 Gemini-2.5-pro 諮詢後，三方候選 stack 與評估：

| 方案 | 優點 | 缺點 |
|------|------|------|
| **A. PySide6 + pynput** | Widget 完整、樣式 CSS 化、AI 寫順 | 打包後 50MB+，依賴重，對長輩電腦不友善 |
| **B. Tkinter + ctypes + pynput** ✅ | stdlib UI 零外部依賴、ctypes 直連 Win32 穩定可靠、打包後 10–15MB | UI 客製化要花工夫，但對 240x320 工具夠用 |
| C. Electron + robotjs | 跨平台 UI 漂亮 | 80MB+ 體積、robotjs 在新版 Node 常 native build 失敗 |

**選 B 的理由（與 Gemini 共識）**：
1. `ctypes` 直接呼叫 `SendInput` / `SetCursorPos`，模擬點擊穩定度最高，輔具場景不能容忍漏點。
2. Tkinter 是 Python stdlib，UI 邏輯 AI 寫得順、不會踩到第三方 widget 的 quirk。
3. PyInstaller `--onefile --noconsole` 出來的 exe ~12MB，可直接放桌面雙擊，無安裝步驟對長輩友善。
4. `pynput` 作為 `SetWindowsHookEx` 的 wrapper 比手寫 ctypes hook 安全（避免 callback GC 引發 crash）。
5. 開機自動啟動有兩種模式，都不寫 registry，符合「不動系統設定」原則：有系統管理員權限時註冊工作排程（登入觸發、最高權限、不跳 UAC），沒有時退回 `Startup` 資料夾的 `.lnk` 捷徑。啟動資料夾本身無法啟動提權程式（捷徑勾「以系統管理員身分執行」會被 UAC 直接擋掉），所以需要管理員權限的情境只能走工作排程。

## 2. 檔案結構

```
fordavicdmouse/
├── DESIGN.md                    # 本文件
├── OVERNIGHT_REPORT.md          # 完工後的早晨報告
├── README.md                    # 啟動說明
├── requirements.txt             # pip 套件清單
├── run.bat                      # 一鍵啟動腳本（純 ASCII）
├── build.bat                    # PyInstaller 打包腳本（純 ASCII）
├── src/
│   ├── __init__.py
│   ├── main.py                  # 程式入口（建立 App 並 mainloop）
│   ├── app.py                   # 主 App class（組合所有 module）
│   ├── ui.py                    # Tkinter UI 元件（按鈕、滑桿、角落箭頭）
│   ├── state.py                 # 應用狀態 + 偏好設定持久化
│   ├── clicker.py               # 全域 hook + dwell time 偵測 + SendInput 模擬點擊
│   ├── win32_input.py           # ctypes SendInput / SetCursorPos / GetCursorPos 包裝
│   ├── corners.py               # 計算螢幕四角座標 + 把視窗移過去
│   └── autostart.py             # 開機自動啟動（工作排程／Startup .lnk）
└── tests/
    └── test_state.py            # state 持久化單元測試（不需要 GUI）
```

## 3. Module 職責

- **main.py** — 純入口；只負責建立 `app.App()` 並啟動 mainloop，方便 PyInstaller 找 entry point。
- **app.py** — `App` class，集中持有 `State`、`Clicker`、`UI` 實例；註冊 UI 事件 → State 變動 → Clicker 行為。
- **ui.py** — 建立 Tk root（240x320、always-on-top）、四角箭頭按鈕、4 個大功能按鈕（60x60+）、dwell time Scale、autostart Checkbutton。發 callback 給 App。
- **state.py** — `State` dataclass：`dwell_seconds`、`auto_click_enabled`、`autostart_enabled`、`window_corner`。讀寫 `%APPDATA%\DavidMouse\settings.json`。
- **clicker.py** — 啟動背景 thread，用 `pynput.mouse.Listener` 監聽滑鼠移動，計算停留時間達 dwell 時呼叫 `win32_input.left_click()`。受 `state.auto_click_enabled` 控制 pause。
- **win32_input.py** — `ctypes` 包 `INPUT` struct + `SendInput`，提供 `left_click(x,y)` / `double_click(x,y)` / `right_click(x,y)`。
- **corners.py** — 用 `ctypes.windll.user32.GetSystemMetrics` 拿螢幕尺寸；計算 4 個角落座標；呼叫 `root.geometry()` 移動視窗。
- **autostart.py** — 兩種模式。程式以系統管理員身分執行時，用 `schtasks /Create /XML` 註冊名為 `DavidMouse` 的工作排程（LogonTrigger、`HighestAvailable`、延遲 15 秒、不限執行時間、電池模式照跑）；否則在 `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\` 建立 `.lnk` 捷徑（用 `pythoncom + win32com.client` 或 fallback 到 PowerShell `WScript.Shell.CreateShortcut`）。兩者互斥，建立其中一個時會清掉另一個，避免開機跑出兩份。獨立的一鍵腳本在 `tools/admin-autostart.ps1`（由 `setup-admin-autostart.bat` 提權呼叫），給不想重新打包 exe 的情況用。

## 4. 關鍵套件清單（requirements.txt）

```
pynput==1.7.7           # 全域滑鼠 hook（避免手寫 SetWindowsHookEx）
pywin32==306            # COM 建立 Startup .lnk 捷徑
pyinstaller==6.10.0     # 打包成單一 .exe（dev only）
```

> Tkinter 是 Python stdlib，不列入 requirements。ctypes 也是 stdlib。

## 5. UI Wireframe（240x320，文字版）

```
┌──────────────────────────────────┐
│ ↖                              ↗ │  ← 兩個小箭頭按鈕（角落 30x30）
│                                  │
│   ╔══════════════════════════╗   │
│   ║   ⏸  PAUSE / RESUME      ║   │  ← 大按鈕 200x60，高對比配色
│   ║   (auto-click status)    ║   │     紅色=暫停中 / 綠色=自動點擊中
│   ╚══════════════════════════╝   │
│                                  │
│   ┌──────────┐  ┌──────────┐     │
│   │  ◐ L     │  │  ◑ R     │     │  ← 左/右鍵單擊 90x70
│   └──────────┘  └──────────┘     │
│   ┌──────────┐                   │
│   │  ◐◐ LL   │                   │  ← 左鍵雙擊 90x70
│   └──────────┘                   │
│                                  │
│   Dwell time: 1.0 s              │
│   [─────●────────────]           │  ← Scale 0.5~3.0 step 0.1
│                                  │
│   ☐ Start with Windows           │  ← Checkbutton autostart
│                                  │
│ ↙                              ↘ │
└──────────────────────────────────┘
```

設計重點：
- 大按鈕：暫停按鈕 200x60、L/R/LL 90x70（皆 ≥ 60x60，符合頭控滑鼠精細度限制）
- 高對比：暫停按鈕用紅/綠雙態，背景深、字體大白色
- 視窗 `attributes('-topmost', True)`，總是顯示在最前面
- `overrideredirect(False)` 保留標題列，方便拖移；之後可選擇開啟 borderless 模式

## 6. 持久化格式（settings.json）

```json
{
  "dwell_seconds": 1.0,
  "auto_click_enabled": true,
  "autostart_enabled": false,
  "window_corner": "top-right"
}
```

存放於 `%APPDATA%\DavidMouse\settings.json`，每次 UI 變動就 atomic write。

## 7. 風險與 TODO

- **全域 hook 在某些防毒下會被擋**：pynput 用了 `SetWindowsHookEx(WH_MOUSE_LL)`，少數防毒會誤判。實裝後若有問題，回退到 polling `GetCursorPos`（耗 CPU 但安全）。
- **dwell time 邏輯邊界**：如何處理「點擊後是否進入 cooldown」防止同一位置連續觸發 — MVP 採 1.5 倍 dwell 的 cooldown。
- **多螢幕**：MVP 只支援主螢幕（`SM_CXSCREEN`/`SM_CYSCREEN`）。多螢幕的角落定位列為 TODO。
