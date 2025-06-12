#!/bin/bash

# Monitor de progreso para la operación paralela

MISSIONS_DIR="$HOME/.batman/missions"
LATEST_MISSION=$(ls -t "$MISSIONS_DIR" | head -1)
MISSION_PATH="$MISSIONS_DIR/$LATEST_MISSION"

echo "🦇 BATMAN INCORPORATED - Monitor de Progreso Paralelo"
echo "====================================================="
echo "Misión: $LATEST_MISSION"
echo ""

# Función para verificar archivos modificados
check_progress() {
    echo -e "\n📊 PROGRESO POR AGENTE:"
    echo "---------------------"
    
    # Alfred - Imports
    echo -e "\n🧙 ALFRED (Arreglar imports):"
    for file in "src/integrations/github_integration.py" "src/integrations/mcp_integration.py" "src/core/arsenal.py" "src/execution/coordinator.py"; do
        if [ -f "$file" ]; then
            mod_time=$(stat -c %Y "$file" 2>/dev/null || stat -f %m "$file" 2>/dev/null)
            current_time=$(date +%s)
            diff=$((current_time - mod_time))
            if [ $diff -lt 300 ]; then
                echo "  ✅ $file (modificado hace $diff segundos)"
            else
                echo "  ⏳ $file"
            fi
        else
            echo "  ❌ $file (no existe)"
        fi
    done
    
    # Oracle - Tests
    echo -e "\n👁️ ORACLE (Tests):"
    for file in "tests/test_arsenal.py" "tests/test_mcp_integration.py" "tests/test_agents.py" "tests/test_config.py"; do
        if [ -f "$file" ]; then
            echo "  ✅ $file (creado)"
        else
            echo "  ⏳ $file"
        fi
    done
    
    # Robin - Scripts y CI/CD
    echo -e "\n🐦 ROBIN (DevOps):"
    for file in "install.sh" "deploy.sh" ".github/workflows/ci.yml"; do
        if [ -f "$file" ]; then
            echo "  ✅ $file (creado)"
        else
            echo "  ⏳ $file"
        fi
    done
    
    # Lucius - Documentación
    echo -e "\n🦊 LUCIUS (Documentación):"
    for file in "docs/API.md" "docs/EXAMPLES.md" "docs/ARCHITECTURE.md"; do
        if [ -f "$file" ]; then
            echo "  ✅ $file (creado)"
        else
            echo "  ⏳ $file"
        fi
    done
}

# Función para mostrar actividad reciente
show_recent_activity() {
    echo -e "\n🔄 ACTIVIDAD RECIENTE (últimos 5 min):"
    echo "------------------------------------"
    find . -type f \( -name "*.py" -o -name "*.md" -o -name "*.sh" -o -name "*.yml" \) -mmin -5 2>/dev/null | grep -v "__pycache__" | head -10
}

# Loop principal
while true; do
    clear
    echo "🦇 BATMAN INCORPORATED - Monitor de Progreso Paralelo"
    echo "====================================================="
    echo "Hora: $(date '+%H:%M:%S')"
    
    check_progress
    show_recent_activity
    
    echo -e "\n\nPresiona Ctrl+C para salir. Actualizando cada 5 segundos..."
    sleep 5
done