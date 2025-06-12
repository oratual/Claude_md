@echo off
:: LANZAR-MENU-DETACHED.bat - Menú GLADOS con ventanas independientes
:: Fecha: 2025-01-10
:: Descripción: Lanza Claude en ventanas completamente independientes
:: Versión: Sin ventanas residuales

setlocal enabledelayedexpansion

:: Crear archivo temporal para comunicación entre procesos
set TEMP_FILE=%TEMP%\glados_menu_choice.tmp
set TEMP_SCRIPT=%TEMP%\glados_launch.bat

:: Limpiar archivos temporales previos
if exist "%TEMP_FILE%" del "%TEMP_FILE%" 2>nul
if exist "%TEMP_SCRIPT%" del "%TEMP_SCRIPT%" 2>nul

:: Cambiar al directorio del usuario
cd /d "%USERPROFILE%" 2>nul

:: Ejecutar el menú y capturar la selección
echo Iniciando menu GLADOS...
wsl bash -c "cd ~/glados && ~/glados/scripts/launchers/proyecto-menu-v2.sh; echo $? > /tmp/menu_exit_code.tmp" 2>nul

:: Leer el código de salida del menú
for /f %%i in ('wsl cat /tmp/menu_exit_code.tmp 2^>nul') do set MENU_EXIT=%%i

:: Si el menú devolvió un código especial, procesar la acción
if "%MENU_EXIT%"=="100" (
    :: Claude sin proyecto
    echo Lanzando Claude Code...
    start "" wezterm start -- wsl bash -lc "~/glados/scripts/launchers/launch-claude-detached.sh ~/glados --dangerously-skip-permissions"
    exit
) else if "%MENU_EXIT%"=="101" (
    :: Claude con selección de conversación
    echo Lanzando Claude Code con seleccion de conversacion...
    start "" wezterm start -- wsl bash -lc "~/glados/scripts/launchers/launch-claude-detached.sh ~/glados --dangerously-skip-permissions --resume"
    exit
) else if "%MENU_EXIT%"=="102" (
    :: Terminal en glados
    echo Abriendo terminal en glados...
    start "" wezterm start -- wsl bash -lc "cd ~/glados && exec bash -l"
    exit
) else if "%MENU_EXIT%"=="200" (
    :: Proyecto con git (Claude Squad)
    for /f "delims=" %%p in ('wsl cat /tmp/glados_project.tmp 2^>nul') do set PROJECT=%%p
    echo Lanzando Claude Squad en !PROJECT!...
    start "" wezterm start -- wsl bash -lc "cd ~/glados/!PROJECT! && source ~/.nvm/nvm.sh && cs -y"
    exit
) else if "%MENU_EXIT%"=="201" (
    :: Proyecto sin git (terminal)
    for /f "delims=" %%p in ('wsl cat /tmp/glados_project.tmp 2^>nul') do set PROJECT=%%p
    echo Abriendo terminal en !PROJECT!...
    start "" wezterm start -- wsl bash -lc "cd ~/glados/!PROJECT! && exec bash -l"
    exit
)

:: Limpiar archivos temporales
wsl rm -f /tmp/menu_exit_code.tmp /tmp/glados_project.tmp 2>nul

endlocal