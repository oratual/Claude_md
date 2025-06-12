# Claude Quota Monitor

Sistema de monitoreo local de cuota para Claude Code. **NO consume cuota** - todo es cálculo local.

## 🎯 Propósito

Monitorea el uso de Claude Code sin gastar prompts adicionales:
- Cuenta prompts usados (Opus vs Sonnet)
- Calcula tiempo exacto hasta refresh (5 horas)
- Sugiere estrategias de activación matutina
- Alerta cuando se acerca el límite

## 📊 Comandos

```bash
# Ver estado completo con gráficos
claude-quota

# Vista rápida de una línea
claude-quota -q
# Ejemplo salida: 🟢 45/500 | ⏱️ 3h 24m 15s

# Registrar prompt manualmente
claude-quota -r opus    # Registra uso de Opus
claude-quota -r sonnet  # Registra uso de Sonnet

# Activación matutina (coffee strategy)
claude-quota -m         # Marca inicio temprano para refresh en horario laboral

# Reset manual (emergencias)
claude-quota --reset

# Ver ayuda
claude-quota --help
```

## 🕐 Estrategia Matutina

El sistema detecta si conviene activar Claude temprano:
- Activar a las 4 AM = refresh a las 9 AM (inicio laboral)
- Activar a las 7 AM = refresh a las 12 PM (después del almuerzo)

```bash
# Marca tu "café matutino" con Claude
claude-quota -m
```

## 📈 Límites Plan Max 20x ($200/mes)

- **Conservador**: 200 prompts (tareas complejas)
- **Promedio**: 500 prompts (uso normal)
- **Optimista**: 800 prompts (consultas simples)

Opus consume cuota **5x más rápido** que Sonnet.

## 🔔 Alertas Automáticas

El monitor alerta cuando:
- Uso > 80% del límite estimado
- Quedan < 30 minutos para refresh
- Detecta cambio Opus → Sonnet
- Velocidad > 100 prompts/hora

## 📁 Archivos

- Config: `~/.config/claude-code/quota_tracking.json`
- Historia: `~/.config/claude-code/quota_history.json`

## 🤖 Integración con Batman Incorporated

Batman puede usar el monitor automáticamente:
```python
# En BaseAgent
from scripts.quota.claude_quota_monitor import ClaudeQuotaMonitor

monitor = ClaudeQuotaMonitor()
monitor.record_prompt('opus')
alerts = monitor.should_alert()
```

## 💡 Tips

1. **Morning Coffee**: Usa `-m` para marcar activaciones tempranas
2. **Quick Check**: `-q` para revisar rápido sin interrumpir flujo
3. **No Auto-track**: El monitor NO intercepta Claude automáticamente (por ahora)

## 🚀 Ejemplo de Uso Típico

```bash
# Al empezar el día (7 AM)
claude-quota -m
# ☕ Activación matutina registrada
#    Refresh a las 12:00
#    ⚠️ Refresh durante horario laboral

# Durante el trabajo
claude-quota -q
# 🟢 45/500 | ⏱️ 3h 24m 15s

# Si ves muchos errores
claude-quota
# [Ver estado completo con análisis]
```

---

**Recuerda**: Este monitor es 100% local y NO consume ningún prompt de tu cuota.