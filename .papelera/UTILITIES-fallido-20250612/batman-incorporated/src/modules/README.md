# Sistema de Módulos de Batman Incorporated

Este directorio contiene módulos temáticos que extienden las capacidades de Batman Incorporated para diferentes dominios.

## 📦 Módulos Disponibles

### software/
Herramientas completas para desarrollo de software con integración WSL2-Windows:
- **windows_interop**: Interoperabilidad completa WSL2-Windows
- **compilation**: Compilación multiplataforma
- **testing**: Testing híbrido Linux/Windows
- **deployment**: Deployment a múltiples plataformas
- **office_automation**: Automatización de Microsoft Office

## 🚀 Crear un Nuevo Módulo

1. Crear directorio con el nombre del módulo
2. Crear `manifest.yaml` con la estructura:

```yaml
name: mi_modulo
version: 1.0.0
description: "Descripción del módulo"
author: "Tu nombre"

capabilities:
  - capacidad_1
  - capacidad_2

required_tools:
  linux:
    - herramienta1
  windows:
    - herramienta.exe
  optional:
    - herramienta_opcional

agent_enhancements:
  alfred:
    capabilities: [...]
    extra_tools: [...]
```

3. Crear `__init__.py` con la clase del módulo:

```python
from ..base_module import BaseModule

class MiModuloModule(BaseModule):
    def initialize(self) -> bool:
        # Inicializar herramientas
        return True
        
    def get_tool(self, tool_name: str):
        return self.tools.get(tool_name)
        
    def get_agent_enhancements(self) -> Dict[str, Dict]:
        return {
            'alfred': {
                'extra_prompt': "...",
                'tools': [...],
                'templates': [...]
            }
        }
```

## 🎯 Uso

Batman automáticamente detecta y carga el módulo apropiado según la tarea:

```bash
batman "compilar aplicación para Windows"
# → Carga módulo 'software'
# → Robin usa windows_interop para compilar

batman "escribir libro sobre Python"
# → Carga módulo 'books' (cuando exista)
# → Alfred y Lucius colaboran con herramientas de escritura
```