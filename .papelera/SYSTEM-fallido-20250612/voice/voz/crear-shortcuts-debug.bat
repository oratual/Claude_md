@echo off
:: Crear accesos directos de Voz Claude en AppsWSL - VERSION DEBUG
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
color 0A
title Creador de Accesos Directos - Voz Claude (DEBUG)

:: Configurar ventana más grande
mode con: cols=100 lines=40

echo ================================================================================
echo                    CREADOR DE ACCESOS DIRECTOS - VOZ CLAUDE
echo                                VERSION DEBUG
echo ================================================================================
echo.

:: Variables
set "APPS_DIR=%USERPROFILE%\Desktop\AppsWSL"
set "SCRIPT_PATH=\\wsl.localhost\Ubuntu-24.04\home\lauta\glados\scripts\voz"
set "LOG_FILE=%TEMP%\voz-claude-shortcuts-log.txt"

:: Iniciar log
echo [%date% %time%] Iniciando creacion de accesos directos > "%LOG_FILE%"
echo Script ejecutado desde: %CD% >> "%LOG_FILE%"

echo [1/7] Verificando entorno...
echo ----------------------------------------

:: Mostrar variables
echo USERPROFILE: %USERPROFILE%
echo APPS_DIR: %APPS_DIR%
echo SCRIPT_PATH: %SCRIPT_PATH%
echo LOG_FILE: %LOG_FILE%
echo.

:: Verificar/crear carpeta AppsWSL
echo [2/7] Verificando carpeta AppsWSL...
echo ----------------------------------------
if exist "%APPS_DIR%" (
    echo [OK] La carpeta ya existe: %APPS_DIR%
    echo [OK] Carpeta existe >> "%LOG_FILE%"
) else (
    echo [!] La carpeta no existe, creandola...
    mkdir "%APPS_DIR%" 2>&1
    if exist "%APPS_DIR%" (
        echo [OK] Carpeta creada exitosamente
        echo [OK] Carpeta creada >> "%LOG_FILE%"
    ) else (
        echo [ERROR] No se pudo crear la carpeta!
        echo [ERROR] Fallo al crear carpeta >> "%LOG_FILE%"
        goto :error
    )
)
echo.

:: Verificar acceso a scripts WSL
echo [3/7] Verificando acceso a scripts WSL...
echo ----------------------------------------
if exist "%SCRIPT_PATH%\VozClaude-Fixed.bat" (
    echo [OK] Acceso a scripts WSL confirmado
    echo [OK] Acceso WSL confirmado >> "%LOG_FILE%"
) else (
    echo [ADVERTENCIA] No se puede acceder a los scripts WSL
    echo Intentando ruta alternativa...
    set "SCRIPT_PATH=\\wsl$\Ubuntu-24.04\home\lauta\glados\scripts\voz"
    if exist "!SCRIPT_PATH!\VozClaude-Fixed.bat" (
        echo [OK] Ruta alternativa funciona
        echo [OK] Ruta alternativa WSL funciona >> "%LOG_FILE%"
    ) else (
        echo [ERROR] No se puede acceder a los scripts en WSL
        echo [ERROR] Sin acceso a scripts WSL >> "%LOG_FILE%"
        echo.
        echo Posibles soluciones:
        echo 1. Verifica que WSL este ejecutandose
        echo 2. Verifica que la distribucion sea Ubuntu-24.04
        echo 3. Intenta ejecutar: wsl --list --verbose
        goto :error
    )
)
echo.

:: Crear accesos directos
echo [4/7] Creando accesos directos...
echo ----------------------------------------

:: Shortcut 1: Voz Claude Moderno
echo.
echo Creando: Voz Claude (Moderno)...
(
    echo Set oWS = WScript.CreateObject("WScript.Shell"^)
    echo sLinkFile = "%APPS_DIR%\Voz Claude Moderno.lnk"
    echo Set oLink = oWS.CreateShortcut(sLinkFile^)
    echo oLink.TargetPath = "cmd.exe"
    echo oLink.Arguments = "/c ""%SCRIPT_PATH%\VozClaude-Fixed.bat"""
    echo oLink.Description = "Configuracion moderna de voz con deteccion mejorada"
    echo oLink.WorkingDirectory = "%SCRIPT_PATH%"
    echo REM oLink.Hotkey = "CTRL+SHIFT+V" - Desactivado para no interferir con pegado
    echo oLink.Save
    echo WScript.Echo "[VBS] Shortcut creado: " ^& sLinkFile
) > "%TEMP%\CreateShortcut1.vbs"

cscript //nologo "%TEMP%\CreateShortcut1.vbs" 2>&1
if %errorlevel%==0 (
    echo [OK] Creado exitosamente
    echo [OK] Shortcut 1 creado >> "%LOG_FILE%"
) else (
    echo [ERROR] Fallo al crear shortcut
    echo [ERROR] Fallo shortcut 1 >> "%LOG_FILE%"
)
del "%TEMP%\CreateShortcut1.vbs" 2>nul

:: Shortcut 2: Voz Claude PowerShell
echo.
echo Creando: Voz Claude (PowerShell)...
(
    echo Set oWS = WScript.CreateObject("WScript.Shell"^)
    echo sLinkFile = "%APPS_DIR%\Voz Claude PowerShell.lnk"
    echo Set oLink = oWS.CreateShortcut(sLinkFile^)
    echo oLink.TargetPath = "powershell.exe"
    echo oLink.Arguments = "-ExecutionPolicy Bypass -File ""%SCRIPT_PATH%\VozClaude-Optimized.ps1"""
    echo oLink.Description = "Version PowerShell optimizada con navegacion fluida"
    echo oLink.WorkingDirectory = "%SCRIPT_PATH%"
    echo oLink.Hotkey = "CTRL+SHIFT+F"
    echo oLink.Save
    echo WScript.Echo "[VBS] Shortcut creado: " ^& sLinkFile
) > "%TEMP%\CreateShortcut2.vbs"

cscript //nologo "%TEMP%\CreateShortcut2.vbs" 2>&1
if %errorlevel%==0 (
    echo [OK] Creado exitosamente
    echo [OK] Shortcut 2 creado >> "%LOG_FILE%"
) else (
    echo [ERROR] Fallo al crear shortcut
    echo [ERROR] Fallo shortcut 2 >> "%LOG_FILE%"
)
del "%TEMP%\CreateShortcut2.vbs" 2>nul

:: Shortcut 3: Voz Claude Simple
echo.
echo Creando: Voz Claude (Simple)...
(
    echo Set oWS = WScript.CreateObject("WScript.Shell"^)
    echo sLinkFile = "%APPS_DIR%\Voz Claude Simple.lnk"
    echo Set oLink = oWS.CreateShortcut(sLinkFile^)
    echo oLink.TargetPath = "cmd.exe"
    echo oLink.Arguments = "/c ""%SCRIPT_PATH%\voz-claude-simple.bat"""
    echo oLink.Description = "Version minimalista y funcional"
    echo oLink.WorkingDirectory = "%SCRIPT_PATH%"
    echo oLink.Save
    echo WScript.Echo "[VBS] Shortcut creado: " ^& sLinkFile
) > "%TEMP%\CreateShortcut3.vbs"

cscript //nologo "%TEMP%\CreateShortcut3.vbs" 2>&1
if %errorlevel%==0 (
    echo [OK] Creado exitosamente
    echo [OK] Shortcut 3 creado >> "%LOG_FILE%"
) else (
    echo [ERROR] Fallo al crear shortcut
    echo [ERROR] Fallo shortcut 3 >> "%LOG_FILE%"
)
del "%TEMP%\CreateShortcut3.vbs" 2>nul

:: Shortcut 4: Configurar Voz Linux
echo.
echo Creando: Configurar Voz (Linux)...
(
    echo Set oWS = WScript.CreateObject("WScript.Shell"^)
    echo sLinkFile = "%APPS_DIR%\Configurar Voz Linux.lnk"
    echo Set oLink = oWS.CreateShortcut(sLinkFile^)
    echo oLink.TargetPath = "wsl.exe"
    echo oLink.Arguments = "-d Ubuntu-24.04 -- bash -c ""cd /home/lauta/glados/scripts/voz && ./configurar-voz.sh"""
    echo oLink.Description = "Configuracion completa desde terminal Linux"
    echo oLink.Save
    echo WScript.Echo "[VBS] Shortcut creado: " ^& sLinkFile
) > "%TEMP%\CreateShortcut4.vbs"

cscript //nologo "%TEMP%\CreateShortcut4.vbs" 2>&1
if %errorlevel%==0 (
    echo [OK] Creado exitosamente
    echo [OK] Shortcut 4 creado >> "%LOG_FILE%"
) else (
    echo [ERROR] Fallo al crear shortcut
    echo [ERROR] Fallo shortcut 4 >> "%LOG_FILE%"
)
del "%TEMP%\CreateShortcut4.vbs" 2>nul

:: Shortcut 5: Probar Voz
echo.
echo Creando: Probar Voz Actual...
(
    echo Set oWS = WScript.CreateObject("WScript.Shell"^)
    echo sLinkFile = "%APPS_DIR%\Probar Voz Actual.lnk"
    echo Set oLink = oWS.CreateShortcut(sLinkFile^)
    echo oLink.TargetPath = "wsl.exe"
    echo oLink.Arguments = "-d Ubuntu-24.04 -- bash -c ""cd /home/lauta/glados/scripts/voz && ./notificar-claude.sh 'Hola, soy tu asistente Claude'"""
    echo oLink.Description = "Prueba rapida de la voz configurada"
    echo oLink.Hotkey = "CTRL+SHIFT+T"
    echo oLink.Save
    echo WScript.Echo "[VBS] Shortcut creado: " ^& sLinkFile
) > "%TEMP%\CreateShortcut5.vbs"

cscript //nologo "%TEMP%\CreateShortcut5.vbs" 2>&1
if %errorlevel%==0 (
    echo [OK] Creado exitosamente
    echo [OK] Shortcut 5 creado >> "%LOG_FILE%"
) else (
    echo [ERROR] Fallo al crear shortcut
    echo [ERROR] Fallo shortcut 5 >> "%LOG_FILE%"
)
del "%TEMP%\CreateShortcut5.vbs" 2>nul

echo.
echo [5/7] Creando archivo README...
echo ----------------------------------------
(
    echo VOZ CLAUDE - ACCESOS DIRECTOS
    echo =============================
    echo.
    echo APLICACIONES DISPONIBLES:
    echo.
    echo 1. Voz Claude Moderno - Ctrl+Shift+V
    echo    Interfaz moderna con deteccion mejorada
    echo.
    echo 2. Voz Claude PowerShell - Ctrl+Shift+F  
    echo    PowerShell optimizado con navegacion fluida
    echo.
    echo 3. Voz Claude Simple
    echo    Version minimalista y funcional
    echo.
    echo 4. Configurar Voz Linux
    echo    Configuracion completa desde terminal
    echo.
    echo 5. Probar Voz Actual - Ctrl+Shift+T
    echo    Prueba rapida de la voz configurada
    echo.
    echo MOTORES DISPONIBLES:
    echo - gtts: Google Text-to-Speech
    echo - pico2wave: Voz femenina natural
    echo - festival: Voz masculina clara
    echo - espeak: Voz robotica
    echo - none: Modo silencioso
    echo.
    echo Configuracion: ~/.config/claude-voz/config
) > "%APPS_DIR%\VozClaude-README.txt" 2>&1

if exist "%APPS_DIR%\VozClaude-README.txt" (
    echo [OK] README creado exitosamente
    echo [OK] README creado >> "%LOG_FILE%"
) else (
    echo [ERROR] No se pudo crear README
    echo [ERROR] Fallo README >> "%LOG_FILE%"
)

echo.
echo [6/7] Verificando resultados...
echo ----------------------------------------
echo.
echo Contenido de la carpeta AppsWSL:
dir "%APPS_DIR%" /B 2>&1
echo.

:: Contar archivos creados
set /a count=0
for %%f in ("%APPS_DIR%\*.lnk") do set /a count+=1
echo Total de accesos directos creados: %count%
echo Total shortcuts: %count% >> "%LOG_FILE%"

echo.
echo [7/7] Finalizando...
echo ----------------------------------------
echo.
echo Log guardado en: %LOG_FILE%
echo.

if %count% GTR 0 (
    echo [EXITO] Se crearon %count% accesos directos!
    echo.
    echo Presiona cualquier tecla para abrir la carpeta AppsWSL...
    pause >nul
    start "" "%APPS_DIR%"
) else (
    echo [ERROR] No se crearon accesos directos!
    goto :error
)

echo.
echo ================================================================================
echo                              PROCESO COMPLETADO
echo ================================================================================
echo.
echo Atajos de teclado configurados:
echo   Ctrl+Shift+F - Voz Claude PowerShell
echo   Ctrl+Shift+T - Probar Voz
echo   (Ctrl+Shift+V removido para no interferir con pegado)
echo.
echo Presiona cualquier tecla para salir...
pause >nul
exit /b 0

:error
echo.
echo ================================================================================
echo                                  ERROR
echo ================================================================================
echo.
echo Ha ocurrido un error durante el proceso.
echo Por favor, revisa el archivo de log: %LOG_FILE%
echo.
echo Puedes copiar el contenido del log y compartirlo para obtener ayuda.
echo.
echo Presiona cualquier tecla para abrir el log...
pause >nul
notepad "%LOG_FILE%"
echo.
echo Presiona cualquier tecla para salir...
pause >nul
exit /b 1