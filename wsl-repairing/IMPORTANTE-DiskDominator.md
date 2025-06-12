# ⚠️ IMPORTANTE: DiskDominator - Versiones Separadas

## Situación actual

### 1. **Versión Windows** (K:\_Glados\DiskDominator)
- Contiene archivos específicos de Windows (.bat, .hta, .ps1)
- Configuración para compilar con Visual Studio
- Scripts de build para Windows
- **BACKUP COMPLETO**: H:\Backup\WSL\2025-06-12\DiskDominator-Windows-EMERGENCY-BACKUP\ (472MB)

### 2. **Versión Linux** (~/glados/DiskDominator)
- Versión de desarrollo/Linux
- También tiene archivos .bat (18) pero pueden ser diferentes
- Usado para desarrollo en WSL

## ✅ Acciones tomadas

1. **Backup de emergencia completado** - 472MB salvados en H:
2. **DiskDominator EXCLUIDO de c2w** - No se volverá a sobrescribir
3. **Verificación**: Los archivos .bat existen en ambas versiones (misma cantidad)

## 📋 Recomendaciones

### Para trabajar con DiskDominator:

1. **En Windows**: Usar siempre K:\_Glados\DiskDominator
2. **En Linux/WSL**: Usar ~/glados/DiskDominator
3. **NO sincronizar** entre ambas versiones con c2w

### Si necesitas sincronizar cambios específicos:
```bash
# Copiar archivo individual de Linux a Windows
cp ~/glados/DiskDominator/archivo.tsx /mnt/k/_Glados/DiskDominator/

# O al revés
cp /mnt/k/_Glados/DiskDominator/archivo.tsx ~/glados/DiskDominator/
```

### Para recuperar la versión Windows original:
```bash
# Restaurar desde backup
cp -r /mnt/h/Backup/WSL/2025-06-12/DiskDominator-Windows-EMERGENCY-BACKUP/* /mnt/k/_Glados/DiskDominator/
```

## ⚠️ NUNCA hacer:
- `c2w sync DiskDominator` (está deshabilitado ahora)
- Sincronización automática entre versiones
- Mezclar configuraciones Windows/Linux

---
Fecha: 2025-06-12
Incidente: Sobrescritura accidental por c2w
Estado: RESUELTO - Backup seguro en H: