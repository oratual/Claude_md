#!/bin/bash
# install-wezterm-orange.sh - Instalación simple para Wezterm Claude Orange

set -e

SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
WEZTERM_CONFIG_DIR="$HOME/.config/wezterm"
WEZTERM_CONFIG="$WEZTERM_CONFIG_DIR/wezterm.lua"

echo "🍊 Instalando Claude Orange para Wezterm..."

# Crear directorio de configuración si no existe
mkdir -p "$WEZTERM_CONFIG_DIR"

# Copiar el módulo
cp "$SCRIPT_DIR/wezterm-claude-orange.lua" "$WEZTERM_CONFIG_DIR/"
echo "✅ Módulo copiado a $WEZTERM_CONFIG_DIR/"

# Verificar si existe configuración de Wezterm
if [[ ! -f "$WEZTERM_CONFIG" ]]; then
    echo "📝 Creando configuración básica de Wezterm..."
    cat > "$WEZTERM_CONFIG" << 'EOF'
local wezterm = require 'wezterm'
local claude_orange = require 'wezterm-claude-orange'

local config = {}

-- Aplicar keybindings del módulo claude orange
config.keys = claude_orange.get_keybindings()

-- Claude orange desactivado por defecto (activar con Ctrl+Shift+O)
config.claude_orange_enabled = false

return config
EOF
    echo "✅ Configuración creada en $WEZTERM_CONFIG"
else
    echo "⚠️  Ya existe $WEZTERM_CONFIG"
    echo "📋 AGREGAR MANUALMENTE estas líneas:"
    cat << 'EOF'

-- Claude Orange Module
local claude_orange = require 'wezterm-claude-orange'

-- Agregar keybindings (o fusionar con existentes)
config.keys = config.keys or {}
for _, key in ipairs(claude_orange.get_keybindings()) do
    table.insert(config.keys, key)
end

-- Claude orange desactivado por defecto
config.claude_orange_enabled = false

EOF
fi

echo ""
echo "🎯 INSTALACIÓN COMPLETA"
echo ""
echo "📖 CÓMO USAR:"
echo "  1. Reinicia Wezterm"
echo "  2. Abre Claude Code en Wezterm"
echo "  3. Presiona Ctrl+Shift+O para activar/desactivar"
echo "  4. Las intervenciones del usuario se verán en naranja intenso"
echo ""
echo "⌨️  ATAJOS:"
echo "  Ctrl+Shift+O = Toggle modo naranja"
echo ""
echo "💡 VENTAJAS:"
echo "  • Cero impacto en rendimiento"
echo "  • Usa capacidades nativas de Wezterm"
echo "  • Toggle instantáneo"
echo "  • No modifica Claude Code"
echo ""