# Batman Enhanced 🦇

Sistema avanzado de automatización nocturna que permite a Claude Code trabajar toda la noche con tareas complejas. Incluye análisis inteligente, optimizaciones automáticas, integración con GitHub y una hermosa interfaz web.

## 🚀 Características Principales

### Sistema Base
- 🌙 Ejecución nocturna automática sin supervisión
- 🤖 Integración con Claude Code para análisis inteligente
- 📝 Tareas definidas en YAML con dependencias
- 🔄 Reintentos automáticos y recuperación de errores
- 📊 Logging completo y reportes detallados
- 🔧 Optimizaciones seguras del sistema

### Batman Enhanced
- 🔍 **Análisis Inteligente**: Disco, logs, seguridad, rendimiento
- 🚀 **Optimizaciones Automáticas**: Limpieza, compresión, git
- 🐙 **GitHub Integration**: Issues y PRs automáticos
- 🔌 **MCP Support**: Filesystem, Memory, Git, Sequential Thinking
- 📈 **Reportes Detallados**: JSON, Markdown, visualizaciones
- 🎨 **UI Web**: Interfaz gráfica con tema Batman

### Interfaz Web
- 🎯 **Wizard de Configuración**: 6 pasos guiados
- 📊 **Dashboard**: Estadísticas en tiempo real
- 📋 **Gestión de Tareas**: Editor visual con plantillas
- 📈 **Centro de Reportes**: Gráficos y exportación
- 🦇 **Tema Batman**: Diseño oscuro profesional

## Arquitectura

```
batman/
├── src/              # Código fuente principal
├── config/           # Configuraciones
├── tasks/            # Archivos de tareas (.txt)
├── logs/             # Logs de ejecución
├── scripts/          # Scripts auxiliares
└── tests/            # Tests automatizados
```

## 🔧 Instalación

### Instalación Rápida
```bash
cd /home/lauta/glados/batman
./setup_batman_enhanced.sh
```

### Instalación Manual
```bash
# 1. Instalar dependencias
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git tmux

# 2. Instalar herramientas avanzadas (opcional pero recomendado)
sudo apt-get install -y ripgrep fd-find bat jq

# 3. Configurar Batman Enhanced
cd /home/lauta/glados/batman
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Crear estructura de directorios
mkdir -p ~/.batman/{tasks,logs,reports,rules,templates}

# 5. Copiar configuración inicial
cp config/enhanced_config.yaml.example ~/.batman/enhanced_config.yaml
```

## 🎯 Uso Rápido

### Opción 1: Interfaz Web (Recomendado)
```bash
# Iniciar la UI
cd batman_ui
./start_ui.sh

# Abrir en navegador: http://localhost:5000
# Usar el wizard para configuración inicial
```

### Opción 2: Línea de Comandos
```bash
# Ejecutar en modo test (sin cambios)
batman-enhanced --test

# Ejecutar análisis completo
batman-enhanced

# Solo análisis sin optimizaciones
batman-enhanced --analyze-only

# Ver ayuda
batman-enhanced --help
```

### Definir Tareas

#### Formato YAML (Recomendado)
Crear archivo en `~/.batman/tasks/maintenance.yaml`:
```yaml
tasks:
  - id: cleanup_logs
    title: "Limpieza de logs antiguos"
    type: maintenance
    priority: 3
    schedule: "0 3 * * *"  # 3:00 AM diario
    command: |
      #!/bin/bash
      find /var/log -name "*.log" -mtime +30 -delete
      find /tmp -type f -atime +7 -delete
    retry_count: 3
    timeout: 300
    
  - id: analyze_security
    title: "Análisis de seguridad"
    type: analysis
    priority: 2
    prompt: |
      Analiza los logs del sistema en busca de:
      - Intentos de acceso no autorizado
      - Patrones sospechosos
      - Vulnerabilidades potenciales
      Genera un reporte con recomendaciones.
    dependencies: []
```

## 🌙 Configuración Nocturna

### Automatización con Cron
```bash
# El setup ya configura esto automáticamente
crontab -l | grep batman

# O configurar manualmente
crontab -e
# Agregar:
0 3 * * * /home/lauta/.local/bin/batman-enhanced >> ~/.batman/logs/cron.log 2>&1
```

## 📊 Reportes y Monitoreo

### Ver Último Reporte
```bash
# JSON detallado
cat ~/.batman/reports/latest.json | jq

# Resumen en texto
batman-enhanced --show-report

# En la UI web
http://localhost:5000/reports
```

### Logs en Tiempo Real
```bash
# Ver logs de la última ejecución
tail -f ~/.batman/logs/enhanced_*.log

# Buscar errores
grep ERROR ~/.batman/logs/*.log
```

## 🎨 Interfaz Web

Batman Enhanced incluye una interfaz web completa con tema Batman:

### Características de la UI
- **Dashboard**: Vista general con estadísticas en tiempo real
- **Wizard de 6 Pasos**: Configuración guiada e intuitiva
- **Editor de Tareas**: Crear y gestionar tareas visualmente
- **Centro de Reportes**: Visualizaciones y exportación
- **Tema Oscuro**: Diseño profesional inspirado en Batman
- **Responsive**: Funciona en desktop y móvil

### Capturas de Pantalla
- Wizard paso a paso con validación
- Dashboard con métricas y gráficos
- Gestión visual de tareas con drag & drop
- Reportes detallados con timeline

## 🔒 Seguridad

- **Modo Seguro**: Solo cambios reversibles
- **Límites Estrictos**: Máx 10 archivos por operación
- **Sin Comandos Arbitrarios**: Lista blanca de operaciones
- **Logs Completos**: Auditoría de todas las acciones
- **Validación de Entrada**: En UI y CLI

## 🤝 Integración con GitHub

```bash
# Configurar GitHub CLI (una vez)
gh auth login

# Batman creará automáticamente:
- Issues para hallazgos críticos
- PRs draft con optimizaciones
- Reportes diarios como issues
- Labels y milestones organizados
```

## 📚 Documentación Adicional

- `CLAUDE.md` - Guía de desarrollo detallada
- `batman_ui/README.md` - Documentación de la UI
- `docs/IDEAS-DETALLADAS.md` - Roadmap y características futuras
- `BATMAN_IMPLEMENTATION_SUMMARY.md` - Resumen técnico completo

## 🐛 Solución de Problemas

### Batman no se ejecuta
```bash
# Verificar instalación
which batman-enhanced

# Ver logs
tail -f ~/.batman/logs/enhanced_*.log

# Ejecutar en modo debug
batman-enhanced --debug
```

### La UI no inicia
```bash
# Verificar puerto
lsof -i :5000

# Reinstalar dependencias
cd batman_ui
rm -rf venv
./start_ui.sh
```

## 🚀 Contribuir

1. Fork el proyecto
2. Crear feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📝 Licencia

Proyecto personal de automatización. Uso libre para fines no comerciales.

---

*"I am vengeance. I am the night. I am Batman!"* 🦇