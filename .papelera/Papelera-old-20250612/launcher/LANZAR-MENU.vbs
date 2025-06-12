' LANZAR-MENU.vbs - Lanzador invisible del menú GLADOS
' No muestra ventana CMD al ejecutar

Set objShell = CreateObject("WScript.Shell")
objShell.CurrentDirectory = objShell.ExpandEnvironmentStrings("%USERPROFILE%")
objShell.Run """C:\Program Files\WezTerm\wezterm-gui.exe"" start -- wsl bash -lc ""cd ~/glados && ~/glados/scripts/launchers/proyecto-menu-v2.sh""", 0, False