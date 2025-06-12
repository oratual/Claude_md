# 🦇 Ejecución Paralela de Batman Incorporated

Esta guía explica cómo ejecutar múltiples instancias de Batman sin conflictos.

## 🚀 Inicio Rápido

### Opción 1: batman-parallel (Recomendado)
```bash
# Terminal 1
./batman-parallel disk "compilar DiskDominator para Windows"

# Terminal 2
./batman-parallel api "desarrollar API REST"

# Terminal 3
./batman-parallel docs "generar documentación del proyecto"
```

Cada proyecto tendrá sus propios logs y archivos temporales en:
- `~/.batman-parallel/[proyecto]/logs/`
- `~/.batman-parallel/[proyecto]/state/`
- `~/.batman-parallel/[proyecto]/tmp/`

## 🔧 Opciones Disponibles

### 1. **batman-parallel** (Simple y Efectivo)
- ✅ No requiere instalaciones adicionales
- ✅ Aislamiento por proyecto
- ✅ Fácil de usar
- ✅ Logs organizados por proyecto

### 2. **batman-isolated** (Aislamiento Avanzado)
Usa características nativas de Linux en orden de preferencia:
1. `unshare` - Namespaces del kernel
2. `firejail` - Sandbox de seguridad
3. `systemd-run` - Aislamiento con systemd
4. Variables de entorno - Fallback básico

```bash
./batman-isolated "tarea compleja"
```

### 3. **batman-multi** (Control Manual)
Para control total sobre el ID de instancia:
```bash
./batman-multi proyecto-alpha "compilar proyecto"
./batman-multi proyecto-beta "ejecutar tests"
```

## 📁 Estructura de Archivos

Sin aislamiento (conflictos potenciales):
```
/tmp/
├── batman_status.json      # ❌ Compartido
├── batman_monitor.log      # ❌ Compartido
├── batman_monitor.pid      # ❌ Solo una instancia
└── batman-worktrees/       # ⚠️  Posibles colisiones
```

Con `batman-parallel`:
```
~/.batman-parallel/
├── proyecto1/
│   ├── logs/
│   ├── state/
│   ├── tmp/
│   └── worktrees/
├── proyecto2/
│   ├── logs/
│   ├── state/
│   ├── tmp/
│   └── worktrees/
```

## 🛡️ Niveles de Aislamiento

### Nivel 1: Variables de Entorno (Básico)
- Archivos en directorios separados
- Sin aislamiento de procesos
- Adecuado para la mayoría de casos

### Nivel 2: Firejail (Recomendado)
```bash
# Instalar firejail
sudo apt install firejail

# Usar batman-parallel (detecta firejail automáticamente)
./batman-parallel proyecto "tarea"
```
- Sandbox de seguridad
- `/tmp` privado
- Mejor aislamiento de recursos

### Nivel 3: Namespaces (Avanzado)
```bash
# batman-isolated usa unshare automáticamente si está disponible
./batman-isolated "tarea crítica"
```
- Aislamiento completo de procesos
- Mount namespace separado
- PID namespace propio

## 🎯 Casos de Uso

### Desarrollo Multi-Proyecto
```bash
# Frontend
./batman-parallel frontend "desarrollar componentes React"

# Backend
./batman-parallel backend "implementar API endpoints"

# Documentación
./batman-parallel docs "actualizar README y guías"
```

### Testing Paralelo
```bash
# Tests unitarios
./batman-parallel test-unit "ejecutar tests unitarios"

# Tests de integración
./batman-parallel test-integration "ejecutar tests de integración"

# Tests E2E
./batman-parallel test-e2e "ejecutar tests end-to-end"
```

### Compilación Simultánea
```bash
# Windows
./batman-parallel build-win "compilar para Windows"

# Linux
./batman-parallel build-linux "compilar para Linux"

# macOS (cross-compile)
./batman-parallel build-mac "compilar para macOS"
```

## 🔍 Monitoreo

### Ver logs de un proyecto específico
```bash
# Logs en tiempo real
tail -f ~/.batman-parallel/proyecto/logs/*.log

# Ver todos los logs
ls ~/.batman-parallel/*/logs/
```

### Estado de las instancias
```bash
# Ver qué proyectos están activos
ps aux | grep batman | grep -E "(disk|api|docs)"

# Ver uso de recursos por proyecto
htop -p $(pgrep -f "batman.*proyecto")
```

## ⚠️ Consideraciones

### SafeMode y Worktrees
- SafeMode crea worktrees con timestamps únicos
- Bajo riesgo de colisión incluso sin aislamiento
- Con aislamiento: riesgo cero

### InfinityMode
- Ya diseñado para múltiples instancias
- Usa UUIDs únicos por sesión
- Compatible con ejecución paralela

### Monitor Web
- Solo una instancia puede usar puerto 8080
- Solución: Deshabilitar con `--no-monitor`
- O usar diferentes puertos (a implementar)

## 🚨 Troubleshooting

### "Address already in use"
El monitor web está usando el puerto 8080:
```bash
# Opción 1: Sin monitor
./batman-parallel proyecto "tarea" --no-monitor

# Opción 2: Matar proceso existente
pkill -f batman-web
```

### "Permission denied"
Verifica permisos de ejecución:
```bash
chmod +x batman-parallel batman-isolated batman-multi
```

### Logs mezclados
Asegúrate de usar uno de los scripts de aislamiento, no `./batman` directamente.

## 💡 Mejores Prácticas

1. **Un proyecto = Una instancia**
   - Usa nombres descriptivos: `frontend`, `backend`, `tests`

2. **Limpieza periódica**
   ```bash
   # Limpiar logs antiguos (más de 7 días)
   find ~/.batman-parallel -name "*.log" -mtime +7 -delete
   ```

3. **Monitoreo centralizado**
   ```bash
   # Script para ver todos los proyectos
   for dir in ~/.batman-parallel/*/logs; do
       echo "=== $(basename $(dirname $dir)) ==="
       tail -5 $dir/*.log 2>/dev/null
   done
   ```

## 🔮 Futuro

Próximas mejoras planeadas:
- [ ] Configuración de puertos dinámicos para monitor web
- [ ] Dashboard unificado para todas las instancias
- [ ] Límites de recursos por instancia (cgroups)
- [ ] Persistencia de estado entre reinicios