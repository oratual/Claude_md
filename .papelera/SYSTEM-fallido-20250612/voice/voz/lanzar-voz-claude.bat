@echo off
:: Lanzador para Voz Claude
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0VozClaude-Fixed.ps1"
if errorlevel 1 (
    echo.
    echo Error al ejecutar PowerShell
    echo Intentando version simple...
    echo.
    call "%~dp0voz-claude-simple.bat"
)