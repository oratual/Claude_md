# Instrucciones de Edición - WSL Restore Tools

## 📁 Estructura del Sistema

### Ubicaciones Principales
```
~/glados/wsl-repairing/                    # Base en Linux
├── restauracion-modular/                  # Scripts principales
│   ├── backup-modular.sh                 # Script de backup
│   ├── restore-modular.sh                # Script de restauración
│   └── post-install.sh                   # Para reinstalación completa
├── wsl-health-monitor.sh                 # Monitor de salud
├── bitacora.md                          # Log de cambios realizados
└── INSTRUCCIONES-EDICION.md             # Este archivo

C:\Users\lauta\Desktop\AppsWSL\WSL-Restore-Tools\  # Copia en Windows
├── RUN-MENU-v3.bat                      # Lanzador principal
├── WSL-Menu-v3.0.ps1                    # Menú PowerShell
└── [copias de los scripts .sh]
```

### Estructura de Backups
```
H:\Backup\WSL\
├── 2025-06-12\                          # Archivos críticos (fecha específica)
│   ├── DiskDominator-Windows-*          # Versión Windows salvada
│   └── *.backup                         # Configs críticas
├── system\                              # Configuraciones WSL
│   └── [fecha]\                         # Por fecha
│       ├── dotfiles.tar.gz              # .bashrc, .gitconfig, etc
│       └── packages.list                # Lista de paquetes
├── projects\                            # Proyectos individuales
│   ├── batman-incorporated\
│   ├── scripts\
│   └── [proyecto]\
│       └── [fecha]\
└── full\                                # Exports completos WSL
    └── Ubuntu-24.04-*.tar
```

## 🔧 Problemas Comunes y Soluciones

### 1. Caracteres Corruptos en Archivos .bat
**Problema**: Al copiar desde WSL a Windows, los caracteres especiales se corrompen
```
"rificar" no se reconoce como un comando interno...
```

**Solución**:
- NO usar emojis ni caracteres Unicode en .bat
- Usar PowerShell (.ps1) en su lugar
- Si necesitas .bat, mantenerlo simple con ASCII puro

### 2. Errores de Sintaxis PowerShell
**Problema**: Llaves faltantes, comillas mal cerradas
```
Token '}' inesperado en la expresión...
```

**Solución**:
- Evitar caracteres especiales en strings
- Usar comillas simples para paths: `'H:\Backup\WSL\'`
- Verificar que todas las llaves { } estén balanceadas

### 3. Rutas No Encontradas
**Problema**: "No existe la carpeta system/projects"

**Solución**:
```bash
# Crear estructura completa
mkdir -p /mnt/h/Backup/WSL/{system,projects,full}
```

### 4. DiskDominator - Versiones Mezcladas
**Problema**: c2w sobrescribió versión Windows con Linux

**Solución**:
- DiskDominator está EXCLUIDO en `projects.conf`
- Mantener versiones separadas:
  - Windows: K:\_Glados\DiskDominator
  - Linux: ~/glados/DiskDominator

## 📝 Cosas a Recordar

### Versionado
- Usar números de versión en archivos: `WSL-Menu-v3.0.ps1`
- Eliminar versiones antiguas para evitar confusión
- El actual es v3.0 (sin caracteres especiales)

### Logs y Debugging
- PowerShell guarda logs en: `%USERPROFILE%\WSL-Restore-Tools.log`
- Bitácora de cambios: `~/glados/wsl-repairing/bitacora.md`
- Siempre actualizar bitácora después de cambios importantes

### Scripts Críticos
1. **backup-modular.sh**: 
   - Sin emojis en el menú
   - Secciones claras: CONFIGURACION WSL / PROYECTOS
   - Solo pide Enter una vez

2. **WSL-Menu-v3.0.ps1**:
   - Sin caracteres Unicode
   - Muestra rutas completas
   - Auto-crea carpetas faltantes

### Comandos Útiles
```bash
# Verificar backups existentes
ls -la /mnt/h/Backup/WSL/

# Copiar scripts actualizados a Windows
cp ~/glados/wsl-repairing/restauracion-modular/*.sh \
   /mnt/c/Users/lauta/Desktop/AppsWSL/WSL-Restore-Tools/

# Test rápido del menú
wsl.exe bash -c "~/glados/wsl-repairing/wsl-health-monitor.sh"
```

## ⚠️ NO HACER

1. **NO** usar `c2w sync DiskDominator` - está excluido por buenas razones
2. **NO** mezclar archivos .bat con caracteres UTF-8/Unicode
3. **NO** asumir que las carpetas existen - siempre verificar/crear
4. **NO** usar rutas relativas en scripts de Windows

## 🚀 Para Continuar Trabajando

Si vuelves después de tiempo:
1. Lee `bitacora.md` para ver último estado
2. Ejecuta opción 7 del menú (Diagnóstico) para verificar rutas
3. Revisa que DiskDominator siga excluido en `projects.conf`
4. Verifica versión actual del menú (debe ser v3.0 o superior)

---
Última actualización: 2025-06-12
Por: Claude (sesión de estabilización WSL)