# LauncherClaude.ps1 - Lanzador PowerShell simple
# Click derecho -> Ejecutar con PowerShell

Start-Process "C:\Program Files\WezTerm\wezterm-gui.exe" -ArgumentList "start","--","wsl","-e","bash","-lc","cd ~/glados && ~/glados/scripts/launchers/proyecto-menu-v2.sh" -NoNewWindow