#\!/bin/bash
# GLADOS Maintenance Script
echo "🔧 GLADOS MAINTENANCE - $(date)"
echo "================================"

# Limpiar temporales
echo "🧹 Limpiando archivos temporales..."
find ~/glados -name "*.tmp" -o -name "*.bak" -mtime +7 -delete 2>/dev/null
find ~/glados -name "*.log" -mtime +30 -delete 2>/dev/null

# Limpiar papelera vieja
echo "🗑️ Limpiando papelera antigua..."
find ~/glados/.papelera -type d -mtime +30 -exec rm -rf {} \; 2>/dev/null

# Verificar integridad
echo "✅ Verificando estructura..."
for dir in UTILITIES SYSTEM scripts; do
    [ -d "$dir" ] && echo "  ✓ $dir OK" || echo "  ✗ $dir MISSING"
done

# Actualizar c2w
echo "🔄 Actualizando sincronización Windows..."
c2w sync SYSTEM >/dev/null 2>&1

echo "✅ Mantenimiento completado"
