#!/bin/bash
# Monitor nocturno - verifica que Batman siga trabajando
while [ ! -f /tmp/batman_emergency_stop ]; do
    sleep 300  # Check every 5 minutes
    
    if ! pgrep -f "batman.py.*MISIÓN NOCTURNA" > /dev/null; then
        echo "⚠️  $(date): Batman process died, restarting..." >> /tmp/batman_night_monitor.log
        cd /home/lauta/glados/batman-incorporated
        nohup python3 batman.py "MISIÓN NOCTURNA RECOVERY: Continuar completando DiskDominator desde donde se quedó" --mode=redundante --real-agents --auto --max-agents=4 --verbose >> /tmp/batman_night_recovery.log 2>&1 &
    fi
    
    # Progress check
    echo "✅ $(date): Batman still running" >> /tmp/batman_night_monitor.log
done
