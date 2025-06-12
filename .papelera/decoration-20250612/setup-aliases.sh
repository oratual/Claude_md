#!/bin/bash
# setup-aliases.sh - Configurar aliases para Claude Orange

SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"

echo "🍊 Configurando aliases para Claude Orange..."

# Verificar si ya existen los aliases
if grep -q "claude-orange\|NaranjaUserChat" ~/.bashrc; then
    echo "⚠️  Aliases ya configurados en ~/.bashrc"
    echo "📋 Aliases actuales:"
    grep -E "claude-orange|NaranjaUserChat|toggle-orange" ~/.bashrc || echo "  (ninguno encontrado)"
else
    echo "📝 Agregando aliases a ~/.bashrc..."
    
    cat >> ~/.bashrc << EOF

# 🍊 Claude Orange - Coloreo de intervenciones de usuario
alias orange="~/glados/scripts/decoration/toggle-orange.sh"
alias claude-orange="~/glados/scripts/decoration/NaranjaUserChat"

EOF
    
    echo "✅ Aliases agregados"
fi

echo ""
echo "🎯 ALIASES DISPONIBLES:"
echo "  orange          # Toggle rápido on/off"
echo "  orange status   # Ver estado actual"
echo "  orange on/off   # Control directo"
echo "  claude-orange   # Claude con wrapper universal"
echo ""
echo "🔄 Para aplicar cambios:"
echo "  source ~/.bashrc"
echo ""

# Ofrecer cargar automáticamente
read -p "¿Cargar aliases ahora? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    source ~/.bashrc
    echo "✅ Aliases cargados"
    
    # Mostrar estado actual
    echo ""
    echo "📊 Estado actual:"
    "$SCRIPT_DIR/toggle-orange.sh" status
else
    echo "💡 Recuerda ejecutar: source ~/.bashrc"
fi