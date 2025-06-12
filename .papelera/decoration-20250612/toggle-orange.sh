#!/bin/bash
# toggle-orange.sh - Control rápido del coloreo naranja en Claude Code

SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
NARANJA_SCRIPT="$SCRIPT_DIR/NaranjaUserChat"

# Verificar que el script principal existe
if [[ ! -f "$NARANJA_SCRIPT" ]]; then
    echo "❌ Error: NaranjaUserChat no encontrado en $NARANJA_SCRIPT"
    exit 1
fi

# Función para mostrar estado con emoji
show_status() {
    "$NARANJA_SCRIPT" --naranja-status
}

# Función para toggle inteligente
toggle() {
    if "$NARANJA_SCRIPT" --naranja-status | grep -q "HABILITADO"; then
        "$NARANJA_SCRIPT" --naranja-off
        echo "🔄 Cambiado a: DESHABILITADO"
    else
        "$NARANJA_SCRIPT" --naranja-on
        echo "🔄 Cambiado a: HABILITADO"
    fi
}

# Función de ayuda
show_help() {
    cat << EOF
🍊 Toggle Orange - Control rápido del coloreo Claude

USO:
  $(basename "$0")           # Toggle automático (on/off)
  $(basename "$0") on        # Forzar habilitado
  $(basename "$0") off       # Forzar deshabilitado
  $(basename "$0") status    # Mostrar estado actual
  $(basename "$0") help      # Esta ayuda

ALIAS RECOMENDADO:
  echo 'alias orange="~/glados/scripts/decoration/toggle-orange.sh"' >> ~/.bashrc

ENTONCES PUEDES USAR:
  orange           # Toggle rápido
  orange status    # Ver estado
  orange on/off    # Control directo

EOF
}

# Procesar argumentos
case "${1:-toggle}" in
    "on"|"enable")
        "$NARANJA_SCRIPT" --naranja-on
        ;;
    "off"|"disable")
        "$NARANJA_SCRIPT" --naranja-off
        ;;
    "status"|"state")
        show_status
        ;;
    "toggle"|"")
        toggle
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        echo "❌ Argumento desconocido: $1"
        echo "💡 Usa: $(basename "$0") help"
        exit 1
        ;;
esac