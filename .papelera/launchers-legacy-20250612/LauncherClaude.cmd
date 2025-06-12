@echo off
cd /d %USERPROFILE%
start "" "C:\Program Files\WezTerm\wezterm-gui.exe" start -- wsl -e bash -lc "cd ~/glados && ~/glados/scripts/launchers/proyecto-menu-v2.sh"