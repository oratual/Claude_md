#!/bin/bash
# Motor de voz: espeak
# Ultra ligero, voz robótica

ENGINE_NAME="espeak"
ENGINE_DESC="eSpeak - Ultra ligero, voz robótica"
ENGINE_QUALITY="★★☆☆☆"
ENGINE_RESOURCE="Mínimo"

# Verificar si está instalado
check_installed() {
    command -v espeak &> /dev/null
}

# Instalar
install_engine() {
    echo "Instalando espeak..."
    sudo apt-get update && sudo apt-get install -y espeak
}

# Hablar
speak() {
    local text="$1"
    espeak -v es -s 150 -p 50 "$text" 2>/dev/null
}

# Info del motor
info() {
    echo "Motor: $ENGINE_NAME"
    echo "Descripción: $ENGINE_DESC"
    echo "Calidad: $ENGINE_QUALITY"
    echo "Recursos: $ENGINE_RESOURCE"
    echo "Nota: Voz muy robótica pero extremadamente ligera"
}