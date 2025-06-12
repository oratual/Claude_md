# Plan de Integración Claude Squad + Batman

## Análisis de Viabilidad

### Fortalezas de Claude Squad para Batman:
1. **Gestión robusta de sesiones tmux** - Ya maneja crear, pausar, reanudar sesiones
2. **Aislamiento con git worktrees** - Perfecto para experimentos nocturnos sin afectar main
3. **Modo daemon con AutoYes** - Base para automatización sin supervisión
4. **Persistencia de estado** - Las sesiones sobreviven reinicios

### Limitaciones Actuales:
1. **Solo responde "Enter"** - No puede tomar decisiones complejas
2. **Sin programación temporal** - No tiene scheduler integrado
3. **Sin API programática** - Solo interfaz TUI interactiva
4. **Hardcodeado para Claude/Aider** - Asume ciertos prompts específicos

## Estrategias de Integración

### Opción 1: Modificación Directa (Go) ⭐ RECOMENDADA
**Ventajas:**
- Máximo control y rendimiento
- Integración profunda con el código existente
- Un solo binario para todo

**Implementación:**
1. Añadir módulo `batman` en Go
2. Extender el daemon con scheduler
3. Añadir API HTTP/gRPC
4. Implementar lógica de tareas

### Opción 2: Bridge Python-Go
**Ventajas:**
- Mantiene Batman en Python
- No requiere tocar código Go
- Más fácil de implementar

**Implementación:**
1. Claude Squad daemon corriendo
2. Batman se comunica via:
   - Comandos tmux directos
   - Parseo de archivos de estado JSON
   - Subprocess para comandos CLI

### Opción 3: Reimplementación en Python
**Ventajas:**
- Consistencia con Batman existente
- Más fácil de mantener
- Mejor integración con el ecosistema Python

**Desventajas:**
- Duplicar trabajo ya hecho
- Posibles bugs al reimplementar

## Plan de Implementación Detallado (Opción 1)

### Fase 1: API de Control (1-2 días)
```go
// batman/api.go
package batman

type BatmanAPI struct {
    daemon *daemon.Daemon
    tasks  *TaskManager
}

func (b *BatmanAPI) CreateTask(req CreateTaskRequest) (*Task, error) {
    // Crear nueva tarea programada
}

func (b *BatmanAPI) ExecuteCommand(instanceID string, command string) error {
    // Ejecutar comando en instancia específica
}
```

### Fase 2: Sistema de Tareas (2-3 días)
```go
// batman/tasks.go
type Task struct {
    ID           string
    Name         string
    Schedule     string // cron format
    InstanceName string
    Steps        []Step
    Status       TaskStatus
}

type Step struct {
    Type    string // "prompt", "wait", "check", "branch"
    Content string
    Condition *Condition
}
```

### Fase 3: Scheduler Integrado (1 día)
```go
// batman/scheduler.go
func (s *Scheduler) Start() {
    ticker := time.NewTicker(1 * time.Minute)
    for range ticker.C {
        tasks := s.GetPendingTasks()
        for _, task := range tasks {
            if s.ShouldRun(task) {
                go s.ExecuteTask(task)
            }
        }
    }
}
```

### Fase 4: Lógica de Decisión (2-3 días)
```go
// batman/decisions.go
type DecisionEngine struct {
    rules []Rule
}

func (d *DecisionEngine) Analyze(content string) Action {
    // Analizar contenido y decidir siguiente acción
    for _, rule := range d.rules {
        if rule.Matches(content) {
            return rule.Action
        }
    }
    return DefaultAction
}
```

### Fase 5: Integración con Batman Python (1 día)
```python
# batman/claude_squad_client.py
class ClaudeSquadClient:
    def __init__(self, api_url="http://localhost:8080"):
        self.api_url = api_url
    
    def create_task(self, task_config):
        return requests.post(f"{self.api_url}/tasks", json=task_config)
    
    def get_instance_output(self, instance_id):
        return requests.get(f"{self.api_url}/instances/{instance_id}/output")
```

## Arquitectura Propuesta

```
┌─────────────────┐     ┌──────────────────┐
│   Batman.py     │────▶│ Claude Squad API │
│  (Orchestrator) │     │   (Go HTTP/gRPC) │
└─────────────────┘     └──────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
            ┌───────▼────────┐     ┌───────▼────────┐
            │ Task Scheduler │     │ Decision Engine│
            │   (Go/Cron)    │     │      (Go)      │
            └───────┬────────┘     └───────┬────────┘
                    │                       │
                    └───────────┬───────────┘
                                │
                        ┌───────▼────────┐
                        │ Session Manager│
                        │  (tmux + git)  │
                        └────────────────┘
```

## Ejemplo de Flujo de Trabajo

### 1. Batman crea tarea nocturna:
```python
task = {
    "name": "optimize-code-base",
    "schedule": "0 2 * * *",  # 2 AM
    "instance": "optimization-bot",
    "steps": [
        {"type": "prompt", "content": "Review and optimize all Python files"},
        {"type": "wait", "condition": "output_contains('Analysis complete')"},
        {"type": "branch", "condition": "has_suggestions", 
         "true": [
             {"type": "prompt", "content": "Apply all safe optimizations"},
             {"type": "commit", "message": "Automated optimizations"}
         ],
         "false": [
             {"type": "log", "content": "No optimizations needed"}
         ]}
    ]
}
```

### 2. Claude Squad ejecuta:
- Crea/reanuda instancia tmux
- Ejecuta pasos secuencialmente
- Aplica lógica condicional
- Guarda resultados
- Pausa/commit al finalizar

## Timeline Estimado

- **Semana 1**: Fases 1-2 (API + Sistema de Tareas)
- **Semana 2**: Fases 3-4 (Scheduler + Decisiones)
- **Semana 3**: Fase 5 + Testing + Documentación

## Próximos Pasos Inmediatos

1. **Crear branch de desarrollo**:
   ```bash
   cd /home/lauta/glados/batman/claude-squad-fork
   git init
   git add .
   git commit -m "Initial fork of Claude Squad for Batman integration"
   ```

2. **Estructura inicial**:
   ```bash
   mkdir -p batman/{api,tasks,scheduler,decisions}
   ```

3. **Primer prototipo**:
   - Implementar API HTTP básica
   - Añadir endpoint para enviar prompts
   - Probar integración con Batman Python

## Alternativa Rápida (Para Probar)

Si queremos algo funcionando rápidamente:

1. Usar Claude Squad como está
2. Batman controla via comandos shell:
   ```bash
   # Crear instancia
   cs new --title "batman-task-1" --program "claude"
   
   # Enviar comando via tmux
   tmux send-keys -t claudesquad_batman-task-1 "optimize this code" Enter
   
   # Capturar output
   tmux capture-pane -t claudesquad_batman-task-1 -p
   ```

Esto permite probar el concepto antes de comprometerse con modificaciones profundas.