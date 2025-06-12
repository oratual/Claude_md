# CLAUDE.md - Batman Incorporated

Este archivo proporciona contexto para Claude Code al trabajar en Batman Incorporated.

## 🦇 Visión General

Batman Incorporated es el sistema unificado de automatización. Los usuarios solo interactúan con Batman, quien coordina un equipo de agentes especializados.

## 🏗️ Arquitectura

```
Usuario → Batman → Agentes (Alfred, Robin, Oracle, Batgirl, Lucius)
                 ↓
           Modos de Ejecución (Seguro/On-the-go/Redundante)
                 ↓
              Arsenal de Herramientas
```

## 👥 Los Agentes

Cada agente es una instancia de Claude con prompt especializado:

- **🧙 Alfred**: Senior Developer - APIs, backend, arquitectura
- **🐦 Robin**: DevOps & Junior Dev - Automatización, CI/CD, scripts
- **👁️ Oracle**: QA & Security - Testing, vulnerabilidades, calidad
- **🦹‍♀️ Batgirl**: Frontend Specialist - UI/UX, componentes, accesibilidad
- **🦊 Lucius**: Research & Innovation - Nuevas tecnologías, optimización

## 🛠️ Tecnología

- **Claude CLI**: Usamos `claude --print --dangerously-skip-permissions` para ejecución sin interrupciones
- **NO API**: Trabajamos con Claude Code (suscripción), no con API de pago por uso
- **Logging Narrativo**: Sistema de capítulos para seguimiento claro
- **Configuración YAML**: Flexible y extensible
- **Cuota**: Max 20x ~500 prompts/5h. Si falla, usar `claude-quota -q`

## 🆕 Claude Code Features (útiles para agentes)
- `think harder` - Para tareas complejas en agentes
- `--output-format json` - Respuestas estructuradas de agentes
- `/compact` - Si prompt muy largo (>100k tokens)
- Git worktrees - Ya usado en Safe Mode
- CLAUDE.md imports - `@path/to/context` para contexto adicional

## 📁 Estructura

```
batman-incorporated/
├── batman.py              # Punto de entrada único
├── src/
│   ├── core/             # Sistema principal
│   ├── agents/           # Implementación de agentes
│   └── features/         # Características (logging, reporting)
├── config/               # Configuración YAML
└── setup.sh             # Instalación
```

## 🚀 Comandos

```bash
# Básico (simulado)
batman "tarea a realizar"

# Con agentes reales
batman "tarea a realizar" --real-agents

# Ver estado
batman --status

# Modo automático
batman --auto

# Monitor de agentes (SEGURO - no interfiere con Claude)
./monitor start          # Inicia monitor en background
./monitor status         # Status compacto
./monitor view           # Status detallado
./monitor watch          # Modo watch interactivo
./monitor stop           # Detiene monitor
```

## 🎯 Reglas de Desarrollo

1. **Un solo Batman**: No crear múltiples versiones
2. **Agentes especializados**: Cada uno con su área de expertise
3. **Claude CLI siempre**: Usar `--dangerously-skip-permissions`
4. **Logging claro**: Capítulos narrativos para seguir el progreso
5. **Git disciplinado**: Commits descriptivos, push frecuente

## 🔄 Estado Actual

- ✅ Estructura base completa
- ✅ 5 agentes implementados con Claude CLI
- ✅ Sistema de tareas unificado
- ✅ 3 modos de ejecución (Safe, Fast, Redundant)
- ✅ Instalador de herramientas sin sudo
- ✅ Monitor seguro que NO interfiere con Claude console
- ⏳ Paralelización (Infinity Mode) pendiente

## 🔧 Monitor Sistema

**PROBLEMA RESUELTO**: El monitor anterior causaba corrupción en la consola de Claude con secuencias de escape (como `38M<32;167;38M`).

**SOLUCIÓN**: Nuevo sistema de monitor seguro:
- `batman-monitor-safe`: Monitor que escribe solo a archivos, nunca a stdout
- `batman-view`: Visor que lee archivos sin interferir con terminal
- `./monitor`: Controlador simple para iniciar/parar/ver status

**Uso seguro**:
```bash
./monitor start    # Inicia en background - NO interfiere con Claude
./monitor status   # Ve status rápido
./monitor view     # Ve detalles completos
```

## 🌐 GitHub

Repository: https://github.com/oratual/Batman-Incorporated

---

*"I am vengeance. I am the night. I am Batman Incorporated!"* 🦇