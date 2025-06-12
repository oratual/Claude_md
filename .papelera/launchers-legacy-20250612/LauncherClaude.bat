@echo off
:: LauncherClaude.bat - Lanzador del menú principal de GLADOS

cd /d "%USERPROFILE%" 2>nul
start "" "C:\Program Files\WezTerm\wezterm-gui.exe" start -- wsl bash -lc "cd ~/glados && ~/glados/scripts/launchers/proyecto-menu-v2.sh"
exit