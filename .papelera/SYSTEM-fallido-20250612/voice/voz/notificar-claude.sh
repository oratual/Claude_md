#!/bin/bash
# Sistema de notificación por voz para Claude
# Notifica cuando una instancia de Claude termina de responder

# Directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENGINES_DIR="$SCRIPT_DIR/engines"
CONFIG_FILE="$HOME/.config/claude-voz/config"

# Cargar configuración
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
fi

# Valores por defecto
CLAUDE_VOICE_ENGINE="${CLAUDE_VOICE_ENGINE:-pico2wave}"
CLAUDE_VOICE_ENABLED="${CLAUDE_VOICE_ENABLED:-1}"

# Detectar el motor configurado
get_engine() {
    echo "$CLAUDE_VOICE_ENGINE"
}


# Obtener título de la terminal actual
get_terminal_title() {
    # Intentar varios métodos para obtener el título
    
    # Método 1: Variable de entorno personalizada
    if [ ! -z "$CLAUDE_INSTANCE_NAME" ]; then
        echo "$CLAUDE_INSTANCE_NAME"
        return
    fi
    
    # Método 2: xdotool (si está en X11)
    if command -v xdotool &> /dev/null && [ ! -z "$DISPLAY" ]; then
        local window_id=$(xdotool getactivewindow 2>/dev/null)
        if [ ! -z "$window_id" ]; then
            local title=$(xdotool getwindowname $window_id 2>/dev/null)
            if [ ! -z "$title" ]; then
                echo "$title"
                return
            fi
        fi
    fi
    
    # Método 3: Título del proceso tmux
    if [ ! -z "$TMUX" ]; then
        local tmux_title=$(tmux display-message -p '#W' 2>/dev/null)
        if [ ! -z "$tmux_title" ]; then
            echo "$tmux_title"
            return
        fi
    fi
    
    # Método 4: Variable PS1 o nombre de host
    echo "${CLAUDE_TERMINAL_NAME:-$HOSTNAME}"
}

# Función para hablar usando el motor configurado
speak() {
    local text="$1"
    
    # Si la voz está deshabilitada, no hacer nada
    if [ "$CLAUDE_VOICE_ENABLED" = "0" ]; then
        return 0
    fi
    
    # Cargar el motor configurado
    local engine_file="$ENGINES_DIR/$CLAUDE_VOICE_ENGINE.sh"
    
    if [ -f "$engine_file" ]; then
        source "$engine_file"
        
        # Verificar si está instalado
        if check_installed; then
            # Usar la función speak del motor
            speak "$text"
        else
            echo "Error: Motor $CLAUDE_VOICE_ENGINE no está instalado" >&2
            echo "Ejecute: $SCRIPT_DIR/configurar-voz.sh" >&2
            return 1
        fi
    else
        echo "Error: Motor $CLAUDE_VOICE_ENGINE no encontrado" >&2
        return 1
    fi
}

# Función principal
main() {
    local terminal_name=$(get_terminal_title)
    local message=""
    
    # Personalizar mensaje según el nombre de la terminal
    case "$terminal_name" in
        *ultrathink*|*UltraThink*)
            message="Ultra think ha terminado"
            ;;
        *claude*|*Claude*)
            message="Claude ha terminado en $terminal_name"
            ;;
        *)
            message="$terminal_name ha terminado"
            ;;
    esac
    
    # Si se proporciona un mensaje personalizado como argumento
    if [ $# -gt 0 ]; then
        message="$*"
    fi
    
    # Hablar el mensaje
    speak "$message"
}

# Verificar si se está ejecutando como script o siendo importado
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi

# Exportar funciones para uso en otros scripts
export -f speak
export -f get_terminal_title