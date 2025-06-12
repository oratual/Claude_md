#!/bin/bash
# Setup Batman Enhanced - Configuración automática del sistema mejorado

set -e

echo "🦇 BATMAN ENHANCED SETUP 🦇"
echo "=========================="
echo

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Directorio base
BATMAN_DIR="$HOME/glados/batman"
BATMAN_HOME="$HOME/.batman"

# Función para verificar comando
check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 disponible"
        return 0
    else
        echo -e "${RED}✗${NC} $1 no encontrado"
        return 1
    fi
}

# Función para crear directorio si no existe
ensure_dir() {
    if [ ! -d "$1" ]; then
        mkdir -p "$1"
        echo -e "${GREEN}✓${NC} Creado directorio: $1"
    else
        echo -e "${YELLOW}→${NC} Directorio existente: $1"
    fi
}

echo "1. Verificando dependencias..."
echo "------------------------------"

# Verificar Python
if ! check_command python3; then
    echo -e "${RED}Error: Python 3 es requerido${NC}"
    exit 1
fi

# Verificar pip
if ! check_command pip3; then
    echo -e "${YELLOW}Instalando pip3...${NC}"
    sudo apt-get update && sudo apt-get install -y python3-pip
fi

# Verificar herramientas del sistema
echo
echo "2. Verificando herramientas del sistema..."
echo "-----------------------------------------"

TOOLS_MISSING=0

# Herramientas esenciales
for tool in git gh tmux; do
    if ! check_command "$tool"; then
        TOOLS_MISSING=$((TOOLS_MISSING + 1))
    fi
done

# Herramientas opcionales pero recomendadas
echo
echo "Herramientas opcionales:"
for tool in rg fdfind batcat jq exa; do
    check_command "$tool" || true
done

if [ $TOOLS_MISSING -gt 0 ]; then
    echo
    echo -e "${YELLOW}Algunas herramientas no están instaladas.${NC}"
    echo "¿Deseas instalarlas ahora? (s/n)"
    read -r response
    if [[ "$response" =~ ^[Ss]$ ]]; then
        echo "Instalando herramientas..."
        sudo apt-get update
        sudo apt-get install -y git gh tmux ripgrep fd-find bat jq exa
    fi
fi

echo
echo "3. Creando estructura de directorios..."
echo "--------------------------------------"

# Crear directorios necesarios
ensure_dir "$BATMAN_HOME"
ensure_dir "$BATMAN_HOME/logs"
ensure_dir "$BATMAN_HOME/reports"
ensure_dir "$BATMAN_HOME/tasks"
ensure_dir "$BATMAN_HOME/thinking"
ensure_dir "$BATMAN_HOME/claude-squad-states"
ensure_dir "$BATMAN_HOME/backups"

echo
echo "4. Instalando dependencias de Python..."
echo "--------------------------------------"

# Crear requirements.txt si no existe
if [ ! -f "$BATMAN_DIR/requirements.txt" ]; then
    cat > "$BATMAN_DIR/requirements.txt" << 'EOF'
pyyaml>=6.0
networkx>=3.0
matplotlib>=3.0
requests>=2.28
aiohttp>=3.8
EOF
    echo -e "${GREEN}✓${NC} Creado requirements.txt"
fi

# Instalar dependencias
cd "$BATMAN_DIR"
pip3 install -r requirements.txt --user
echo -e "${GREEN}✓${NC} Dependencias instaladas"

echo
echo "5. Configurando GitHub CLI..."
echo "-----------------------------"

if check_command gh; then
    if gh auth status &> /dev/null; then
        echo -e "${GREEN}✓${NC} GitHub CLI autenticado"
        
        # Obtener información del repo
        if [ -d "$HOME/glados/.git" ]; then
            cd "$HOME/glados"
            REPO_INFO=$(gh repo view --json owner,name 2>/dev/null || true)
            if [ -n "$REPO_INFO" ]; then
                echo -e "${GREEN}✓${NC} Repositorio detectado"
            fi
        fi
    else
        echo -e "${YELLOW}GitHub CLI no autenticado${NC}"
        echo "Para autenticar, ejecuta: gh auth login"
    fi
fi

echo
echo "6. Creando archivos de configuración..."
echo "---------------------------------------"

# Crear configuración de ejemplo si no existe
if [ ! -f "$BATMAN_HOME/enhanced_config.yaml" ]; then
    cat > "$BATMAN_HOME/enhanced_config.yaml" << 'EOF'
# Batman Enhanced Configuration
github_enabled: true
github_repo: 'lauta/glados'  # Ajustar según tu repo
mcp_enabled: true

analyses:
  disk_usage:
    enabled: true
    threshold_gb: 100
    large_file_mb: 100
  
  log_analysis:
    enabled: true
    error_threshold: 10
    patterns: ['ERROR', 'CRITICAL', 'FAILED', 'WARNING']
  
  security_audit:
    enabled: true
    check_permissions: true
    check_ports: true
  
  performance_metrics:
    enabled: true
    cpu_threshold: 80
    memory_threshold: 90

optimizations:
  auto_cleanup: true
  compress_logs: true
  optimize_git: true

reporting:
  create_github_issues: false  # Cambiar a true cuando esté listo
  daily_summary: true
  alert_threshold: 'high'
EOF
    echo -e "${GREEN}✓${NC} Creada configuración enhanced_config.yaml"
else
    echo -e "${YELLOW}→${NC} Configuración existente encontrada"
fi

echo
echo "7. Creando tareas de ejemplo..."
echo "-------------------------------"

# Crear tarea de ejemplo
if [ ! -f "$BATMAN_HOME/tasks/example_night_tasks.yaml" ]; then
    cat > "$BATMAN_HOME/tasks/example_night_tasks.yaml" << 'EOF'
# Tareas nocturnas de ejemplo para Batman
tasks:
  - id: check_disk_space
    title: "Verificar espacio en disco"
    description: "Analizar uso de disco y buscar archivos grandes"
    type: analysis
    priority: 2
    
  - id: analyze_system_logs
    title: "Analizar logs del sistema"
    description: "Buscar errores y patrones inusuales en logs"
    type: analysis
    priority: 1
    
  - id: security_check
    title: "Auditoría de seguridad básica"
    description: "Verificar permisos, puertos abiertos y configuraciones"
    type: security
    priority: 1
    
  - id: backup_configs
    title: "Backup de configuraciones"
    description: "Crear backup de archivos de configuración importantes"
    type: maintenance
    priority: 3
    command: |
      backup_dir="$HOME/.batman/backups/$(date +%Y%m%d)"
      mkdir -p "$backup_dir"
      cp ~/.bashrc ~/.profile ~/.gitconfig "$backup_dir/" 2>/dev/null || true
EOF
    echo -e "${GREEN}✓${NC} Creadas tareas de ejemplo"
fi

echo
echo "8. Creando comando batman-enhanced..."
echo "------------------------------------"

# Crear script ejecutable
cat > "$HOME/.local/bin/batman-enhanced" << EOF
#!/bin/bash
# Batman Enhanced launcher

cd "$BATMAN_DIR"
python3 batman_enhanced_night.py "\$@"
EOF

chmod +x "$HOME/.local/bin/batman-enhanced"
echo -e "${GREEN}✓${NC} Comando batman-enhanced creado"

# Verificar que ~/.local/bin esté en PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo -e "${YELLOW}Nota: Agrega ~/.local/bin a tu PATH${NC}"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo -e "${GREEN}✓${NC} PATH actualizado en .bashrc"
fi

echo
echo "9. Configurando cron (opcional)..."
echo "---------------------------------"

echo "¿Deseas configurar Batman para ejecutarse automáticamente cada noche? (s/n)"
read -r response

if [[ "$response" =~ ^[Ss]$ ]]; then
    # Agregar entrada a crontab
    CRON_CMD="0 3 * * * $HOME/.local/bin/batman-enhanced >> $BATMAN_HOME/logs/cron.log 2>&1"
    
    # Verificar si ya existe
    if ! crontab -l 2>/dev/null | grep -q "batman-enhanced"; then
        (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
        echo -e "${GREEN}✓${NC} Cron configurado para ejecutar a las 3:00 AM"
    else
        echo -e "${YELLOW}→${NC} Cron ya configurado"
    fi
fi

echo
echo "10. Verificación final..."
echo "------------------------"

# Probar importaciones
echo "Verificando módulos Python..."
if python3 -c "import yaml, networkx" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Módulos Python OK"
else
    echo -e "${RED}✗${NC} Error con módulos Python"
fi

# Verificar scripts principales
for script in batman_enhanced_night.py batman_github_integration.py batman_mcp_manager.py; do
    if [ -f "$BATMAN_DIR/$script" ]; then
        echo -e "${GREEN}✓${NC} $script presente"
    else
        echo -e "${RED}✗${NC} $script faltante"
    fi
done

echo
echo "========================================"
echo "🦇 SETUP COMPLETADO 🦇"
echo "========================================"
echo
echo "Próximos pasos:"
echo "1. Ejecutar modo test: batman-enhanced --test"
echo "2. Ver configuración: cat ~/.batman/enhanced_config.yaml"
echo "3. Editar tareas: nano ~/.batman/tasks/example_night_tasks.yaml"
echo "4. Ver logs: tail -f ~/.batman/logs/enhanced_*.log"
echo
echo "Comandos disponibles:"
echo "  batman-enhanced          - Ejecutar análisis completo"
echo "  batman-enhanced --test   - Modo test (no aplica cambios)"
echo "  batman-enhanced --analyze-only - Solo análisis"
echo

# Preguntar si ejecutar test
echo "¿Deseas ejecutar un test ahora? (s/n)"
read -r response

if [[ "$response" =~ ^[Ss]$ ]]; then
    echo
    echo "Ejecutando test..."
    cd "$BATMAN_DIR"
    python3 batman_enhanced_night.py --test
fi

echo
echo "¡Batman Enhanced está listo para proteger tu sistema! 🦇"