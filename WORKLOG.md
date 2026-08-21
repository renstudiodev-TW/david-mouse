# David Mouse 進度日誌

新的在上面，舊的在下面。開工時讀最上面那一筆。

> 這個專案的 `docs/` 是對外的教學網站（Netlify 部署，已在 `.gitignore` 排除），
> 所以團隊文件不放 `docs/team/`，避免內部決策被公開到 davidmouse.renstudio.tw。
> 決策簿放在專案根目錄的 `DECISIONS.md`。

---

## 2026-08-21

### 做了什麼

- **開機以系統管理員權限自動啟動**。`src/autostart.py` 改成雙模式：程式本身以系統管理員身分執行時，用 `schtasks /Create /XML` 註冊名為 `DavidMouse` 的工作排程（登入時觸發、`HighestAvailable`、延遲 15 秒）；否則退回原本的 Startup 資料夾 `.lnk` 捷徑。兩者互斥，建立其中一個時會清掉另一個。
- **一鍵設定腳本**。`setup-admin-autostart.bat` 與 `remove-admin-autostart.bat`（純 ASCII，會自行提權）加上實作本體 `tools/admin-autostart.ps1`，讓不想重新打包 exe 的情況也能設定。`build.bat` 已把三支腳本一起包進 release zip。
- **UI 與 i18n**。按鈕新增「開（管理員）」狀態，四語系字串到齊。App 啟動時會以系統現況校正設定檔，避免使用者手動刪掉排程後狀態不同步。
- **發布 v1.1.0**。合併進 main、重新打包 exe、發 GitHub Release，網站四個語系頁面補上管理員模式說明並部署到 Netlify。
- **修掉多重實例 bug**。新增 `src/single_instance.py`，用 `%APPDATA%\DavidMouse\instance.lock` 的獨占鎖擋掉第二份；搶不到鎖就把先開的視窗叫到前面並閃標題列，自己安靜退場。補 5 個測試，測試總數 9 到 14。

### 決策

- 開機提權自動啟動改用工作排程器而非啟動資料夾捷徑（詳見 `DECISIONS.md` D-004）。
- 單一實例用鎖檔而非具名 Mutex（D-005）。
- 團隊文件放專案根目錄而非 `docs/team/`（D-006）。

### 未完成

- **v1.1.1 尚未發布**。單一實例修正已合併 main（commit `4e0fbe2`）、exe 已重新打包在 `dist\david-mouse.exe`，但依 RC 指示暫不發 Release，等他自己在 David 的電腦上測過再決定。網站下載鍵目前仍指向 v1.1.0。
- **一種組合沒實測到**：排程工作開的「管理員實例」加上使用者手動開的「一般實例」。要提權才測得到，需要有人按 UAC。理論上鎖檔在使用者自己的 AppData 底下、兩種權限都存取得到所以會擋下來，但值得在 David 的電腦上實際試一次。就算真的沒擋到，結果也只是回到修正前的行為，不會更糟。
- 產品化檢查表沒有逐項對過。這是一個已經交付給實際使用者的工具，下次值得花一輪把邊界情境與已知限制寫清楚。

### 卡點

無。

### 下一步

1. RC 在 David 的電腦上驗證單一實例（開起來後再點一次捷徑，應該只會閃一下不會多開）。
2. 驗過就發 v1.1.1 Release，網站下載鍵會自動指向新版（不需要重新部署 Netlify，除非要在網站上補說明）。
3. 提醒使用者換版時要把舊的完全關掉，軟導航式的重開不保證拿到新的執行檔。

### 環境備註

- 打包用的是 scoop 那支 Python（`C:\Users\boren\scoop\apps\python\current`，`pyinstaller` 裝在那裡）。今天補裝了 `pynput` 進去，之前缺這個所以打包會失敗。
- 專案放在 `C:\Users\boren\Desktop\fordavicdmouse`，不在全域預設的 `C:\RenStudio\case` 底下。這是既有狀態，沒有搬動。
