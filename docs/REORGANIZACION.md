# 🔄 GUÍA DE REORGANIZACIÓN SEGURA PARA GLADOS

## 📋 CUÁNDO USAR ESTA GUÍA
Consultar este documento SIEMPRE que se solicite:
- Reorganizar estructura de carpetas
- Consolidar scripts o utilidades
- Eliminar duplicados o "limpiar" el sistema
- Crear nueva estructura organizativa

## 🛡️ PRINCIPIOS DE MODIFICACIÓN SEGURA

### 1️⃣ ANTES de cualquier reorganización:
- **BACKUP COMPLETO**: Crear snapshot en `/mnt/h/BACKUPS/` o `.papelera/`
- **DOCUMENTAR ESTADO ACTUAL**: Mapear qué funciona, dónde está y sus dependencias
- **PLAN DETALLADO**: Definir estructura objetivo Y ruta de migración
- **CREAR EN PARALELO**: Usar carpetas nuevas (ej: SYSTEM/, UTILITIES/) sin tocar originales

### 2️⃣ DURANTE las modificaciones:
- **VERIFICAR PROGRESIVAMENTE**: Probar funcionalidad mientras se avanza
- **MANTENER COMPATIBILIDAD**: Crear symlinks para comandos que el usuario usa
- **ACTUALIZAR DOCS**: Modificar CLAUDE.md y otros inmediatamente
- **LOG DE CAMBIOS**: Documentar cada movimiento en `.estado-reorganizacion.md`

### 3️⃣ PUNTOS CRÍTICOS DE ATENCIÓN:

#### 🔸 WRAPPERS
- **Realidad**: Son útiles pero frágiles
- **Verificar**: Que los ejecutables base existan
- **Documentar**: Qué hace cada wrapper
- **Alternativa**: Considerar versiones directas cuando sea posible

#### 🔸 EXTENSIONES Y PERMISOS
- Scripts DEBEN tener extensión `.sh`
- Ejecutables DEBEN tener permisos `chmod +x`
- Symlinks DEBEN apuntar a rutas válidas

#### 🔸 RUTAS Y REFERENCIAS
- Actualizar TODAS las referencias en:
  - CLAUDE.md
  - Scripts que llaman a otros scripts
  - Documentación
  - Configuraciones

### 4️⃣ DESPUÉS de reorganizar:
- **TEST COMPLETO**: Ejecutar TODOS los comandos principales
- **GUÍA MIGRACIÓN**: Documentar qué cambió y dónde está ahora
- **PERÍODO PRUEBA**: Mantener estructura antigua mínimo 24h
- **ROLLBACK PLAN**: Tener comando exacto para revertir todo

## ✅ CHECKLIST OBLIGATORIO

```bash
[ ] Backup completo en H:/ o tar.gz creado
[ ] Estado actual documentado en .md
[ ] Estructura paralela creada (no sobrescribir)
[ ] Comandos principales probados en nueva ubicación
[ ] CLAUDE.md actualizado con nuevas rutas
[ ] Script de rollback preparado
[ ] Usuario informado de los cambios
```

## 🚫 PROHIBICIONES

1. **NUNCA** mover sin copiar primero
2. **NUNCA** eliminar hasta confirmar que lo nuevo funciona
3. **NUNCA** cambiar batman-incorporated o DiskDominator sin permiso explícito
4. **NUNCA** trabajar sin backup previo
5. **NUNCA** asumir que un wrapper es "innecesario" sin entender su propósito

## 📝 PLANTILLA DE DOCUMENTACIÓN

Al reorganizar, crear siempre:
```markdown
## REORGANIZACIÓN [FECHA]

### Estado Anterior:
- Estructura: [describir]
- Problemas: [listar]

### Estado Nuevo:
- Estructura: [describir]
- Mejoras: [listar]

### Cambios Realizados:
1. [archivo/carpeta] → [nueva ubicación]
2. ...

### Cómo Revertir:
```bash
# Comandos exactos para rollback
```
```

## 🔄 EJEMPLO DE REORGANIZACIÓN CORRECTA

```bash
# 1. Backup
tar -czf /mnt/h/BACKUPS/glados-pre-reorg-$(date +%Y%m%d).tar.gz ~/glados/

# 2. Crear estructura paralela
mkdir -p ~/glados/NEW_STRUCTURE/{bin,lib,config}

# 3. Copiar (no mover)
cp -r ~/glados/scripts/* ~/glados/NEW_STRUCTURE/bin/

# 4. Probar
~/glados/NEW_STRUCTURE/bin/launcher.sh

# 5. Solo si funciona, crear symlinks
ln -sf ~/glados/NEW_STRUCTURE/bin/launcher.sh ~/glados/launcher

# 6. Después de período de prueba, archivar antiguos
mv ~/glados/scripts ~/glados/.papelera/scripts-$(date +%Y%m%d)
```

---
*Esta guía existe porque la reorganización del 2025-06-12 nos enseñó la importancia de un proceso estructurado*