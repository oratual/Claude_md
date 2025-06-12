#!/bin/bash

# Script para lanzar automáticamente los agentes en paralelo

MISSION_DIR="/home/lauta/.batman/missions/20250610_235850"

echo "🦇 Lanzando agentes Batman Incorporated en paralelo..."

# Función para lanzar un agente
launch_agent() {
    local agent_name=$1
    local mission_file=$2
    local log_file="/tmp/batman_${agent_name}.log"
    
    echo "🚀 Lanzando $agent_name..."
    
    # Crear script temporal para el agente
    cat > "/tmp/launch_${agent_name}.sh" << EOF
#!/bin/bash
cd /home/lauta/glados/batman-incorporated
claude --model opus --print --dangerously-skip-permissions "\$(cat $mission_file)" > "$log_file" 2>&1
EOF
    
    chmod +x "/tmp/launch_${agent_name}.sh"
    
    # Lanzar en background
    nohup "/tmp/launch_${agent_name}.sh" &
    
    echo "✅ $agent_name lanzado (PID: $!)"
}

# Lanzar todos los agentes
launch_agent "alfred" "$MISSION_DIR/alfred_mission.md"
sleep 2
launch_agent "oracle" "$MISSION_DIR/oracle_mission.md"
sleep 2
launch_agent "robin" "$MISSION_DIR/robin_mission.md"
sleep 2
launch_agent "lucius" "$MISSION_DIR/lucius_mission.md"

echo ""
echo "✅ Todos los agentes lanzados!"
echo ""
echo "📊 Para monitorear el progreso:"
echo "  ./monitor_parallel_progress.sh"
echo ""
echo "📝 Para ver logs de cada agente:"
echo "  tail -f /tmp/batman_alfred.log"
echo "  tail -f /tmp/batman_oracle.log"
echo "  tail -f /tmp/batman_robin.log"
echo "  tail -f /tmp/batman_lucius.log"