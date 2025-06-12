@echo off
:: Script para crear accesos directos de Voz Claude en AppsWSL
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1

set "APPS_DIR=%USERPROFILE%\Desktop\AppsWSL"
set "SCRIPT_DIR=%~dp0"

echo.
echo ====================================================
echo    Creador de Accesos Directos - Voz Claude
echo ====================================================
echo.

:: Verificar carpeta AppsWSL
if not exist "%APPS_DIR%" (
    echo Creando carpeta AppsWSL...
    mkdir "%APPS_DIR%"
)

:: Crear accesos directos usando PowerShell en línea
echo Creando accesos directos...

:: 1. Voz Claude Moderno
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%APPS_DIR%\Voz Claude (Moderno).lnk'); $s.TargetPath = 'cmd.exe'; $s.Arguments = '/c \"%SCRIPT_DIR%VozClaude-Fixed.bat\"'; $s.Description = 'Configuracion moderna de voz con deteccion mejorada'; $s.IconLocation = '%SCRIPT_DIR%voz-claude-lips.ico,0'; $s.Hotkey = 'CTRL+SHIFT+V'; $s.Save()"
echo [OK] Voz Claude (Moderno)

:: 2. Voz Claude PowerShell
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%APPS_DIR%\Voz Claude (PowerShell).lnk'); $s.TargetPath = 'powershell.exe'; $s.Arguments = '-ExecutionPolicy Bypass -File \"%SCRIPT_DIR%VozClaude-Optimized.ps1\"'; $s.Description = 'Version PowerShell optimizada con navegacion fluida'; $s.IconLocation = '%SCRIPT_DIR%voz-claude-lips.ico,0'; $s.Hotkey = 'CTRL+SHIFT+F'; $s.Save()"
echo [OK] Voz Claude (PowerShell)

:: 3. Voz Claude Simple
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%APPS_DIR%\Voz Claude (Simple).lnk'); $s.TargetPath = 'cmd.exe'; $s.Arguments = '/c \"%SCRIPT_DIR%voz-claude-simple.bat\"'; $s.Description = 'Version minimalista y funcional'; $s.IconLocation = '%SCRIPT_DIR%voz-claude-lips.ico,0'; $s.Save()"
echo [OK] Voz Claude (Simple)

:: 4. Configurar Voz Linux
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%APPS_DIR%\Configurar Voz (Linux).lnk'); $s.TargetPath = 'wsl.exe'; $s.Arguments = '-d Ubuntu-24.04 -- bash -c \"cd /home/lauta/glados/scripts/voz ^&^& ./configurar-voz.sh\"'; $s.Description = 'Configuracion completa desde terminal Linux'; $s.IconLocation = '%SCRIPT_DIR%voz-claude-lips.ico,0'; $s.Save()"
echo [OK] Configurar Voz (Linux)

:: 5. Probar Voz
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%APPS_DIR%\Probar Voz Actual.lnk'); $s.TargetPath = 'wsl.exe'; $s.Arguments = '-d Ubuntu-24.04 -- bash -c \"cd /home/lauta/glados/scripts/voz ^&^& ./notificar-claude.sh ''Hola, soy tu asistente Claude''\"'; $s.Description = 'Prueba rapida de la voz configurada'; $s.IconLocation = '%SCRIPT_DIR%voz-claude-lips.ico,0'; $s.Hotkey = 'CTRL+SHIFT+T'; $s.Save()"
echo [OK] Probar Voz Actual

:: Crear README
echo.
echo Creando archivo README...
(
echo # Voz Claude - Accesos Directos
echo.
echo ## Aplicaciones disponibles:
echo.
echo 1. **Voz Claude (Moderno)** - Ctrl+Shift+V
echo    Interfaz moderna con deteccion mejorada
echo.
echo 2. **Voz Claude (PowerShell)** - Ctrl+Shift+F
echo    Version optimizada con navegacion fluida
echo.
echo 3. **Voz Claude (Simple)**
echo    Version minimalista y funcional
echo.
echo 4. **Configurar Voz (Linux)**
echo    Configuracion completa desde terminal
echo.
echo 5. **Probar Voz Actual** - Ctrl+Shift+T
echo    Prueba rapida de la voz configurada
echo.
echo ## Motores disponibles:
echo - gtts: Google Text-to-Speech
echo - pico2wave: Voz femenina natural
echo - festival: Voz masculina clara
echo - espeak: Voz robotica minimalista
echo - none: Modo silencioso
echo.
echo Configuracion: ~/.config/claude-voz/config
) > "%APPS_DIR%\VozClaude-README.txt"

:: Verificar si necesitamos crear el icono
if not exist "%SCRIPT_DIR%voz-claude-lips.ico" (
    echo.
    echo ADVERTENCIA: No se encontro el icono voz-claude-lips.ico
    echo Ejecuta crear-icono-labios-mejorado.ps1 para crearlo
)

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
echo Presiona cualquier tecla para abrir la carpeta...
pause >nul

:: Abrir carpeta
start "" "%APPS_DIR%"