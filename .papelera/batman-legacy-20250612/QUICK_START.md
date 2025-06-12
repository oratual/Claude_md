# 🚀 Batman Enhanced - Guía de Inicio Rápido

Esta guía te ayudará a configurar Batman Enhanced en menos de 5 minutos.

## 📋 Pre-requisitos

- Ubuntu 20.04+ o WSL2
- Python 3.8+
- Conexión a internet

## ⚡ Instalación Rápida (2 minutos)

```bash
# 1. Ir al directorio de Batman
cd /home/lauta/glados/batman

# 2. Ejecutar instalador
./setup_batman_enhanced.sh

# 3. ¡Listo! Batman Enhanced está instalado
```

## 🎯 Configuración con UI Web (3 minutos)

### Opción A: Wizard Guiado (Recomendado)

```bash
# 1. Iniciar la interfaz web
cd batman_ui
./start_ui.sh

# 2. Abrir navegador
# http://localhost:5000

# 3. Hacer clic en "Configuración Rápida"
# 4. Seguir los 6 pasos del wizard
# 5. Guardar configuración
```

### Opción B: Configuración Manual

```bash
# 1. Copiar configuración de ejemplo
cp config/enhanced_config.yaml.example ~/.batman/config/enhanced_config.yaml

# 2. Editar con tu editor favorito
nano ~/.batman/config/enhanced_config.yaml

# 3. Cambiar estos valores mínimos:
#    - github.repo: "tu-usuario/tu-repo"
#    - analyses.disk_usage.threshold_gb: 50
#    - schedule.cron: "0 3 * * *"
```

## 🏃 Primera Ejecución

### Test Sin Cambios
```bash
# Ejecutar en modo test (no hace cambios)
batman-enhanced --test

# Ver qué haría Batman
```

### Ejecución Real
```bash
# Ejecutar análisis completo
batman-enhanced

# Esperar 2-5 minutos
# Ver reporte generado
```

## 📊 Ver Resultados

### En Terminal
```bash
# Ver último reporte
batman-enhanced --show-report

# Ver logs
tail -f ~/.batman/logs/enhanced_*.log
```

### En UI Web
1. Ir a http://localhost:5000/reports
2. Click en el último reporte
3. Explorar descubrimientos y optimizaciones

## 🌙 Programar Ejecución Nocturna

```bash
# Automático (ya configurado por el instalador)
crontab -l | grep batman

# Manual si necesitas cambiar horario
crontab -e
# Agregar: 0 3 * * * /usr/local/bin/batman-enhanced
```

## 🎨 Personalización Rápida

### Cambiar Análisis
En la UI: Configuración → Análisis → Toggle on/off

### Agregar Tarea
En la UI: Tareas → Nueva Tarea → Usar plantilla

### Integrar GitHub
```bash
# 1. Instalar GitHub CLI
sudo apt install gh

# 2. Autenticar
gh auth login

# 3. En UI: Configuración → GitHub → Habilitar
```

## ❓ Comandos Útiles

```bash
# Ver ayuda
batman-enhanced --help

# Estado del sistema
batman-enhanced --status

# Ejecutar tarea específica
batman-enhanced --task cleanup_logs

# Ver versión
batman-enhanced --version
```

## 🚨 Solución Rápida de Problemas

### "Comando no encontrado"
```bash
sudo ln -s $(pwd)/batman_enhanced_night.py /usr/local/bin/batman-enhanced
```

### "Puerto 5000 en uso"
```bash
FLASK_PORT=5001 ./batman_ui/start_ui.sh
```

### "No se ejecuta de noche"
```bash
# Verificar cron
crontab -l
systemctl status cron
```

## 📚 Próximos Pasos

1. **Explorar UI Web**: Dashboard, estadísticas, gráficos
2. **Crear Tareas**: Automatiza más procesos
3. **GitHub Issues**: Activa para tracking automático
4. **Leer Docs**: `docs/COMPLETE_DOCUMENTATION.md`

## 🎉 ¡Felicidades!

Batman Enhanced está protegiendo tu sistema. Duerme tranquilo sabiendo que Batman trabaja por ti.

---

**¿Necesitas ayuda?** 
- Documentación completa: `docs/COMPLETE_DOCUMENTATION.md`
- Reportar issues: GitHub Issues
- UI Web: http://localhost:5000

*"I am the night!"* 🦇