# LANZAR-MENU.ps1 - Lanzador PowerShell del menú GLADOS
# Ejecuta sin mostrar ventana

$host.ui.RawUI.WindowTitle = "GLADOS Menu"
Set-Location $env:USERPROFILE
Start-Process "C:\Program Files\WezTerm\wezterm-gui.exe" -ArgumentList "start","--","wsl","bash","-lc","`"cd ~/glados && ~/glados/scripts/launchers/proyecto-menu-v2.sh`"" -WindowStyle Hidden