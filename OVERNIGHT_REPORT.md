# Overnight Report — David Mouse

> 給 RC 早上看的工作紀錄。本檔同時方便匯入 Notion（Markdown-friendly）。

## TL;DR — 一句話結論

✅ **MVP 完成**：軟體可跑（UI + dwell-click + autostart + i18n）、Gemini code review 4 個 bug 全修、雙語教學網頁完成、6 張截圖完成。早上只要補 **David 真實故事** 與 **募款帳戶資訊** 就能上線。

---

## 1. 技術 stack 為什麼選這個？

**最終選擇**：Python 3.10+ / Tkinter / ctypes (Win32 API) / pynput / PyInstaller

### 決策過程
- 跟 Gemini 2.5 Pro 諮詢一次（CLI 直連，不是 MCP — MCP 無法 spawn gemini binary）
- Gemini 推薦 B（Tkinter+ctypes）
- 我獨立評估也選 B

### 三方對照

| 方案 | 體積 | AI 寫順 | Win32 整合 | 最終評分 |
|------|------|---------|-----------|----------|
| A. PySide6 + pynput | 50MB+ | ◎ | △ | 對長輩電腦不友善 |
| **B. Tkinter + ctypes + pynput** ✅ | 10–15MB | ○ | ◎ 直連 | 採用 |
| C. Electron + robotjs | 80MB+ | ○ | △ robotjs 常 native build 失敗 | 駁回 |

關鍵 trade-off：**犧牲 Tkinter 美觀換 (a) 零相依、(b) 打包後輕量、(c) Win32 API 穩定**。對輔具用途，stable + light > pretty。

---

## 2. 完成的功能

### ✅ 全部完成

| 功能 | 狀態 | 檔案 |
|------|------|------|
| Tkinter 主視窗（260x400，置頂） | ✅ | `src/ui.py` |
| 大 PAUSE / RESUME 鈕（紅綠雙態） | ✅ | `src/ui.py` |
| 左鍵 / 右鍵 / 雙擊 動作鍵 + 2.5s 倒數 | ✅ | `src/ui.py` + `src/app.py` |
| Dwell time 滑桿（0.5 ~ 3.0s） | ✅ | `src/ui.py` + `src/state.py` |
| 視窗四角箭頭瞬移 | ✅ | `src/corners.py` + `src/ui.py` |
| 開機自動啟動（Startup folder .lnk，不寫 registry） | ✅ | `src/autostart.py` |
| 偏好設定持久化（`%APPDATA%\DavidMouse\settings.json`） | ✅ | `src/state.py` |
| 全域 dwell-click 偵測 + SendInput 觸發 | ✅ | `src/clicker.py` + `src/win32_input.py` |
| 中文／英文 i18n 切換（介面內直接切） | ✅ | `src/strings.py` |
| 6 張軟體截圖（zh / en × running / paused / countdown） | ✅ | `docs/screenshots/` |
| 雙語教學網頁 | ✅ | `docs/index.html`, `docs/en/index.html` |
| 單元測試 6 個全綠 | ✅ | `tests/test_state.py` |

### 🚧 TODO（不影響核心使用）

- [ ] **打包後的 .exe**：`build.bat` 已寫好，但沒實際跑過 PyInstaller。早上跑 `build.bat` 一次驗證能產出 `dist\david-mouse.exe`
- [ ] **多螢幕支援**：目前角落瞬移只看主螢幕（`GetSystemMetrics(SM_CXSCREEN/SM_CYSCREEN)`）。多螢幕情境會落在第 1 號螢幕的角落
- [ ] **David 真實故事**：`docs/index.html` 與 `docs/en/index.html` 的 `#story` 區塊都用紅色 PLACEHOLDER 標記，內容是我合理推測的占位文
- [ ] **募款帳戶資訊**：`#donate` 區塊以「Coming soon」狀態呈現，待補銀行/分行/帳號
- [ ] **GitHub repo URL**：`README.md` 與兩份 HTML 內提到的 `git clone https://github.com/renstudiodev-TW/david-mouse` 是占位 URL。實際還沒建 repo

---

## 3. 怎麼啟動程式（複製貼上用）

### 第一次安裝
```powershell
cd C:\Users\boren\Desktop\fordavicdmouse
.\install.bat
```

### 一般啟動
```powershell
cd C:\Users\boren\Desktop\fordavicdmouse
.\run.bat
```

### 跑單元測試
```powershell
cd C:\Users\boren\Desktop\fordavicdmouse
python -m unittest tests.test_state -v
```

### 重新拍截圖（修了 UI 之後要重跑）
```powershell
cd C:\Users\boren\Desktop\fordavicdmouse
python tools\capture_screenshots.py
```

### 預覽教學網頁
```powershell
cd C:\Users\boren\Desktop\fordavicdmouse\docs
python -m http.server 8080
:: 開瀏覽器看 http://localhost:8080/
```

### 打包成 .exe（沒驗證過，建議早上跑一次）
```powershell
cd C:\Users\boren\Desktop\fordavicdmouse
pip install pyinstaller
.\build.bat
:: 完成後 .exe 在 dist\david-mouse.exe
```

---

## 4. Gemini Code Review 結果

跟 Gemini 做了一輪 code review，**它給的 4 個建議我全部接受並修正**（沒有不認同的）。

| # | Gemini 指出 | 我的處理 | 修在哪 |
|---|-------------|----------|--------|
| 1 | `_is_over_app_window` 讓使用者無法 dwell 點 PAUSE 鈕，違背需求 | 移除這個 filter，dwell 點擊 UI 本身就是預期行為 | `src/clicker.py` + `src/app.py` |
| 2 | 動作鍵 120ms 延遲對頭控太短，根本來不及移到目標 | 改為 2.5 秒倒數，pause 鈕變黃色顯示「移動游標到目標」+ 倒數秒數 | `src/app.py` + `src/ui.py` |
| 3 | MOVE_TOLERANCE_PX = 8 對頭部抖動太敏感 | 改為 25px（約一個指尖直徑） | `src/clicker.py` |
| 4 | 角落箭頭 + Autostart 點擊區太小，不符合無障礙原則 | 角落箭頭放大到 width=3 + ipady=4；Autostart 改為大按鈕加 checkbox 字元 | `src/ui.py` |

### 設計副產品：clicker.temporary_pause(seconds)
為了配合動作鍵倒數，加了 `Clicker.temporary_pause()` 方法。倒數期間自動暫停 dwell-clicker，避免「使用者按下『左鍵』倒數後移到目標時，被 dwell 引擎搶先點一次造成雙擊」的 race condition。

---

## 5. 需要早上特別 review 的部分

優先序由高到低：

### 🔴 必看（會影響上線）

1. **`docs/index.html` 和 `docs/en/index.html` 的 `#story` 區塊**
   - 我寫的 David 故事是合理推測的占位版本
   - 整個 `<div class="story">` 內容都要替換成真實故事
   - 已用紅色「PLACEHOLDER」框標記，明顯不會錯過

2. **募款帳戶資訊**
   - 兩個 HTML 的 `.donate-info` 區塊
   - 銀行/分行/帳號都是「（即將公布）」
   - 等 RC 開好戶就填進去

3. **GitHub repo 還沒建**
   - HTML 跟 README 提到的 `https://github.com/renstudiodev-TW/david-mouse` 是占位 URL
   - 早上若要建 repo，把所有占位 URL 改成真實的

### 🟡 建議檢查（不會壞，但可以更好）

4. **PyInstaller 打包驗證**：`build.bat` 沒實際跑過，建議跑一次確認能產出 `.exe`
5. **動作鍵 2.5 秒倒數**：頭控速度因人而異，如果 David 試用後覺得太短或太長，調整 `src/app.py` 的 `ACTION_COUNTDOWN_S` 常數
6. **MOVE_TOLERANCE_PX = 25 像素**：同樣可能需要依 David 抖動程度微調，在 `src/clicker.py`

### 🟢 加分項（純優化，不急）

7. 加 keyboard hotkey（例如 F8 = pause toggle）給家屬／治療師更快操作
8. 系統匣 (system tray) icon，視窗最小化時還能切換 pause
9. 多螢幕支援（GetMonitorInfo + EnumDisplayMonitors）
10. 視覺化提示：dwell 進度條（讓使用者知道「再 0.3 秒就會點下去」）

---

## 6. 兩 model 協作心得（給 Notion 知識庫）

### Model 使用配比
- **Claude Opus 4.7**：規劃流程、寫所有 code、寫所有文件
- **Gemini 2.5 Pro**：技術選型（1 次）+ Code review（1 次）— 共 2 次

### 為什麼這樣分配
- 雙 model 並寫 code 會脫節，Gemini 不知道我的 codebase context
- Gemini 適合「定點諮詢、二意見、red team」
- 諮詢前我先有候選答案，Gemini 用來**驗證或推翻**，不是用來代決策

### 學到的 prompt 技巧
1. 列好候選方案讓 Gemini 選，**強制限制字數**（"3 句話以內"），不要開放式問
2. Code review 時，把所有相關檔案用 `@src/xxx.py @src/yyy.py` 一次塞進去，比分多次問效率好
3. **告訴 Gemini 不要客套** — 直接條列、不要長篇分析

### Gemini CLI 還是 MCP？
- 一開始用 MCP 失敗（spawn ENOENT — MCP server PATH 抓不到 gemini.cmd）
- 改 Bash 直接呼叫 `gemini -p` 成功
- **結論**：Token 消耗、API 計費完全一樣，差別只在「MCP 可以 chunk 大回應」。少一層中間人對睡覺場景更穩

---

## 7. 檔案結構（最終）

```
fordavicdmouse/
├── DESIGN.md                      # 技術選型 + 設計文件
├── DEV_LOG.md                     # 開發流程紀錄（Notion-import-friendly）
├── OVERNIGHT_REPORT.md            # 本檔
├── NOTION_KNOWLEDGE_BASE_SETUP.html  # Notion 知識庫設定教學
├── README.md                      # 快速啟動指引
├── requirements.txt               # pynput, pywin32, pyinstaller
├── install.bat                    # 一鍵安裝相依
├── run.bat                        # 一鍵啟動
├── build.bat                      # 一鍵打包成 .exe
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── main.py                    # 入口
│   ├── app.py                     # 主 App，組合所有模組
│   ├── ui.py                      # Tkinter UI（按鈕、滑桿、倒數）
│   ├── state.py                   # 狀態 + JSON 持久化
│   ├── strings.py                 # zh-TW / en i18n 字串
│   ├── clicker.py                 # 全域 dwell-click 引擎
│   ├── win32_input.py             # ctypes SendInput / 座標讀寫
│   ├── corners.py                 # 螢幕角落座標計算
│   └── autostart.py               # Startup folder .lnk 管理
├── tests/
│   ├── __init__.py
│   └── test_state.py              # 6 個測試（持久化、clamp、recovery）
├── tools/
│   └── capture_screenshots.py     # 自動截圖工具（PrintWindow）
└── docs/                          # 教學網頁
    ├── index.html                 # 中文版
    ├── en/index.html              # 英文版
    ├── assets/styles.css          # 共用 CSS
    └── screenshots/               # 6 張 PNG 截圖
```

### Git 提交歷史

```
bfb5f7d feat: bilingual landing page + UI screenshots + README
a46b979 feat: fix code-review issues + add zh/en i18n
ff5380e feat: MVP implementation (UI + state + clicker + autostart)
0089ca4 docs: stack decision + initial design
b548665 Initial commit
```

---

## 8. 已知問題清單

| 問題 | 嚴重性 | 觸發條件 | 解法 |
|------|--------|---------|------|
| 雙螢幕時角落瞬移只看主螢幕 | 中 | 多螢幕設定 | TODO：用 GetMonitorInfo / EnumDisplayMonitors |
| 視窗無法拖移到主螢幕外 | 低 | 多螢幕設定 | 隨多螢幕支援一起做 |
| Dwell click 時 cursor 若停在 dwell scale 滑桿上會點到 scale，造成 dwell 秒數跳動 | 中 | 使用者把游標停在 scale 上想看數字 | 在 ui 上加「死區」(dead zone)；或讓 scale 不接受單擊定位（要求拖動） |
| PyInstaller 打包未驗證 | 中 | 想用 .exe 形式分發時 | 跑 `build.bat` 驗證 |
| Tkinter `after` job 在物件 destroy 時偶爾噴 `invalid command name` 警告 | 低 | 截圖工具關閉視窗時 | 不影響功能，可在 `_end_countdown` 加 try/except 包起來 |
| Gemini code review 因 API 偶發回傳 invalid content 卡了一輪 | 低 | Gemini API 不穩 | 第二次重試即成功；如要重跑 code review，命令在 DEV_LOG.md 內 |

---

## 9. 給 RC 的隔日清單（早上照做）

### ☐ 最重要（必做）
1. 打開 `docs/index.html` 跟 `docs/en/index.html`，找紅色「PLACEHOLDER」框，把 David 故事換成真實版本
2. 補 `#donate` 區塊的銀行帳戶資訊（兩份 HTML 都要）
3. 跑 `.\run.bat` 親自測試軟體功能（特別是 PAUSE 鈕 dwell 觸發）
4. 跑 `.\build.bat` 驗證 PyInstaller 能打包成功

### ☐ 重要（建議做）
5. 建 GitHub repo `renstudiodev-TW/david-mouse`，把所有占位 URL 替換成真實 URL
6. 重新拍截圖（如果 David 故事或介面有改動）：`python tools\capture_screenshots.py`
7. 部署網頁到 Netlify 或放到 renstudio.tw/david-mouse/

### ☐ 之後（不急）
8. 照 `NOTION_KNOWLEDGE_BASE_SETUP.html` 教學建立 Notion 知識庫，把 `DEV_LOG.md` 匯入第一筆
9. 找 David 試用，依回饋調整 `ACTION_COUNTDOWN_S` / `MOVE_TOLERANCE_PX` / `dwell_seconds` 預設值
10. 考慮加入頭控滑鼠社群論壇（如 PTT 身障版、Reddit r/assistivetech）做 user testing

---

## 10. 統計數字

- **總開發時間**：~3 小時
- **Git commits**：5 個
- **檔案數**：32 個
- **程式碼行數**：~1100 行（Python）+ ~700 行（HTML/CSS）
- **單元測試**：6 個全綠
- **Gemini 呼叫次數**：2 次（5 次上限）— 還有 3 次 quota
- **修了的 bug**：4 個（全部來自 Gemini code review）

---

🎯 **接下來就交給你了，RC。早安！**
