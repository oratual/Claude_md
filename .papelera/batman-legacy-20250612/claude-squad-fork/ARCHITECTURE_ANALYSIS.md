# Análisis de Arquitectura de Claude Squad

## Resumen Ejecutivo

Claude Squad es una aplicación Go que gestiona múltiples sesiones de agentes de IA (Claude, Aider, etc.) usando tmux y git worktrees. La aplicación tiene un modo daemon experimental que permite ejecución automatizada con la funcionalidad AutoYes.

## Componentes Principales

### 1. Gestión de Sesiones (`session/`)

**Características clave:**
- **Instance**: Representa una sesión de trabajo que combina:
  - Sesión tmux (para ejecutar el agente de IA)
  - Git worktree (para aislar cambios en una rama separada)
  - Estado persistente (Running, Ready, Loading, Paused)
  
**Funcionalidades importantes:**
- `Start()`: Crea tmux session + git worktree
- `Pause()`: Guarda el estado, hace commit automático, elimina worktree pero mantiene la rama
- `Resume()`: Recrea el worktree y reinicia la sesión tmux
- `TapEnter()`: Envía Enter a la sesión (usado por AutoYes)
- `SendPrompt()`: Envía texto a la sesión tmux

### 2. Modo Daemon (`daemon/`)

**Características:**
- Ejecuta en segundo plano (`--daemon` flag)
- Monitorea todas las instancias activas
- Si AutoYes está habilitado, automáticamente presiona Enter cuando detecta prompts
- Polling configurable (default: 1000ms)
- Se detiene con SIGINT/SIGTERM
- Guarda PID en `~/.claude-squad/daemon.pid`

**Limitaciones actuales:**
- Solo responde con Enter a prompts
- No puede procesar contenido de prompts
- No tiene lógica de decisión inteligente
- Requiere que las instancias ya estén creadas

### 3. Almacenamiento y Persistencia (`session/storage.go`, `config/`)

**Estado persistente:**
- Instancias guardadas en JSON en `~/.claude-squad/`
- Incluye: título, path, rama, estado, programa, dimensiones, timestamps
- Git worktree data (repo path, branch, commit SHA)
- Diff stats (cambios agregados/eliminados)

**Configuración (`config.json`):**
```json
{
  "default_program": "claude",
  "auto_yes": false,
  "daemon_poll_interval": 1000,
  "branch_prefix": "username/"
}
```

### 4. Integración con tmux (`session/tmux/`)

**Capacidades:**
- Crear/destruir sesiones tmux
- Capturar contenido del panel
- Enviar keystrokes
- Detectar cambios en el contenido
- Resize dinámico
- Attach/detach de sesiones

### 5. Integración con Git (`session/git/`)

**Funcionalidades:**
- Crear/eliminar git worktrees
- Gestión automática de ramas
- Commits automáticos al pausar
- Tracking de cambios (diff stats)
- Verificación de branch checkout

## Puntos Clave para Modificación

### 1. **Ejecutar Comandos Programados**
- El daemon ya existe pero es básico
- Necesitaríamos agregar:
  - Scheduler para tareas programadas
  - Parser de comandos/instrucciones
  - Lógica de decisión más compleja que solo "Enter"

### 2. **Ejecución Sin Supervisión**
- AutoYes mode ya existe pero es limitado
- Para mejorar:
  - Añadir lógica condicional (if X then Y)
  - Integrar con un sistema de tareas/misiones
  - Añadir timeouts y manejo de errores

### 3. **Mecanismos de Persistencia**
- Ya tiene buen soporte de persistencia
- Se podría extender para:
  - Guardar logs de sesiones
  - Historial de comandos
  - Estado de tareas/misiones

### 4. **Integración con Batman**

**Opción A: Fork y Modificar**
- Añadir endpoint HTTP/gRPC al daemon
- Permitir creación de instancias via API
- Añadir comandos personalizados además de Enter
- Integrar sistema de tareas de Batman

**Opción B: Wrapper/Bridge**
- Mantener Claude Squad sin modificar
- Crear un puente que:
  - Use la CLI de Claude Squad
  - Parse outputs capturando tmux panes
  - Envíe comandos según lógica de Batman

**Opción C: Inspiración Solo**
- Usar conceptos de Claude Squad:
  - tmux para gestión de sesiones
  - git worktrees para aislamiento
  - JSON para persistencia
- Implementar en Python para Batman

## Modificaciones Necesarias para Batman

### 1. **API de Control Remoto**
```go
// Nuevo endpoint en daemon/daemon.go
func (d *Daemon) HandleCommand(instanceName string, command Command) error {
    instance := d.findInstance(instanceName)
    switch command.Type {
    case "prompt":
        return instance.SendPrompt(command.Text)
    case "pause":
        return instance.Pause()
    case "resume":
        return instance.Resume()
    }
}
```

### 2. **Sistema de Tareas**
```go
// Nueva estructura para tareas
type Task struct {
    ID          string
    InstanceID  string
    Commands    []Command
    Schedule    string // cron format
    Status      TaskStatus
}
```

### 3. **Lógica de Decisión**
```go
// Extender el monitor de sesiones
func (m *statusMonitor) analyzeContent(content string) Action {
    // Analizar el contenido y decidir acción
    if strings.Contains(content, "error") {
        return Action{Type: "pause", Reason: "error detected"}
    }
    // ... más lógica
}
```

## Conclusiones

Claude Squad proporciona una base sólida con:
- ✅ Gestión de sesiones tmux
- ✅ Aislamiento con git worktrees
- ✅ Persistencia de estado
- ✅ Modo daemon básico
- ✅ AutoYes mode

Para Batman necesitaríamos añadir:
- 🔧 API de control programático
- 🔧 Sistema de tareas/misiones
- 🔧 Lógica de decisión inteligente
- 🔧 Integración con scheduler (cron-like)
- 🔧 Mejor manejo de errores y timeouts

La arquitectura es extensible y bien estructurada, facilitando las modificaciones necesarias.