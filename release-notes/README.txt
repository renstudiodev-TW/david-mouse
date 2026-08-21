David Mouse
===========

A free Windows tool that helps head-mouse users avoid accidental clicks
while watching YouTube and elsewhere.

How to run
----------
1. Unzip this archive.
2. Double-click david-mouse.exe.

That's it. No installer, no Python required.

Start at logon as Administrator
-------------------------------
Some apps (and some elevated windows) ignore simulated clicks unless David
Mouse itself runs as Administrator. If you need that, double-click:

    setup-admin-autostart.bat

It asks for administrator rights once, then registers a Scheduled Task that
launches David Mouse at every logon with the highest available privileges,
without any UAC prompt. To undo it, double-click remove-admin-autostart.bat.

Note: the Windows Startup folder cannot do this. A shortcut there with "Run
as administrator" checked is silently blocked by UAC, which is why a
Scheduled Task is used instead.

Windows SmartScreen warning
---------------------------
On first launch, Windows may show:

    Windows protected your PC
    Microsoft Defender SmartScreen prevented an unrecognized app from
    starting.

This happens because the binary is not code-signed with a paid
certificate. The app is open-source and safe to run.

To proceed, click "More info" -> "Run anyway".

Full documentation, screenshots, and the David story:
    https://davidmouse.renstudio.tw

Source code (MIT license):
    https://github.com/renstudiodev-TW/david-mouse

Made by Ren Studio for David and all head-mouse users.
