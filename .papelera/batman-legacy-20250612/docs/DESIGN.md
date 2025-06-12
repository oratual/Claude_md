# Batman - Diseño del Sistema

## Filosofía del Proyecto

Batman opera bajo el principio de **"Set and Forget"** - configuras las tareas y el sistema se encarga del resto sin intervención humana.

## Arquitectura Propuesta

```
┌─────────────────┐     ┌──────────────┐     ┌──────────────┐
│   Task Files    │────▶│    Parser    │────▶│  Task Queue  │
│  (.txt files)   │     │              │     │              │
└─────────────────┘     └──────────────┘     └──────┬───────┘
                                                     │
                                                     ▼
┌─────────────────┐     ┌──────────────┐     ┌──────────────┐
│     Logger      │◀────│   Executor   │◀────│  Scheduler   │
│                 │     │              │     │              │
└─────────────────┘     └──────┬───────┘     └──────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │Error Handler │
                        │              │
                        └──────────────┘
```

## Componentes Principales

### 1. Task Parser
- Lee archivos .txt con definiciones de tareas
- Valida sintaxis y parámetros
- Convierte a objetos Task internos

### 2. Scheduler
- Gestiona cuándo ejecutar cada tarea
- Maneja cron expressions
- Persiste estado entre reinicios

### 3. Executor
- Ejecuta comandos de forma segura
- Implementa timeouts
- Gestiona reintentos
- Captura salida y errores

### 4. Error Handler
- Decide qué hacer cuando falla una tarea
- Opciones: continue, stop, notify
- Nunca detiene el sistema por errores

### 5. Logger
- Registra toda actividad
- Rotación automática de logs
- Diferentes niveles de detalle

## Flujo de Ejecución

1. **Inicio**: Batman lee todos los archivos de tareas
2. **Validación**: Verifica sintaxis y permisos
3. **Scheduling**: Programa tareas según su schedule
4. **Ejecución**: Cuando llega la hora, ejecuta la tarea
5. **Manejo de Resultados**:
   - Éxito → Log y continuar
   - Fallo → Reintentar según configuración
   - Fallo final → Ejecutar acción ON_ERROR
6. **Loop**: Volver a esperar siguiente tarea

## Decisiones de Diseño

### Sin Intervención Humana
- Todas las decisiones se toman automáticamente
- Los defaults son seguros y conservadores
- Los errores se loguean pero no detienen el sistema

### Seguridad
- Validación estricta de comandos
- Sin ejecución de código arbitrario
- Timeouts obligatorios
- Ejecución con permisos mínimos

### Robustez
- Reintentos configurables
- Graceful shutdown
- Recuperación ante caídas
- Estado persistente

### Simplicidad
- Archivos de texto plano para tareas
- Sin dependencias complejas
- Fácil de debuggear
- Logs legibles

## Casos de Uso

1. **Mantenimiento del Sistema**
   - Limpieza de logs
   - Rotación de archivos
   - Actualizaciones de índices

2. **Backups Automatizados**
   - Bases de datos
   - Configuraciones
   - Archivos importantes

3. **Monitoreo**
   - Espacio en disco
   - Servicios activos
   - Logs de seguridad

4. **Optimización**
   - Desfragmentación
   - Limpieza de caché
   - Compactación de DBs

## Manejo de Errores

### Estrategias por Tipo de Error

1. **Command Not Found**
   - Log error
   - Marcar tarea como fallida
   - Continuar con siguientes

2. **Timeout**
   - Terminar proceso
   - Reintentar si está configurado
   - Log con duración

3. **Permission Denied**
   - No reintentar
   - Log crítico
   - Notificar si está configurado

4. **System Resources**
   - Esperar antes de reintentar
   - Reducir concurrencia
   - Modo degradado

## Extensibilidad

El sistema está diseñado para ser extensible:

- Nuevos tipos de schedule
- Plugins para notificaciones
- Hooks pre/post ejecución
- Integración con sistemas externos