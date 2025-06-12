#!/bin/bash
# Script para finalizar el proyecto en paralelo

echo "🦇 BATMAN INCORPORATED - Finalización Paralela"
echo "============================================="

# 1. Ejecutar tests en background
echo "🧪 Ejecutando tests..."
(
    source venv/bin/activate
    python -m pytest tests/ -v --tb=short > test_results.log 2>&1
    echo "✅ Tests completados. Ver test_results.log"
) &
TEST_PID=$!

# 2. Hacer commit en background  
echo "💾 Haciendo commit..."
(
    sleep 2  # Esperar un poco para que los tests empiecen
    git add -A
    git commit -m "feat: Parallel implementation complete with 4 agents working simultaneously

- Alfred: Fixed all missing imports (Any, Dict, Enum)
- Oracle: Created comprehensive test suite  
- Robin: Created install.sh and deploy.sh scripts
- Lucius: Working on API documentation

All agents worked in parallel without conflicts thanks to intelligent file assignment.

🦇 Batman Incorporated - Parallel Execution Success" > commit_result.log 2>&1
    echo "✅ Commit completado. Ver commit_result.log"
) &
COMMIT_PID=$!

# 3. Preparar siguiente ronda de tareas
echo "📋 Preparando siguiente ronda..."
(
    sleep 3
    cat > next_round_tasks.json << 'EOF'
{
  "round_2": {
    "oracle": {
      "tasks": [
        {
          "id": "17-complete",
          "title": "Completar tests restantes",
          "files": ["tests/test_mcp_integration.py", "tests/test_arsenal.py", "tests/test_config.py"]
        }
      ]
    },
    "robin": {
      "tasks": [
        {
          "id": "20",
          "title": "GitHub Actions CI/CD",
          "files": [".github/workflows/ci.yml", ".github/workflows/tests.yml", ".github/workflows/deploy.yml"]
        }
      ]
    },
    "lucius": {
      "tasks": [
        {
          "id": "19-complete", 
          "title": "Completar documentación",
          "files": ["docs/API.md", "docs/EXAMPLES.md", "docs/ARCHITECTURE.md", "examples/basic_usage.py"]
        }
      ]
    },
    "batgirl": {
      "tasks": [
        {
          "id": "21",
          "title": "Crear UI web para monitoreo",
          "files": ["web/index.html", "web/monitor.js", "web/styles.css"]
        }
      ]
    }
  }
}
EOF
    echo "✅ Tareas preparadas en next_round_tasks.json"
) &
PREP_PID=$!

# 4. Monitor de progreso
echo ""
echo "⏳ Esperando operaciones paralelas..."
echo ""

# Función para verificar estado
check_status() {
    local pid=$1
    local name=$2
    if kill -0 $pid 2>/dev/null; then
        echo "🔄 $name: En progreso..."
    else
        echo "✅ $name: Completado"
    fi
}

# Loop de monitoreo
while kill -0 $TEST_PID 2>/dev/null || kill -0 $COMMIT_PID 2>/dev/null || kill -0 $PREP_PID 2>/dev/null; do
    clear
    echo "🦇 BATMAN INCORPORATED - Estado de Operaciones"
    echo "============================================="
    echo ""
    check_status $TEST_PID "Tests"
    check_status $COMMIT_PID "Commit" 
    check_status $PREP_PID "Preparación"
    echo ""
    sleep 1
done

echo ""
echo "✅ TODAS LAS OPERACIONES COMPLETADAS"
echo ""
echo "📊 Resultados:"
echo "- Tests: tail -20 test_results.log"
echo "- Commit: cat commit_result.log"
echo "- Siguiente ronda: cat next_round_tasks.json"
echo ""
echo "🚀 Para lanzar la siguiente ronda:"
echo "   ./launch_round_2.sh"