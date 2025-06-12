#!/bin/bash

# Colores para el menú
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;36m'  # Cambiado a cyan brillante
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Variables para manejo de selección
selected_index=0
total_options=0

# Detectar directorio base
if [ -d "$HOME/glados" ]; then
    BASE_DIR="$HOME/glados"
elif [ -d "/home/lauta/glados" ]; then
    BASE_DIR="/home/lauta/glados"
else
    echo "Error: No se encuentra el directorio glados"
    exit 1
fi

# Función para mostrar el banner
show_banner() {
    clear
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════════╗"
    echo "║          GLADOS PROJECT LAUNCHER          ║"
    echo "╚═══════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Función para obtener las subcarpetas
get_projects() {
    cd "$BASE_DIR" || {
        echo "Error: No se puede acceder a $BASE_DIR" >&2
        return 1
    }
    
    # Excluir directorios ocultos y scripts
    find . -maxdepth 1 -type d ! -path . ! -path '*/\.*' ! -path './scripts' -printf '%f\n' | sort
}

# Función para mostrar una opción del menú
print_option() {
    local index=$1
    local text=$2
    local extra=$3
    
    if [ $index -eq $selected_index ]; then
        echo -e "${WHITE}▶ ${GREEN}$((index+1))${NC}) ${BLUE}$text${NC} $extra"
    else
        echo -e "  ${GREEN}$((index+1))${NC}) ${BLUE}$text${NC} $extra"
    fi
}

# Función para mostrar el menú principal
show_menu() {
    show_banner
    echo -e "${YELLOW}Selecciona una opción:${NC}\n"
    
    # Opciones especiales primero
    print_option 0 "Claude Code (sin proyecto)" ""
    print_option 1 "Claude Code (elegir conversación)" "${PURPLE}[seleccionar de todas]${NC}"
    print_option 2 "Terminal en glados" ""
    
    echo -e "${CYAN}───────────────────────────────────────────${NC}"
    echo -e "${YELLOW}Proyectos:${NC}"
    
    # Obtener lista de proyectos
    projects=($(get_projects))
    
    # Mostrar proyectos
    local idx=3
    for project in "${projects[@]}"; do
        # Verificar si es un repositorio git
        if [ -d "$BASE_DIR/$project/.git" ]; then
            print_option $idx "$project" "${PURPLE}[git → cs]${NC}"
        else
            print_option $idx "$project" "${CYAN}[terminal]${NC}"
        fi
        ((idx++))
    done
    
    echo -e "${CYAN}───────────────────────────────────────────${NC}"
    print_option $idx "Salir" ""
    
    total_options=$((idx+1))
}

# Función para manejar input con soporte de flechas y números
handle_input() {
    local key
    local number_buffer=""
    
    while true; do
        show_menu
        
        # Mostrar buffer de números si existe
        if [ -n "$number_buffer" ]; then
            echo -en "\n${PURPLE}Número ingresado: ${WHITE}$number_buffer${NC} (Enter para confirmar, Esc para cancelar)"
        else
            echo -en "\n${PURPLE}Usa ↑/↓ o ingresa un número:${NC} "
        fi
        
        # Leer entrada
        IFS= read -rsn1 key
        
        # Verificar si no se leyó nada (Enter)
        if [ -z "$key" ]; then
            # Enter presionado
            if [ -n "$number_buffer" ]; then
                # Procesar número ingresado
                local num=$((10#$number_buffer))
                if [ $num -ge 1 ] && [ $num -le $total_options ]; then
                    selected_index=$((num-1))
                    execute_option
                    return
                else
                    echo -e "\n${RED}Número inválido: $number_buffer${NC}"
                    sleep 1
                    number_buffer=""
                fi
            else
                # Ejecutar opción seleccionada con flechas
                execute_option
                return
            fi
        elif [[ $key == $'\x1b' ]]; then
            # Detectar secuencias de escape (flechas)
            read -rsn2 key
            if [ -n "$number_buffer" ]; then
                # Esc presionado, limpiar buffer
                number_buffer=""
                continue
            fi
            case $key in
                '[A') # Flecha arriba
                    ((selected_index--))
                    if [ $selected_index -lt 0 ]; then
                        selected_index=$((total_options-1))
                    fi
                    ;;
                '[B') # Flecha abajo
                    ((selected_index++))
                    if [ $selected_index -ge $total_options ]; then
                        selected_index=0
                    fi
                    ;;
            esac
        elif [[ $key =~ ^[0-9]$ ]]; then
            # Acumular dígitos
            number_buffer="${number_buffer}${key}"
        fi
    done
}

# Función para ejecutar la opción seleccionada (versión independiente)
execute_option() {
    # Obtener lista de proyectos nuevamente
    projects=($(get_projects))
    
    # Restaurar terminal
    stty sane 2>/dev/null || true
    
    if [ $selected_index -eq 0 ]; then
        # Claude Code sin proyecto - lanzar en ventana nueva
        echo -e "\n${GREEN}Preparando Claude Code...${NC}"
        sleep 1
        # Abrir nueva ventana de Wezterm con Claude
        nohup wezterm start -- bash -lc "cd $BASE_DIR && source ~/.nvm/nvm.sh && claude --dangerously-skip-permissions" >/dev/null 2>&1 &
        echo -e "${CYAN}Claude Code lanzado en nueva ventana${NC}"
        sleep 2
        exit 0
    elif [ $selected_index -eq 1 ]; then
        # Claude Code con resume - lanzar en ventana nueva
        echo -e "\n${GREEN}Preparando selección de conversaciones...${NC}"
        sleep 1
        # Abrir nueva ventana de Wezterm con Claude resume
        nohup wezterm start -- bash -lc "cd $BASE_DIR && source ~/.nvm/nvm.sh && claude --dangerously-skip-permissions --resume" >/dev/null 2>&1 &
        echo -e "${CYAN}Claude Code lanzado con selector de conversaciones${NC}"
        sleep 2
        exit 0
    elif [ $selected_index -eq 2 ]; then
        # Solo terminal
        echo -e "\n${GREEN}Abriendo terminal en glados...${NC}"
        cd "$BASE_DIR"
        exec bash -l
    elif [ $selected_index -eq $((total_options-1)) ]; then
        # Salir
        echo -e "\n${RED}Saliendo...${NC}"
        exit 0
    else
        # Proyecto seleccionado
        local project_idx=$((selected_index-3))
        local selected_project="${projects[$project_idx]}"
        
        cd "$BASE_DIR/$selected_project"
        
        # Verificar si es un repositorio git
        if [ -d .git ]; then
            echo -e "\n${GREEN}Preparando Claude Squad en $selected_project...${NC}"
            sleep 1
            # Abrir nueva ventana con Claude Squad
            nohup wezterm start -- bash -lc "cd $BASE_DIR/$selected_project && source ~/.nvm/nvm.sh && cs -y" >/dev/null 2>&1 &
            echo -e "${CYAN}Claude Squad lanzado en $selected_project${NC}"
            sleep 2
            exit 0
        else
            echo -e "\n${CYAN}Abriendo terminal en $selected_project...${NC}"
            echo -e "${YELLOW}Este directorio no es un repositorio git.${NC}"
            echo -e "${WHITE}Puedes inicializar git con:${NC} ${GREEN}git init${NC}\n"
            exec bash -l
        fi
    fi
}

# Cargar NVM al inicio
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Habilitar soporte para secuencias de escape
if [ -t 0 ]; then
    stty -echo -icanon time 0 min 0 2>/dev/null || true
fi

# Restaurar configuración de terminal al salir
trap 'stty sane 2>/dev/null || true' EXIT

# Flujo principal
handle_input