# PROJECT_CREATION.md - Guía de Creación de Proyectos

Esta guía contiene todo lo necesario para crear nuevos proyectos con las mejores prácticas.

## 🚀 Comandos Rápidos por Tipo de Proyecto

### Web App (Next.js/React)
```bash
# Opción 1: Con menú interactivo
~/glados/scripts/launchers/proyecto-menu-v2.sh

# Opción 2: Directo
cd ~/mi-proyecto && npx create-next-app@latest . --typescript --tailwind --app
```

### API REST (Node.js)
```bash
mkdir mi-api && cd mi-api
npm init -y
npm install express cors dotenv
npm install -D typescript @types/node @types/express nodemon ts-node
```

### Python Project
```bash
mkdir mi-proyecto && cd mi-proyecto
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### CLI Tool
```bash
mkdir mi-cli && cd mi-cli
npm init -y
npm install commander chalk
chmod +x index.js
```

## 📁 Estructura de Proyectos Estándar

```
proyecto/
├── CLAUDE.md           # Instrucciones específicas del proyecto
├── historialDeProyecto.md  # CRÍTICO: Siempre inicializar
├── README.md           # Solo si es necesario
├── src/                # Código fuente
├── tests/              # Pruebas
├── docs/               # Documentación
└── scripts/            # Scripts de utilidad
```

## 🔧 Automatización con Automator

### Setup Completo de Proyecto
```bash
# Inicializar proyecto con mejores prácticas
~/glados/setups/automator/01-setup/scripts/setup-completo.sh

# Crear proyecto con plantilla
~/glados/setups/automator/01-setup/scripts/crear-proyecto.sh "NombreProyecto"
```

### Herramientas del Toolkit
```bash
# Instalar todas las herramientas avanzadas
~/glados/setups/automator/02-toolkit/install.sh

# Verificar instalación
check-tools
```

## 📊 Protocol - Historial Persistente (CRÍTICO)

```bash
# SIEMPRE al iniciar un proyecto nuevo
cd /ruta/al/proyecto
~/glados/setups/automator/06-protocol/scripts/init-project-history.sh "NombreProyecto" "Objetivo del proyecto"

# Actualizar después de cambios importantes
~/glados/setups/automator/06-protocol/scripts/update-project-history.sh "Implementé feature X"
```

## 🎯 Proyectos Especiales

### DiskDominator (Gestión de Discos)
```bash
cd ~/glados/DiskDominator
npm install
npm run dev -- --host 0.0.0.0  # Para acceso desde Windows
```

### Batman (Automatización Nocturna)
```bash
cd ~/glados/batman
source venv/bin/activate  # Si usa venv
python batman.py
```

### Suite Standards (Aplicaciones Tipo Office)
```bash
~/glados/setups/automator/05-suite-standards/create-suite.sh "MiSuite"
```

## 🔌 Integración con Servicios

### GitHub
```bash
# Asegurar SSH activo
source ~/1p_env_setup.sh
ssh -T git@github.com

# Inicializar repo
git init
git remote add origin git@github.com:usuario/repo.git
```

### Desarrollo Web con Acceso desde Windows
```bash
# Siempre bind a 0.0.0.0
npm run dev -- --host 0.0.0.0

# Verificar IP para acceder desde Windows
~/glados/scripts/check-connectivity.sh
```

### MCP Servers
```bash
# Para desarrollo de MCP servers
cd ~/glados/MPC/source/custom/mi-mcp
npm init -y
npm install @modelcontextprotocol/sdk

# Ejecutar con binding correcto
node server.js --host 0.0.0.0 --port 5000
```

## 📋 Checklist para Proyecto Nuevo

- [ ] Crear directorio del proyecto
- [ ] Inicializar historialDeProyecto.md con Protocol
- [ ] Crear CLAUDE.md específico del proyecto
- [ ] Setup Git con .gitignore apropiado
- [ ] Instalar dependencias base
- [ ] Configurar scripts en package.json
- [ ] Verificar conectividad si es web/API
- [ ] Commit inicial

## 🛠️ Templates Disponibles

```bash
# Ver templates disponibles
ls ~/glados/setups/automator/03-templates/

# Copiar template
cp -r ~/glados/setups/automator/03-templates/web-app/* ./
```

## ⚡ Scripts Útiles de Proyecto

### Sincronización con Windows
```bash
# Script para sincronizar archivos con Windows
~/glados/MPC/scripts/sync-to-windows.sh
```

### Testing de Conectividad
```bash
# Para proyectos web
curl http://$(~/glados/scripts/check-connectivity.sh | grep "WSL2 IP" | awk '{print $3}'):3000
```

## 🎨 Mejores Prácticas

1. **Siempre** inicializar Protocol (historialDeProyecto.md)
2. **Usar** herramientas modernas (rg, fd, bat) en scripts
3. **Documentar** en CLAUDE.md específico del proyecto
4. **Bind** servicios a 0.0.0.0 para acceso desde Windows
5. **Commitear** frecuentemente con mensajes descriptivos
6. **NO** crear README.md a menos que sea necesario

## 🔗 Referencias

- Automator completo: `~/glados/setups/automator/`
- Scripts útiles: `~/glados/scripts/`
- Ejemplos de proyectos: `~/glados/mi-proyecto-demo/`
- Batman docs: `~/glados/batman/docs/`