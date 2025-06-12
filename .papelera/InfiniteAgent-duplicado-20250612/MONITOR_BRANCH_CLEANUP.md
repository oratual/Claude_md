# 🧹 THE MONITOR: Gestión de Branches

## 📋 Flujo de Branches

### 1. **Creación**
```bash
# Monitor crea branches temporales
monitor/agent-0-20250609_143022
monitor/agent-1-20250609_143022
monitor/agent-2-20250609_143022
```

### 2. **Trabajo**
- Cada agente trabaja en su branch
- Commits frecuentes
- Opcionalmente push a GitHub

### 3. **Merge**
```bash
# Merge a main/master
git merge --no-ff monitor/agent-0-20250609_143022
```

### 4. **Limpieza Automática**
```python
# Después del merge exitoso:
if merge_successful:
    # Verificar si existe en GitHub
    if branch_exists_on_github:
        print("Branch preserved on GitHub")
    
    # Eliminar branch local
    git branch -d monitor/agent-0-20250609_143022
```

## 🔄 Estrategias de Preservación

### **Opción 1: Push Automático (Recomendado)**
```python
# En el agent prompt:
"After completing your task:
1. Commit all changes
2. Push to GitHub: git push -u origin <branch>
3. This preserves your work even after local deletion"
```

### **Opción 2: Push Selectivo**
```python
# Solo pushear branches con cambios significativos
if significant_changes or conflicts_expected:
    subprocess.run(["git", "push", "-u", "origin", branch])
```

### **Opción 3: Archivo de Historia**
```python
# Antes de eliminar, guardar metadata
branch_history = {
    "branch": "monitor/agent-0-20250609_143022",
    "commits": get_commit_list(branch),
    "merge_commit": merge_sha,
    "deleted_at": timestamp
}
save_to_history(branch_history)
```

## 🗑️ Limpieza de Branches

### **Automática (Por Defecto)**
```python
# Después de cada merge exitoso
✓ Merged agent-0 successfully
  → Branch monitor/agent-0-xyz preserved on GitHub
  → Local branch monitor/agent-0-xyz deleted
```

### **Manual**
```bash
# Ver branches del Monitor
git branch | grep monitor/

# Limpiar branches mergeadas
git branch --merged | grep monitor/ | xargs git branch -d

# Limpiar branches huérfanas
/monitor:cleanup --prune-orphaned
```

### **Recuperación desde GitHub**
```bash
# Si necesitas recuperar una branch eliminada
git fetch origin monitor/agent-0-xyz:monitor/agent-0-xyz
git checkout monitor/agent-0-xyz
```

## 📊 Gestión de Espacio

### **Sin limpieza:**
```
- 10 tareas = 10 branches
- 100 tareas = 100 branches
- Rápidamente se vuelve inmanejable
```

### **Con limpieza automática:**
```
- Siempre limpio localmente
- Historia preservada en GitHub
- Fácil navegación
- git branch muestra solo branches activas
```

## 🔧 Configuración

```python
# monitor_config.yaml
branch_management:
  auto_delete_after_merge: true
  push_to_remote: "optional"  # always/optional/never
  preserve_failed_merges: true
  cleanup_worktrees: true
  
  naming_pattern: "monitor/{agent_id}-{timestamp}"
  
  github_preservation:
    enabled: true
    auto_push: false  # Dejar que agentes decidan
    preserve_days: 30  # GitHub puede limpiar después
```

## 💡 Mejores Prácticas

### 1. **Branches Descriptivas**
```bash
# Bien
monitor/auth-oauth2-20250609
monitor/fix-bug-521-20250609

# Mal  
monitor/agent-0
monitor/temp
```

### 2. **Commits Frecuentes**
- Los agentes deben commitear frecuentemente
- Facilita el debugging si algo falla
- Mejor historia para revisión

### 3. **Push Estratégico**
```python
# Agent decide basándose en:
if large_changes or experimental_approach:
    # Push para preservar
    git push -u origin branch
```

## 🚨 Casos Especiales

### **Conflictos No Resueltos**
```python
# Branches con conflictos NO se eliminan
if merge_conflict:
    print(f"Branch {branch} preserved for manual resolution")
    # No delete
```

### **Trabajo Experimental**
```python
# Marcar branches experimentales
if experimental:
    branch_name = f"monitor/experimental-{feature}-{timestamp}"
    # Siempre push estas
```

### **Recuperación de Emergencia**
```bash
# Si eliminaste algo importante
git reflog  # Ver commits recientes
git checkout -b recovered <commit-sha>
```

## 📈 Beneficios

1. **Espacio Limpio**: No acumulas branches viejas
2. **Historia en GitHub**: Todo respaldado remotamente
3. **Navegación Fácil**: Solo ves branches activas
4. **Performance**: Git más rápido con menos branches
5. **Profesional**: Flujo limpio como equipos reales

---

**Resumen**: The Monitor limpia automáticamente después de merge exitoso, pero preserva todo en GitHub si fue pusheado. Lo mejor de ambos mundos: local limpio, historia completa en la nube.