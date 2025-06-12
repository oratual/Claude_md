# Guía de Contexto Compartido - Batman Incorporated

## 🌟 Revolución: Múltiples Instancias Trabajando Juntas

Batman Incorporated ahora soporta múltiples instancias de Claude Code trabajando en paralelo, compartiendo contexto en tiempo real.

## 🔄 Métodos de Compartir Contexto

### 1. MCP Memory (Recomendado)
```bash
# Instancia Alfred
#memoria Encontré bug crítico en auth.js línea 45

# Instancia Oracle (ve inmediatamente)
# El conocimiento se comparte via knowledge graph
```

### 2. TodoRead/TodoWrite
```bash
# Batman asigna
TodoWrite: "Alfred: Implementar API REST"
TodoWrite: "Robin: Configurar CI/CD"

# Cada agente ve sus tareas actualizadas
```

### 3. Archivos Compartidos
```bash
# Alfred escribe
echo "Bug encontrado: null pointer en auth" > ~/.batman/shared/discoveries.txt

# Oracle lee
cat ~/.batman/shared/discoveries.txt
```

### 4. Archivos de Sesión JSONL
- Ubicación: `~/.claude/projects/[project]/[session].jsonl`
- Contiene toda la conversación
- Útil para análisis posterior

## 🚀 Workflow Infinity Mode

### Paso 1: Lanzar Batman en Infinity Mode
```bash
batman "implementar sistema completo de usuarios" --mode=infinity
```

### Paso 2: Abrir Terminales para Agentes
Batman mostrará instrucciones como:
```
Terminal 1 - Alfred:
  claude  # Luego: cat ~/.batman/infinity/context/agent_alfred_abc123.md

Terminal 2 - Robin:
  claude  # Luego: cat ~/.batman/infinity/context/agent_robin_def456.md
```

### Paso 3: Coordinación Automática
- Cada agente lee sus instrucciones
- Comparten descubrimientos via #memoria
- Actualizan progreso en archivos compartidos
- Batman monitorea todo

## 💡 Mejores Prácticas

### Para Compartir Descubrimientos
```bash
# BUENO: Específico y accionable
#memoria API endpoint /users necesita validación de email

# MALO: Muy general
#memoria hay un problema
```

### Para Actualizar Estado
```bash
# Alfred actualiza su estado
echo '{"agent": "alfred", "status": "working", "task": "API REST"}' > ~/.batman/status/alfred.json
```

### Para Resultados
```bash
# Guardar resultados estructurados
echo '{"task": "API REST", "completed": true, "files": ["api.js"]}' > ~/.batman/results/alfred/task1.json
```

## 🔍 Monitoreo

### Ver progreso en tiempo real
```bash
# En otra terminal
watch -n 2 batman --status

# O manualmente
cat ~/.batman/infinity/status/session_*.json | jq
```

### Ver memoria compartida
```bash
# Si tienes acceso al MCP memory
claude "muestra la memoria compartida del proyecto"
```

## 🎯 Casos de Uso Perfectos

### 1. Desarrollo Full-Stack
- Alfred: Backend API
- Batgirl: Frontend React
- Robin: Docker y deployment
- Oracle: Tests e2e

### 2. Refactoring Masivo
- Múltiples agentes trabajando en diferentes módulos
- Compartiendo patrones encontrados
- Evitando conflictos via worktrees

### 3. Bug Hunt
- Oracle: Análisis de logs
- Alfred: Debugging código
- Robin: Reproduciendo el bug
- Compartiendo pistas via #memoria

## ⚠️ Limitaciones

1. **Requiere múltiples ventanas/terminales**
2. **Cada instancia consume cuota**
3. **Coordinación manual al inicio**

## 🚨 Troubleshooting

### "No veo los cambios de otros agentes"
- Verifica que estés leyendo los archivos correctos
- Usa `#memoria` para compartir descubrimientos importantes
- Refresca con `cat` el archivo compartido

### "Los agentes chocan en el mismo archivo"
- Usa modo Seguro (Safe) con worktrees
- Asigna archivos específicos a cada agente
- Coordina via TodoWrite

## 🔮 Futuro

- Integración automática con sesiones JSONL
- UI web para monitorear agentes
- Auto-balanceo de tareas
- Learning de patrones de colaboración

---

*"Juntos somos más fuertes" - Batman Incorporated* 🦇