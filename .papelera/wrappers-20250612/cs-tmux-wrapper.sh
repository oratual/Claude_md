#!/bin/bash

# Wrapper para ejecutar Claude Squad dentro de tmux para evitar errores de captura

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Verificar si tmux está instalado
if ! command -v tmux &> /dev/null; then
    echo -e "${YELLOW}tmux no está instalado. Instalando...${NC}"
    sudo apt-get update && sudo apt-get install -y tmux
fi

# Cargar NVM
source ~/.nvm/nvm.sh

# Verificar si ya estamos en tmux
if [ -n "$TMUX" ]; then
    echo -e "${CYAN}Ya estás en tmux. Ejecutando Claude Squad directamente...${NC}"
    cs -y
else
    echo -e "${GREEN}Iniciando Claude Squad en tmux para evitar errores de captura...${NC}"
    echo -e "${CYAN}Nota: Usa 'Ctrl+B' seguido de 'D' para salir de tmux${NC}"
    sleep 2
    
    # Crear o adjuntar a sesión tmux
    tmux new-session -s claudesquad -d "cs -y" 2>/dev/null || \
    tmux attach-session -t claudesquad 2>/dev/null || \
    tmux new-session -s claudesquad "cs -y"
fi