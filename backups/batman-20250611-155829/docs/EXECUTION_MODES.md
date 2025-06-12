# Modos de Ejecución - Batman Incorporated

Batman Incorporated soporta cuatro modos de ejecución diferentes, cada uno optimizado para diferentes escenarios.

## 🛡️ Modo Seguro (Safe Mode)

**Cuándo usar**: Desarrollo de features complejas con múltiples agentes trabajando en paralelo.

### Características:
- Usa Git worktrees para aislar el trabajo de cada agente
- Cada agente trabaja en su propio branch y directorio
- Merge controlado al final con detección de conflictos
- Máxima seguridad contra pérdida de trabajo

### Funcionamiento:
1. Crea un worktree por cada agente único
2. Cada agente trabaja aislado en su directorio
3. Commits automáticos por tarea completada
4. Merge final con resolución de conflictos

### Ejemplo:
```bash
batman "implementar sistema de autenticación completo" --mode=seguro --real-agents
```

### Configuración:
```yaml
execution:
  safe_mode:
    enabled: true
    auto_merge: true
    conflict_strategy: "manual"
    cleanup_after: true
    worktree_base: "/tmp/batman-worktrees"
```

## ⚡ Modo Rápido (Fast Mode)

**Cuándo usar**: Tareas simples, prototipos rápidos, o cuando trabajas solo.

### Características:
- Ejecuta directamente en el directorio actual
- Sin branches ni worktrees
- Opción de auto-commit
- Máxima velocidad

### Funcionamiento:
1. Verifica estado del repositorio
2. Ejecuta tareas secuencialmente
3. Auto-commit opcional después de cada tarea
4. Reporte final de cambios

### Ejemplo:
```bash
batman "añadir endpoint GET /users" --mode=rapido
```

### Configuración:
```yaml
execution:
  fast_mode:
    enabled: true
    auto_commit: false
    direct_commit: true
```

## 🌌 Modo Infinity (Infinity Mode)

**Cuándo usar**: Proyectos grandes que requieren verdadero paralelismo con múltiples instancias de Claude Code.

### Características:
- Múltiples instancias reales de Claude Code trabajando en paralelo
- Contexto compartido via MCP Memory y archivos
- Coordinación via TodoRead/TodoWrite
- Monitoreo en tiempo real del progreso
- Sin simulación - trabajo real en paralelo

### Funcionamiento:
1. Genera instrucciones específicas para cada agente
2. Usuario abre múltiples terminales (una por agente)
3. Cada instancia trabaja independientemente
4. Comparten descubrimientos via #memoria
5. Batman monitorea el progreso general

### Ejemplo:
```bash
batman "desarrollar aplicación completa con frontend y backend" --mode=infinity
```

### Configuración:
```yaml
execution:
  infinity_mode:
    enabled: true
    shared_dir: "~/.batman/infinity"
    monitor_interval: 5
    timeout: 3600
```

### Ventajas:
- **Paralelismo real**: No es simulación, son instancias reales
- **Contexto compartido**: Via MCP Memory y archivos
- **Escalabilidad**: Tantos agentes como ventanas puedas abrir
- **Flexibilidad**: Puedes intervenir en cualquier instancia

## 🎯 Modo Redundante (Redundant Mode)

**Cuándo usar**: Features críticas donde necesitas la mejor implementación posible (autenticación, pagos, seguridad).

### Características:
- Genera múltiples implementaciones de la misma tarea
- Cada implementación con enfoque diferente
- Permite comparar y elegir la mejor
- Ideal para código crítico

### Funcionamiento:
1. Crea directorio para cada implementación
2. Varía el prompt para generar diferentes enfoques
3. Análisis automático de resultados
4. Usuario selecciona la mejor implementación

### Ejemplo:
```bash
batman "implementar autenticación OAuth2" --mode=redundante --real-agents
```

### Configuración:
```yaml
execution:
  redundant_mode:
    enabled: true
    min_implementations: 2
    max_implementations: 5
    selection_strategy: "manual"
    results_dir: "/tmp/batman-redundant"
    copy_base_files: true
```

### Variaciones generadas:
1. **Simplicidad**: Prioriza código claro y mantenible
2. **Performance**: Optimiza velocidad y eficiencia
3. **Seguridad**: Validación exhaustiva y mejores prácticas
4. **Moderno**: Últimas tecnologías y patterns
5. **Escalable**: Pensado para crecimiento

## 🤖 Modo Auto

**Comportamiento por defecto**: Batman analiza la complejidad y decide el modo apropiado.

### Criterios de decisión:
- **Seguro**: >10 tareas o dependencias complejas
- **Rápido**: <2 horas estimadas, tareas simples
- **Redundante**: Tareas marcadas como CRITICAL

### Ejemplo:
```bash
batman "refactorizar sistema de pagos"  # Batman decide el modo
```

## 📊 Comparación de Modos

| Característica | Seguro | Rápido | Infinity | Redundante |
|----------------|--------|---------|----------|------------|
| Velocidad | Media | Alta | Alta | Baja |
| Seguridad | Alta | Baja | Alta | Alta |
| Paralelización | ✅ Sí | ❌ No | ✅ Real | ✅ Sí |
| Conflictos | Gestionados | Posibles | Via worktrees | No aplica |
| Uso de recursos | Alto | Bajo | Muy alto | Muy alto |
| Complejidad | Alta | Baja | Media | Media |
| Instancias Claude | 1 | 1 | Múltiples | 1 |

## 🎮 Comandos

```bash
# Especificar modo explícitamente
batman "tarea" --mode=seguro
batman "tarea" --mode=rapido
batman "tarea" --mode=infinity
batman "tarea" --mode=redundante

# Dejar que Batman decida
batman "tarea"  # Modo auto

# Ver qué modo usaría Batman
batman "tarea" --dry-run
```

## 💡 Mejores Prácticas

1. **Modo Seguro**: 
   - Siempre para trabajo en equipo
   - Features que tocan múltiples archivos
   - Cuando no puedes permitir conflictos

2. **Modo Rápido**:
   - Prototipos y experimentos
   - Fixes pequeños y urgentes
   - Trabajo individual sin riesgo

3. **Modo Infinity**:
   - Proyectos grandes con múltiples componentes
   - Cuando necesitas verdadero paralelismo
   - Desarrollo full-stack simultáneo
   - Máximo aprovechamiento de recursos

4. **Modo Redundante**:
   - Autenticación y seguridad
   - Algoritmos críticos de negocio
   - Cuando el costo de error es alto

5. **Dejar que Batman decida**:
   - La mayoría de las veces
   - Batman aprende de tus preferencias
   - Optimiza basado en el contexto