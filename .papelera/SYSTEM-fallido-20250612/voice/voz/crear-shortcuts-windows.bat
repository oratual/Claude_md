@echo off
:: Crear accesos directos de Voz Claude en AppsWSL
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1

set "APPS_DIR=%USERPROFILE%\Desktop\AppsWSL"
set "SCRIPT_PATH=\\wsl.localhost\Ubuntu-24.04\home\lauta\glados\scripts\voz"

echo.
echo ====================================================
echo    Creador de Accesos Directos - Voz Claude
echo ====================================================
echo.

:: Crear carpeta si no existe
if not exist "%APPS_DIR%" (
    echo Creando carpeta AppsWSL...
    mkdir "%APPS_DIR%"
)

:: Crear accesos directos usando VBScript (más confiable)
echo Creando accesos directos...

:: 1. Voz Claude Moderno
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%temp%\CreateShortcut1.vbs"
echo sLinkFile = "%APPS_DIR%\Voz Claude (Moderno).lnk" >> "%temp%\CreateShortcut1.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%temp%\CreateShortcut1.vbs"
echo oLink.TargetPath = "cmd.exe" >> "%temp%\CreateShortcut1.vbs"
echo oLink.Arguments = "/c ""%SCRIPT_PATH%\VozClaude-Fixed.bat""" >> "%temp%\CreateShortcut1.vbs"
echo oLink.Description = "Configuracion moderna de voz con deteccion mejorada" >> "%temp%\CreateShortcut1.vbs"
echo oLink.Hotkey = "CTRL+SHIFT+V" >> "%temp%\CreateShortcut1.vbs"
echo oLink.Save >> "%temp%\CreateShortcut1.vbs"
cscript //nologo "%temp%\CreateShortcut1.vbs"
del "%temp%\CreateShortcut1.vbs"
echo [OK] Voz Claude (Moderno) - Ctrl+Shift+V

:: 2. Voz Claude PowerShell
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%temp%\CreateShortcut2.vbs"
echo sLinkFile = "%APPS_DIR%\Voz Claude (PowerShell).lnk" >> "%temp%\CreateShortcut2.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%temp%\CreateShortcut2.vbs"
echo oLink.TargetPath = "powershell.exe" >> "%temp%\CreateShortcut2.vbs"
echo oLink.Arguments = "-ExecutionPolicy Bypass -File ""%SCRIPT_PATH%\VozClaude-Optimized.ps1""" >> "%temp%\CreateShortcut2.vbs"
echo oLink.Description = "Version PowerShell optimizada con navegacion fluida" >> "%temp%\CreateShortcut2.vbs"
echo oLink.Hotkey = "CTRL+SHIFT+F" >> "%temp%\CreateShortcut2.vbs"
echo oLink.Save >> "%temp%\CreateShortcut2.vbs"
cscript //nologo "%temp%\CreateShortcut2.vbs"
del "%temp%\CreateShortcut2.vbs"
echo [OK] Voz Claude (PowerShell) - Ctrl+Shift+F

:: 3. Voz Claude Simple
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%temp%\CreateShortcut3.vbs"
echo sLinkFile = "%APPS_DIR%\Voz Claude (Simple).lnk" >> "%temp%\CreateShortcut3.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%temp%\CreateShortcut3.vbs"
echo oLink.TargetPath = "cmd.exe" >> "%temp%\CreateShortcut3.vbs"
echo oLink.Arguments = "/c ""%SCRIPT_PATH%\voz-claude-simple.bat""" >> "%temp%\CreateShortcut3.vbs"
echo oLink.Description = "Version minimalista y funcional" >> "%temp%\CreateShortcut3.vbs"
echo oLink.Save >> "%temp%\CreateShortcut3.vbs"
cscript //nologo "%temp%\CreateShortcut3.vbs"
del "%temp%\CreateShortcut3.vbs"
echo [OK] Voz Claude (Simple)

:: 4. Configurar Voz Linux
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%temp%\CreateShortcut4.vbs"
echo sLinkFile = "%APPS_DIR%\Configurar Voz (Linux).lnk" >> "%temp%\CreateShortcut4.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%temp%\CreateShortcut4.vbs"
echo oLink.TargetPath = "wsl.exe" >> "%temp%\CreateShortcut4.vbs"
echo oLink.Arguments = "-d Ubuntu-24.04 -- bash -c ""cd /home/lauta/glados/scripts/voz && ./configurar-voz.sh""" >> "%temp%\CreateShortcut4.vbs"
echo oLink.Description = "Configuracion completa desde terminal Linux" >> "%temp%\CreateShortcut4.vbs"
echo oLink.Save >> "%temp%\CreateShortcut4.vbs"
cscript //nologo "%temp%\CreateShortcut4.vbs"
del "%temp%\CreateShortcut4.vbs"
echo [OK] Configurar Voz (Linux)

:: 5. Probar Voz
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%temp%\CreateShortcut5.vbs"
echo sLinkFile = "%APPS_DIR%\Probar Voz Actual.lnk" >> "%temp%\CreateShortcut5.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%temp%\CreateShortcut5.vbs"
echo oLink.TargetPath = "wsl.exe" >> "%temp%\CreateShortcut5.vbs"
echo oLink.Arguments = "-d Ubuntu-24.04 -- bash -c ""cd /home/lauta/glados/scripts/voz && ./notificar-claude.sh 'Hola, soy tu asistente Claude'""" >> "%temp%\CreateShortcut5.vbs"
echo oLink.Description = "Prueba rapida de la voz configurada" >> "%temp%\CreateShortcut5.vbs"
echo oLink.Hotkey = "CTRL+SHIFT+T" >> "%temp%\CreateShortcut5.vbs"
echo oLink.Save >> "%temp%\CreateShortcut5.vbs"
cscript //nologo "%temp%\CreateShortcut5.vbs"
del "%temp%\CreateShortcut5.vbs"
echo [OK] Probar Voz Actual - Ctrl+Shift+T

:: Crear README
echo.
echo Creando archivo README...
(
echo VOZ CLAUDE - ACCESOS DIRECTOS
echo =============================
echo.
echo APLICACIONES DISPONIBLES:
echo.
echo 1. Voz Claude (Moderno) - Ctrl+Shift+V
echo    Interfaz moderna con deteccion mejorada
echo.
echo 2. Voz Claude (PowerShell) - Ctrl+Shift+F  
echo    PowerShell optimizado con navegacion fluida
echo.
echo 3. Voz Claude (Simple)
echo    Version minimalista y funcional
echo.
echo 4. Configurar Voz (Linux)
echo    Configuracion completa desde terminal
echo.
echo 5. Probar Voz Actual - Ctrl+Shift+T
echo    Prueba rapida de la voz configurada
echo.
echo MOTORES DISPONIBLES:
echo - gtts: Google Text-to-Speech (requiere internet)
echo - pico2wave: Voz femenina natural (offline)
echo - festival: Voz masculina clara (offline)
echo - espeak: Voz robotica (offline)
echo - none: Modo silencioso
echo.
echo CONFIGURACION:
echo ~/.config/claude-voz/config
) > "%APPS_DIR%\VozClaude-README.txt"

echo.
echo ====================================================
echo    Proceso completado!
echo ====================================================
echo.
echo Accesos directos creados en: %APPS_DIR%
echo.
echo Atajos de teclado configurados:
echo   Ctrl+Shift+V - Voz Claude (Moderno)
echo   Ctrl+Shift+F - Voz Claude (PowerShell)
echo   Ctrl+Shift+T - Probar Voz
echo.
pause

:: Abrir carpeta
start "" "%APPS_DIR%"