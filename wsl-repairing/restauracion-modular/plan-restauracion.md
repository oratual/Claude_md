# Plan de Restauración Modular WSL

## 🎯 Objetivo
Crear un sistema de restauración por capas que permita recuperar:
1. Solo configuraciones del sistema
2. Solo proyectos específicos
3. Sistema completo
4. Mix personalizado

## 📦 Estructura Modular

### Capa 1: SISTEMA BASE
- **Configuraciones dotfiles**: .bashrc, .gitconfig, .ssh/
- **Configuraciones sistema**: /etc/wsl.conf, hosts
- **Herramientas instaladas**: Lista de paquetes apt
- **Configuraciones de desarrollo**: nvm, node, etc.

### Capa 2: PROYECTOS
- **glados/batman-incorporated**: Sistema principal
- **glados/scripts**: Utilidades y herramientas
- **glados/MPC**: Servidores MCP
- **glados/DiskDominator**: SOLO versión Linux
- **glados/SYSTEM**: Launcher y configuraciones
- **glados/UTILITIES**: InfiniteAgent, etc.

### Capa 3: DATOS Y LOGS
- **Logs históricos**: bitácoras, historiales
- **Backups locales**: .papelera, backups/
- **Documentación**: *.md files

## 🔧 Herramientas

### 1. backup-modular.sh
Script principal que permite:
- Backup selectivo por módulos
- Compresión opcional
- Versionado automático

### 2. restore-modular.sh
Script de restauración que:
- Lista backups disponibles
- Permite restauración selectiva
- Verifica integridad

### 3. wsl-restore-menu.sh
Menú interactivo que ofrece:
- Restauración guiada
- Opciones predefinidas
- Modo experto

## 📋 Casos de Uso

### Caso 1: WSL corrupto pero accesible
1. Ejecutar desde WSL: `~/glados/wsl-repairing/restore-modular.sh`
2. Seleccionar componentes a restaurar
3. Aplicar cambios

### Caso 2: WSL completamente roto
1. Desde PowerShell: `wsl --import` con backup base
2. Ejecutar script de post-instalación
3. Restaurar proyectos selectivamente

### Caso 3: Migración a nuevo PC
1. Exportar módulos necesarios
2. Importar sistema base
3. Restaurar proyectos uno por uno

## 🗂️ Estructura de Backups

```
H:\Backup\WSL\
├── system/
│   ├── 2025-06-12/
│   │   ├── dotfiles.tar.gz
│   │   ├── configs.tar.gz
│   │   └── packages.list
│   └── latest -> 2025-06-12/
├── projects/
│   ├── batman-incorporated/
│   ├── scripts/
│   ├── MPC/
│   └── DiskDominator-Linux/
└── full/
    └── Ubuntu-24.04-complete.tar
```