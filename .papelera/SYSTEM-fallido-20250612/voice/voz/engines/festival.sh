#!/bin/bash
# Motor de voz: Festival
# Más pesado pero con voces de mejor calidad

ENGINE_NAME="festival"
ENGINE_DESC="Festival - Voces de calidad, más recursos"
ENGINE_QUALITY="★★★★☆"
ENGINE_RESOURCE="Medio-Alto"

# Verificar si está instalado
check_installed() {
    command -v festival &> /dev/null && [ -d /usr/share/festival/voices ]
}

# Instalar
install_engine() {
    echo "Instalando Festival con voces en español..."
    sudo apt-get update && sudo apt-get install -y \
        festival \
        festvox-ellpc11k \
        festival-freebsoft-utils
    
    # Intentar instalar voces adicionales si están disponibles
    sudo apt-get install -y festvox-us-slt-hts 2>/dev/null || true
}

# Hablar
speak() {
    local text="$1"
    echo "$text" | festival --tts --language spanish 2>/dev/null
}

# Info del motor
info() {
    echo "Motor: $ENGINE_NAME"
    echo "Descripción: $ENGINE_DESC"
    echo "Calidad: $ENGINE_QUALITY"
    echo "Recursos: $ENGINE_RESOURCE"
    echo "Nota: Mejor calidad pero usa más memoria (~100MB)"
}