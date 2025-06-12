# Advanced PowerShell script
param(
    [string]$Message = "Default message"
)

Write-Host "=== System Information ===" -ForegroundColor Cyan
$os = Get-WmiObject Win32_OperatingSystem
Write-Host "OS: $($os.Caption) $($os.Version)"
Write-Host "Architecture: $($os.OSArchitecture)"

Write-Host "`n=== Network Information ===" -ForegroundColor Yellow
Get-NetIPAddress | Where-Object {$_.AddressFamily -eq 'IPv4'} | Select-Object -First 3 | Format-Table

Write-Host "`n=== Message ===" -ForegroundColor Green
Write-Host $Message

# Test file operations
$testFile = Join-Path $env:TEMP "test_from_ps.txt"
"Created at $(Get-Date)" | Out-File $testFile
Write-Host "`nCreated file: $testFile"