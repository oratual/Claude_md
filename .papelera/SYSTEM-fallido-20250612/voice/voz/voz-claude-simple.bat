@echo off
:: Voz Claude - Version Simple y Funcional
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
mode con: cols=65 lines=30
color 5F
title Voz Claude

set "WSL=Ubuntu-24.04"
set "DIR=/home/lauta/glados/scripts/voz"

:menu
cls
echo.
echo     ================================================
echo                    VOZ CLAUDE
echo     ================================================
echo.

:: Estado
for /f "tokens=*" %%a in ('wsl -d %WSL% -- bash -c "source ~/.config/claude-voz/config 2>/dev/null && echo $CLAUDE_VOICE_ENGINE || echo gtts" 2^>nul') do set "engine=%%a"
for /f "tokens=*" %%a in ('wsl -d %WSL% -- bash -c "source ~/.config/claude-voz/config 2>/dev/null && [ \"$CLAUDE_VOICE_ENABLED\" = \"1\" ] && echo SI || echo NO" 2^>nul') do set "status=%%a"

echo     Motor actual: %engine%
echo     Estado: %status%
echo.
echo     ------------------------------------------------
echo.
echo     1. Cambiar voz
echo     2. Probar voz
echo     3. Personalizar nombre
echo     4. Activar/Desactivar
echo     5. Configuracion completa
echo     6. Salir
echo.
echo     ------------------------------------------------
echo.
set /p "op=    Selecciona (1-6): "

if "%op%"=="1" goto cambiar
if "%op%"=="2" goto probar
if "%op%"=="3" goto nombre
if "%op%"=="4" goto toggle
if "%op%"=="5" goto config
if "%op%"=="6" exit
goto menu

:cambiar
cls
echo.
echo     SELECCIONA TU VOZ
echo     ================================================
echo.
echo     1. gtts      - Google (voz femenina)
echo     2. pico2wave - Natural femenina
echo     3. festival  - Masculina clara
echo     4. espeak    - Robotica
echo     5. none      - Silencioso
echo     6. Volver
echo.
set /p "voz=    Elige (1-6): "

if "%voz%"=="1" set "nuevo=gtts"
if "%voz%"=="2" set "nuevo=pico2wave"
if "%voz%"=="3" set "nuevo=festival"
if "%voz%"=="4" set "nuevo=espeak"
if "%voz%"=="5" set "nuevo=none"
if "%voz%"=="6" goto menu

if defined nuevo (
    wsl -d %WSL% -- bash -c "mkdir -p ~/.config/claude-voz && echo 'CLAUDE_VOICE_ENGINE=\"%nuevo%\"' > ~/.config/claude-voz/config && echo 'CLAUDE_VOICE_ENABLED=1' >> ~/.config/claude-voz/config" 2>nul
    echo.
    echo     Voz cambiada a: %nuevo%
    timeout /t 2 >nul
)
goto menu

:probar
cls
echo.
echo     PRUEBA DE VOZ
echo     ================================================
echo.
echo     1. Hola, soy Claude
echo     2. Ultra think terminado
echo     3. Tu asistente lista
echo     4. Mensaje personalizado
echo     5. Volver
echo.
set /p "test=    Elige (1-5): "

if "%test%"=="1" set "msg=Hola, soy Claude"
if "%test%"=="2" set "msg=Ultra think ha terminado"
if "%test%"=="3" set "msg=Tu asistente esta lista"
if "%test%"=="4" (
    echo.
    set /p "msg=    Escribe tu mensaje: "
)
if "%test%"=="5" goto menu

if defined msg (
    echo.
    echo     Reproduciendo...
    wsl -d %WSL% -- bash -c "cd %DIR% && ./notificar-claude.sh '%msg%'" 2>nul
    echo.
    pause
)
goto menu

:nombre
cls
echo.
echo     PERSONALIZA TU TERMINAL
echo     ================================================
echo.
echo     Sugerencias:
echo     - ultrathink
echo     - dreamweaver
echo     - speedster
echo     - nightowl
echo.
set /p "nombre=    Tu nombre: "

if defined nombre (
    wsl -d %WSL% -- bash -c "sed -i '/CLAUDE_INSTANCE_NAME/d' ~/.config/claude-voz/config 2>/dev/null && echo 'CLAUDE_INSTANCE_NAME=\"%nombre%\"' >> ~/.config/claude-voz/config" 2>nul
    echo.
    echo     Nombre configurado: %nombre%
    timeout /t 2 >nul
)
goto menu

:toggle
for /f "tokens=*" %%a in ('wsl -d %WSL% -- bash -c "source ~/.config/claude-voz/config 2>/dev/null && [ \"$CLAUDE_VOICE_ENABLED\" = \"1\" ] && echo 0 || echo 1" 2^>nul') do set "new=%%a"
wsl -d %WSL% -- bash -c "sed -i 's/CLAUDE_VOICE_ENABLED=.*/CLAUDE_VOICE_ENABLED=%new%/' ~/.config/claude-voz/config" 2>nul

if "%new%"=="1" (
    echo.
    echo     Voz ACTIVADA
) else (
    echo.
    echo     Voz DESACTIVADA
)
timeout /t 2 >nul
goto menu

:config
echo.
echo     Abriendo configuracion completa...
wsl -d %WSL% -- bash -c "cd %DIR% && ./configurar-voz.sh"
goto menu