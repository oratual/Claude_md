# 📦 Wrappers de Batman Incorporated

Este documento explica TODOS los wrappers y scripts ejecutables de Batman.

## 🎯 Resumen Rápido

| Wrapper | Propósito | Cuándo Usar |
|---------|-----------|-------------|
| `batman` | Ejecución estándar | Una sola tarea, sin paralelización |
| `batman-parallel` | Múltiples proyectos | **RECOMENDADO** para múltiples instancias |
| `batman-isolated` | Aislamiento máximo | Tareas críticas que requieren sandbox |
| `batman-multi` | Control manual de IDs | Debugging o casos especiales |

## 🔧 Wrappers Principales

### 1. `batman` (Original)
```bash
./batman "tarea"
```
- **Qué hace**: Ejecuta batman.py directamente
- **Problema**: Archivos compartidos en `/tmp/` causan conflictos
- **Usar cuando**: Solo tienes UNA instancia ejecutándose

### 2. `batman-parallel` (RECOMENDADO)
```bash
./batman-parallel <nombre-proyecto> "descripción de tarea"
```
- **Qué hace**: Aísla cada proyecto en su propio directorio
- **Ventajas**: 
  - Sin conflictos entre proyectos
  - Logs organizados por proyecto
  - No requiere herramientas adicionales
- **Archivos**: `~/.batman-parallel/[proyecto]/`

**Ejemplo real:**
```bash
# Terminal 1
./batman-parallel diskdom "compilar DiskDominator para Windows"

# Terminal 2  
./batman-parallel api "desarrollar endpoints REST"

# Terminal 3
./batman-parallel frontend "crear componentes React"
```

### 3. `batman-isolated`
```bash
./batman-isolated "tarea crítica"
```
- **Qué hace**: Usa herramientas Linux para aislamiento fuerte
- **Orden de preferencia**:
  1. `unshare` - Namespaces del kernel
  2. `firejail` - Sandbox de seguridad  
  3. `systemd-run` - Aislamiento systemd
  4. Variables de entorno - Fallback
- **Ventajas**: Aislamiento de seguridad tipo container
- **Usar cuando**: Necesitas máxima seguridad/aislamiento

### 4. `batman-multi`
```bash
./batman-multi [instance-id] "tarea"
```
- **Qué hace**: Permite especificar ID de instancia manualmente
- **Archivos**: `/tmp/batman-[instance-id]/`
- **Usar cuando**: Necesitas control específico del ID

## 📁 Estructura de Archivos por Wrapper

### batman (sin wrapper)
```
/tmp/
├── batman_status.json      # ⚠️ CONFLICTO si múltiples instancias
├── batman_monitor.log      # ⚠️ CONFLICTO
├── batman_monitor.pid      # ⚠️ Solo permite 1 instancia
└── batman-worktrees/       # ⚠️ Posibles colisiones

~/.glados/batman-incorporated/
└── logs/
    └── session_YYYYMMDD_HHMMSS.log  # ✅ Único por timestamp
```

### batman-parallel
```
~/.batman-parallel/
└── [proyecto]/             # Nombre que especificas
    ├── logs/              # Todos los logs del proyecto
    ├── state/             # status.json, monitor.pid
    ├── tmp/               # Archivos temporales
    └── worktrees/         # Git worktrees para SafeMode
```

### batman-isolated
```
/tmp/batman-instances/
└── [timestamp-pid]/        # ID generado automáticamente
    ├── tmp/               # /tmp aislado
    ├── home/              # $HOME aislado (con firejail)
    ├── logs/              # Logs de sesión
    └── work/              # Worktrees
```

### batman-multi
```
/tmp/batman-[instance-id]/  # ID que especificas o aleatorio
├── status.json
├── monitor.log
├── monitor.pid
└── worktrees/
```

## 🔌 Variables de Entorno

Todos los wrappers configuran estas variables:

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `BATMAN_INSTANCE_ID` | ID único de la instancia | `proyecto1`, `1234-5678` |
| `BATMAN_PROJECT` | Nombre del proyecto | `diskdom`, `api`, `frontend` |
| `BATMAN_LOG_DIR` | Directorio de logs | `~/.batman-parallel/api/logs` |
| `BATMAN_TEMP_DIR` | Directorio temporal | `~/.batman-parallel/api/tmp` |
| `BATMAN_STATE_DIR` | Directorio de estado | `~/.batman-parallel/api/state` |
| `BATMAN_WORKTREE_BASE` | Base para git worktrees | `~/.batman-parallel/api/worktrees` |
| `BATMAN_STATUS_FILE` | Archivo de estado JSON | `[STATE_DIR]/status.json` |
| `BATMAN_MONITOR_LOG` | Log del monitor | `[LOG_DIR]/monitor.log` |
| `BATMAN_MONITOR_PID` | PID del monitor | `[STATE_DIR]/monitor.pid` |

## 🚀 Casos de Uso Específicos

### Desarrollo normal (una tarea)
```bash
./batman "implementar feature X"
```

### Múltiples proyectos simultáneos
```bash
# SIEMPRE usa batman-parallel para esto
./batman-parallel proyecto1 "tarea 1"
./batman-parallel proyecto2 "tarea 2"
```

### Testing con aislamiento
```bash
# Para tests que pueden ser destructivos
./batman-isolated "ejecutar tests de integración"
```

### Debugging con ID específico
```bash
# Para reproducir problemas
./batman-multi debug-session-123 "reproducir bug"
```

## ⚠️ Problemas Comunes y Soluciones

### "comando no encontrado"
```bash
# Hacer ejecutables
chmod +x batman*

# O usar python directamente
python3 batman.py "tarea"
```

### "Address already in use" (puerto 8080)
```bash
# El monitor web está activo
# Opción 1: Usar --no-monitor
./batman-parallel proyecto "tarea" --no-monitor

# Opción 2: Matar proceso
pkill -f batman-web
```

### Logs mezclados
- **Problema**: Usaste `./batman` para múltiples instancias
- **Solución**: SIEMPRE usa `batman-parallel` para múltiples proyectos

### "Permission denied" en /tmp
- **Con batman-isolated**: Normal si usa namespaces
- **Solución**: Los archivos están en el directorio de instancia

## 🧹 Limpieza

### Limpiar proyectos antiguos
```bash
# Ver espacio usado
du -sh ~/.batman-parallel/*

# Limpiar proyecto específico
rm -rf ~/.batman-parallel/proyecto-viejo

# Limpiar logs de más de 7 días
find ~/.batman-parallel -name "*.log" -mtime +7 -delete
```

### Limpiar instancias temporales
```bash
# batman-isolated deja directorios en /tmp
rm -rf /tmp/batman-instances/*

# batman-multi también
rm -rf /tmp/batman-*
```

## 🔍 Monitoreo

### Ver todas las instancias activas
```bash
# Procesos batman
ps aux | grep -E "batman.*py" | grep -v grep

# Por proyecto (batman-parallel)
ls ~/.batman-parallel/*/state/monitor.pid 2>/dev/null | \
  while read pid_file; do
    project=$(echo $pid_file | cut -d'/' -f5)
    pid=$(cat $pid_file 2>/dev/null)
    if kill -0 $pid 2>/dev/null; then
      echo "✓ $project (PID: $pid)"
    fi
  done
```

### Logs en tiempo real
```bash
# Un proyecto específico
tail -f ~/.batman-parallel/proyecto/logs/*.log

# Todos los proyectos
tail -f ~/.batman-parallel/*/logs/*.log
```

## 📋 Checklist: ¿Qué Wrapper Usar?

1. ¿Cuántas instancias necesitas?
   - **Una**: `batman`
   - **Múltiples**: `batman-parallel` ✓

2. ¿Necesitas aislamiento de seguridad?
   - **No**: `batman-parallel`
   - **Sí**: `batman-isolated`

3. ¿Necesitas control manual del ID?
   - **No**: `batman-parallel`
   - **Sí**: `batman-multi`

## 🔮 Notas de Implementación

### batman-parallel
- Detecta automáticamente si firejail está instalado
- Fallback a directorios separados si no hay firejail
- Crea estructura completa en `~/.batman-parallel/`

### batman-isolated
- Intenta métodos en orden de más a menos aislamiento
- `cleanup()` automático al salir
- Compatible con usuarios sin sudo

### batman-multi
- Genera ID aleatorio si no se especifica
- Opcional: limpieza al salir (comentada por defecto)
- Más simple, menos features

## ⚡ Tips de Performance

1. **firejail** agrega ~100ms de overhead
2. **Directorios separados** no tienen overhead
3. **unshare** es el más rápido después de directorios
4. **systemd-run** tiene más overhead (~200ms)

Para máxima velocidad: usa `batman-parallel` sin firejail.