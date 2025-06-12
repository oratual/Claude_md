#\!/bin/bash
# GLADOS System Verifier
echo "🔍 GLADOS SYSTEM VERIFICATION"
echo "============================="

ERRORS=0

# Verificar estructura
echo "📁 Verificando estructura..."
for dir in UTILITIES SYSTEM scripts docs batman-incorporated DiskDominator; do
    if [ -d "$dir" ]; then
        echo "  ✓ $dir"
    else
        echo "  ✗ $dir MISSING"
        ((ERRORS++))
    fi
done

# Verificar symlinks
echo -e "\n🔗 Verificando symlinks..."
for link in launcher voz-claude; do
    if [ -L "$link" ]; then
        echo "  ✓ $link → $(readlink $link)"
    else
        echo "  ✗ $link MISSING"
        ((ERRORS++))
    fi
done

# Verificar ejecutables
echo -e "\n🚀 Verificando ejecutables..."
for exe in SYSTEM/launcher/main-launcher.sh batman-incorporated/batman.py scripts/Copy2Windows/copy2windows-menu.sh; do
    if [ -x "$exe" ]; then
        echo "  ✓ $exe"
    else
        echo "  ✗ $exe NOT EXECUTABLE"
        ((ERRORS++))
    fi
done

# Resultado
echo -e "\n📊 RESULTADO:"
if [ $ERRORS -eq 0 ]; then
    echo "✅ Sistema verificado correctamente"
else
    echo "❌ Se encontraron $ERRORS errores"
fi

exit $ERRORS
