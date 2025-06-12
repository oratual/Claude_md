@echo off
:: Voz Claude - Version Corregida con Detección Mejorada
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
mode con: cols=70 lines=35
color 0D
title 💋 Voz Claude

set "WSL=Ubuntu-24.04"
set "DIR=/home/lauta/glados/scripts/voz"
set "CONFIG_FILE=~/.config/claude-voz/config"

:menu
cls
echo.
echo    ╔═══════════════════════════════════════════════════════╗
echo    ║       💋  VOZ CLAUDE - Tu asistente personal          ║
echo    ╚═══════════════════════════════════════════════════════╝
echo.

:: Obtener estado actual con mejor escape
for /f "usebackq tokens=*" %%a in (`wsl -d %WSL% -- bash -c "if [ -f %CONFIG_FILE% ]; then grep '^CLAUDE_VOICE_ENGINE=' %CONFIG_FILE% 2^>/dev/null ^| cut -d'=' -f2 ^| tr -d '\"' ^| tr -d \"'\" ; else echo gtts; fi"`) do set "engine=%%a"
for /f "usebackq tokens=*" %%a in (`wsl -d %WSL% -- bash -c "if [ -f %CONFIG_FILE% ]; then grep '^CLAUDE_VOICE_ENABLED=' %CONFIG_FILE% 2^>/dev/null ^| cut -d'=' -f2; else echo 1; fi"`) do set "enabled=%%a"
for /f "usebackq tokens=*" %%a in (`wsl -d %WSL% -- bash -c "if [ -f %CONFIG_FILE% ]; then grep '^CLAUDE_INSTANCE_NAME=' %CONFIG_FILE% 2^>/dev/null ^| cut -d'=' -f2 ^| tr -d '\"' ^| tr -d \"'\" ; else echo Terminal; fi"`) do set "instance=%%a"

:: Limpiar valores
set "engine=%engine: =%"
set "enabled=%enabled: =%"
set "instance=%instance: =%"

:: Verificar valores por defecto
if "%engine%"=="" set "engine=gtts"
if "%enabled%"=="" set "enabled=1"
if "%instance%"=="" set "instance=Terminal"

:: Convertir estado a texto
if "%enabled%"=="1" (set "status=ACTIVADA") else (set "status=DESACTIVADA")

echo    ┌─── Estado Actual ─────────────────────────────────────┐
echo    │                                                       │

:: Mostrar motor con icono
if "%engine%"=="gtts" (
    echo    │  🌟 Motor: Google TTS (Voz femenina perfecta^)        │
) else if "%engine%"=="pico2wave" (
    echo    │  💃 Motor: Pico2wave (Voz femenina natural^)          │
) else if "%engine%"=="festival" (
    echo    │  🎭 Motor: Festival (Voz masculina clara^)            │
) else if "%engine%"=="espeak" (
    echo    │  🤖 Motor: Espeak (Voz robótica^)                     │
) else if "%engine%"=="none" (
    echo    │  🔇 Motor: Silencioso                                 │
) else (
    echo    │  ❓ Motor: %engine%                                      │
)

echo    │  🔊 Estado: %status%                                  │
echo    │  🏷️  Instancia: %instance%                             │
echo    │                                                       │
echo    └───────────────────────────────────────────────────────┘
echo.
echo    ┌─── Acciones Rápidas ──────────────────────────────────┐
echo    │                                                       │
echo    │  [1] 🎤 Cambiar voz        [4] 💡 ON/OFF              │
echo    │  [2] 🔊 Probar voz         [5] 📥 Instalar voces      │
echo    │  [3] 🏷️  Personalizar      [6] 👋 Salir               │
echo    │                                                       │
echo    └───────────────────────────────────────────────────────┘
echo.
choice /c 123456 /n /m "    Elige una opción (1-6): "

if %errorlevel%==1 goto voice
if %errorlevel%==2 goto test
if %errorlevel%==3 goto name
if %errorlevel%==4 goto toggle
if %errorlevel%==5 goto install
if %errorlevel%==6 exit

:voice
cls
echo.
echo    ╔═══════════════════════════════════════════════════════╗
echo    ║              🎤 ELIGE TU VOZ FAVORITA                 ║
echo    ╚═══════════════════════════════════════════════════════╝
echo.
echo    [1] 🌟 Google TTS      - La reina de las voces
echo    [2] 💃 Pico2wave       - Natural y coqueta
echo    [3] 🎭 Festival        - El caballero español
echo    [4] 🤖 Espeak          - Minimalista futurista
echo    [5] 🔇 Silencioso      - Para concentrarte
echo    [6] 🔙 Volver
echo.
choice /c 123456 /n /m "    Tu elección: "

set "new_engine="
if %errorlevel%==1 set "new_engine=gtts"
if %errorlevel%==2 set "new_engine=pico2wave"
if %errorlevel%==3 set "new_engine=festival"
if %errorlevel%==4 set "new_engine=espeak"
if %errorlevel%==5 set "new_engine=none"
if %errorlevel%==6 goto menu

if defined new_engine (
    :: Crear archivo de configuración con el nuevo motor
    wsl -d %WSL% -- bash -c "mkdir -p ~/.config/claude-voz && { echo 'CLAUDE_VOICE_ENGINE=%new_engine%'; echo 'CLAUDE_VOICE_ENABLED=1'; if [ -f %CONFIG_FILE% ]; then grep '^CLAUDE_INSTANCE_NAME=' %CONFIG_FILE% 2^>/dev/null ^|^| echo 'CLAUDE_INSTANCE_NAME=Terminal'; else echo 'CLAUDE_INSTANCE_NAME=Terminal'; fi; } > %CONFIG_FILE%"
    echo.
    echo    ✨ ¡Perfecto! Ahora hablo con voz %new_engine%
    timeout /t 2 >nul
)
goto menu

:test
cls
echo.
echo    ╔═══════════════════════════════════════════════════════╗
echo    ║              🔊 PRUEBA DE VOZ                         ║
echo    ╚═══════════════════════════════════════════════════════╝
echo.
echo    [1] 💬 "Hola cariño, soy Claude"
echo    [2] 🚀 "Ultra think ha completado su magia"
echo    [3] 💋 "Tu asistente favorita está lista"
echo    [4] ✏️  Mensaje personalizado
echo    [5] 🔙 Volver
echo.
choice /c 12345 /n /m "    ¿Qué quieres escuchar? "

set "msg="
if %errorlevel%==1 set "msg=Hola cariño, soy Claude"
if %errorlevel%==2 set "msg=Ultra think ha completado su magia"
if %errorlevel%==3 set "msg=Tu asistente favorita está lista"
if %errorlevel%==4 (
    echo.
    set /p "msg=    Escribe tu mensaje: "
)
if %errorlevel%==5 goto menu

if defined msg (
    echo.
    echo    🔊 Reproduciendo...
    wsl -d %WSL% -- bash -c "cd %DIR% && ./notificar-claude.sh '%msg%'"
    echo    ✨ ¡Qué tal suena?
    pause >nul
)
goto menu

:name
cls
echo.
echo    ╔═══════════════════════════════════════════════════════╗
echo    ║           🏷️  PERSONALIZA TU TERMINAL                 ║
echo    ╚═══════════════════════════════════════════════════════╝
echo.
echo    Dale un nombre único a tu espacio de trabajo:
echo.
echo    💡 Sugerencias creativas:
echo       • ultrathink     - Para análisis profundos
echo       • dreamweaver    - Para proyectos creativos
echo       • speedster      - Para tareas rápidas
echo       • nightowl       - Para sesiones nocturnas
echo.
echo    Actual: %instance%
echo.
set /p "nombre=    Tu nombre elegido: "

if defined nombre (
    :: Actualizar solo el nombre de instancia
    wsl -d %WSL% -- bash -c "if [ -f %CONFIG_FILE% ]; then sed -i '/^CLAUDE_INSTANCE_NAME=/d' %CONFIG_FILE%; fi; echo 'CLAUDE_INSTANCE_NAME=%nombre%' >> %CONFIG_FILE%"
    echo.
    echo    ✨ ¡Genial! Ahora eres "%nombre%"
    timeout /t 2 >nul
)
goto menu

:toggle
:: Leer estado actual y cambiarlo
for /f "usebackq tokens=*" %%a in (`wsl -d %WSL% -- bash -c "if [ -f %CONFIG_FILE% ]; then grep '^CLAUDE_VOICE_ENABLED=' %CONFIG_FILE% 2^>/dev/null ^| cut -d'=' -f2; else echo 1; fi"`) do set "current_state=%%a"
set "current_state=%current_state: =%"

if "%current_state%"=="1" (set "new_state=0") else (set "new_state=1")

:: Actualizar configuración
wsl -d %WSL% -- bash -c "if [ -f %CONFIG_FILE% ]; then sed -i 's/^CLAUDE_VOICE_ENABLED=.*/CLAUDE_VOICE_ENABLED=%new_state%/' %CONFIG_FILE%; else echo 'CLAUDE_VOICE_ENABLED=%new_state%' > %CONFIG_FILE%; fi"

if "%new_state%"=="1" (
    echo.
    echo    🔊 ¡Voz activada! Escucharás mi dulce voz
) else (
    echo.
    echo    🔇 Modo ninja activado - Sin sonidos
)
timeout /t 2 >nul
goto menu

:install
cls
echo.
echo    ╔═══════════════════════════════════════════════════════╗
echo    ║              📥 INSTALAR NUEVAS VOCES                 ║
echo    ╚═══════════════════════════════════════════════════════╝
echo.
echo    Abriendo el instalador completo...
echo.
wsl -d %WSL% -- bash -c "cd %DIR% && ./configurar-voz.sh"
goto menu