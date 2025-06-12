# Workflow de Desarrollo con Batman Incorporated

## 🚀 Inicio Rápido

### 1. Instalación Básica
```bash
cd ~/glados/batman-incorporated
./setup.sh
batman --install-tools  # Instala herramientas sin sudo
```

### 2. Primer Proyecto
```bash
# Tarea simple
batman "crear función hello world en Python"

# Tarea compleja con modo específico
batman "implementar API REST completa" --mode=infinity --real-agents
```

## 🛠️ Arsenal de Herramientas

Batman Incorporated detecta y usa automáticamente las mejores herramientas disponibles:

### Búsqueda y Navegación
| Herramienta | Comando | Ventaja |
|-------------|---------|---------|
| **ripgrep** | `rg "pattern"` | 10x más rápido que grep |
| **fd** | `fd "*.py"` | Búsqueda moderna de archivos |
| **fzf** | `find . \| fzf` | Búsqueda fuzzy interactiva |
| **zoxide** | `z proyecto` | Navegación inteligente |

### Visualización y Edición
| Herramienta | Comando | Ventaja |
|-------------|---------|---------|
| **bat** | `bat file.py` | Cat con sintaxis highlighting |
| **exa** | `exa -la --git` | ls mejorado con git status |
| **delta** | `git diff \| delta` | Diffs hermosos |
| **sd** | `sd 'old' 'new' file` | Reemplazo seguro de texto |

### Análisis y Monitoreo
| Herramienta | Comando | Ventaja |
|-------------|---------|---------|
| **procs** | `procs --tree` | Visualizador de procesos moderno |
| **htop** | `htop` | Monitor interactivo del sistema |
| **ncdu** | `ncdu /` | Análisis de disco interactivo |
| **cloc** | `cloc src/` | Contador de líneas de código |

### Desarrollo y Git
| Herramienta | Comando | Ventaja |
|-------------|---------|---------|
| **gh** | `gh pr create` | GitHub CLI integrado |
| **jq** | `cat data.json \| jq '.'` | Procesador JSON |
| **tldr** | `tldr git` | Man pages simplificadas |
| **httpie** | `http GET api.com` | Cliente HTTP amigable |

## 🎮 Modos de Ejecución

### 1. Modo Rápido (Prototipos)
```bash
batman "añadir endpoint GET /users" --mode=rapido
```
- Desarrollo directo
- Sin branches
- Ideal para cambios pequeños

### 2. Modo Seguro (Producción)
```bash
batman "refactorizar sistema de autenticación" --mode=seguro
```
- Git worktrees aislados
- Merge controlado
- Para cambios complejos

### 3. Modo Infinity (Paralelismo Real) 🌟
```bash
batman "desarrollar app completa con frontend React y backend Node" --mode=infinity
```

**Workflow Infinity Mode:**
1. Batman genera instrucciones para cada agente
2. Abre 5 terminales (una por agente)
3. En cada terminal: `claude` y sigue instrucciones
4. Los agentes comparten contexto via:
   - `#memoria` - Knowledge graph compartido
   - Archivos en `~/.batman/infinity/`
   - TodoRead/TodoWrite

**Ejemplo de coordinación:**
```bash
# Terminal 1 - Alfred (Backend)
#memoria API endpoint /users implementado en puerto 3000

# Terminal 2 - Batgirl (Frontend) 
# Ve inmediatamente el mensaje y puede conectarse
```

### 4. Modo Redundante (Código Crítico)
```bash
batman "implementar sistema de pagos" --mode=redundante
```
- Múltiples implementaciones
- Comparación de enfoques
- Para features críticas

## 📊 Monitoreo y Cuota

### Monitor de Cuota Claude
```bash
# Ver estado completo
claude-quota

# Vista rápida
claude-quota -q  # 🟢 45/500 | ⏱️ 3h 24m

# Activación matutina (estrategia 5h)
claude-quota -m
```

### Monitor de Sistema
```bash
# Ver estado de Batman
batman --status

# Monitorear progreso en tiempo real
watch -n 2 batman --status

# Ver logs narrativos
tail -f ~/.glados/batman-incorporated/logs/latest.log
```

## 🔄 Workflows Completos

### Desarrollo Full-Stack
```bash
# 1. Iniciar con Infinity Mode
batman "crear aplicación de tareas con React y Express" --mode=infinity --real-agents

# 2. Abrir terminales:
# Terminal 1: Alfred - Backend API
# Terminal 2: Batgirl - Frontend React  
# Terminal 3: Robin - Docker y CI/CD
# Terminal 4: Oracle - Tests E2E
# Terminal 5: Lucius - Documentación

# 3. Monitorear progreso
batman --status
```

### Refactoring Masivo
```bash
# 1. Análisis inicial
batman "analizar código para refactoring" --mode=rapido

# 2. Ejecutar refactoring
batman "refactorizar módulo de usuarios" --mode=seguro --real-agents

# 3. Verificar cambios
git diff main..refactor-usuarios
```

### Bug Hunt Colaborativo
```bash
# 1. Modo Infinity para búsqueda paralela
batman "encontrar y arreglar bug de memoria" --mode=infinity

# Agentes trabajando en paralelo:
# - Oracle: Análisis de logs
# - Alfred: Debugging del código
# - Robin: Profiling de memoria
# - Comparten pistas via #memoria
```

## 🏗️ Integración con GitHub

### PRs Automáticos
```bash
# Batman crea PRs automáticamente
batman "implementar feature X" --real-agents

# El PR incluirá:
# - Descripción detallada
# - Lista de cambios
# - Labels apropiados
```

### Issues Automáticos
```bash
# Si encuentra errores, Batman crea issues
# Con toda la información de debugging
```

## 💡 Tips Avanzados

### 1. Combinar Herramientas
```bash
# Búsqueda inteligente
fd "*.py" | xargs rg "TODO" | fzf

# Análisis de código
cloc src/ | jq '.Python'

# Refactoring masivo
fd "*.js" -x sd 'console.log' 'logger.debug'
```

### 2. Aliases Útiles
```bash
# Añadir a ~/.bashrc
alias bs='batman --status'
alias bq='batman --mode=rapido'
alias bi='batman --mode=infinity --real-agents'
```

### 3. Integración con VSCode
```bash
# Abrir proyecto con cambios
code $(git diff --name-only)

# Ver resultados de Batman
code ~/.glados/batman-incorporated/reports/latest.md
```

## 🚨 Troubleshooting

### "No encuentra las herramientas"
```bash
batman --install-tools  # Instala todo sin sudo
check-tools            # Verifica qué está instalado
```

### "Los agentes no se coordinan"
```bash
# Verificar archivos compartidos
ls ~/.batman/infinity/context/
cat ~/.batman/infinity/status/*.json
```

### "Se acabó la cuota de Claude"
```bash
claude-quota -q  # Ver tiempo hasta refresh
# Esperar o cambiar a modo simulado (sin --real-agents)
```

## 🎯 Mejores Prácticas

1. **Empieza Simple**: Usa modo rápido para prototipos
2. **Escala Gradualmente**: Pasa a seguro cuando funcione
3. **Paraleliza Cuando Sea Grande**: Infinity para proyectos complejos
4. **Monitorea Siempre**: `batman --status` es tu amigo
5. **Confía en el Arsenal**: Las herramientas están optimizadas

## 🔮 Comandos Esenciales

```bash
# Los 10 comandos que más usarás
batman "tarea"                    # Ejecución básica
batman "tarea" --mode=infinity    # Paralelismo real
batman --status                   # Ver progreso
batman --install-tools            # Instalar arsenal
claude-quota -q                   # Check de cuota
rg "pattern"                      # Búsqueda rápida
fd "*.py"                         # Encontrar archivos
bat file.py                       # Ver con colores
gh pr create                      # Crear PR
z proyecto                        # Navegar rápido
```

---

*"Con gran poder viene gran responsabilidad... y grandes herramientas"* 🦇

**Batman Incorporated** - Automatización inteligente con el mejor arsenal disponible.