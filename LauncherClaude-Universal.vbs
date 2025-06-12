' LauncherClaude-Universal.vbs
' Lanzador universal que no depende de rutas WSL específicas

Set objShell = CreateObject("WScript.Shell")

' Cambiar al directorio del usuario
objShell.CurrentDirectory = objShell.ExpandEnvironmentStrings("%USERPROFILE%")

' Ejecutar comando directamente sin depender de rutas WSL
objShell.Run """C:\Program Files\WezTerm\wezterm-gui.exe"" start -- wsl -e bash -lc ""cd ~/glados && ~/glados/scripts/launchers/proyecto-menu-v2.sh""", 0, False