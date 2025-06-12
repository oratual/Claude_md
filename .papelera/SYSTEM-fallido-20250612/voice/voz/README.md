# Sistema de Notificación por Voz para Claude

Sistema modular de notificación por voz en español que anuncia cuando una instancia de Claude termina de responder, con múltiples opciones de motores de voz.

## 🎯 Características

- **Múltiples motores**: 5 opciones desde robótica hasta calidad humana
- **Configuración fácil**: Menú interactivo para elegir y configurar
- **Modular**: Fácil agregar nuevos motores
- **Inteligente**: Detecta el nombre de la terminal
- **Flexible**: Modo silencioso disponible

## 🚀 Instalación Rápida

```bash
# Configurador interactivo
./configurar-voz.sh
```

El configurador te guiará para:
1. Elegir motor de voz
2. Instalarlo si es necesario 
3. Configurar nombre de instancia
4. Probar la voz

## 📦 Motores de Voz Disponibles

| Motor | Calidad | Recursos | Características |
|-------|---------|----------|------------------|
| **pico2wave** | ★★★☆☆ | Muy bajo | Ligero, calidad media, offline |
| **espeak** | ★★☆☆☆ | Mínimo | Ultra ligero, robótico, offline |
| **festival** | ★★★★☆ | Medio-Alto | Buena calidad, más pesado, offline |
| **mimic3** | ★★★★★ | Alto | Voz neuronal, casi humana, offline |
| **gtts** | ★★★★★ | Bajo* | Google TTS, excelente, requiere internet |
| **none** | N/A | Ninguno | Modo silencioso |

## 🎙️ Uso

### Básico
```bash
# Ejecutar Claude con notificación al terminar
claude-con-voz "explica que es rust"

# Solo probar la notificación
./notificar-claude.sh
```

### Configurar Motor y Nombre
```bash
# Menú de configuración completo
./configurar-voz.sh

# O manualmente:
export CLAUDE_VOICE_ENGINE="mimic3"  # Motor a usar
export CLAUDE_INSTANCE_NAME="ultrathink"
export CLAUDE_VOICE_ENABLED=1
```

### Múltiples Terminales
```bash
# Terminal 1 - UltraThink
export CLAUDE_INSTANCE_NAME="ultrathink"
claude-con-voz

# Terminal 2 - DeepAnalysis  
export CLAUDE_INSTANCE_NAME="deep analysis"
claude-con-voz

# Terminal 3 - QuickTask
export CLAUDE_INSTANCE_NAME="quick task"
claude-con-voz
```

## ⚙️ Configuración Avanzada

### Variables de Entorno

- `CLAUDE_VOICE_ENGINE`: Motor de voz a usar (pico2wave, espeak, festival, mimic3, gtts, none)
- `CLAUDE_INSTANCE_NAME`: Nombre de la instancia actual
- `CLAUDE_VOICE_ENABLED`: Activar/desactivar voz (1/0)

### Agregar Nuevo Motor

1. Crear archivo en `engines/nuevo-motor.sh`
2. Implementar funciones: `check_installed()`, `install_engine()`, `speak()`
3. Definir variables: `ENGINE_NAME`, `ENGINE_DESC`, `ENGINE_QUALITY`

### Integración con .bashrc

```bash
# Agregar al final de ~/.bashrc
export CLAUDE_INSTANCE_NAME="mi-terminal"
export CLAUDE_VOICE_ENABLED=1
export PATH="$HOME/glados/scripts/voz:$PATH"
alias claude='claude-con-voz'
```

## 🔧 Solución de Problemas

### No se escucha nada
1. Ejecutar configurador: `./configurar-voz.sh`
2. Verificar motor instalado (opción 3 del menú)
3. Verificar audio del sistema: `speaker-test -t sine -f 1000 -l 1`

### Estática en pico2wave
- Es normal debido a la baja frecuencia de muestreo (16kHz)
- Cambiar a `festival` o `mimic3` para mejor calidad
- O usar `gtts` si tienes internet

### Error de permisos
```bash
chmod +x *.sh engines/*.sh
```

## 📁 Estructura del Sistema

```
voz/
├── configurar-voz.sh      # Menú principal de configuración
├── notificar-claude.sh    # Sistema de notificación
├── claude-con-voz         # Wrapper para Claude
├── engines/               # Motores de voz
│   ├── pico2wave.sh
│   ├── espeak.sh
│   ├── festival.sh
│   ├── mimic3.sh
│   ├── gtts.sh
│   └── none.sh
└── README.md
```

Configuración guardada en: `~/.config/claude-voz/config`

## 💡 Tips

- **Calidad vs Recursos**: 
  - Rápido: `espeak` o `pico2wave`
  - Calidad: `mimic3` o `gtts`
  - Equilibrio: `festival`
- **Para desarrollo**: Usa `none` para trabajar en silencio
- **Múltiples terminales**: Cada una puede tener su propio motor
- **Voz casi humana**: Instala `mimic3` para calidad neuronal offline

## 🌐 Comparación Rápida

- **¿Quieres la mejor calidad?** → `mimic3` (offline) o `gtts` (online)
- **¿PC con pocos recursos?** → `espeak` o `pico2wave`  
- **¿Balance calidad/recursos?** → `festival`
- **¿Trabajar en silencio?** → `none`