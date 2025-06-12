#!/bin/bash
# Script para sincronizar TODOS los proyectos a K:\_Glados
# Ejecutar regularmente para mantener backup actualizado

echo "🔄 Iniciando sincronización completa a K:\\_Glados..."
echo "Fecha: $(date)"

# Array de proyectos
projects=(
    "DiskDominator"
    "batman-incorporated"
    "MPC"
    "InfiniteAgent"
    "scripts"
    "SYSTEM"
)

# Sincronizar cada proyecto
for project in "${projects[@]}"; do
    echo ""
    echo "📦 Sincronizando $project..."
    c2w sync "$project"
    
    if [ $? -eq 0 ]; then
        echo "✅ $project sincronizado correctamente"
    else
        echo "❌ Error sincronizando $project"
    fi
done

# Backup adicional de archivos importantes no incluidos
echo ""
echo "📄 Copiando archivos adicionales..."
cp ~/glados/*.md /mnt/k/_Glados/ 2>/dev/null
cp ~/glados/launcher /mnt/k/_Glados/ 2>/dev/null

# Copiar carpeta wsl-repairing
echo "🔧 Copiando documentación de reparación..."
cp -r ~/glados/wsl-repairing /mnt/k/_Glados/

echo ""
echo "✅ Sincronización completa finalizada"
echo "📍 Todo respaldado en K:\\_Glados"