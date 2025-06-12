@echo off
setlocal EnableDelayedExpansion
title WSL Restore Tools - Menu Principal
color 0A

:MENU_PRINCIPAL
cls
echo ╔══════════════════════════════════════════════════╗
echo ║         WSL Restore Tools - Windows              ║
echo ║            Sistema de Recuperacion               ║
echo ╚══════════════════════════════════════════════════╝
echo.
echo   1. 📦 Hacer Backup Modular
echo   2. 🔄 Restaurar desde Backup
echo   3. 🏥 Verificar Salud de WSL
echo   4. 📊 Ver Backups Disponibles
echo   5. 🚨 Restauracion de Emergencia
echo   6. 📋 Ver Logs
echo   7. ❓ Ayuda
echo   0. ❌ Salir
echo.
set /p opcion="Selecciona una opcion: "

if "%opcion%"=="1" goto BACKUP_MODULAR
if "%opcion%"=="2" goto RESTAURAR
if "%opcion%"=="3" goto VERIFICAR_SALUD
if "%opcion%"=="4" goto VER_BACKUPS
if "%opcion%"=="5" goto EMERGENCIA
if "%opcion%"=="6" goto VER_LOGS
if "%opcion%"=="7" goto AYUDA
if "%opcion%"=="0" exit
goto MENU_PRINCIPAL

:BACKUP_MODULAR
cls
echo ╔══════════════════════════════════════════════════╗
echo ║              Backup Modular WSL                  ║
echo ╚══════════════════════════════════════════════════╝
echo.
echo Ejecutando script de backup modular...
echo.
wsl.exe bash -c "~/glados/wsl-repairing/restauracion-modular/backup-modular.sh"
pause
goto MENU_PRINCIPAL

:RESTAURAR
cls
echo ╔══════════════════════════════════════════════════╗
echo ║           Restaurar desde Backup                 ║
echo ╚══════════════════════════════════════════════════╝
echo.
echo Ejecutando script de restauracion...
echo.
wsl.exe bash -c "~/glados/wsl-repairing/restauracion-modular/restore-modular.sh"
pause
goto MENU_PRINCIPAL

:VERIFICAR_SALUD
cls
echo ╔══════════════════════════════════════════════════╗
echo ║            Verificar Salud de WSL                ║
echo ╚══════════════════════════════════════════════════╝
echo.
wsl.exe bash -c "~/glados/wsl-repairing/wsl-health-monitor.sh"
echo.
pause
goto MENU_PRINCIPAL

:VER_BACKUPS
cls
echo ╔══════════════════════════════════════════════════╗
echo ║           Backups Disponibles                    ║
echo ╚══════════════════════════════════════════════════╝
echo.
echo === SISTEMA ===
dir /b /ad "H:\Backup\WSL\system\" 2>nul || echo No hay backups del sistema
echo.
echo === PROYECTOS ===
dir /b /ad "H:\Backup\WSL\projects\" 2>nul || echo No hay backups de proyectos
echo.
pause
goto MENU_PRINCIPAL

:EMERGENCIA
cls
echo ╔══════════════════════════════════════════════════╗
echo ║         RESTAURACION DE EMERGENCIA               ║
echo ╚══════════════════════════════════════════════════╝
echo.
echo   1. Exportar distro completa (backup total)
echo   2. Reimportar distro desde backup
echo   3. Reinstalar WSL desde cero
echo   4. Restaurar solo archivos criticos
echo   0. Volver
echo.
set /p emergency="Opcion: "

if "%emergency%"=="1" goto EXPORT_DISTRO
if "%emergency%"=="2" goto IMPORT_DISTRO
if "%emergency%"=="3" goto REINSTALL_WSL
if "%emergency%"=="4" goto CRITICAL_FILES
goto MENU_PRINCIPAL

:EXPORT_DISTRO
cls
echo Exportando distro completa...
echo Esto puede tardar varios minutos...
set export_file=H:\Backup\WSL\full\Ubuntu-24.04-%date:~-4,4%%date:~-7,2%%date:~-10,2%.tar
wsl.exe --export Ubuntu-24.04 "%export_file%"
echo.
echo Distro exportada a: %export_file%
pause
goto EMERGENCIA

:IMPORT_DISTRO
cls
echo Archivos de backup disponibles:
dir /b "H:\Backup\WSL\full\*.tar" 2>nul || echo No hay backups completos
echo.
set /p backup_file="Nombre del archivo .tar a importar: "
set /p install_path="Ruta de instalacion (ej: C:\WSL\Ubuntu-Restored): "
echo.
echo Importando...
wsl.exe --import Ubuntu-Restored "%install_path%" "H:\Backup\WSL\full\%backup_file%"
echo.
echo Para establecer como default: wsl --set-default Ubuntu-Restored
pause
goto EMERGENCIA

:CRITICAL_FILES
cls
echo Copiando archivos criticos desde backup...
echo.
copy "H:\Backup\WSL\2025-06-12\bashrc.backup" "%USERPROFILE%\wsl-restore-bashrc.txt"
copy "H:\Backup\WSL\2025-06-12\gitconfig.backup" "%USERPROFILE%\wsl-restore-gitconfig.txt"
copy "H:\Backup\WSL\2025-06-12\ssh-config.backup" "%USERPROFILE%\wsl-restore-ssh-config.txt"
echo.
echo Archivos copiados a tu carpeta de usuario de Windows
pause
goto EMERGENCIA

:VER_LOGS
cls
echo ╔══════════════════════════════════════════════════╗
echo ║                    Logs                          ║
echo ╚══════════════════════════════════════════════════╝
echo.
echo Ultimos logs de restauracion:
echo.
wsl.exe bash -c "ls -la ~/glados/wsl-repairing/restore-*.log 2>/dev/null | tail -5"
echo.
set /p ver_log="Ver algun log? (nombre del archivo o n): "
if not "%ver_log%"=="n" (
    wsl.exe bash -c "cat ~/glados/wsl-repairing/%ver_log%"
)
pause
goto MENU_PRINCIPAL

:REINSTALL_WSL
cls
echo ╔══════════════════════════════════════════════════╗
echo ║          REINSTALACION COMPLETA WSL              ║
echo ╚══════════════════════════════════════════════════╝
echo.
echo ADVERTENCIA: Esto borrara WSL completamente
echo.
echo Pasos a seguir:
echo 1. wsl --shutdown
echo 2. wsl --unregister Ubuntu-24.04
echo 3. wsl --install -d Ubuntu-24.04
echo 4. Ejecutar script de post-instalacion
echo.
echo ¿Continuar? (S/N)
set /p confirm="Respuesta: "
if /i "%confirm%"=="S" (
    echo.
    echo Ejecutando shutdown...
    wsl.exe --shutdown
    echo.
    echo Para continuar, ejecuta manualmente:
    echo   wsl --unregister Ubuntu-24.04
    echo   wsl --install -d Ubuntu-24.04
)
pause
goto EMERGENCIA

:AYUDA
cls
echo ╔══════════════════════════════════════════════════╗
echo ║                    AYUDA                         ║
echo ╚══════════════════════════════════════════════════╝
echo.
echo ESTRUCTURA DE BACKUPS:
echo   H:\Backup\WSL\
echo   ├── system\         (configuraciones y dotfiles)
echo   ├── projects\       (proyectos individuales)
echo   └── full\          (distros completas)
echo.
echo PROCESO RECOMENDADO:
echo   1. Hacer backups regulares (opcion 1)
echo   2. Si WSL falla, intentar restaurar (opcion 2)
echo   3. Si no funciona, usar emergencia (opcion 5)
echo.
echo ARCHIVOS IMPORTANTES:
echo   - wsl-plan-emergencia.md (en el escritorio)
echo   - IMPORTANTE-DiskDominator.md (en K:\_Glados)
echo.
pause
goto MENU_PRINCIPAL