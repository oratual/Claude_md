# Batman - Tareas Pendientes para Operatividad

## Estado Actual
- ✅ Dream mode implementado (análisis creativo)
- ✅ Morning report implementado (reportes matutinos)
- ❌ Sistema core de ejecución de tareas NO implementado

## Tareas Prioritarias (High)

### 1. Parser de Tareas (`src/parser.py`)
- Leer archivos .txt del directorio `tasks/`
- Validar sintaxis (TASK, SCHEDULE, COMMAND, etc.)
- Retornar objetos Task

### 2. Ejecutor de Comandos (`src/executor.py`)
- Ejecutar comandos con subprocess
- Implementar timeouts
- Sistema de reintentos configurables
- Capturar output y errores

### 3. Scheduler (`src/scheduler.py`)
- Integración con cron de Linux
- Parsear expresiones cron
- Manejar tareas perdidas

### 4. CLI Principal (`batman`)
- Comandos: start, stop, status, run, validate
- Modo daemon vs ejecución única
- Integración con systemd/cron

### 5. Requirements (`requirements.txt`)
```
apscheduler>=3.10.0
pyyaml>=6.0
click>=8.0
croniter>=1.3.0
```

## Tareas Secundarias (Medium)

### 6. Manejo de Errores (`src/error_handler.py`)
- Estrategias de fallback
- Notificaciones (log por ahora)
- Decisiones automáticas sin bloqueo

### 7. Sistema de Logs (`src/logger.py`)
- Rotación automática
- Diferentes niveles por componente
- Formato estructurado

### 8. Script de Instalación (`scripts/install.sh`)
- Crear directorios necesarios
- Instalar dependencias
- Configurar permisos
- Setup de cron

## Tareas Futuras (Low)

### 9. Tests (`tests/`)
- Tests unitarios con pytest
- Mocks para system calls
- Cobertura > 80%

### 10. Integración Dream Mode
- Conectar insights del dream mode con el scheduler
- Auto-optimización basada en patrones detectados

## Próximos Pasos

1. Crear `requirements.txt` con las dependencias
2. Implementar `parser.py` básico
3. Crear `executor.py` con reintentos
4. Desarrollar CLI mínimo funcional
5. Probar con `tasks/example-maintenance.txt`

## Notas
- Ambiente: WSL2 Ubuntu con cron disponible
- Python 3.10+ ya instalado
- Priorizar funcionalidad core sobre features avanzadas