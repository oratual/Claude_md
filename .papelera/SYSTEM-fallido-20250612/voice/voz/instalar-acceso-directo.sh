#!/bin/bash
# Script para instalar accesos directos al menú de voz

echo "📦 Instalando accesos directos..."

# 1. Crear alias en .bashrc
if ! grep -q "alias voz=" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# Acceso directo al menú de voz" >> ~/.bashrc
    echo "alias voz='~/glados/scripts/voz/configurar-voz.sh'" >> ~/.bashrc
    echo "✅ Alias 'voz' agregado"
fi

# 2. Copiar .bat a escritorio de Windows
cp ~/glados/scripts/voz/configurar-voz-windows.bat /mnt/c/Users/lauta/Desktop/ 2>/dev/null && \
    echo "✅ Acceso directo copiado al escritorio" || \
    echo "⚠️  No se pudo copiar al escritorio"

# 3. Agregar al PATH (opcional)
if ! echo $PATH | grep -q "$HOME/glados/scripts/voz"; then
    echo "export PATH=\"\$HOME/glados/scripts/voz:\$PATH\"" >> ~/.bashrc
    echo "✅ Agregado al PATH"
fi

echo ""
echo "🎉 ¡Listo! Ahora puedes usar:"
echo ""
echo "   Desde Linux/WSL:"
echo "   $ voz"
echo ""
echo "   Desde Windows:"
echo "   Doble clic en 'configurar-voz-windows.bat' en el escritorio"
echo ""
echo "⚠️  Ejecuta 'source ~/.bashrc' para activar el alias ahora"