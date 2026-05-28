' David Mouse - silent launcher (no console window)
' Double-click this file (or pin it to Start / taskbar) to run the app
' without the black console window that run.bat opens.
'
' Behaviour: invokes run.bat with a hidden window. run.bat finds Python
' and launches the app; when the app exits, the hidden process ends too.

Option Explicit

Dim shell, fso, scriptDir, batPath
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
batPath = scriptDir & "\run.bat"

' 0 = hidden window, False = don't wait for it to finish.
shell.Run """" & batPath & """", 0, False
