@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
title Configuracion de Voz para Claude

:: Detectar distribucion WSL - Ubuntu-24.04 es la tuya
set "WSL_DISTRO=Ubuntu-24.04"

:: Alternativa: detectar automaticamente (mas complejo por encoding UTF-16)
:: for /f "tokens=*" %%i in ('wsl -l -q 2^>nul ^| findstr /v "^$" ^| findstr /v "docker"') do (
::     set "WSL_DISTRO=%%i"
::     goto :found_distro
:: )
:: :found_distro

:: Directorio de scripts en WSL
set "SCRIPT_DIR=/home/lauta/glados/scripts/voz"

:menu
cls
echo ============================================================
echo          CONFIGURACION DE VOZ PARA CLAUDE
echo                  (Windows Edition)
echo ============================================================
echo.

:: Mostrar estado actual
echo Estado actual:
for /f "tokens=*" %%a in ('wsl -d %WSL_DISTRO% -- bash -c "source ~/.config/claude-voz/config 2>/dev/null && echo $CLAUDE_VOICE_ENGINE || echo pico2wave"') do set "current_engine=%%a"
echo   Motor: %current_engine%

for /f "tokens=*" %%a in ('wsl -d %WSL_DISTRO% -- bash -c "source ~/.config/claude-voz/config 2>/dev/null && [ \"$CLAUDE_VOICE_ENABLED\" = \"1\" ] && echo Si || echo No"') do set "voice_enabled=%%a"
echo   Habilitado: %voice_enabled%
echo.

echo Motores disponibles:
echo   [OK] pico2wave - Voz femenina, ligera (con algo de estatica)
wsl -d %WSL_DISTRO% -- command -v espeak >nul 2>&1 && (echo   [OK] espeak - Ultra ligero, robotico) || (echo   [--] espeak - No instalado)
wsl -d %WSL_DISTRO% -- command -v festival >nul 2>&1 && (echo   [OK] festival - Voz masculina, buena calidad) || (echo   [--] festival - No instalado)
wsl -d %WSL_DISTRO% -- python3 -c "import gtts" 2>nul && (echo   [OK] gtts - Google TTS, voz femenina excelente) || (echo   [--] gtts - No instalado)
echo   [OK] none - Modo silencioso
echo.

echo Opciones:
echo   1. Cambiar motor de voz
echo   2. Probar voz actual
echo   3. Configurar nombre de instancia
echo   4. Activar/Desactivar notificaciones
echo   5. Instalar motor faltante
echo   6. Abrir configurador Linux completo
echo   7. Salir
echo.

set /p option=Seleccione una opcion (1-7): 

if "%option%"=="1" goto change_engine
if "%option%"=="2" goto test_voice
if "%option%"=="3" goto set_instance
if "%option%"=="4" goto toggle_voice
if "%option%"=="5" goto install_engine
if "%option%"=="6" goto linux_config
if "%option%"=="7" exit /b

echo Opcion invalida
timeout /t 2 >nul
goto menu

:change_engine
cls
echo SELECCIONE EL MOTOR DE VOZ:
echo.
echo   1. pico2wave - Voz femenina, ligera
echo   2. espeak - Ultra ligero, robotico
echo   3. festival - Voz masculina, mejor calidad
echo   4. gtts - Voz femenina Google (requiere internet)
echo   5. none - Modo silencioso
echo   6. Volver
echo.

set /p engine_choice=Seleccione motor (1-6): 

set "new_engine="
if "%engine_choice%"=="1" set "new_engine=pico2wave"
if "%engine_choice%"=="2" set "new_engine=espeak"
if "%engine_choice%"=="3" set "new_engine=festival"
if "%engine_choice%"=="4" set "new_engine=gtts"
if "%engine_choice%"=="5" set "new_engine=none"
if "%engine_choice%"=="6" goto menu

if not "%new_engine%"=="" (
    wsl -d %WSL_DISTRO% -- bash -c "mkdir -p ~/.config/claude-voz && echo 'CLAUDE_VOICE_ENGINE=\"%new_engine%\"' > ~/.config/claude-voz/config && echo 'CLAUDE_VOICE_ENABLED=1' >> ~/.config/claude-voz/config"
    echo.
    echo Motor cambiado a: %new_engine%
    timeout /t 2 >nul
)
goto menu

:test_voice
cls
echo PROBANDO VOZ...
echo.
echo Seleccione mensaje de prueba:
echo   1. "Hola, soy Claude"
echo   2. "Ultra think ha terminado"
echo   3. "Notificacion de Windows"
echo   4. Mensaje personalizado
echo.

set /p test_choice=Seleccione (1-4): 

set "test_msg="
if "%test_choice%"=="1" set "test_msg=Hola, soy Claude"
if "%test_choice%"=="2" set "test_msg=Ultra think ha terminado"
if "%test_choice%"=="3" set "test_msg=Notificacion de Windows"
if "%test_choice%"=="4" (
    set /p test_msg=Escriba el mensaje: 
)

if not "%test_msg%"=="" (
    echo.
    echo Reproduciendo: "%test_msg%"
    wsl -d %WSL_DISTRO% -- bash -c "cd %SCRIPT_DIR% && ./notificar-claude.sh '%test_msg%'"
)

echo.
pause
goto menu

:set_instance
cls
echo CONFIGURAR NOMBRE DE INSTANCIA
echo.
echo Sugerencias: ultrathink, deepanalysis, quicktask, research
echo.
set /p instance_name=Nombre de instancia (vacio para quitar): 

wsl -d %WSL_DISTRO% -- bash -c "sed -i '/CLAUDE_INSTANCE_NAME/d' ~/.config/claude-voz/config 2>/dev/null; echo 'CLAUDE_INSTANCE_NAME=\"%instance_name%\"' >> ~/.config/claude-voz/config"

if "%instance_name%"=="" (
    echo Nombre de instancia eliminado
) else (
    echo Nombre configurado: %instance_name%
)
timeout /t 2 >nul
goto menu

:toggle_voice
for /f "tokens=*" %%a in ('wsl -d %WSL_DISTRO% -- bash -c "source ~/.config/claude-voz/config 2>/dev/null && [ \"$CLAUDE_VOICE_ENABLED\" = \"1\" ] && echo 0 || echo 1"') do set "new_state=%%a"

wsl -d %WSL_DISTRO% -- bash -c "sed -i 's/CLAUDE_VOICE_ENABLED=.*/CLAUDE_VOICE_ENABLED=%new_state%/' ~/.config/claude-voz/config"

if "%new_state%"=="1" (
    echo Notificaciones activadas
) else (
    echo Notificaciones desactivadas
)
timeout /t 2 >nul
goto menu

:install_engine
cls
echo INSTALAR MOTOR DE VOZ
echo.
echo   1. espeak - Ultra ligero
echo   2. festival - Mejor calidad
echo   3. gtts - Google TTS (voz femenina)
echo   4. Volver
echo.

set /p install_choice=Seleccione motor a instalar (1-4): 

if "%install_choice%"=="1" (
    echo Instalando espeak...
    wsl -d %WSL_DISTRO% -- bash -c "echo '1pirao' ^| sudo -S apt-get update && echo '1pirao' ^| sudo -S apt-get install -y espeak"
)
if "%install_choice%"=="2" (
    echo Instalando festival...
    wsl -d %WSL_DISTRO% -- bash -c "echo '1pirao' ^| sudo -S apt-get update && echo '1pirao' ^| sudo -S apt-get install -y festival festvox-ellpc11k festival-freebsoft-utils"
)
if "%install_choice%"=="3" (
    echo Instalando Google TTS...
    wsl -d %WSL_DISTRO% -- bash -c "pip3 install --user --break-system-packages gtts && echo '1pirao' ^| sudo -S apt-get install -y mpg123"
)

if "%install_choice%" geq "1" if "%install_choice%" leq "3" (
    echo.
    echo Instalacion completada
    pause
)
goto menu

:linux_config
echo.
echo Abriendo configurador completo de Linux...
wsl -d %WSL_DISTRO% -- bash -c "cd %SCRIPT_DIR% && ./configurar-voz.sh"
goto menu