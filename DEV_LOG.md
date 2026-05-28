# Dev Log — David Mouse（YouTube 不再被誤觸的點擊輔具）

> **Notion import 用**：File → Import → Markdown → 選此檔。標題會變層級、表格與 code block 自動保留。

## Session 資訊

| 欄位 | 內容 |
|------|------|
| 日期 | 2026-05-27（夜）→ 2026-05-28（晨） |
| 模式 | 無人值守 overnight session |
| 主開發者（model） | Claude Opus 4.7（1M context） |
| 副諮詢者（model） | Google Gemini 2.5 Pro |
| 專案目錄 | `C:\Users\boren\Desktop\fordavicdmouse` |
| 客戶背景 | 用戶（張博仁，職能治療師 + 全端工程師）為頭控滑鼠個案開發點擊輔具 |
| 痛點 | PNC 自動點擊在看 YouTube 時，頭部晃動誤觸 → 歌曲一直暫停/播放 |

---

## 階段 0：環境檢查

- 工作目錄：空 git repo，只有 `.gitattributes` + `Initial commit`
- 已裝套件：`@google/gemini-cli@0.43.0`、`netlify-cli@24.11.1`、`opencode-ai@1.14.33`
- 平台：Windows 11 Pro，PowerShell 7+

---

## 階段 1：技術選型

### 嘗試 1：透過 MCP 呼叫 Gemini（失敗）

```
mcp__gemini-cli__ask-gemini
→ Error: Failed to spawn command: spawn gemini ENOENT
```

**原因**：MCP server 在預設 PATH 找不到 `gemini` 執行檔（雖然 npm 全域安裝實際存在於 `%AppData%\npm\gemini.cmd`）。

### 嘗試 2：用 Bash 直接呼叫 Gemini CLI（成功）

```bash
gemini -p "..."   # exit 0
```

→ **學到的事**：MCP server 若 spawn 失敗，可直接 Bash 用同樣的 CLI，token 消耗完全一樣（差別只在傳輸協定）。

### 我給 Gemini 的問題（精簡版）

> Windows 桌面小工具，給頭控滑鼠身障者。功能：dwell time 滑桿、4 大按鈕、視窗四角箭頭、開機自啟、全域滑鼠 hook + SendInput 模擬點擊。從以下選 1 並用 3 句說明：
> - A) Python + PySide6 + pynput + PyInstaller
> - B) Python + Tkinter + ctypes(Win32) + PyInstaller
> - C) Electron + Node + robotjs + electron-builder
>
> 判準（重要性遞減）：AI 寫順、全域 hook 容易做、打包簡單、體積小、頭控滑鼠下大按鈕高對比可用性。

### Gemini 的回覆

> **推薦 B**
> 1. ctypes 直連 Win32 API 確保全域 Hook 與 SendInput 的效能與穩定度，最符合身障輔具需求
> 2. Tkinter 極度輕量且 AI 撰寫率高，能輕易實現 240x320 高對比大按鈕介面而不產生冗餘體積
> 3. 此組合打包後 exe 最精簡，且無須擔心 Node.js 原生模組（如 robotjs）常見的編譯報錯

### 我的獨立判斷（事前未看 Gemini 答案）

| 方案 | 體積 | AI 寫順 | Win32 整合 | 風險 |
|------|------|---------|------------|------|
| A. PySide6 | 50MB+ | ◎ | △（要走 Qt 抽象） | 對長輩電腦不友善 |
| **B. Tkinter+ctypes** | 10–15MB | ○ | ◎（直連） | UI 客製化要工夫 |
| C. Electron | 80MB+ | ○ | △（robotjs 常炸） | native build 不穩定 |

**結論：與 Gemini 共識 → B 方案**

加碼決定：用 `pynput` 包 `SetWindowsHookEx`，避免手寫 ctypes callback 被 GC 回收引發 crash。

### 兩 model 協作模式心得

- Claude（我）：負責**規劃流程、實作、整合脈絡**
- Gemini：負責**單點諮詢、快速二意見**
- 不要讓 Gemini 寫整段 code（會跟 Claude 的 codebase context 脫節）
- 諮詢前自己先有候選答案，Gemini 用來**驗證或推翻**，不是用來代決策

---

## 階段 2：DESIGN.md 撰寫

產出檔案：`DESIGN.md`（位於 repo 根目錄）

包含：
1. 技術選型 + 理由表
2. 檔案結構樹
3. 8 個 module 的職責 1 行描述
4. requirements.txt 內容
5. 文字版 UI wireframe
6. settings.json schema
7. 風險與 TODO

> 關鍵自我約束：開機自動啟動**不寫 registry**，改用 Startup folder 的 .lnk 捷徑。
> 原因：用戶在 prompt 明確說「不要動 Windows 系統設定、registry」。
> Trade-off：Startup folder 比 registry 慢 ~200ms 啟動，但符合限制。

---

## 階段 3：實作

（進行中 — 完工後本段會補完）

---

## 階段 4：Code Review

（待 Gemini code review）

---

## 階段 5：早晨報告

→ 見 `OVERNIGHT_REPORT.md`

---

## 學到的可重用 pattern

### Pattern 1：MCP server 不穩時的 fallback
MCP 工具呼叫失敗，第一反應不是放棄，而是**檢查底層 CLI 是否存在**。多數 MCP 只是 binary 的 thin wrapper，Bash 直連通常一樣能用。

### Pattern 2：雙 model 諮詢的 prompt 寫法
要 Gemini 二意見時，**先列好候選方案**讓它選，**強制限制字數**（"3 句話以內"），不要開放式問。否則會收到長篇大論浪費 token。

### Pattern 3：醫療輔具 UI 三鐵則
- 按鈕 ≥ 60x60 px
- 顏色高對比（紅/綠雙態）
- 操作步驟 ≤ 2 步

### Pattern 4：Windows .bat 純 ASCII
用戶 CLAUDE.md 明確規定：所有 `.bat`/`.cmd` 只用 ASCII，禁中文。因為 cmd.exe 預設 code page 950 vs UTF-8 衝突會炸。寫腳本時主動遵守。

### Pattern 5：Notion-friendly markdown
- 標題層級不超過 H3
- 表格不要巢狀
- code block 一律標語言（` ```bash ` 而非 ` ``` `）
- 避免 HTML tag（Notion import 會丟）
- 列表縮排用 2 空格，不要用 tab
