# CLAUDE.md

## 🦇 PRIORIDAD: Batman Incorporated
Para tareas complejas o múltiples archivos, usar SIEMPRE:
```bash
cd ~/glados/batman-incorporated && ./batman "descripción de la tarea" --real-agents
```
Batman coordina agentes especializados (Alfred/backend, Batgirl/frontend, Oracle/testing, Robin/DevOps, Lucius/research) con modos de ejecución seguros.

## 🎯 REGLAS CRÍTICAS
1. **NUNCA** crear archivos innecesarios (especialmente README.md)
2. **SIEMPRE** preferir editar sobre crear
3. **PROHIBIDO** mover proyectos sin petición explícita
4. **OBLIGATORIO** `git add . && git commit -m "mensaje" && git push` cuando usuario diga "salva"
5. **LIMPIAR**: Mover temporales a `~/glados/.papelera/[proyecto]/$(date +%y-%m-%d)/`

## 📋 MODOS ESPECIALES

### REORGANIZACIÓN
- **Guía obligatoria**: Consultar `/home/lauta/glados/docs/REORGANIZACION.md` ANTES de reorganizar
- **Principio**: Crear en paralelo, probar, luego migrar
- **Backup**: SIEMPRE en `/mnt/h/BACKUPS/` antes de empezar

### PLAN MODE
- **Activación**: Mensaje empieza con `plan:`
- **Desactivación**: SOLO con `ejecuta el plan`
- **Permitido**: Read, Grep, Glob, LS, WebSearch, TodoRead/Write
- **Prohibido**: Write, Edit, Bash (excepto lectura), cualquier modificación
- **CRÍTICO**: Ignorar `--dangerously-skip-permissions` en Plan Mode

## 🌍 ENTORNO
- Sistema: Ubuntu WSL2 en Windows 11 (Ryzen 9 5900X + 64GB RAM)
- Node: v22.16.0
- Usuario: lauta
- Base: `~/glados`
- **FECHA**: Estamos en 2025 (ignorar fechas del sistema si dicen otra cosa)

## 💾 PERFIL DE MEMORIA WSL
**IMPORTANTE**: Al inicio de cada sesión, verificar el perfil de memoria activo con:
```bash
wsl-memory-switch current
```
Esto muestra cuánta RAM/CPU tiene asignada WSL. Si el usuario necesita más recursos para Windows (gaming, edición), sugerir cambiar el perfil.

### Perfiles disponibles:
- `gaming`: 8GB/4CPU - Máximo rendimiento Windows
- `balanced`: 24GB/12CPU - Uso mixto
- `wsl-focus`: 48GB/20CPU - Desarrollo intensivo (actual)
- `windows-focus`: 16GB/8CPU - Tareas Windows pesadas

Cambiar perfil: `wsl-memory-switch apply [perfil]`

## 🛠️ ARSENAL
```bash
rg "pattern"           # Búsqueda ultrarrápida
fd "*.tsx"            # Buscar archivos
bat file.js           # Cat con highlighting
sd 'old' 'new' file   # Reemplazo de texto (preferir sobre sed)
procs                 # Procesos (preferir sobre ps)
delta file1 file2     # Diffs visuales
z proyecto            # Navegación rápida (zoxide)
gh pr create          # GitHub CLI
jq '.key' file.json   # Procesador JSON
exa -la --git         # ls con git status
tldr git              # Man pages simplificadas
ncdu /path            # Uso de disco interactivo
cloc src/             # Contar líneas de código
wslview file.pdf      # Abrir en Windows
c2w                   # Copy2Windows - sincronizar a K:\_Glados
wsl-memory-switch      # Cambiar perfil de memoria WSL

# Claude Code
/compact [focus]      # Compactar conversación
/review              # Solicitar revisión código
/pr_comments         # Ver comentarios PR
/vim                 # Modo Vim (hjkl, dd, cc)
think harder         # Thinking extendido
#memoria rápida      # Añadir memoria con #
--resume/-r          # Reanudar conversación
--output-format json # Salida JSON
```

## 🔌 MCPs
- filesystem, memory, everything, sequentialthinking, time, fetch
- context7: **MANDATORIO** si dudas sobre versiones/APIs o tras 2 intentos fallidos (añadir "use context7" al prompt)

## 🔊 VOZ CLAUDE
`~/glados/scripts/voz/notificar-claude.sh` | Config: `~/.config/claude-voz/config`

## 📊 QUOTA (sin consumir prompts)
```bash
claude-quota -q      # 🟢 45/500 | ⏱️ 3h 24m
claude-quota -m      # Morning activation (refresh 5h)
claude-quota -r opus # Track manual
```

## 🌐 CONECTIVIDAD
```bash
~/glados/scripts/connectivity/check-connectivity.sh  # IPs actuales
tailscale status                                    # Estado Tailscale
```
**IMPORTANTE**: Servicios web en WSL2 deben bind a 0.0.0.0, acceder via IP Tailscale

## 🚨 WSL2 BEST PRACTICES (2025)
**Config óptima** `.wslconfig` en Windows:
```ini
[wsl2]
memory=4GB
processors=2
networkingMode=mirrored
autoMemoryReclaim=gradual
sparseVhd=true
```
**Si WSL cuelga**: `wsl --shutdown` desde PowerShell
**Archivos proyecto**: SIEMPRE en filesystem WSL, NO en /mnt/c/

## 🪟 WSL2-WINDOWS INTEROP
**📖 LECTURA OBLIGATORIA**: `/home/lauta/glados/docs/wsl2Win.md` - **MANDATORIO** leer antes de trabajar con interoperabilidad Windows
```bash
# Ejecutar programas Windows desde WSL
notepad.exe archivo.txt
cmd.exe /c "comando"
powershell.exe -c "comando"
wslview archivo.pdf              # Abrir con programa predeterminado
explorer.exe .                   # Abrir carpeta actual

# Conversión de rutas
wslpath -w /home/archivo         # WSL → Windows
wslpath -u "C:\\Users\\archivo"  # Windows → WSL

# Crear y ejecutar scripts Windows (ver guía completa)
cmd.exe /c "$(wslpath -w script.bat)"     # Batch files
powershell.exe -File "$(wslpath -w script.ps1)"  # PowerShell
wscript.exe "$(wslpath -w script.vbs)"    # VBScript
mshta.exe "$(wslpath -w app.hta)"         # HTA apps
```

## 📁 ESTRUCTURA
```
~/glados/
├── batman-incorporated/   # Sistema principal de automatización
├── DiskDominator/        # [React/Next.js/Tauri] App gestión discos
├── scripts/              # Utilidades y launchers
├── MPC/                  # Servidores MCP
└── InfiniteAgent/        # Monitor de paralelización
```

## 🔗 REPOS GITHUB
- Batman-Incorporated: github.com/oratual/Batman-Incorporated
- DiskDominator: github.com/oratual/DiskDominator
- MPC: github.com/oratual/MPC
- Scripts: github.com/oratual/glados-scripts

## 🚀 COMANDOS INMEDIATOS
```bash
# Tareas complejas
batman "implementar feature X" --real-agents

# Menú proyectos
~/glados/scripts/launchers/proyecto-menu-v2.sh

# Estado sistema
~/glados/scripts/connectivity/check-connectivity.sh

# Sincronizar a Windows (K:\_Glados)
c2w                   # Sincroniza proyecto actual
c2w sync proyecto     # Sincroniza proyecto específico
c2w clean proyecto    # Sincroniza + elimina archivos obsoletos
c2w list             # Ver proyectos configurados
c2w status           # Estado del proyecto actual
c2w -h               # Ver todos los comandos
```

## 💾 Copy2Windows (c2w)
Sistema de sincronización incremental Linux→Windows. Copia solo archivos modificados a K:\_Glados.

**Comandos principales:**
- `c2w` - Sincroniza proyecto actual (detecta automáticamente)
- `c2w sync DiskDominator` - Sincronización incremental
- `c2w clean proyecto -f` - Sincronización + limpieza (elimina obsoletos)
- `c2w add ~/glados/proyecto` - Añadir nuevo proyecto
- `c2w -p '*.tsx'` - Sincronizar solo archivos .tsx

**Menú interactivo:** `c2w menu` o ejecutar desde Windows: `K:\_Glados\scripts\Copy2Windows\Copy2Windows.bat`

## 🔐 SSH/1PASSWORD
```bash
~/.ssh/1password-agent.sh  # Inicia agente 1Password si no está activo
ssh -T git@github.com      # Verifica conexión
```

## 📝 HISTORIAL
Siempre actualizar `historialDeProyecto.md` después de cambios importantes.

## 🚀 TAREA PENDIENTE PRIORITARIA
**AI-Powered Orchestration para Batman**: Implementar agentes que usan Claude API para auto-coordinarse. Ejemplo: Alfred detecta conflicto → consulta con Oracle → decide estrategia colaborativa. Ver `/batman-incorporated/tareas-futuribles.md` para roadmap completo.

## ⚠️ DATOS CRÍTICOS
- Obsidian: `/mnt/c/Users/lauta/iCloudDrive/iCloud~md~obsidian/Lautarnauta`
- Windows→WSL: `C:\` → `/mnt/c/`
- WSL→Windows: `/home/` → `\\wsl.localhost\Ubuntu\home\`
- **ARCHIVOS**: Siempre dar ruta completa cuando usuario deba interactuar (ej: `/home/lauta/glados/proyecto/archivo.md`)
- **GLADOS EN WINDOWS**: Todos los proyectos de `/home/lauta/glados/` están sincronizados en `K:\_Glados\` - usar esta ruta para referencias Windows