# INFORMACIÓN CRÍTICA DE BACKUPS - REORGANIZACIÓN 2025-06-12

## ⚠️ IMPORTANTE: GUARDAR ESTA INFORMACIÓN

### 📍 UBICACIONES DE BACKUPS

#### 1. BACKUP PRINCIPAL EN DISCO H:
```
/mnt/h/BACKUPS/Glados-Ecosystem/
├── MPC-COMPLETO-20250612_031923.tar.gz         # 404MB - MPC completo
├── scripts-COMPLETO-20250612_031937.tar.gz     # Scripts completos
└── BACKUP_SIN_BATMAN_20250612_031631/          # Backup parcial con rsync
```

#### 2. ARCHIVOS MOVIDOS (NO ELIMINADOS):
```
/home/lauta/glados/.papelera/
├── launchers-legacy-20250612/        # LauncherClaude.bat, .cmd, .ps1, etc.
├── batman-legacy-20250612/           # Carpeta batman/ completa (legacy)
├── decoration-20250612/              # Scripts decoración
├── wrappers-20250612/               # cs-wrapper.sh, cs-tmux-wrapper.sh
├── batman-wrappers-20250612/        # batman-multi, batman-parallel, batman-isolated
├── InfiniteAgent-duplicado-20250612/ # Duplicado que estaba en raíz
├── Papelera-old-20250612/           # Carpeta Papelera antigua
└── ProyectosArchivados/             # Proyectos archivados

```

### 🔄 SISTEMAS MOVIDOS (UBICACIONES NUEVAS):

| Sistema Original | Nueva Ubicación | Estado |
|-----------------|-----------------|---------|
| `scripts/voz/` | `SYSTEM/voice/voz/` | MOVIDO (no hay copia) |
| `scripts/quota/` | `SYSTEM/monitoring/quota/` | MOVIDO (no hay copia) |
| `scripts/cs-fixes/` | `UTILITIES/claude-squad-tools/` | MOVIDO (no hay copia) |
| `MPC/` (raíz) | `UTILITIES/MPC/` | MOVIDO (404MB completos) |
| `InfiniteAgent/` (raíz) | `UTILITIES/InfiniteAgent/` | MOVIDO |

### 🚨 SISTEMAS QUE DEJARON DE FUNCIONAR:

1. **Comando voz original**: `~/glados/scripts/voz/notificar-claude.sh` → NO EXISTE
2. **Scripts quota originales**: En `scripts/quota/` → NO EXISTEN
3. **Launchers en raíz**: LauncherClaude.* → ARCHIVADOS en .papelera
4. **CS fixes**: `scripts/cs-fixes/` → VACÍO

### ✅ SISTEMAS INTACTOS:

- `batman-incorporated/` - NO TOCADO
- `DiskDominator/` - NO TOCADO
- `scripts/launchers/proyecto-menu-v2.sh` - FUNCIONANDO
- `scripts/backup/` - INTACTO
- `scripts/connectivity/` - INTACTO
- `scripts/Copy2Windows/` - INTACTO

### 🔧 PARA RECUPERAR:

#### Recuperar sistema de voz:
```bash
cp -r ~/glados/SYSTEM/voice/voz/* ~/glados/scripts/voz/
```

#### Recuperar launchers:
```bash
cp ~/glados/.papelera/launchers-legacy-20250612/* ~/glados/
```

#### Recuperar desde backup H:
```bash
cd ~/glados
tar -xzf /mnt/h/BACKUPS/Glados-Ecosystem/scripts-COMPLETO-20250612_031937.tar.gz
```

### 📅 TIMESTAMP REORGANIZACIÓN:
- Inicio: 2025-06-12 03:00 CEST
- Fin: 2025-06-12 03:31 CEST
- Duración: 31 minutos

### ⚠️ NOTA CRÍTICA:
El sistema "nuevo" (SYSTEM/ y UTILITIES/) NO FUNCIONA correctamente.
Los symlinks están mal configurados y las rutas no son correctas.
El sistema antiguo fue parcialmente desmantelado.