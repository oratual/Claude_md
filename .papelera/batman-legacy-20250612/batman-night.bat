@echo off
echo.
echo  ==================================================
echo  ^|              BATMAN NIGHT MODE                ^|
echo  ==================================================
echo.
echo  [!] ADVERTENCIA: El PC se apagara al terminar
echo      todas las tareas nocturnas.
echo.
echo  Tareas a ejecutar:
echo  - Backups automaticos
echo  - Limpieza de logs
echo  - Analisis de sistema
echo  - Generacion de informe matutino
echo.
echo  Presiona Ctrl+C para cancelar
echo  o cualquier tecla para continuar...
echo.
pause > nul

:: Limpiar pantalla
cls

echo.
echo  [*] Iniciando Batman en modo nocturno...
echo.

:: Ejecutar Batman en WSL2
wsl -e /home/lauta/glados/batman/batman.py night-shift

:: Si llegamos aqui, algo fallo
echo.
echo  [X] Error: Batman no pudo completar las tareas
echo      Revisa los logs en: logs/batman.log
echo.
echo  Presiona cualquier tecla para cerrar...
pause > nul