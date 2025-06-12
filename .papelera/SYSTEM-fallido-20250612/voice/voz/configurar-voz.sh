#!/bin/bash
# Menú de configuración de voces para Claude

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENGINES_DIR="$SCRIPT_DIR/engines"
CONFIG_FILE="$HOME/.config/claude-voz/config"

# Crear directorio de configuración si no existe
mkdir -p "$HOME/.config/claude-voz"

# Cargar configuración actual
load_config() {
    if [ -f "$CONFIG_FILE" ]; then
        source "$CONFIG_FILE"
    else
        # Valores por defecto
        CLAUDE_VOICE_ENGINE="pico2wave"
        CLAUDE_VOICE_ENABLED=1
    fi
}

# Guardar configuración
save_config() {
    cat > "$CONFIG_FILE" << EOF
# Configuración de voz para Claude
CLAUDE_VOICE_ENGINE="$CLAUDE_VOICE_ENGINE"
CLAUDE_VOICE_ENABLED=$CLAUDE_VOICE_ENABLED
CLAUDE_INSTANCE_NAME="$CLAUDE_INSTANCE_NAME"
EOF
}

# Mostrar estado de motores
show_engines_status() {
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}           Motores de Voz Disponibles${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    local current_engine="${CLAUDE_VOICE_ENGINE:-pico2wave}"
    
    for engine_file in "$ENGINES_DIR"/*.sh; do
        if [ -f "$engine_file" ]; then
            source "$engine_file"
            local engine_name=$(basename "$engine_file" .sh)
            local status_color=$RED
            local status_text="No instalado"
            local current_mark=""
            
            if check_installed; then
                status_color=$GREEN
                status_text="Instalado"
            fi
            
            if [ "$engine_name" = "$current_engine" ]; then
                current_mark="${YELLOW} [ACTUAL]${NC}"
            fi
            
            printf "  %-12s ${status_color}%-15s${NC} %s %s%s\n" \
                "$ENGINE_NAME" "$status_text" "$ENGINE_QUALITY" "$ENGINE_DESC" "$current_mark"
        fi
    done
    echo ""
}

# Menú principal
main_menu() {
    clear
    load_config
    
    echo -e "${MAGENTA}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║          🔊 Configuración de Voz para Claude 🔊           ║${NC}"
    echo -e "${MAGENTA}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Estado actual
    echo -e "${BLUE}Estado actual:${NC}"
    echo -e "  Motor: ${GREEN}$CLAUDE_VOICE_ENGINE${NC}"
    echo -e "  Habilitado: $([ "$CLAUDE_VOICE_ENABLED" = "1" ] && echo -e "${GREEN}Sí${NC}" || echo -e "${RED}No${NC}")"
    echo -e "  Instancia: ${YELLOW}${CLAUDE_INSTANCE_NAME:-No configurada}${NC}"
    echo ""
    
    show_engines_status
    
    echo -e "${CYAN}Opciones:${NC}"
    echo "  1) Cambiar motor de voz"
    echo "  2) Instalar motor de voz"
    echo "  3) Probar voz actual"
    echo "  4) $([ "$CLAUDE_VOICE_ENABLED" = "1" ] && echo "Desactivar" || echo "Activar") notificaciones de voz"
    echo "  5) Configurar nombre de instancia"
    echo "  6) Configuración avanzada"
    echo "  7) Salir"
    echo ""
    
    read -p "Seleccione una opción: " option
    
    case $option in
        1) change_engine ;;
        2) install_engine_menu ;;
        3) test_voice ;;
        4) toggle_voice ;;
        5) set_instance_name ;;
        6) advanced_config ;;
        7) exit 0 ;;
        *) echo -e "${RED}Opción inválida${NC}"; sleep 1; main_menu ;;
    esac
}

# Cambiar motor
change_engine() {
    echo ""
    echo -e "${YELLOW}Motores disponibles:${NC}"
    
    local engines=()
    local i=1
    
    for engine_file in "$ENGINES_DIR"/*.sh; do
        if [ -f "$engine_file" ]; then
            local engine_name=$(basename "$engine_file" .sh)
            engines+=("$engine_name")
            source "$engine_file"
            
            local installed=""
            if check_installed; then
                installed="${GREEN}[Instalado]${NC}"
            else
                installed="${RED}[No instalado]${NC}"
            fi
            
            echo "  $i) $ENGINE_NAME $installed"
            ((i++))
        fi
    done
    
    echo ""
    read -p "Seleccione motor (1-${#engines[@]}): " selection
    
    if [[ "$selection" =~ ^[0-9]+$ ]] && [ "$selection" -ge 1 ] && [ "$selection" -le "${#engines[@]}" ]; then
        CLAUDE_VOICE_ENGINE="${engines[$((selection-1))]}"
        save_config
        echo -e "${GREEN}Motor cambiado a: $CLAUDE_VOICE_ENGINE${NC}"
        
        # Verificar si está instalado
        source "$ENGINES_DIR/$CLAUDE_VOICE_ENGINE.sh"
        if ! check_installed; then
            echo -e "${YELLOW}Este motor no está instalado.${NC}"
            read -p "¿Desea instalarlo ahora? (s/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Ss]$ ]]; then
                install_engine
            fi
        fi
    else
        echo -e "${RED}Selección inválida${NC}"
    fi
    
    sleep 2
    main_menu
}

# Instalar motor
install_engine_menu() {
    echo ""
    echo -e "${YELLOW}Seleccione motor a instalar:${NC}"
    
    local engines=()
    local i=1
    
    for engine_file in "$ENGINES_DIR"/*.sh; do
        if [ -f "$engine_file" ]; then
            local engine_name=$(basename "$engine_file" .sh)
            source "$engine_file"
            
            if ! check_installed && [ "$engine_name" != "none" ]; then
                engines+=("$engine_name")
                echo "  $i) $ENGINE_NAME - $ENGINE_DESC"
                ((i++))
            fi
        fi
    done
    
    if [ ${#engines[@]} -eq 0 ]; then
        echo -e "${GREEN}Todos los motores ya están instalados${NC}"
        sleep 2
        main_menu
        return
    fi
    
    echo ""
    read -p "Seleccione motor (1-${#engines[@]}): " selection
    
    if [[ "$selection" =~ ^[0-9]+$ ]] && [ "$selection" -ge 1 ] && [ "$selection" -le "${#engines[@]}" ]; then
        local engine="${engines[$((selection-1))]}"
        source "$ENGINES_DIR/$engine.sh"
        echo ""
        install_engine
        echo -e "${GREEN}Instalación completada${NC}"
    else
        echo -e "${RED}Selección inválida${NC}"
    fi
    
    sleep 2
    main_menu
}

# Probar voz
test_voice() {
    if [ "$CLAUDE_VOICE_ENABLED" = "0" ]; then
        echo -e "${YELLOW}Las notificaciones de voz están desactivadas${NC}"
        sleep 2
        main_menu
        return
    fi
    
    source "$ENGINES_DIR/$CLAUDE_VOICE_ENGINE.sh"
    
    if ! check_installed; then
        echo -e "${RED}El motor $CLAUDE_VOICE_ENGINE no está instalado${NC}"
        sleep 2
        main_menu
        return
    fi
    
    echo -e "${BLUE}Probando voz con motor: $CLAUDE_VOICE_ENGINE${NC}"
    
    local test_messages=(
        "Hola, soy Claude"
        "Ultra think ha terminado"
        "Proceso completado exitosamente"
        "${CLAUDE_INSTANCE_NAME:-Sistema} ha finalizado"
    )
    
    echo "1) Mensaje corto"
    echo "2) Notificación Ultra think"
    echo "3) Mensaje medio"
    echo "4) Mensaje personalizado"
    echo "5) Escribir mensaje propio"
    echo ""
    
    read -p "Seleccione prueba (1-5): " test_option
    
    case $test_option in
        1|2|3|4)
            speak "${test_messages[$((test_option-1))]}"
            ;;
        5)
            read -p "Escriba el mensaje: " custom_message
            speak "$custom_message"
            ;;
        *)
            echo -e "${RED}Opción inválida${NC}"
            ;;
    esac
    
    sleep 1
    main_menu
}

# Activar/Desactivar voz
toggle_voice() {
    if [ "$CLAUDE_VOICE_ENABLED" = "1" ]; then
        CLAUDE_VOICE_ENABLED=0
        echo -e "${YELLOW}Notificaciones de voz desactivadas${NC}"
    else
        CLAUDE_VOICE_ENABLED=1
        echo -e "${GREEN}Notificaciones de voz activadas${NC}"
    fi
    
    save_config
    sleep 1
    main_menu
}

# Configurar nombre de instancia
set_instance_name() {
    echo ""
    echo -e "${BLUE}Configurar nombre de instancia${NC}"
    echo "Actual: ${CLAUDE_INSTANCE_NAME:-No configurado}"
    echo ""
    echo "Sugerencias: ultrathink, deepanalysis, quicktask, research"
    echo ""
    read -p "Nuevo nombre (vacío para quitar): " new_name
    
    CLAUDE_INSTANCE_NAME="$new_name"
    save_config
    
    if [ -z "$new_name" ]; then
        echo -e "${YELLOW}Nombre de instancia eliminado${NC}"
    else
        echo -e "${GREEN}Nombre configurado: $new_name${NC}"
    fi
    
    sleep 2
    main_menu
}

# Configuración avanzada
advanced_config() {
    clear
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}           Configuración Avanzada${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    echo "1) Exportar configuración a .bashrc"
    echo "2) Crear alias personalizado"
    echo "3) Ver configuración actual"
    echo "4) Resetear configuración"
    echo "5) Volver"
    echo ""
    
    read -p "Seleccione opción: " adv_option
    
    case $adv_option in
        1)
            echo "" >> ~/.bashrc
            echo "# Claude Voice Configuration" >> ~/.bashrc
            echo "export CLAUDE_VOICE_ENGINE=\"$CLAUDE_VOICE_ENGINE\"" >> ~/.bashrc
            echo "export CLAUDE_VOICE_ENABLED=$CLAUDE_VOICE_ENABLED" >> ~/.bashrc
            echo "export CLAUDE_INSTANCE_NAME=\"$CLAUDE_INSTANCE_NAME\"" >> ~/.bashrc
            echo "export PATH=\"$SCRIPT_DIR:\$PATH\"" >> ~/.bashrc
            echo -e "${GREEN}Configuración exportada a .bashrc${NC}"
            echo -e "${YELLOW}Ejecute: source ~/.bashrc${NC}"
            ;;
        2)
            read -p "Nombre del alias: " alias_name
            echo "alias $alias_name='CLAUDE_INSTANCE_NAME=\"$CLAUDE_INSTANCE_NAME\" $SCRIPT_DIR/claude-con-voz'" >> ~/.bashrc
            echo -e "${GREEN}Alias '$alias_name' creado${NC}"
            ;;
        3)
            echo -e "${BLUE}Configuración actual:${NC}"
            cat "$CONFIG_FILE"
            ;;
        4)
            rm -f "$CONFIG_FILE"
            echo -e "${YELLOW}Configuración reseteada${NC}"
            ;;
        5)
            main_menu
            return
            ;;
    esac
    
    echo ""
    read -p "Presione Enter para continuar..."
    advanced_config
}

# Iniciar
main_menu