#!/bin/bash
# Lanzador automático para la segunda ronda de agentes

echo "🦇 BATMAN INCORPORATED - Ronda 2 de Paralelización"
echo "================================================="

MISSION_DIR="$HOME/.batman/missions/round2_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$MISSION_DIR"

# Crear misiones para cada agente
cat > "$MISSION_DIR/oracle_mission.md" << 'EOF'
# Misión para Oracle - Completar Tests

## 🎯 Objetivo
Completar la suite de tests para garantizar 100% de cobertura.

## 📋 Tareas
1. Crear `tests/test_mcp_integration.py` - Tests para el sistema MCP
2. Crear `tests/test_arsenal.py` - Tests para detección de herramientas
3. Crear `tests/test_config.py` - Tests para sistema de configuración

## 🔒 Archivos asignados
- tests/test_mcp_integration.py
- tests/test_arsenal.py  
- tests/test_config.py

## 💡 Contexto
Los tests de agentes ya pasaron (23/25). Necesitamos tests para los otros módulos críticos.

¡Adelante Oracle! 🦇
EOF

cat > "$MISSION_DIR/robin_mission.md" << 'EOF'
# Misión para Robin - GitHub Actions CI/CD

## 🎯 Objetivo
Configurar pipeline completo de CI/CD con GitHub Actions.

## 📋 Tareas
1. Crear `.github/workflows/ci.yml` - Pipeline principal
2. Crear `.github/workflows/tests.yml` - Pipeline de tests
3. Crear `.github/workflows/deploy.yml` - Pipeline de deployment

## 🔒 Archivos asignados
- .github/workflows/ci.yml
- .github/workflows/tests.yml
- .github/workflows/deploy.yml

## 💡 Contexto
Ya tienes install.sh y deploy.sh creados. Úsalos en los workflows.

¡Adelante Robin! 🦇
EOF

cat > "$MISSION_DIR/lucius_mission.md" << 'EOF'
# Misión para Lucius - Documentación Completa

## 🎯 Objetivo
Crear documentación completa de APIs y ejemplos de uso.

## 📋 Tareas
1. Crear `docs/API.md` - Documentación de todas las APIs
2. Crear `docs/EXAMPLES.md` - Ejemplos de uso prácticos
3. Crear `docs/ARCHITECTURE.md` - Arquitectura detallada del sistema
4. Crear `examples/basic_usage.py` - Script ejemplo funcional

## 🔒 Archivos asignados
- docs/API.md
- docs/EXAMPLES.md
- docs/ARCHITECTURE.md
- examples/basic_usage.py

## 💡 Contexto
El sistema ya está funcionando. Documenta cómo usarlo efectivamente.

¡Adelante Lucius! 🦇
EOF

cat > "$MISSION_DIR/batgirl_mission.md" << 'EOF'
# Misión para Batgirl - UI de Monitoreo

## 🎯 Objetivo
Crear interfaz web para monitorear agentes en tiempo real.

## 📋 Tareas
1. Crear `web/index.html` - Página principal con dashboard
2. Crear `web/monitor.js` - JavaScript para actualización en tiempo real
3. Crear `web/styles.css` - Estilos modernos y responsive

## 🔒 Archivos asignados
- web/index.html
- web/monitor.js
- web/styles.css

## 💡 Contexto
Usa WebSockets o polling para mostrar estado de agentes en tiempo real.

¡Adelante Batgirl! 🦇
EOF

# Función para lanzar agente
launch_agent() {
    local agent=$1
    local mission="$MISSION_DIR/${agent}_mission.md"
    
    echo "🚀 Lanzando $agent..."
    nohup claude --model opus --print --dangerously-skip-permissions "$(cat $mission)" > "/tmp/batman_${agent}_r2.log" 2>&1 &
    echo "✅ $agent lanzado (PID: $!)"
    sleep 2
}

# Lanzar todos los agentes
echo ""
echo "🚀 Lanzando agentes para Ronda 2..."
echo ""

launch_agent "oracle"
launch_agent "robin"
launch_agent "lucius"
launch_agent "batgirl"

echo ""
echo "✅ Todos los agentes de Ronda 2 lanzados!"
echo ""
echo "📊 Monitorear con:"
echo "  watch 'ps aux | grep claude | grep -v grep'"
echo ""
echo "📝 Ver logs:"
echo "  tail -f /tmp/batman_oracle_r2.log"
echo "  tail -f /tmp/batman_robin_r2.log"
echo "  tail -f /tmp/batman_lucius_r2.log"
echo "  tail -f /tmp/batman_batgirl_r2.log"