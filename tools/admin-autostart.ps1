#Requires -Version 5.1
<#
David Mouse 大衛滑鼠：以系統管理員權限開機自動啟動。

Windows 的「啟動」資料夾沒辦法啟動需要提權的程式，就算把捷徑勾了「以系統管理員
身分執行」，UAC 也會直接擋掉。要開機就自動取得管理員權限，唯一可靠的方式是註冊
一個工作排程（Task Scheduler），登入時觸發、以最高可用權限執行，而且不會跳 UAC。

用法（需要系統管理員權限，一般由 setup-admin-autostart.bat 代為提權呼叫）：
  powershell -NoProfile -ExecutionPolicy Bypass -File admin-autostart.ps1 -Action install -BaseDir <資料夾>
  powershell -NoProfile -ExecutionPolicy Bypass -File admin-autostart.ps1 -Action uninstall
#>
[CmdletBinding()]
param(
    [ValidateSet('install', 'uninstall', 'status')]
    [string]$Action = 'install',

    [string]$BaseDir = '',

    [string]$TaskName = 'DavidMouse'
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8

function Assert-Admin {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = [Security.Principal.WindowsPrincipal]$identity
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw '這支腳本需要系統管理員權限。請改用 setup-admin-autostart.bat（它會自動提權）。'
    }
}

function Find-Exe {
    param([string]$Base)

    $candidates = @()
    if ($Base) {
        $candidates += (Join-Path $Base 'david-mouse.exe')
        $candidates += (Join-Path $Base 'dist\david-mouse.exe')
    }
    $here = Split-Path -Parent $PSCommandPath
    $candidates += (Join-Path $here 'david-mouse.exe')
    $candidates += (Join-Path $here '..\dist\david-mouse.exe')

    foreach ($path in $candidates) {
        if (Test-Path -LiteralPath $path -PathType Leaf) {
            return (Resolve-Path -LiteralPath $path).Path
        }
    }
    throw "找不到 david-mouse.exe。請把這個腳本放在 exe 旁邊，或用 -BaseDir 指定 exe 所在的資料夾。`n已找過：`n  " + ($candidates -join "`n  ")
}

function Install-Task {
    $exe = Find-Exe -Base $BaseDir
    $workDir = Split-Path -Parent $exe
    $account = "$env:USERDOMAIN\$env:USERNAME"

    $action = New-ScheduledTaskAction -Execute $exe -WorkingDirectory $workDir

    $trigger = New-ScheduledTaskTrigger -AtLogOn -User $account
    try {
        # 登入後延遲 15 秒再啟動，讓桌面先載入完成，避免視窗被其他程式蓋掉。
        $trigger.Delay = 'PT15S'
    } catch {
        Write-Host '（此版本 Windows 不支援登入延遲，改為登入後立即啟動。）'
    }

    $principal = New-ScheduledTaskPrincipal -UserId $account -LogonType Interactive -RunLevel Highest

    # 筆電使用者很重要：預設值會讓工作在電池模式下不啟動、插頭一拔就被停掉。
    # ExecutionTimeLimit 設為 0 代表不限制，預設的三天上限會把長時間開機的程式砍掉。
    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -ExecutionTimeLimit ([TimeSpan]::Zero) `
        -MultipleInstances IgnoreNew `
        -StartWhenAvailable:$false

    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger `
        -Principal $principal -Settings $settings -Force `
        -Description 'David Mouse 大衛滑鼠：登入時以系統管理員權限自動啟動。' | Out-Null

    # 排程工作與啟動資料夾捷徑同時存在會開兩份，把舊捷徑清掉。
    $startup = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Startup'
    foreach ($name in @('DavidMouse.lnk', 'HeadMouseHelper.lnk')) {
        $lnk = Join-Path $startup $name
        if (Test-Path -LiteralPath $lnk) {
            Remove-Item -LiteralPath $lnk -Force
            Write-Host "已移除舊的啟動捷徑：$name"
        }
    }

    Write-Host ''
    Write-Host '設定完成。' -ForegroundColor Green
    Write-Host "  程式：$exe"
    Write-Host "  帳號：$account"
    Write-Host "  工作名稱：$TaskName"
    Write-Host '  下次登入 Windows 後會自動以系統管理員權限啟動，不會跳出 UAC 視窗。'
}

function Uninstall-Task {
    if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host '已移除自動啟動排程工作。' -ForegroundColor Green
    } else {
        Write-Host '本來就沒有這個排程工作，不用移除。'
    }
}

function Show-Status {
    try {
        Write-Host "找到程式：$(Find-Exe -Base $BaseDir)"
    } catch {
        Write-Host "找不到 david-mouse.exe（安裝時會失敗）。" -ForegroundColor Yellow
    }

    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if (-not $task) {
        Write-Host '目前沒有設定以系統管理員權限自動啟動。'
        return
    }
    Write-Host '目前已設定自動啟動：'
    Write-Host "  執行權限：$($task.Principal.RunLevel)"
    Write-Host "  執行檔：$($task.Actions[0].Execute)"
    Write-Host "  狀態：$($task.State)"
}

switch ($Action) {
    'install'   { Assert-Admin; Install-Task }
    'uninstall' { Assert-Admin; Uninstall-Task }
    'status'    { Show-Status }
}
