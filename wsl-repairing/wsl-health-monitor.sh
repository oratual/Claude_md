#!/bin/bash
# Script de monitoreo de salud WSL
# Ejecutar regularmente para detectar problemas temprano

echo "═══════════════════════════════════════════════════"
echo "        WSL Health Monitor - $(date)"
echo "═══════════════════════════════════════════════════"

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. Información básica
echo -e "\n📊 INFORMACIÓN DEL SISTEMA:"
echo "Hostname: $(hostname)"
echo "Uptime: $(uptime -p)"
echo "Kernel: $(uname -r)"

# 2. Memoria
echo -e "\n💾 MEMORIA:"
free -h | grep -E 'Mem:|Swap:'
MEM_PERCENT=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
if [ $MEM_PERCENT -gt 80 ]; then
    echo -e "${RED}⚠️  Uso de memoria alto: ${MEM_PERCENT}%${NC}"
elif [ $MEM_PERCENT -gt 60 ]; then
    echo -e "${YELLOW}⚡ Uso de memoria moderado: ${MEM_PERCENT}%${NC}"
else
    echo -e "${GREEN}✅ Uso de memoria normal: ${MEM_PERCENT}%${NC}"
fi

# 3. Disco
echo -e "\n💿 ESPACIO EN DISCO:"
df -h / | tail -1
DISK_PERCENT=$(df / | tail -1 | awk '{print int($5)}')
if [ $DISK_PERCENT -gt 90 ]; then
    echo -e "${RED}⚠️  Disco casi lleno: ${DISK_PERCENT}%${NC}"
elif [ $DISK_PERCENT -gt 70 ]; then
    echo -e "${YELLOW}⚡ Espacio en disco moderado: ${DISK_PERCENT}%${NC}"
else
    echo -e "${GREEN}✅ Espacio en disco OK: ${DISK_PERCENT}%${NC}"
fi

# 4. Servicios fallidos
echo -e "\n🔧 SERVICIOS:"
FAILED_SERVICES=$(systemctl --failed --no-pager 2>/dev/null | grep -c "failed")
if [ $FAILED_SERVICES -gt 0 ]; then
    echo -e "${RED}⚠️  Hay $FAILED_SERVICES servicios fallidos:${NC}"
    systemctl --failed --no-pager
else
    echo -e "${GREEN}✅ Todos los servicios funcionando${NC}"
fi

# 5. Procesos problemáticos
echo -e "\n🔍 PROCESOS CRÍTICOS:"
# Verificar Xorg
if pgrep Xorg > /dev/null; then
    echo -e "${GREEN}✅ Xorg funcionando${NC}"
else
    echo -e "${YELLOW}⚡ Xorg no está corriendo (normal si no usas GUI)${NC}"
fi

# Verificar PulseAudio
if systemctl --user is-active pulseaudio.service &>/dev/null; then
    echo -e "${GREEN}✅ PulseAudio activo${NC}"
else
    echo -e "${YELLOW}⚡ PulseAudio inactivo${NC}"
fi

# 6. Conectividad
echo -e "\n🌐 CONECTIVIDAD:"
# DNS
if nslookup google.com > /dev/null 2>&1; then
    echo -e "${GREEN}✅ DNS funcionando${NC}"
else
    echo -e "${RED}⚠️  Problemas con DNS${NC}"
fi

# Tailscale
if command -v tailscale &> /dev/null; then
    if tailscale status &> /dev/null; then
        echo -e "${GREEN}✅ Tailscale conectado${NC}"
    else
        echo -e "${YELLOW}⚡ Tailscale desconectado${NC}"
    fi
fi

# 7. Archivos de log grandes
echo -e "\n📝 LOGS GRANDES (>100MB):"
find /var/log -type f -size +100M 2>/dev/null | while read -r log; do
    SIZE=$(du -h "$log" | cut -f1)
    echo -e "${YELLOW}⚡ $log: $SIZE${NC}"
done

# 8. Temperatura y recursos (si está disponible)
echo -e "\n🌡️  CARGA DEL SISTEMA:"
echo "Load average: $(uptime | awk -F'load average:' '{print $2}')"

# 9. WSL específico
echo -e "\n🐧 WSL ESPECÍFICO:"
# Verificar montajes
MOUNTS=$(mount | grep -c "9p\|drvfs")
echo "Unidades Windows montadas: $MOUNTS"

# Verificar WSLg
if [ -d "/mnt/wslg" ]; then
    echo -e "${GREEN}✅ WSLg disponible${NC}"
else
    echo -e "${YELLOW}⚡ WSLg no disponible${NC}"
fi

# Resumen final
echo -e "\n═══════════════════════════════════════════════════"
echo -e "📋 RESUMEN:"
if [ $MEM_PERCENT -gt 80 ] || [ $DISK_PERCENT -gt 90 ] || [ $FAILED_SERVICES -gt 0 ]; then
    echo -e "${RED}⚠️  ATENCIÓN REQUERIDA - Revisa los problemas arriba${NC}"
else
    echo -e "${GREEN}✅ SISTEMA SALUDABLE${NC}"
fi
echo "═══════════════════════════════════════════════════"

# Guardar reporte
REPORT_FILE="$HOME/glados/wsl-repairing/health-reports/$(date +%Y%m%d-%H%M%S).txt"
mkdir -p "$HOME/glados/wsl-repairing/health-reports"
echo "Guardando reporte en: $REPORT_FILE"