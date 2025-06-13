# GLADOS CHEATSHEET - Comandos Rápidos

## 🚀 Comandos Esenciales

```bash
# Launcher principal
launcher                    # Menú interactivo

# Batman (tareas complejas)
batman "tarea"                 # Agentes reales por defecto
batman "tarea" --simulate      # Solo para testing (simulado)
batman-direct "tarea"          # Versión directa sin wrappers

# Sincronización Windows
c2w menu                    # Menú interactivo
c2w sync MPC               # Sincronizar proyecto
c2w list                   # Ver proyectos

# Sistema de voz
voz-claude                 # Toggle voz on/off

# Monitoreo
claude-quota -q            # Ver quota Claude
~/glados/SYSTEM/monitoring/system-status.sh   # Status sistema

# Backup
~/glados/scripts/backup/quick-backup.sh      # Backup rápido

# Mantenimiento
~/glados/SYSTEM/maintenance.sh               # Limpieza y verificación
```

## 📁 Estructura Rápida

```
launcher → SYSTEM/launcher/main-launcher.sh
voz-claude → SYSTEM/voice/voz/notificar-claude.sh
MPC → UTILITIES/MPC/
InfiniteAgent → UTILITIES/InfiniteAgent/
```

## 🔧 Troubleshooting

```bash
# Verificar conectividad WSL2-Windows
~/glados/scripts/connectivity/check-connectivity.sh

# Ver logs
tail -f SYSTEM/logs/*.log

# Restaurar desde backup
scripts/backup/restore-glados.sh
```
