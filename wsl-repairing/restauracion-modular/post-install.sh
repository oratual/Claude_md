#!/bin/bash
# Script de Post-Instalación para WSL limpio
# Ejecutar después de reinstalar WSL desde cero

echo "╔══════════════════════════════════════════════════╗"
echo "║       Post-Instalación WSL - Setup Inicial       ║"
echo "╚══════════════════════════════════════════════════╝"
echo

# Actualizar sistema
echo "📦 Actualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar herramientas básicas
echo "🔧 Instalando herramientas esenciales..."
sudo apt install -y \
    build-essential \
    git \
    curl \
    wget \
    zip \
    unzip \
    jq \
    htop \
    tmux \
    neovim \
    python3 \
    python3-pip \
    software-properties-common

# Instalar herramientas avanzadas
echo "🚀 Instalando herramientas avanzadas..."
sudo apt install -y \
    ripgrep \
    fd-find \
    bat \
    exa \
    httpie \
    fzf \
    ncdu \
    tldr \
    socat

# Configurar aliases para herramientas
echo "📝 Configurando aliases..."
{
    echo "# Aliases para herramientas"
    echo "alias fd='fdfind'"
    echo "alias bat='batcat'"
    echo "alias ls='exa'"
    echo "alias la='exa -la'"
    echo "alias ll='exa -l'"
} >> ~/.bashrc

# Instalar Node.js via NVM
echo "📦 Instalando Node.js..."
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 22
nvm use 22

# Configurar Git
echo "🔧 Configurando Git..."
read -p "Email para Git: " git_email
read -p "Nombre para Git: " git_name
git config --global user.email "$git_email"
git config --global user.name "$git_name"

# Instalar Tailscale
echo "🌐 Instalando Tailscale..."
curl -fsSL https://tailscale.com/install.sh | sh

# Crear estructura de directorios
echo "📁 Creando estructura de directorios..."
mkdir -p ~/glados/{scripts,SYSTEM,UTILITIES,batman-incorporated,MPC,DiskDominator}
mkdir -p ~/glados/wsl-repairing

# Restaurar desde backup si existe
if [ -d "/mnt/h/Backup/WSL/system/latest" ]; then
    echo "✅ Backup encontrado, restaurando configuraciones..."
    tar -xzf /mnt/h/Backup/WSL/system/latest/dotfiles.tar.gz -C ~/ 2>/dev/null
    source ~/.bashrc
else
    echo "⚠️  No se encontró backup, configuración manual necesaria"
fi

# Clonar repositorios desde GitHub
echo "📥 Clonando repositorios..."
cd ~/glados
git clone https://github.com/oratual/glados-scripts.git scripts 2>/dev/null || echo "Scripts ya existe"
git clone https://github.com/oratual/Batman-Incorporated.git batman-incorporated 2>/dev/null || echo "Batman ya existe"
git clone https://github.com/oratual/MPC.git MPC 2>/dev/null || echo "MPC ya existe"

# Configurar 1Password SSH (si aplica)
echo "🔐 Configuración 1Password SSH..."
if [ -f ~/.ssh/1password-agent.sh ]; then
    ~/.ssh/1password-agent.sh
fi

echo
echo "✅ Post-instalación completada!"
echo
echo "Próximos pasos:"
echo "1. Ejecutar: source ~/.bashrc"
echo "2. Configurar Tailscale: sudo tailscale up"
echo "3. Restaurar proyectos: ~/glados/wsl-repairing/restauracion-modular/restore-modular.sh"
echo "4. Verificar salud: ~/glados/wsl-repairing/wsl-health-monitor.sh"