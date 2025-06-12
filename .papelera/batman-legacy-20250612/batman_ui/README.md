# 🦇 Batman Enhanced UI

Una interfaz web hermosa y funcional para configurar y monitorear Batman Enhanced.

## 🚀 Características

- **Dashboard Interactivo**: Vista en tiempo real del estado del sistema
- **Wizard de Configuración**: Proceso guiado paso a paso para configurar Batman
- **Gestión de Tareas**: Crear, editar y organizar tareas con interfaz visual
- **Centro de Reportes**: Visualización detallada de análisis y hallazgos
- **Tema Batman**: Diseño oscuro con acentos amarillos inspirado en el Caballero de la Noche
- **Responsive**: Funciona perfectamente en desktop y móvil

## 📋 Requisitos

- Python 3.8+
- Flask
- Batman Enhanced instalado y configurado

## 🔧 Instalación

1. **Navegar al directorio**:
   ```bash
   cd /home/lauta/glados/batman/batman_ui
   ```

2. **Ejecutar el script de inicio**:
   ```bash
   ./start_ui.sh
   ```

3. **Acceder a la interfaz**:
   Abre tu navegador y ve a: `http://localhost:5000`

## 🎯 Uso Rápido

### Primera vez
1. Abre la UI en tu navegador
2. Haz clic en "Configuración Rápida" o ve a `/wizard`
3. Sigue el wizard de 6 pasos
4. Guarda tu configuración
5. ¡Listo! Batman trabajará cada noche

### Dashboard
- Ver estadísticas en tiempo real
- Ejecutar análisis manualmente
- Acceder a acciones rápidas

### Tareas
- Crear tareas desde plantillas
- Importar archivos YAML
- Gestionar prioridades y dependencias

### Reportes
- Ver historial de ejecuciones
- Exportar en múltiples formatos
- Gráficos de tendencias

## 🎨 Estructura de la UI

```
batman_ui/
├── app.py              # Aplicación Flask principal
├── templates/          # Plantillas HTML
│   ├── base.html      # Plantilla base con tema Batman
│   ├── index.html     # Página de inicio
│   ├── dashboard.html # Panel de control
│   ├── wizard.html    # Wizard de configuración
│   ├── config.html    # Configuración detallada
│   ├── tasks.html     # Gestión de tareas
│   └── reports.html   # Centro de reportes
├── static/            # Archivos estáticos (CSS, JS, imágenes)
└── start_ui.sh        # Script de inicio
```

## 🔌 Endpoints API

- `GET /api/config` - Obtener configuración actual
- `POST /api/config` - Actualizar configuración
- `GET /api/tasks` - Listar todas las tareas
- `POST /api/tasks` - Crear nueva tarea
- `DELETE /api/tasks?id=X` - Eliminar tarea
- `POST /api/upload` - Subir archivos
- `POST /api/test` - Ejecutar prueba
- `POST /api/run` - Ejecutar Batman
- `GET /api/stats` - Obtener estadísticas

## 🎭 Características del Tema

- **Colores**: Negro Gotham (#0a0a0a), Amarillo Batman (#FFD700)
- **Fuentes**: Bebas Neue para títulos, Roboto para texto
- **Animaciones**: Transiciones suaves, efectos hover, bat-signal pulsante
- **Easter Egg**: Código Konami activa una animación especial

## 🛡️ Seguridad

- Validación de entrada en todos los formularios
- Sanitización de nombres de archivo
- Sin ejecución directa de comandos desde la UI
- Límite de tamaño para uploads (16MB)

## 🐛 Solución de Problemas

### La UI no inicia
- Verifica que Python 3 esté instalado
- Asegúrate de estar en el directorio correcto
- Revisa que el puerto 5000 esté libre

### No se guardan los cambios
- Verifica permisos en `~/.batman/`
- Revisa los logs de Flask en la terminal

### Los gráficos no se muestran
- Actualiza tu navegador
- Verifica la consola para errores de JavaScript

## 🚀 Desarrollo

Para modo desarrollo con recarga automática:
```bash
export FLASK_DEBUG=1
./start_ui.sh
```

## 📝 Licencia

Parte del proyecto Batman Enhanced. Uso libre para automatización personal.

---

*"It's not who I am underneath, but what I do that defines me."* - Batman