# Acceso a /home/lauta/glados desde Windows

## ⚠️ IMPORTANTE: Depende del estado de WSL

### Si WSL funciona (aunque sea parcialmente):
- **Ruta**: `\\wsl.localhost\Ubuntu-24.04\home\lauta\glados`
- **Alternativa**: `\\wsl$\Ubuntu-24.04\home\lauta\glados`
- Puedes navegar con Explorer o copiar archivos

### Si WSL está COMPLETAMENTE ROTO:
- **NO SE PUEDE ACCEDER** a `\\wsl.localhost\`
- Los archivos están en un disco virtual (.vhdx) no accesible directamente

## 🛡️ Por eso tenemos MÚLTIPLES BACKUPS:

### 1. **K:\_Glados** (Sincronización activa)
- Usa `c2w` para sincronizar regularmente
- Accesible SIEMPRE desde Windows
- Comando: `c2w sync --all`

### 2. **H:\Backup\WSL** (Backup manual)
- Archivos críticos copiados
- Backup completo de ~/glados (pendiente)

### 3. **GitHub** (Código versionado)
- github.com/oratual/glados-scripts
- github.com/oratual/Batman-Incorporated
- github.com/oratual/DiskDominator
- github.com/oratual/MPC

## Comando para sincronizar TODO ahora:
```bash
# Sincronizar todos los proyectos a K:\_Glados
cd ~/glados && c2w sync --all

# O manualmente cada proyecto importante
c2w sync batman-incorporated
c2w sync DiskDominator
c2w sync scripts
c2w sync MPC
```

## Si necesitas recuperar archivos con WSL roto:
1. Primero busca en K:\_Glados
2. Luego en H:\Backup\WSL
3. Como último recurso, clona desde GitHub