# Nueva Estructura GLADOS - Reorganización 2025-06-12

## 📁 Estructura Principal

```
~/glados/
├── 🦇 batman-incorporated/    # Sistema principal (NO MOVIDO - EN USO)
├── 💾 DiskDominator/          # Producto comercial (NO TOCADO)
├── 📦 UTILITIES/              # Herramientas consolidadas
│   ├── MPC/                   # Servidores MCP (404MB)
│   ├── InfiniteAgent/         # Monitor paralelización
│   ├── batman-incorporated/   # Copia de respaldo
│   └── claude-squad-tools/    # Herramientas CS
├── 🎛️ SYSTEM/                 # Sistema core
│   ├── launcher/              # Launcher unificado
│   ├── voice/                 # Sistema de voz
│   ├── monitoring/            # Quota y status
│   └── config/                # Configuración central
├── 📜 scripts/                # Scripts organizados
│   ├── Copy2Windows/          # Sincronización Windows
│   ├── backup/                # Scripts backup
│   ├── connectivity/          # WSL2-Windows
│   └── launchers/             # Launchers legacy
├── 📚 docs/                   # Documentación
├── 🔧 setups/                 # Scripts instalación
└── 🗑️ .papelera/              # Archivos archivados

```

## 🚀 Accesos Directos

- `~/glados/launcher` → `SYSTEM/launcher/main-launcher.sh`
- `~/glados/voz-claude` → `SYSTEM/voice/voz/notificar-claude.sh`

## 📊 Cambios Realizados

### ✅ Consolidaciones
- **Launchers**: 8+ diferentes → 1 unificado
- **Wrappers**: 18 → 12 (6 eliminados)
- **Scripts**: Reorganizados por función
- **C2W**: 1 proyecto → 6 proyectos configurados

### 🗂️ Migraciones
- `scripts/voz/` → `SYSTEM/voice/`
- `scripts/quota/` → `SYSTEM/monitoring/`
- `scripts/cs-fixes/` → `UTILITIES/claude-squad-tools/`
- `MPC/` → `UTILITIES/MPC/`
- `InfiniteAgent/` → `UTILITIES/InfiniteAgent/`

### 🗑️ Archivados
- `batman/` → `.papelera/batman-legacy-20250612/`
- `LauncherClaude*` → `.papelera/launchers-legacy-20250612/`
- `ProyectosArchivados/` → `.papelera/`
- Wrappers obsoletos → `.papelera/wrappers-20250612/`

## 🔧 Configuración Central

Archivo: `SYSTEM/config/glados.conf`
- Rutas de todos los componentes
- Configuración de Windows sync
- Features habilitados

## 💡 Uso

### Launcher Principal
```bash
~/glados/launcher
# O directamente:
~/glados/SYSTEM/launcher/main-launcher.sh
```

### Sistema de Voz
```bash
~/glados/voz-claude
# O directamente:
~/glados/SYSTEM/voice/voz/notificar-claude.sh
```

### Copy2Windows
```bash
c2w menu        # Menú interactivo
c2w sync MPC    # Sincronizar proyecto específico
c2w list        # Ver proyectos configurados
```

### Monitor Sistema
```bash
~/glados/SYSTEM/monitoring/system-status.sh
```

## ⚠️ Componentes NO Tocados

1. **batman-incorporated/** - En uso activo durante reorganización
2. **DiskDominator/** - Producto comercial, requiere estabilidad

## 📅 Realizado

- Fecha: 2025-06-12
- Hora: 03:00 - 06:00 CEST
- Protocolo: Antisueño activo
- Duración: 3 horas continuas