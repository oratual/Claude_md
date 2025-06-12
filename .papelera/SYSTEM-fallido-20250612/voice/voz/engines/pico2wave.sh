#!/bin/bash
# Motor de voz: pico2wave (SVOX Pico)
# Ligero, calidad media, incluido en repositorios

ENGINE_NAME="pico2wave"
ENGINE_DESC="SVOX Pico - Ligero, calidad media"
ENGINE_QUALITY="★★★☆☆"
ENGINE_RESOURCE="Muy bajo"

# Verificar si está instalado
check_installed() {
    command -v pico2wave &> /dev/null
}

# Instalar
install_engine() {
    echo "Instalando pico2wave..."
    sudo apt-get update && sudo apt-get install -y libttspico-utils
}

# Hablar
speak() {
    local text="$1"
    local temp_file="/tmp/claude_pico_$$.wav"
    
    pico2wave -l es-ES -w "$temp_file" "$text"
    
    # Usar paplay si está disponible (mejor manejo)
    if command -v paplay &> /dev/null; then
        paplay "$temp_file" 2>/dev/null
    else
        aplay -q -B 200000 "$temp_file" 2>/dev/null
    fi
    
    rm -f "$temp_file"
}

# Info del motor
info() {
    echo "Motor: $ENGINE_NAME"
    echo "Descripción: $ENGINE_DESC"
    echo "Calidad: $ENGINE_QUALITY"
    echo "Recursos: $ENGINE_RESOURCE"
    echo "Idiomas: es-ES, en-US, en-GB, de-DE, fr-FR, it-IT"
}