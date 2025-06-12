#!/bin/bash
# Wrapper para Claude Squad que detecta el entorno y aplica fixes

# Detectar si estamos siendo ejecutados desde PowerShell/Windows Terminal
detect_powershell() {
    # Verificar variables de entorno típicas de PowerShell
    if [[ -n "$WT_SESSION" ]] || [[ -n "$WT_PROFILE_ID" ]]; then
        return 0  # Windows Terminal detectado
    fi
    
    # Verificar si el proceso padre es PowerShell
    if ps -p $PPID | grep -q "powershell\|pwsh"; then
        return 0
    fi
    
    # Verificar TERM
    if [[ "$TERM" == "ms-terminal" ]] || [[ "$TERM" == "xterm-256color" && -n "$WT_SESSION" ]]; then
        return 0
    fi
    
    return 1
}

# Si estamos en PowerShell/Windows Terminal, aplicar workarounds
if detect_powershell; then
    echo "⚠️  Detectado PowerShell/Windows Terminal"
    echo "📌 Aplicando configuración de compatibilidad..."
    echo ""
    
    # Opción 1: Sugerir usar CMD
    echo "🎯 RECOMENDACIÓN: Claude Squad funciona mejor en CMD"
    echo "   Ejecuta este comando en PowerShell para abrir en CMD:"
    echo ""
    echo "   cmd /c 'wsl -e bash -c \"cd $(pwd) && cs\"'"
    echo ""
    echo "   O presiona Enter para continuar con modo compatibilidad..."
    read -p ""
    
    # Configurar terminal para máxima compatibilidad
    export TERM=dumb
    export NO_COLOR=1
    export FORCE_COLOR=0
    export CLICOLOR=0
    export COLORTERM=""
    
    # Deshabilitar secuencias de escape problemáticas
    export LESS="-R"
    export PAGER="less -R"
    
    # Limpiar pantalla de forma segura
    printf '\033[2J\033[H'
fi

# Cambiar al directorio del proyecto si se proporciona
if [ -n "$1" ]; then
    cd "$1" || exit 1
fi

# Verificar que estamos en un repositorio git
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: No estás en un repositorio Git"
    echo "   Claude Squad necesita ejecutarse dentro de un proyecto Git"
    exit 1
fi

# Ejecutar Claude Squad
echo "🚀 Iniciando Claude Squad..."
cs

# Si hubo problemas, ofrecer alternativas
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Claude Squad encontró un error"
    echo ""
    echo "Alternativas:"
    echo "1. Abre una ventana CMD y ejecuta:"
    echo "   wsl cs"
    echo ""
    echo "2. Usa Ubuntu directamente desde el menú inicio"
    echo ""
    echo "3. En Windows Terminal, usa el perfil 'Ubuntu' en lugar de PowerShell"
fi