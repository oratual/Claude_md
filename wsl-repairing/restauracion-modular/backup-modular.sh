#!/bin/bash
# Script de Backup Modular para WSL
# Permite hacer backups selectivos del sistema y proyectos

# Configuración
BACKUP_ROOT="/mnt/h/Backup/WSL"
DATE_STAMP=$(date +%Y-%m-%d_%H-%M-%S)
TEMP_DIR="/tmp/wsl-backup-$$"

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Crear directorios
mkdir -p "$TEMP_DIR"
mkdir -p "$BACKUP_ROOT/system/$DATE_STAMP"
mkdir -p "$BACKUP_ROOT/projects"

# Función para mostrar menú
show_menu() {
    clear
    echo "============================================"
    echo "         WSL Backup Modular"
    echo "         Destino: H:\\Backup\\WSL\\"
    echo "============================================"
    echo
    echo "=== CONFIGURACION WSL (Ubuntu) ==="
    echo "  1) Archivos de configuracion (.bashrc, .gitconfig, .ssh)"
    echo "  2) Lista de paquetes instalados (apt)"
    echo "  3) Todo el sistema WSL"
    echo
    echo "=== PROYECTOS EN ~/glados/ ==="
    echo "  4) batman-incorporated"
    echo "  5) scripts"
    echo "  6) MPC"
    echo "  7) DiskDominator (version Linux)"
    echo "  8) SYSTEM"
    echo "  9) UTILITIES"
    echo " 10) TODOS los proyectos"
    echo
    echo "=== OPCIONES RAPIDAS ==="
    echo " 11) Backup completo (sistema + todos los proyectos)"
    echo " 12) Solo proyectos importantes (batman, scripts, MPC)"
    echo
    echo "  0) Salir"
    echo
}

# Backup del sistema base
backup_system() {
    echo -e "${BLUE}🔄 Respaldando sistema base...${NC}"
    
    # Dotfiles
    echo "  → Empaquetando dotfiles..."
    tar -czf "$BACKUP_ROOT/system/$DATE_STAMP/dotfiles.tar.gz" \
        -C "$HOME" \
        .bashrc .profile .gitconfig .ssh/config \
        2>/dev/null
    
    # Configuraciones del sistema
    echo "  → Empaquetando configuraciones..."
    sudo tar -czf "$BACKUP_ROOT/system/$DATE_STAMP/configs.tar.gz" \
        -C / \
        etc/wsl.conf \
        etc/hosts \
        2>/dev/null
    
    # Lista de paquetes instalados
    echo "  → Guardando lista de paquetes..."
    dpkg -l > "$BACKUP_ROOT/system/$DATE_STAMP/packages.list"
    
    # Herramientas especiales
    echo "  → Documentando herramientas..."
    {
        echo "# Herramientas instaladas"
        echo "Node version: $(node -v 2>/dev/null || echo 'No instalado')"
        echo "NPM version: $(npm -v 2>/dev/null || echo 'No instalado')"
        echo "Python version: $(python3 --version 2>/dev/null || echo 'No instalado')"
        echo "Git version: $(git --version)"
        command -v rg && echo "ripgrep: instalado"
        command -v fd && echo "fd: instalado"
        command -v bat && echo "bat: instalado"
    } > "$BACKUP_ROOT/system/$DATE_STAMP/tools.info"
    
    # Actualizar enlace a latest
    ln -sfn "$DATE_STAMP" "$BACKUP_ROOT/system/latest"
    
    echo -e "${GREEN}✅ Sistema base respaldado${NC}"
}

# Backup de proyecto individual
backup_project() {
    local project_name=$1
    local project_path=$2
    
    if [ ! -d "$project_path" ]; then
        echo -e "${RED}❌ No existe: $project_path${NC}"
        return 1
    fi
    
    echo -e "${BLUE}🔄 Respaldando $project_name...${NC}"
    
    # Crear directorio si no existe
    mkdir -p "$BACKUP_ROOT/projects/$project_name"
    
    # Respaldar con rsync (incremental)
    rsync -av --delete \
        --exclude='node_modules' \
        --exclude='.git' \
        --exclude='target' \
        --exclude='dist' \
        --exclude='build' \
        --exclude='*.log' \
        "$project_path/" \
        "$BACKUP_ROOT/projects/$project_name/$DATE_STAMP/"
    
    # Crear archivo de info
    {
        echo "Proyecto: $project_name"
        echo "Fecha: $(date)"
        echo "Ruta original: $project_path"
        echo "Tamaño: $(du -sh "$project_path" | cut -f1)"
        if [ -d "$project_path/.git" ]; then
            echo "Git branch: $(cd "$project_path" && git branch --show-current 2>/dev/null)"
            echo "Last commit: $(cd "$project_path" && git log -1 --oneline 2>/dev/null)"
        fi
    } > "$BACKUP_ROOT/projects/$project_name/$DATE_STAMP/backup.info"
    
    # Enlace a latest
    ln -sfn "$DATE_STAMP" "$BACKUP_ROOT/projects/$project_name/latest"
    
    echo -e "${GREEN}✅ $project_name respaldado${NC}"
}

# Backup de todos los proyectos
backup_all_projects() {
    backup_project "batman-incorporated" "$HOME/glados/batman-incorporated"
    backup_project "scripts" "$HOME/glados/scripts"
    backup_project "MPC" "$HOME/glados/MPC"
    backup_project "DiskDominator-Linux" "$HOME/glados/DiskDominator"
    backup_project "SYSTEM" "$HOME/glados/SYSTEM"
    backup_project "UTILITIES" "$HOME/glados/UTILITIES"
}

# Backup solo configuraciones
backup_configs() {
    echo -e "${BLUE}Respaldando configuraciones...${NC}"
    tar -czf "$BACKUP_ROOT/system/$DATE_STAMP/dotfiles.tar.gz" \
        -C "$HOME" \
        .bashrc .profile .gitconfig .ssh/config \
        2>/dev/null
    echo -e "${GREEN}✅ Configuraciones respaldadas${NC}"
}

# Backup lista de paquetes
backup_packages() {
    echo -e "${BLUE}Guardando lista de paquetes...${NC}"
    dpkg -l > "$BACKUP_ROOT/system/$DATE_STAMP/packages.list"
    apt list --installed > "$BACKUP_ROOT/system/$DATE_STAMP/apt-installed.list"
    echo -e "${GREEN}✅ Lista de paquetes guardada${NC}"
}

# Backup proyectos importantes
backup_important_projects() {
    echo -e "${BLUE}Respaldando proyectos importantes...${NC}"
    backup_project "batman-incorporated" "$HOME/glados/batman-incorporated"
    backup_project "scripts" "$HOME/glados/scripts"
    backup_project "MPC" "$HOME/glados/MPC"
    echo -e "${GREEN}✅ Proyectos importantes respaldados${NC}"
}

# Función principal
main() {
    while true; do
        show_menu
        read -p "Selecciona una opción: " choice
        
        case $choice in
            1)
                backup_configs
                ;;
            2)
                backup_packages
                ;;
            3)
                backup_system
                ;;
            4)
                backup_project "batman-incorporated" "$HOME/glados/batman-incorporated"
                ;;
            5)
                backup_project "scripts" "$HOME/glados/scripts"
                ;;
            6)
                backup_project "MPC" "$HOME/glados/MPC"
                ;;
            7)
                backup_project "DiskDominator-Linux" "$HOME/glados/DiskDominator"
                ;;
            8)
                backup_project "SYSTEM" "$HOME/glados/SYSTEM"
                ;;
            9)
                backup_project "UTILITIES" "$HOME/glados/UTILITIES"
                ;;
            10)
                echo -e "${YELLOW}Respaldando todos los proyectos...${NC}"
                backup_all_projects
                ;;
            11)
                echo -e "${YELLOW}Backup completo en proceso...${NC}"
                backup_system
                backup_all_projects
                echo -e "${GREEN}✅ Backup completo finalizado${NC}"
                ;;
            12)
                backup_important_projects
                ;;
            0)
                echo "Saliendo..."
                rm -rf "$TEMP_DIR"
                exit 0
                ;;
            *)
                echo -e "${RED}Opción inválida${NC}"
                sleep 1
                ;;
        esac
        
        if [ "$choice" != "0" ]; then
            echo
            read -p "Presiona Enter para volver al menú..."
        fi
    done
}

# Verificar permisos
if [ ! -w "$BACKUP_ROOT" ]; then
    echo -e "${RED}❌ No tienes permisos de escritura en $BACKUP_ROOT${NC}"
    exit 1
fi

# Ejecutar
main