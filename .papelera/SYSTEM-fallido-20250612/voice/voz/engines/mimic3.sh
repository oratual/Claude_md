#!/bin/bash
# Motor de voz: Mimic3
# Voz neuronal local de alta calidad

ENGINE_NAME="mimic3"
ENGINE_DESC="Mimic3 - Voz neuronal local, alta calidad"
ENGINE_QUALITY="★★★★★"
ENGINE_RESOURCE="Alto"

# Verificar si está instalado
check_installed() {
    command -v mimic3 &> /dev/null || [ -f ~/.local/bin/mimic3 ]
}

# Instalar
install_engine() {
    echo "Instalando Mimic3 (voz neuronal)..."
    echo "Nota: Requiere Python 3.7+ y ~1GB de espacio"
    
    # Instalar con pip en modo usuario
    pip3 install --user mycroft-mimic3-tts
    
    echo ""
    echo "Descargando voz en español..."
    # La primera vez descarga el modelo automáticamente
    ~/.local/bin/mimic3 --voice es_ES/carlfm "Prueba" 2>/dev/null || true
}

# Hablar
speak() {
    local text="$1"
    if [ -f ~/.local/bin/mimic3 ]; then
        ~/.local/bin/mimic3 --voice es_ES/carlfm "$text"
    else
        mimic3 --voice es_ES/carlfm "$text"
    fi
}

# Info del motor
info() {
    echo "Motor: $ENGINE_NAME"
    echo "Descripción: $ENGINE_DESC"
    echo "Calidad: $ENGINE_QUALITY"
    echo "Recursos: $ENGINE_RESOURCE"
    echo "Nota: Calidad casi humana, requiere ~500MB RAM"
    echo "Voces españolas: es_ES/carlfm, es_ES/karen"
}