# Diagnóstico de Inestabilidad WSL2 - 2025-06-12

## Problemas Identificados

### 1. **Fallos de Xorg (CRÍTICO)**
- Múltiples crashes del servidor X con señal 6 (SIGABRT)
- PIDs afectados: 818, 849, 896
- Errores capturados por WSL CaptureCrash

### 2. **PulseAudio en bucle de fallos**
- Error: "Too many levels of symbolic links" en `/run/user/1000/pulse/pid`
- El servicio falla repetidamente y entra en "service-start-limit-hit"
- El enlace simbólico apunta a `/mnt/wslg/runtime-dir/pulse/pid`
- **CAUSA PROBABLE**: Proyecto voz-claude (`~/glados/scripts/voz/`) que usa audio para notificaciones
- Los scripts TTS (gtts.sh, espeak.sh, pico2wave.sh) pueden haber dejado PulseAudio en estado corrupto

### 3. **Errores del driver gráfico (dxg)**
- Múltiples fallos de ioctl: `-22` (Invalid argument) y `-2` (No such file or directory)
- Afecta la comunicación con el subsistema gráfico de Windows

### 4. **Problemas de conectividad**
- WSL-Pro-Service no puede conectar con Windows Agent
- Archivo faltante: `/mnt/c/Users/lauta/.ubuntupro/.address`
- Errores de resolución DNS con Tailscale

### 5. **Inestabilidad del reloj del sistema**
- systemd-resolved detecta cambios de reloj frecuentes
- Puede indicar problemas de sincronización WSL2↔Windows

## Soluciones Propuestas

### Solución Inmediata (Reinicio limpio)
```bash
# 1. Detener WSL desde PowerShell (Windows)
wsl --shutdown

# 2. Limpiar caché de WSL (PowerShell como Admin)
net stop LxssManager
net start LxssManager

# 3. Reiniciar WSL
wsl
```

### Soluciones Específicas

#### Fix PulseAudio
```bash
# Remover enlace simbólico problemático
sudo rm -f /run/user/1000/pulse/pid
systemctl --user stop pulseaudio.socket pulseaudio.service
systemctl --user reset-failed pulseaudio.service
systemctl --user start pulseaudio.socket
```

#### Fix WSLg/Xorg
```bash
# Reiniciar servicio WSLg
sudo systemctl restart wslg-*

# Si persiste, deshabilitar temporalmente WSLg
echo "[wsl2]" | sudo tee -a /etc/wsl.conf
echo "guiApplications=false" | sudo tee -a /etc/wsl.conf
```

#### Fix DNS/Tailscale
```bash
# Restaurar resolv.conf
sudo rm /etc/resolv.conf
sudo bash -c 'echo "nameserver 8.8.8.8" > /etc/resolv.conf'
sudo chattr +i /etc/resolv.conf  # Prevenir sobrescritura

# O permitir que Tailscale maneje DNS
sudo tailscale up --accept-dns
```

### Configuración Preventiva

#### 1. Crear `.wslconfig` en Windows
Crear archivo `C:\Users\lauta\.wslconfig`:
```ini
[wsl2]
memory=6GB
processors=4
localhostForwarding=true
guiApplications=true
systemd=true

[experimental]
autoMemoryReclaim=gradual
sparseVhd=true
```

#### 2. Actualizar `/etc/wsl.conf`
```bash
sudo tee /etc/wsl.conf <<EOF
[boot]
systemd=true

[network]
generateResolvConf=false
hostname=Cerebro

[interop]
enabled=true
appendWindowsPath=true

[user]
default=lauta
EOF
```

### Script de Monitoreo
```bash
#!/bin/bash
# Guardar como ~/glados/scripts/wsl-health-check.sh

echo "=== WSL Health Check ==="
echo "Memory: $(free -h | grep Mem | awk '{print $3"/"$2}')"
echo "Load: $(uptime | awk -F'load average:' '{print $2}')"
echo "Failed services: $(systemctl --failed --no-pager | grep -c failed)"
echo "Xorg status: $(pgrep Xorg > /dev/null && echo "Running" || echo "Not running")"
echo "WSLg mounts: $(mount | grep -c wslg)"
echo "DNS working: $(nslookup google.com > /dev/null 2>&1 && echo "Yes" || echo "No")"
```

### Recolección de Logs Completa
Para usar el script oficial de Microsoft:
```powershell
# En PowerShell (Windows)
Invoke-WebRequest -Uri https://aka.ms/wsl/collect-logs -OutFile collect-wsl-logs.ps1
.\collect-wsl-logs.ps1
```

## Recomendaciones

1. **Actualizar WSL**: `wsl --update` desde PowerShell
2. **Revisar drivers GPU**: Actualizar drivers NVIDIA/AMD/Intel
3. **Considerar WSL Preview**: Más estable para WSLg
4. **Monitorear recursos**: El sistema parece quedarse sin recursos intermitentemente

## Estado Actual
- Memoria: 955MB/7.8GB usados ✓
- Uptime: Solo 3 minutos (recién reiniciado)
- WSL2 versión: Ubuntu 24.04, WSL2 kernel 6.6.87.1

Ejecuta las soluciones en orden y monitorea la estabilidad.