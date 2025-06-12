#\!/bin/bash
# System Status Monitor for Glados
echo "🤖 GLADOS SYSTEM STATUS - $(date)"
echo "================================"
echo "📊 Disk Usage:"
df -h /home/lauta/glados  < /dev/null |  tail -1
echo
echo "📁 Main Directories:"
du -sh ~/glados/{batman-incorporated,DiskDominator,UTILITIES,SYSTEM,scripts} 2>/dev/null
echo
echo "🔧 Active Services:"
pgrep -a claude | head -5
echo
echo "🌐 Connectivity:"
tailscale status --peers=false 2>/dev/null || echo "Tailscale not running"
