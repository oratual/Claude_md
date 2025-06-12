@echo off
:: launch-detached.bat - Script auxiliar para lanzar comandos en ventana independiente
:: Usado por el menú para abrir Claude/CS en nuevas ventanas sin mantener la ventana padre

set CMD_TO_RUN=%*

:: Lanzar en nueva ventana independiente y cerrar inmediatamente esta
start "" wezterm start -- wsl bash -lc "%CMD_TO_RUN%"
exit