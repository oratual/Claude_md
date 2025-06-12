# SECURITY_AND_TOOLS.md - Seguridad y Herramientas Avanzadas

Este documento contiene información detallada sobre seguridad (1Password) y herramientas avanzadas disponibles.

## 🔐 1Password SSH Integration - Detalles Completos

### Arquitectura
El sistema crea un bridge entre:
- **Windows**: 1Password app con SSH agent
- **WSL2**: Ubuntu necesitando acceso SSH
- **Bridge**: npiperelay.exe + socat creando Unix socket en `~/.ssh/agent.sock`

### Scripts Específicos

#### 1Password Environment Setup
```bash
# Ubicación exacta
source ~/1p_env_setup.sh
```
Este script:
- Configura SSH agent para usar socket de 1Password
- Exporta variables necesarias incluyendo `CLAUDE_API_KEY`

#### SSH Agent Setup
```bash
# Ubicación exacta
~/fix-1p-agent.sh
```

Después de ejecutar, agregar a `~/.bashrc`:
```bash
export SSH_AUTH_SOCK="$HOME/.ssh/agent.sock"
if [ ! -S "$SSH_AUTH_SOCK" ]; then
    rm -f "$SSH_AUTH_SOCK"
    (setsid nohup socat UNIX-LISTEN:$SSH_AUTH_SOCK,fork EXEC:"$HOME/.local/bin/npiperelay.exe -ei -s //./pipe/openssh-ssh-agent" >/dev/null 2>&1 &)
fi
```

#### Diagnósticos
```bash
~/1p_diag.sh
```

### Configuración Git
En `~/.gitconfig` está configurado SSH signing con `op-ssh-sign-wsl`

### Requisitos
- 1Password en Windows con SSH Agent habilitado
- `socat` instalado: `sudo apt-get install socat`
- `npiperelay.exe` en `~/.local/bin/`
- 1Password CLI (`op`) para features avanzadas

## 🛠️ Herramientas Avanzadas Completas

### Lista Completa de Herramientas

| Herramienta | Comando | Función | Cuándo Usar |
|-------------|---------|---------|-------------|
| **ripgrep** | `rg` | Búsqueda ultrarrápida con regex | Siempre para búsqueda de texto |
| **fd** | `fd` o `fdfind` | Búsqueda moderna de archivos | En lugar de `find` |
| **bat** | `bat` o `batcat` | Cat con syntax highlighting | Para ver archivos con color |
| **jq** | `jq` | Procesador JSON avanzado | Para manipular JSON |
| **exa** | `exa` | ls mejorado con git status | Para listar archivos con más info |
| **httpie** | `http` | Cliente HTTP amigable | Para testing de APIs |
| **fzf** | `fzf` | Búsqueda fuzzy interactiva | Para selección interactiva |
| **sd** | `sd` | Reemplazo de texto (mejor que sed) | Para refactoring masivo |
| **procs** | `procs` | Visualizador de procesos mejorado | En lugar de `ps` |
| **delta** | `delta` | Diffs mejorados | Para comparar archivos |
| **zoxide** | `z` | Navegación rápida | Para cambiar entre directorios frecuentes |

### WSL Utilities
- `wslview` - Abrir archivos en Windows
- `wslfetch` - Info del sistema
- `wsl-open` - Abrir URLs/archivos

### Documentación Completa
```bash
cat ~/claude-tools/docs/COMMANDS.md
```

## 📋 Instrucciones de Uso Proactivo para Claude

### Debes usar automáticamente:

1. **sd** en lugar de sed:
   ```bash
   # Cambiar todas las URLs de http a https
   sd 'http://' 'https://' **/*.{js,html,css}
   ```

2. **procs** cuando pidan ver procesos:
   ```bash
   procs --sortd cpu    # Por CPU
   procs --tree         # Árbol de procesos
   procs nginx          # Proceso específico
   ```

3. **delta** para diferencias:
   ```bash
   delta file1 file2
   ```

4. **zoxide** para navegación:
   ```bash
   z proyecto    # Salta a ~/alguna/ruta/proyecto si ya lo visitaste
   ```

### Ejemplos de Uso Avanzado

#### Búsqueda Compleja
```bash
# Buscar TODOs en archivos TypeScript, excluyendo node_modules
rg "TODO" --type ts -g '!node_modules'

# Buscar archivos modificados en las últimas 24h
fd --changed-within 24h

# Buscar y reemplazar con confirmación
sd -i 's/oldFunction/newFunction/g' src/**/*.js
```

#### Procesamiento JSON
```bash
# Extraer valores específicos
curl api.example.com/data | jq '.users[] | {name, email}'

# Pretty print con bat
curl api.example.com/data | jq . | bat -l json
```

#### Análisis de Sistema
```bash
# Ver qué proceso usa más memoria
procs --sortd mem | head -10

# Árbol de procesos de Node
procs --tree node
```

## 🌐 Tailscale - Comandos Específicos

```bash
# Ver estado detallado
tailscale-status

# Conectar a la red
tailscale-connect

# Diagnosticar problemas
tailscale-troubleshoot

# Instalación si no está configurado
~/glados/setups/automator/07-connectivity/install.sh
```

## 🖥️ Aplicaciones GUI Linux (WSLg)

### Estado
- XFCE4 instalado y funcional
- WSLg activo (verificado por /mnt/wslg/)
- Solo aplicaciones individuales, no escritorio completo

### Lanzar desde Windows
**Archivo**: `Linux-Apps-Final.bat` en escritorio Windows
- Comando base: `wsl -- bash -c "DISPLAY=:0 aplicacion &"`

### Aplicaciones Disponibles
- `xfce4-terminal` - Terminal
- `thunar` - Gestor de archivos
- `firefox` - Navegador
- `mousepad` - Editor
- `xfce4-panel` - Panel
- `xfce4-settings-manager` - Configuración
- `xfce4-taskmanager` - Monitor sistema

## 🎯 Mejores Prácticas de Herramientas

1. **Búsqueda**: Siempre `rg` > `grep`, `fd` > `find`
2. **Visualización**: `bat` > `cat` para archivos de código
3. **JSON**: Siempre usar `jq` para procesamiento
4. **HTTP**: `httpie` para testing manual de APIs
5. **Reemplazos**: `sd` para cambios masivos en código
6. **Procesos**: `procs` da información más clara que `ps`
7. **Navegación**: Usar `z` después de visitar directorios

## 📝 Notas Técnicas

- Las herramientas están instaladas via `apt` y scripts en `~/glados/setups/automator/02-toolkit/`
- Los wrappers (`search`, `find-files`, `view`) detectan y usan las mejores herramientas disponibles
- Algunas herramientas tienen aliases (ej: `batcat` → `bat`)
- La configuración de estas herramientas está en sus respectivos archivos dotfile