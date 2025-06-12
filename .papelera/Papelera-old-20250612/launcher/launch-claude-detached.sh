#!/bin/bash
# launch-claude-detached.sh - Lanza Claude en ventana independiente
# Descripción: Script auxiliar para lanzar Claude sin mantener ventana padre
# Autor: Claude Code
# Fecha: 2025-01-10

# Cargar NVM
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Cambiar al directorio apropiado
if [ -n "$1" ]; then
    cd "$1" || exit 1
else
    cd ~/glados || exit 1
fi

# Ejecutar Claude con los parámetros recibidos
shift  # Remover el primer parámetro (directorio)
exec claude "$@"