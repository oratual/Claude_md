# 🚨 WSL Plan de Emergencia - El Día de la Marmota

## 📅 Historial de Crashes (12/06/2025)
- **18:12** - Primer crash detectado, errores de .wslconfig
- **18:32** - Segundo crash tras intento de corrección
- **18:37** - Tercer crash, se corrigió .wslconfig
- **18:41** - WSL funcionando pero se volvió a colgar minutos después
- **~18:45** - Claude Desktop corrupto, requirió reinstalación
- **19:49** - ✅ WSL ESTABLE con nueva configuración

## 🔍 CAUSA RAÍZ IDENTIFICADA

### El problema real:
1. **Configuración restrictiva de memoria (4GB)** - Insuficiente para WSL con múltiples servicios
2. **WSLg (GUI) crasheando constantemente** - Xorg con señales SIGABRT repetidas
3. **Servicios gráficos fallando en cascada** - lightdm, xrdp todos en estado FAILED

### Configuración problemática inicial:
```ini
memory=4GB       # MUY POCO - causaba ahogo de memoria
processors=2     # Limitado
guiApplications=true  # WSLg crasheando constantemente
```

## 🛠️ SOLUCIÓN FINAL APLICADA

### Nueva configuración .wslconfig (Sistema: Ryzen 9 5900X + 64GB RAM):
```ini
[wsl2]
memory=48GB             # 75% de 64GB - WSL es el sistema principal
processors=20           # 20 de 24 threads - máximo rendimiento
swap=0                  # Sin swap - con 48GB es innecesario
guiApplications=false   # DESHABILITADO - previene crashes de Xorg
networkingMode=mirrored
dnsTunneling=true
firewall=true

[experimental]
autoMemoryReclaim=gradual
sparseVhd=true
```

### Servicios deshabilitados permanentemente:
```bash
sudo systemctl mask lightdm.service xrdp.service xrdp-sesman.service
sudo systemctl reset-failed
```

## 📊 Resultados Finales

### Antes (con 4GB):
- Systemd con timeouts constantes
- Crashes de Xorg repetidos
- WSL congelándose cada ~30 minutos
- Claude Desktop corrompiéndose

### Después (con 48GB):
- **Estado del sistema**: `running` ✅
- **Memoria disponible**: 45GB de 47GB
- **Tiempo de respuesta**: 3ms (0.003s)
- **Carga del sistema**: 0.08 (casi nula)
- **Sin crashes en los logs**

## 🚀 Comandos de Verificación

```bash
# Estado del sistema
systemctl is-system-running  # Debe mostrar "running"

# Recursos disponibles
free -h     # ~48GB disponibles
nproc       # 20 procesadores

# Monitor de salud
~/glados/scripts/wsl-claude-monitor.sh --check
```

## 📝 Lecciones Aprendidas

1. **WSL necesita recursos generosos** - No escatimar en RAM/CPU
2. **WSLg puede ser inestable** - Mejor deshabilitarlo si no es esencial
3. **Servicios gráficos no necesarios** - Los menús TUI funcionan sin ellos
4. **Con 64GB de RAM, usar al menos 32-48GB para WSL**

## ⚠️ Qué NO afecta deshabilitar WSLg:
- ✅ Menús de consola (dialog, whiptail)
- ✅ Aplicaciones TUI (htop, vim, mc)
- ✅ Colores y emojis en terminal
- ✅ VS Code Remote-WSL
- ✅ Docker con interfaces web

## 🔧 Plan de Emergencia Si Vuelve a Fallar

1. **Verificar logs**:
   ```bash
   dmesg -T | tail -50
   journalctl -n 100 --no-pager
   ```

2. **Reinicio rápido desde PowerShell**:
   ```powershell
   wsl --shutdown
   Stop-Service LxssManager -Force
   Start-Service LxssManager
   wsl
   ```

3. **Si persiste, revisar**:
   - Actualizaciones de Windows pendientes
   - Versión de WSL: `wsl --version`
   - Considerar actualizar WSL: `wsl --update`

## 🔍 Monitor de Salud WSL

Script creado: `~/glados/scripts/wsl-claude-monitor.sh`

### Uso:
```bash
# Monitoreo continuo
~/glados/scripts/wsl-claude-monitor.sh

# Chequeo rápido
~/glados/scripts/wsl-claude-monitor.sh --check

# Ver estadísticas
~/glados/scripts/wsl-claude-monitor.sh --stats

# En background
nohup ~/glados/scripts/wsl-claude-monitor.sh > /dev/null 2>&1 &
```

### Logs guardados en:
- `~/.wsl2-monitor/freeze-detection.log` - Eventos en tiempo real
- `~/.wsl2-monitor/crash-report-*.txt` - Reportes detallados

---
Última actualización: 12/06/2025 19:52
Estado: ✅ RESUELTO - WSL estable con 48GB RAM + 20 CPUs