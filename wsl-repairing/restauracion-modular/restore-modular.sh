#!/bin/bash
# Script de Restauración Modular para WSL
# Permite restaurar selectivamente componentes del sistema

# Configuración
BACKUP_ROOT="/mnt/h/Backup/WSL"
RESTORE_LOG="$HOME/glados/wsl-repairing/restore-$(date +%Y%m%d-%H%M%S).log"

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Función de logging
log() {
    echo "$1" | tee -a "$RESTORE_LOG"
}

# Verificar backups disponibles
check_available_backups() {
    echo -e "${BLUE}📦 Backups disponibles:${NC}"
    echo
    
    # Sistema
    if [ -d "$BACKUP_ROOT/system" ]; then
        echo "SISTEMA:"
        ls -1d "$BACKUP_ROOT/system"/*/ 2>/dev/null | while read dir; do
            basename "$dir"
        done | sort -r | head -5
        echo
    fi
    
    # Proyectos
    if [ -d "$BACKUP_ROOT/projects" ]; then
        echo "PROYECTOS:"
        for project in "$BACKUP_ROOT/projects"/*/; do
            if [ -d "$project" ]; then
                project_name=$(basename "$project")
                latest_backup=$(ls -1d "$project"/*/ 2>/dev/null | sort -r | head -1)
                if [ -n "$latest_backup" ]; then
                    echo "  - $project_name: $(basename "$latest_backup")"
                fi
            fi
        done
    fi
}

# Restaurar sistema base
restore_system() {
    local backup_date=$1
    
    if [ -z "$backup_date" ]; then
        backup_date="latest"
    fi
    
    local system_backup="$BACKUP_ROOT/system/$backup_date"
    
    if [ ! -d "$system_backup" ]; then
        log "❌ No existe backup del sistema para: $backup_date"
        return 1
    fi
    
    log "🔄 Restaurando sistema desde $backup_date..."
    
    # Crear backup de seguridad actual
    log "  → Creando backup de seguridad de configuraciones actuales..."
    mkdir -p "$HOME/.config/wsl-restore-backup"
    cp "$HOME/.bashrc" "$HOME/.config/wsl-restore-backup/" 2>/dev/null
    cp "$HOME/.gitconfig" "$HOME/.config/wsl-restore-backup/" 2>/dev/null
    
    # Restaurar dotfiles
    if [ -f "$system_backup/dotfiles.tar.gz" ]; then
        log "  → Restaurando dotfiles..."
        tar -xzf "$system_backup/dotfiles.tar.gz" -C "$HOME"
    fi
    
    # Restaurar configuraciones del sistema (requiere sudo)
    if [ -f "$system_backup/configs.tar.gz" ]; then
        log "  → Restaurando configuraciones del sistema..."
        sudo tar -xzf "$system_backup/configs.tar.gz" -C /
    fi
    
    # Mostrar información de paquetes
    if [ -f "$system_backup/packages.list" ]; then
        log "  → Lista de paquetes guardada en: $system_backup/packages.list"
        echo "    Para reinstalar paquetes, ejecuta:"
        echo "    cat $system_backup/packages.list | grep '^ii' | awk '{print \$2}' | xargs sudo apt install -y"
    fi
    
    log "${GREEN}✅ Sistema restaurado${NC}"
}

# Restaurar proyecto individual
restore_project() {
    local project_name=$1
    local backup_date=$2
    local target_path=$3
    
    if [ -z "$backup_date" ]; then
        backup_date="latest"
    fi
    
    if [ -z "$target_path" ]; then
        target_path="$HOME/glados/$project_name"
    fi
    
    local project_backup="$BACKUP_ROOT/projects/$project_name/$backup_date"
    
    if [ ! -d "$project_backup" ]; then
        log "❌ No existe backup de $project_name para: $backup_date"
        return 1
    fi
    
    log "🔄 Restaurando $project_name desde $backup_date..."
    
    # Verificar si existe el proyecto actual
    if [ -d "$target_path" ]; then
        echo -e "${YELLOW}⚠️  El proyecto ya existe en $target_path${NC}"
        read -p "¿Hacer backup del actual? (s/n): " backup_current
        if [ "$backup_current" = "s" ]; then
            mv "$target_path" "${target_path}.backup-$(date +%Y%m%d-%H%M%S)"
        fi
    fi
    
    # Crear directorio padre si no existe
    mkdir -p "$(dirname "$target_path")"
    
    # Restaurar con rsync
    rsync -av "$project_backup/" "$target_path/"
    
    # Reinicializar git si es necesario
    if [ -d "$target_path/.git" ]; then
        log "  → Reestableciendo git..."
        cd "$target_path"
        git config --local core.filemode false
        git config --local core.autocrlf input
    fi
    
    log "${GREEN}✅ $project_name restaurado en $target_path${NC}"
}

# Menú de restauración
show_restore_menu() {
    clear
    echo "╔══════════════════════════════════════════════════╗"
    echo "║       WSL Restauración Modular - Sistema         ║"
    echo "╚══════════════════════════════════════════════════╝"
    echo
    check_available_backups
    echo
    echo "¿Qué deseas restaurar?"
    echo
    echo "  1) 📁 Sistema Base (dotfiles, configs)"
    echo "  2) 🦇 Batman Incorporated"
    echo "  3) 📜 Scripts"
    echo "  4) 🔌 MPC"
    echo "  5) 💾 DiskDominator (Linux)"
    echo "  6) 🔧 SYSTEM"
    echo "  7) 🛠️  UTILITIES"
    echo "  8) 📊 Todos los proyectos"
    echo "  9) 🔧 Restauración personalizada"
    echo "  0) ❌ Salir"
    echo
}

# Restauración personalizada
custom_restore() {
    echo -e "${BLUE}🔧 Restauración personalizada${NC}"
    echo
    echo "Proyectos disponibles:"
    ls -1 "$BACKUP_ROOT/projects/" 2>/dev/null
    echo
    read -p "Nombre del proyecto: " project
    read -p "Fecha del backup (o 'latest'): " date
    read -p "Ruta destino (Enter para default): " path
    
    restore_project "$project" "$date" "$path"
}

# Función principal
main() {
    # Crear directorio de logs
    mkdir -p "$(dirname "$RESTORE_LOG")"
    
    while true; do
        show_restore_menu
        read -p "Selecciona una opción: " choice
        
        case $choice in
            1)
                restore_system
                read -p "Presiona Enter para continuar..."
                ;;
            2)
                restore_project "batman-incorporated"
                read -p "Presiona Enter para continuar..."
                ;;
            3)
                restore_project "scripts"
                read -p "Presiona Enter para continuar..."
                ;;
            4)
                restore_project "MPC"
                read -p "Presiona Enter para continuar..."
                ;;
            5)
                restore_project "DiskDominator-Linux" "" "$HOME/glados/DiskDominator"
                read -p "Presiona Enter para continuar..."
                ;;
            6)
                restore_project "SYSTEM"
                read -p "Presiona Enter para continuar..."
                ;;
            7)
                restore_project "UTILITIES"
                read -p "Presiona Enter para continuar..."
                ;;
            8)
                echo -e "${YELLOW}🔄 Restaurando todos los proyectos...${NC}"
                restore_project "batman-incorporated"
                restore_project "scripts"
                restore_project "MPC"
                restore_project "DiskDominator-Linux" "" "$HOME/glados/DiskDominator"
                restore_project "SYSTEM"
                restore_project "UTILITIES"
                echo -e "${GREEN}✅ Todos los proyectos restaurados${NC}"
                read -p "Presiona Enter para continuar..."
                ;;
            9)
                custom_restore
                read -p "Presiona Enter para continuar..."
                ;;
            0)
                echo "Log guardado en: $RESTORE_LOG"
                exit 0
                ;;
            *)
                echo -e "${RED}Opción inválida${NC}"
                sleep 2
                ;;
        esac
    done
}

# Verificar permisos
if [ ! -r "$BACKUP_ROOT" ]; then
    echo -e "${RED}❌ No puedo leer desde $BACKUP_ROOT${NC}"
    exit 1
fi

# Ejecutar
main