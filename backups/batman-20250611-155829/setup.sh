#!/bin/bash
# Setup script para Batman Incorporated

echo "🦇 Instalando Batman Incorporated..."
echo "=================================="

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Directorio base
BATMAN_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 1. Verificar Python
echo -e "\n${YELLOW}Verificando Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 no encontrado. Por favor instala Python 3.8+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}✅ Python $PYTHON_VERSION encontrado${NC}"

# 2. Crear entorno virtual
echo -e "\n${YELLOW}Creando entorno virtual...${NC}"
if [ ! -d "$BATMAN_DIR/venv" ]; then
    python3 -m venv "$BATMAN_DIR/venv"
    echo -e "${GREEN}✅ Entorno virtual creado${NC}"
else
    echo -e "${GREEN}✅ Entorno virtual ya existe${NC}"
fi

# 3. Activar entorno e instalar dependencias
echo -e "\n${YELLOW}Instalando dependencias...${NC}"
source "$BATMAN_DIR/venv/bin/activate"

# Crear requirements.txt si no existe
if [ ! -f "$BATMAN_DIR/requirements.txt" ]; then
    cat > "$BATMAN_DIR/requirements.txt" << EOF
# Batman Incorporated Dependencies
pyyaml>=6.0
python-dotenv>=1.0.0
click>=8.1.0
rich>=13.0.0
gitpython>=3.1.0
EOF
fi

pip install -q --upgrade pip
pip install -q -r "$BATMAN_DIR/requirements.txt"
echo -e "${GREEN}✅ Dependencias instaladas${NC}"

# 4. Crear directorios de configuración
echo -e "\n${YELLOW}Creando estructura de directorios...${NC}"
mkdir -p ~/.glados/batman-incorporated/{logs,tasks,reports,cache,worktrees}
echo -e "${GREEN}✅ Directorios creados${NC}"

# 5. Copiar configuración por defecto si no existe
if [ ! -f ~/.glados/batman-incorporated/config.yaml ]; then
    echo -e "\n${YELLOW}Creando configuración inicial...${NC}"
    cp "$BATMAN_DIR/config/default_config.yaml" ~/.glados/batman-incorporated/config.yaml
    echo -e "${GREEN}✅ Configuración creada en ~/.glados/batman-incorporated/config.yaml${NC}"
else
    echo -e "${GREEN}✅ Configuración existente preservada${NC}"
fi

# 6. Crear enlace simbólico para comando global
echo -e "\n${YELLOW}Instalando comando 'batman'...${NC}"
INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

# Crear wrapper script
cat > "$INSTALL_DIR/batman" << EOF
#!/bin/bash
# Batman Incorporated launcher
source "$BATMAN_DIR/venv/bin/activate"
python "$BATMAN_DIR/batman.py" "\$@"
EOF

chmod +x "$INSTALL_DIR/batman"

# Verificar si ~/.local/bin está en PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo -e "${YELLOW}⚠️  Añade $HOME/.local/bin a tu PATH:${NC}"
    echo -e "    echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
    echo -e "    source ~/.bashrc"
else
    echo -e "${GREEN}✅ Comando 'batman' instalado${NC}"
fi

# 7. Crear alias adicionales
echo -e "\n${YELLOW}Creando alias útiles...${NC}"
ALIAS_FILE="$HOME/.bash_aliases"
if ! grep -q "batman-incorporated" "$ALIAS_FILE" 2>/dev/null; then
    cat >> "$ALIAS_FILE" << EOF

# Batman Incorporated aliases
alias batman-status='batman --status'
alias batman-auto='batman --auto'
alias batman-stop='batman --off'
EOF
    echo -e "${GREEN}✅ Alias creados (requiere: source ~/.bash_aliases)${NC}"
else
    echo -e "${GREEN}✅ Alias ya existen${NC}"
fi

# 8. Verificar herramientas opcionales
echo -e "\n${YELLOW}Verificando herramientas del Arsenal...${NC}"
tools=("rg" "fd" "bat" "jq" "gh" "delta" "sd" "procs")
missing_tools=()

for tool in "${tools[@]}"; do
    if command -v "$tool" &> /dev/null; then
        echo -e "  ${GREEN}✅ $tool${NC}"
    else
        echo -e "  ${YELLOW}⚠️  $tool (opcional)${NC}"
        missing_tools+=("$tool")
    fi
done

if [ ${#missing_tools[@]} -gt 0 ]; then
    echo -e "\n${YELLOW}🎯 Para instalar herramientas faltantes SIN SUDO:${NC}"
    echo -e "  ${GREEN}batman --install-tools${NC}"
    echo ""
    echo -e "${YELLOW}Alternativa con apt (requiere sudo):${NC}"
    echo "  sudo apt install ripgrep fd-find bat jq"
    echo "  gh auth login  # Para GitHub CLI"
fi

# 9. Test rápido
echo -e "\n${YELLOW}Ejecutando test rápido...${NC}"
if source "$BATMAN_DIR/venv/bin/activate" && python "$BATMAN_DIR/batman.py" --status &> /dev/null; then
    echo -e "${GREEN}✅ Batman Incorporated instalado correctamente${NC}"
else
    echo -e "${RED}❌ Error en la instalación${NC}"
    exit 1
fi

# Resumen final
echo -e "\n${GREEN}🦇 ¡Batman Incorporated está listo!${NC}"
echo "=================================="
echo -e "Comandos disponibles:"
echo -e "  ${YELLOW}batman${NC} \"crear API REST\"     # Ejecutar tarea"
echo -e "  ${YELLOW}batman --status${NC}             # Ver estado"
echo -e "  ${YELLOW}batman --auto${NC}               # Modo automático"
echo -e "  ${YELLOW}batman --help${NC}               # Ver ayuda"
echo ""
echo -e "${GREEN}I am vengeance. I am the night. I am Batman Incorporated!${NC} 🦇"