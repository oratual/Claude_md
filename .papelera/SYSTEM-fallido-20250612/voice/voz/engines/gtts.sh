#!/bin/bash
# Motor de voz: Google TTS (online)
# Requiere conexión a internet

ENGINE_NAME="gtts"
ENGINE_DESC="Google TTS - Online, excelente calidad"
ENGINE_QUALITY="★★★★★"
ENGINE_RESOURCE="Bajo (requiere internet)"

# Verificar si está instalado
check_installed() {
    command -v gtts-cli &> /dev/null || python3 -c "import gtts" 2>/dev/null
}

# Instalar
install_engine() {
    echo "Instalando Google TTS..."
    pip3 install --user gtts
    
    # Verificar que mpg123 esté instalado para reproducir MP3
    if ! command -v mpg123 &> /dev/null; then
        echo "Instalando reproductor MP3..."
        sudo apt-get install -y mpg123
    fi
}

# Hablar
speak() {
    local text="$1"
    local temp_file="/tmp/claude_gtts_$$.mp3"
    
    # Generar audio con Google TTS
    if command -v gtts-cli &> /dev/null; then
        gtts-cli "$text" -l es --output "$temp_file" 2>/dev/null
    else
        python3 -c "from gtts import gTTS; tts = gTTS('$text', lang='es'); tts.save('$temp_file')"
    fi
    
    # Reproducir
    if [ -f "$temp_file" ]; then
        mpg123 -q "$temp_file" 2>/dev/null
        rm -f "$temp_file"
    fi
}

# Info del motor
info() {
    echo "Motor: $ENGINE_NAME"
    echo "Descripción: $ENGINE_DESC"
    echo "Calidad: $ENGINE_QUALITY"
    echo "Recursos: $ENGINE_RESOURCE"
    echo "Nota: Requiere conexión a internet"
    echo "Límite: Sin límite conocido para uso personal"
}