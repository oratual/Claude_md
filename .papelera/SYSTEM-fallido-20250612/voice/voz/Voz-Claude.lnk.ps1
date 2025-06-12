# Script simplificado para crear acceso directo con icono

# Crear acceso directo
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\💋 Voz Claude.lnk")
$Shortcut.TargetPath = "cmd.exe"
$Shortcut.Arguments = "/c `"$env:USERPROFILE\Desktop\configurar-voz-windows.bat`""
$Shortcut.WorkingDirectory = "$env:USERPROFILE\Desktop"
$Shortcut.Description = "Configuración de Voz para Claude - Voces femeninas y más"
$Shortcut.WindowStyle = 1

# Si tienes un icono, úsalo, sino usa el de cmd
$iconPath = "$env:USERPROFILE\Desktop\lips-icon.ico"
if (Test-Path $iconPath) {
    $Shortcut.IconLocation = $iconPath
} else {
    # Usar icono de sistema (bocina/audio)
    $Shortcut.IconLocation = "%SystemRoot%\System32\mmres.dll,0"
}

$Shortcut.Save()

Write-Host "✅ Acceso directo '💋 Voz Claude' creado en el escritorio" -ForegroundColor Green
Write-Host "" -ForegroundColor Green
Write-Host "Para crear el icono de labios:" -ForegroundColor Yellow
Write-Host "1. Abre 'lips-icon.html' en el navegador" -ForegroundColor Yellow
Write-Host "2. Descarga el PNG" -ForegroundColor Yellow
Write-Host "3. Convierte a ICO en convertio.co" -ForegroundColor Yellow
Write-Host "4. Clic derecho en el acceso directo > Propiedades > Cambiar icono" -ForegroundColor Yellow