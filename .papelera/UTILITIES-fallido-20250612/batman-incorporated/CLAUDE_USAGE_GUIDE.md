# 🤖 Guía para que Claude use Batman CORRECTAMENTE

## ⚡ REGLAS CRÍTICAS PARA CLAUDE

1. **SIEMPRE usar --real-agents** para tareas reales
2. **NUNCA simular** - Batman debe hacer trabajo real
3. **ESPECIFICAR el modo** apropiado (safe, fast, infinity)
4. **INCLUIR contexto** con --context
5. **USAR módulos** cuando aplique

## 🎯 Plantillas de Uso OBLIGATORIAS

### Para Desarrollo de Software
```bash
cd ~/glados/batman-incorporated && ./batman-parallel proyecto \
  "desarrollar [descripción específica]" \
  --real-agents \
  --mode safe \
  --context "$(pwd)" \
  --module software
```

### Para Compilación Windows
```bash
cd ~/glados/batman-incorporated && ./batman-parallel build \
  "compilar [proyecto] para Windows usando el módulo software" \
  --real-agents \
  --mode fast \
  --context "[ruta-proyecto]" \
  --module software
```

### Para Testing Multiplataforma
```bash
cd ~/glados/batman-incorporated && ./batman-parallel test \
  "ejecutar tests en Linux y Windows para [proyecto]" \
  --real-agents \
  --mode safe \
  --context "[ruta-proyecto]" \
  --module software
```

### Para Tareas Complejas/Largas
```bash
cd ~/glados/batman-incorporated && ./batman \
  "[descripción detallada de la tarea]" \
  --real-agents \
  --mode infinity \
  --agents 5 \
  --timeout 3600
```

## 📋 Checklist ANTES de Ejecutar Batman

### ✅ ¿Especificaste --real-agents?
Sin esto, Batman solo simula. SIEMPRE incluirlo.

### ✅ ¿Elegiste el modo correcto?
- **safe**: Para desarrollo normal (git worktrees)
- **fast**: Para cambios rápidos en un solo archivo
- **infinity**: Para tareas largas con múltiples agentes
- **redundant**: Para tareas críticas con verificación

### ✅ ¿Incluiste contexto?
```bash
--context "$(pwd)"  # Directorio actual
--context "/home/lauta/glados/DiskDominator"  # Proyecto específico
```

### ✅ ¿Necesitas un módulo?
```bash
--module software  # Para desarrollo, Windows, Office
--module books     # Para escribir documentación (futuro)
--module data      # Para análisis de datos (futuro)
```

### ✅ ¿Múltiples instancias?
Usa `batman-parallel` en lugar de `batman`:
```bash
./batman-parallel nombre-proyecto "tarea" --real-agents
```

## 🚀 Ejemplos COMPLETOS Reales

### 1. Compilar DiskDominator para Windows
```bash
cd ~/glados/batman-incorporated && ./batman-parallel diskdom \
  "compilar DiskDominator para Windows. El proyecto está en /home/lauta/glados/DiskDominator. 
   Usar el módulo software para compilación Tauri. 
   Generar instalador .msi y .exe.
   Verificar que todas las dependencias estén instaladas." \
  --real-agents \
  --mode safe \
  --context "/home/lauta/glados/DiskDominator" \
  --module software
```

### 2. Desarrollar Feature Compleja
```bash
cd ~/glados/batman-incorporated && ./batman \
  "implementar sistema de autenticación OAuth2 con Google y GitHub.
   Incluir:
   - Backend endpoints en Node.js/Express
   - Frontend con React hooks
   - Tests unitarios y de integración
   - Documentación de API
   - Migration de base de datos" \
  --real-agents \
  --mode infinity \
  --agents 5 \
  --context "$(pwd)" \
  --verbose
```

### 3. Refactorización Grande
```bash
cd ~/glados/batman-incorporated && ./batman \
  "refactorizar toda la capa de datos para usar Repository Pattern.
   Migrar de acceso directo a BD a repositorios.
   Mantener retrocompatibilidad.
   Actualizar todos los tests.
   Documentar cambios." \
  --real-agents \
  --mode safe \
  --redundant \
  --context "$(pwd)"
```

### 4. Generar Documentación Completa
```bash
cd ~/glados/batman-incorporated && ./batman-parallel docs \
  "generar documentación completa del proyecto:
   - README.md actualizado
   - Documentación de API con ejemplos
   - Guías de instalación para Windows/Linux/Mac
   - Diagramas de arquitectura
   - Ejemplos de uso" \
  --real-agents \
  --mode fast \
  --context "$(pwd)"
```

## 🔧 Flags Importantes que Claude DEBE Conocer

### Flags Esenciales
- `--real-agents`: OBLIGATORIO para trabajo real
- `--mode [safe|fast|infinity|redundant]`: Modo de ejecución
- `--context [path]`: Directorio del proyecto
- `--module [name]`: Cargar módulo específico

### Flags de Control
- `--agents N`: Número de agentes para infinity mode
- `--timeout N`: Tiempo máximo en segundos
- `--verbose`: Salida detallada
- `--dry-run`: Ver plan sin ejecutar

### Flags de Configuración
- `--config [file]`: Usar config personalizada
- `--no-monitor`: Sin monitor web
- `--force`: Forzar ejecución sin confirmación

## ❌ Errores Comunes de Claude

### 1. NO hacer esto:
```bash
# MAL - Sin --real-agents
batman "compilar proyecto"

# MAL - Sin contexto
batman "desarrollar feature" --real-agents

# MAL - Modo incorrecto
batman "tarea rápida" --real-agents --mode infinity
```

### 2. SIEMPRE hacer esto:
```bash
# BIEN - Completo
cd ~/glados/batman-incorporated && ./batman-parallel proyecto \
  "descripción clara y específica" \
  --real-agents \
  --mode safe \
  --context "/ruta/al/proyecto" \
  --module software
```

## 📊 Cuándo Usar Cada Modo

### Safe Mode (DEFAULT)
- ✅ Desarrollo normal
- ✅ Múltiples archivos
- ✅ Necesitas rollback
- ✅ Trabajo en equipo

### Fast Mode
- ✅ Hotfixes
- ✅ Un solo archivo
- ✅ Cambios urgentes
- ❌ NO para refactoring grande

### Infinity Mode
- ✅ Tareas > 1 hora
- ✅ Múltiples componentes
- ✅ Requiere coordinación
- ✅ Desarrollo paralelo

### Redundant Mode
- ✅ Código crítico
- ✅ Necesitas verificación
- ✅ Múltiples enfoques
- ❌ NO para prototipos

## 🎨 Plantilla para Claude - COPIAR Y ADAPTAR

```bash
# PLANTILLA BASE - ADAPTAR SEGÚN NECESIDAD
cd ~/glados/batman-incorporated && ./batman-parallel [PROYECTO] \
  "[DESCRIPCIÓN DETALLADA DE LA TAREA.
    Incluir:
    - Objetivo principal
    - Requisitos específicos  
    - Tecnologías a usar
    - Resultado esperado]" \
  --real-agents \
  --mode [safe|fast|infinity|redundant] \
  --context "[RUTA_PROYECTO]" \
  --module [software|none] \
  [--agents N] \
  [--timeout N] \
  [--verbose]
```

## 🚨 RECORDATORIO FINAL

1. **Batman puede hacer TODO** - úsalo completamente
2. **--real-agents** es OBLIGATORIO
3. **Contexto específico** = mejores resultados
4. **Modo apropiado** = eficiencia máxima
5. **Módulos** = capacidades especializadas

Si Claude no está usando estas características, NO está aprovechando Batman.