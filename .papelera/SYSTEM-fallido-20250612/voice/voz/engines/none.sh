#!/bin/bash
# Motor de voz: Ninguno (silencioso)

ENGINE_NAME="none"
ENGINE_DESC="Sin voz - Modo silencioso"
ENGINE_QUALITY="N/A"
ENGINE_RESOURCE="Ninguno"

# Siempre está "instalado"
check_installed() {
    return 0
}

# No necesita instalación
install_engine() {
    echo "Modo silencioso activado"
    return 0
}

# No habla
speak() {
    # Silencio
    return 0
}

# Info del motor
info() {
    echo "Motor: $ENGINE_NAME"
    echo "Descripción: $ENGINE_DESC"
    echo "Nota: No emite ningún sonido"
}