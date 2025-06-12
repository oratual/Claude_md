#!/bin/bash
# ========================================
# GLADOS UNIFIED LAUNCHER v2.0
# ========================================
# Reemplaza todos los launchers anteriores
# Ejecutable desde cualquier lugar
# ========================================

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Base directory
GLADOS_HOME="${HOME}/glados"
cd "$GLADOS_HOME"

# Banner
clear
echo -e "${CYAN}${BOLD}"
cat << 'EOF'
   _____ _               _  ____   _____ 
  / ____| |        /\   | |/ __ \ / ____|
 | |  __| |       /  \  | | |  | | (___  
 | | |_ | |      / /\ \ | | |  | |\___ \ 
 | |__| | |____ / ____ \| | |__| |____) |
  \_____|______/_/    \_\_|\____/|_____/ 
                                         
EOF
echo -e "${NC}"
echo -e "${YELLOW}Sistema Unificado de Lanzamiento v2.0${NC}"
echo -e "${CYAN}═══════════════════════════════════════${NC}"
echo

# Función para ejecutar comandos
run_command() {
    local cmd=$1
    local desc=$2
    echo -e "${BLUE}→ ${desc}${NC}"
    eval "$cmd"
}

# Menú principal
show_menu() {
    echo -e "${GREEN}${BOLD}PROYECTOS PRINCIPALES:${NC}"
    echo -e "  ${BOLD}1)${NC} 🦇 Batman Incorporated"
    echo -e "  ${BOLD}2)${NC} 💾 DiskDominator"
    echo -e "  ${BOLD}3)${NC} 🤖 MCP Servers"
    echo -e "  ${BOLD}4)${NC} ♾️  InfiniteAgent"
    echo
    echo -e "${MAGENTA}${BOLD}UTILIDADES:${NC}"
    echo -e "  ${BOLD}5)${NC} 📊 Monitor Sistema"
    echo -e "  ${BOLD}6)${NC} 🔧 Herramientas"
    echo -e "  ${BOLD}7)${NC} 🔗 Copy2Windows (c2w)"
    echo -e "  ${BOLD}8)${NC} 📝 Ver TODO actual"
    echo
    echo -e "${YELLOW}${BOLD}CLAUDE:${NC}"
    echo -e "  ${BOLD}9)${NC} 🧠 Claude con contexto"
    echo -e "  ${BOLD}10)${NC} 📢 Sistema de voz"
    echo -e "  ${BOLD}11)${NC} 📊 Ver quota Claude"
    echo
    echo -e "${RED}${BOLD}SISTEMA:${NC}"
    echo -e "  ${BOLD}12)${NC} 🌐 Check conectividad"
    echo -e "  ${BOLD}13)${NC} 💻 Shell tmux"
    echo -e "  ${BOLD}0)${NC} ❌ Salir"
    echo
}

# Loop principal
while true; do
    show_menu
    read -p "$(echo -e ${CYAN}Selecciona una opción: ${NC})" choice
    
    case $choice in
        1)
            run_command "cd ~/glados/batman-incorporated && ./batman --help" "Batman Incorporated"
            ;;
        2)
            run_command "cd ~/glados/DiskDominator && code ." "Abriendo DiskDominator en VSCode"
            ;;
        3)
            run_command "cd ~/glados/UTILITIES/MPC && ls -la" "MCP Servers"
            ;;
        4)
            run_command "cd ~/glados/UTILITIES/InfiniteAgent && ./infinity-demo" "InfiniteAgent Demo"
            ;;
        5)
            run_command "~/glados/batman-incorporated/monitor status" "Monitor Sistema"
            ;;
        6)
            echo -e "${YELLOW}Herramientas disponibles:${NC}"
            echo "  - rg: Búsqueda rápida"
            echo "  - fd: Buscar archivos"
            echo "  - bat: Ver archivos con colores"
            echo "  - procs: Procesos mejorado"
            echo "  - z: Navegación rápida"
            ;;
        7)
            run_command "c2w menu" "Copy2Windows Menu"
            ;;
        8)
            run_command "claude-read-todo" "Ver TODO actual"
            ;;
        9)
            run_command "~/glados/scripts/launchers/claude-auto-context.sh" "Claude con contexto automático"
            ;;
        10)
            run_command "~/glados/SYSTEM/voice/voz/notificar-claude.sh" "Toggle sistema de voz"
            ;;
        11)
            run_command "claude-quota -q" "Verificando quota Claude"
            ;;
        12)
            run_command "~/glados/scripts/connectivity/check-connectivity.sh" "Verificando conectividad"
            ;;
        13)
            run_command "tmux new-session -s glados || tmux attach -t glados" "Tmux session"
            ;;
        0)
            echo -e "${GREEN}¡Hasta luego!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Opción inválida${NC}"
            ;;
    esac
    
    echo
    read -p "$(echo -e ${YELLOW}Presiona ENTER para continuar...${NC})"
    clear
done