@echo off
:: Archivo CMD avanzado

echo === Test CMD Avanzado ===
echo.

:: Crear variable con timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set timestamp=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%_%datetime:~8,2%-%datetime:~10,2%-%datetime:~12,2%
echo Timestamp: %timestamp%

:: Verificar versión de Windows
for /f "tokens=4-5 delims=[.] " %%i in ('ver') do set version=%%i.%%j
echo Version Windows: %version%

:: Operaciones con archivos
set tempfile=%TEMP%\wsl_cmd_test_%timestamp%.txt
echo Creando archivo temporal: %tempfile%
echo Prueba desde CMD > "%tempfile%"
echo Contenido: 
type "%tempfile%"
del "%tempfile%"

:: Llamar a PowerShell desde CMD
echo.
echo Ejecutando PowerShell desde CMD:
powershell -NoProfile -Command "Write-Host 'PowerShell llamado desde CMD' -ForegroundColor Green; $PSVersionTable.PSVersion"

:: Verificar conectividad
echo.
ping -n 1 8.8.8.8 >nul 2>&1 && echo [OK] Conectividad Internet || echo [ERROR] Sin Internet

echo.
echo CMD avanzado completado!