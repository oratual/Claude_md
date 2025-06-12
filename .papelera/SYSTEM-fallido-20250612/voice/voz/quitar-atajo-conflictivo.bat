@echo off
:: Script para quitar el atajo Ctrl+Shift+V que interfiere con el pegado
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
color 0E

echo ====================================================
echo     REMOVEDOR DE ATAJO CONFLICTIVO (Ctrl+Shift+V)
echo ====================================================
echo.
echo Este script quitara el atajo Ctrl+Shift+V de los
echo accesos directos de Voz Claude para evitar conflictos
echo con el pegado en la consola.
echo.
pause

set "APPS_DIR=%USERPROFILE%\Desktop\AppsWSL"
set "DESKTOP=%USERPROFILE%\Desktop"
set "count=0"

echo.
echo Buscando accesos directos de Voz Claude...
echo.

:: Buscar en AppsWSL
if exist "%APPS_DIR%" (
    echo Revisando carpeta AppsWSL...
    for %%f in ("%APPS_DIR%\*.lnk") do (
        echo Procesando: %%~nxf
        powershell -Command "$sh = New-Object -ComObject WScript.Shell; $lnk = $sh.CreateShortcut('%%f'); if ($lnk.Hotkey -eq 'CTRL+SHIFT+V') { $lnk.Hotkey = ''; $lnk.Save(); Write-Host '[MODIFICADO]' -ForegroundColor Green } else { Write-Host '[Sin cambios]' -ForegroundColor Gray }"
        set /a count+=1
    )
)

:: Buscar en Escritorio
echo.
echo Revisando escritorio...
for %%f in ("%DESKTOP%\Voz Claude*.lnk" "%DESKTOP%\*Claude*.lnk") do (
    if exist "%%f" (
        echo Procesando: %%~nxf
        powershell -Command "$sh = New-Object -ComObject WScript.Shell; $lnk = $sh.CreateShortcut('%%f'); if ($lnk.Hotkey -eq 'CTRL+SHIFT+V') { $lnk.Hotkey = ''; $lnk.Save(); Write-Host '[MODIFICADO]' -ForegroundColor Green } else { Write-Host '[Sin cambios]' -ForegroundColor Gray }"
        set /a count+=1
    )
)

echo.
echo ====================================================
echo                    PROCESO COMPLETADO
echo ====================================================
echo.
echo Se revisaron %count% accesos directos.
echo El atajo Ctrl+Shift+V ha sido removido donde existia.
echo.
echo Ahora puedes usar Ctrl+Shift+V para pegar normalmente.
echo.
echo Atajos que siguen funcionando:
echo   Ctrl+Shift+F - Voz Claude PowerShell
echo   Ctrl+Shift+T - Probar Voz
echo.
pause