# Script PowerShell Básico
Write-Host "=== Test PowerShell 1 ===" -ForegroundColor Cyan
Write-Host "Fecha: $(Get-Date)"
Write-Host "Usuario: $env:USERNAME"
Write-Host "Computadora: $env:COMPUTERNAME"
Write-Host ""

# Información del sistema
$os = Get-WmiObject Win32_OperatingSystem
Write-Host "Sistema: $($os.Caption)"
Write-Host "Versión: $($os.Version)"
Write-Host ""

# Listar procesos top 5 por CPU
Write-Host "Top 5 procesos por CPU:" -ForegroundColor Yellow
Get-Process | Sort-Object CPU -Descending | Select-Object -First 5 | Format-Table Name, CPU, WS -AutoSize