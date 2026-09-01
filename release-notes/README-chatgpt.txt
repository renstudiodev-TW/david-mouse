David Mouse（支援 ChatGPT 語音輸入版）
=======================================

跟一般版功能完全相同，多了一顆「語音聽寫」按鈕，讓頭控滑鼠使用者可以
不必碰鍵盤，就能觸發 ChatGPT 桌面版的語音聽寫功能來打字。

怎麼用
------
1. 解壓縮這個壓縮檔。
2. 雙擊 david-mouse-chatgpt.exe 執行。
3. 打開 ChatGPT 桌面版，到設定裡把「語音聽寫」的快捷鍵設定為 Ctrl+/
   （David Mouse 的語音聽寫按鈕就是送出這個組合鍵，兩邊要設成一樣才會有反應）。
4. 用頭控滑鼠停留在 David Mouse 的「🎙 語音聽寫」按鈕上，跟左鍵／右鍵／
   雙擊按鈕的用法一樣：按下後會倒數幾秒，趁倒數的時候把游標移到 ChatGPT
   的輸入框上，時間一到就會先點一下輸入框、接著送出 Ctrl+/ 啟動聽寫。
   不需要先手動點過輸入框，倒數時移過去就好。

不需要安裝程式，也不需要另外裝 Python。

開機以系統管理員身分自動啟動
----------------------------
如果某些視窗會忽略模擬點擊，需要 David Mouse 本身以系統管理員身分執行，
雙擊：

    setup-admin-autostart.bat

會跳出一次系統管理員授權，之後每次登入都會以最高權限自動啟動 David
Mouse，不會再跳出 UAC 視窗。要取消就雙擊 remove-admin-autostart.bat。

注意：Windows 的「啟動」資料夾捷徑無法做到這件事，勾選「以系統管理員
身分執行」的捷徑會被 UAC 靜默擋下，所以改用工作排程器。

Windows SmartScreen 警告
------------------------
第一次執行時，Windows 可能會顯示：

    Windows 已保護您的電腦
    Microsoft Defender SmartScreen 已防止執行來路不明的應用程式。

這是因為這個程式沒有花錢買程式碼簽章憑證，不代表軟體不安全，是開放原
始碼的免費工具。

點「其他資訊」→「仍要執行」即可繼續。

完整說明、截圖與大衛的故事：
    https://davidmouse.renstudio.tw

原始碼（MIT 授權）：
    https://github.com/renstudiodev-TW/david-mouse

由 Ren Studio 為大衛以及所有頭控滑鼠使用者製作。
