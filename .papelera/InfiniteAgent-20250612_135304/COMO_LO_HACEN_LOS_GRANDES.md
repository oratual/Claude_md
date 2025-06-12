# 🏢 CÓMO LOS GRANDES SISTEMAS MANEJAN LA CONCURRENCIA

## 🐙 GitHub: Distributed Version Control

### **Estrategia: Optimistic Concurrency + Branch Isolation**

```
Usuario A ─┐
           ├─→ Branch A ─┐
Usuario B ─┤             ├─→ Pull Request → Merge/Conflict Resolution
           ├─→ Branch B ─┘
Usuario C ─┘
```

**Técnicas clave:**
1. **Branch Isolation**: Cada desarrollador trabaja en su rama
2. **Merge Commits**: Git detecta y resuelve conflictos
3. **Pull Request Reviews**: Humanos validan antes de merge
4. **Conflict Markers**: `<<<<<<< HEAD` para resolución manual

```bash
# GitHub no previene conflictos, los abraza
git pull origin main
# Auto-merging src/index.js
# CONFLICT (content): Merge conflict in src/index.js
# Automatic merge failed; fix conflicts and then commit
```

### **GitHub Actions: Concurrent Workflows**
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true  # Cancela builds anteriores
```

## 📝 Google Docs: Operational Transformation (OT)

### **Estrategia: Real-time Collaborative Editing**

```javascript
// Transformación Operacional
Operation A: Insert("Hello", position: 5)
Operation B: Delete(3, position: 2)

// Si A llega primero a B:
B' = Transform(B, A) = Delete(3, position: 2)  // Sin cambio

// Si B llega primero a A:
A' = Transform(A, B) = Insert("Hello", position: 2)  // Ajusta posición
```

**Arquitectura:**
1. **Central Authority**: Servidor ordena todas las operaciones
2. **Operation Log**: Historial completo de cambios
3. **Transformation Engine**: Ajusta operaciones según contexto
4. **Cursor Tracking**: Ve dónde está cada usuario

## 🔄 Git (Core): Three-way Merge

### **Estrategia: Content-based Merging**

```
      Common Ancestor
           /    \
          /      \
    Branch A    Branch B
         \      /
          \    /
        Merged Result
```

**Algoritmo:**
1. Encuentra ancestro común
2. Calcula diff de A→Ancestor y B→Ancestor
3. Aplica ambos diffs si no se solapan
4. Marca conflictos si se solapan

## 💻 VS Code Live Share: Shared Editing Sessions

### **Estrategia: Host-Guest Architecture**

```
Host (Owner)
    │
    ├── File System (Real)
    ├── Language Server
    └── Debug Session
         │
    ┌────┴────┐
    │ Relay   │
    │ Server  │
    └────┬────┘
         │
    ┌────┴────┬─────┬─────┐
Guest 1    Guest 2    Guest 3
```

**Técnicas:**
1. **Single Source of Truth**: Host tiene los archivos reales
2. **Differential Sync**: Solo envía cambios, no archivos completos
3. **Presence Awareness**: Cursores y selecciones de cada usuario
4. **Permission System**: Read-only vs Read-write guests

## 🗄️ Databases: MVCC (Multi-Version Concurrency Control)

### **PostgreSQL/MySQL InnoDB Strategy**

```sql
-- Transaction 1 ve versión V1
BEGIN;
SELECT * FROM users WHERE id = 1;  -- Ve: {name: "Alice", age: 25}

-- Transaction 2 modifica (crea versión V2)
UPDATE users SET age = 26 WHERE id = 1;
COMMIT;

-- Transaction 1 sigue viendo V1 hasta que haga COMMIT
SELECT * FROM users WHERE id = 1;  -- Sigue viendo: {age: 25}
```

**Implementación:**
1. **Row Versioning**: Cada fila tiene múltiples versiones
2. **Transaction IDs**: Determina qué versión ve cada transacción
3. **Garbage Collection**: Limpia versiones viejas
4. **No Locks for Reads**: Lecturas nunca bloquean

## 🌐 Kubernetes: Optimistic Concurrency

### **Estrategia: Resource Versioning**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-config
  resourceVersion: "12345"  # Versión del recurso
data:
  key: value
```

```bash
# Cliente A y B obtienen versión 12345
kubectl get configmap my-config

# Cliente A actualiza (nueva versión 12346)
kubectl apply -f config-a.yaml

# Cliente B intenta actualizar con versión vieja
kubectl apply -f config-b.yaml
# Error: Operation cannot be fulfilled on configmaps "my-config":
# the object has been modified
```

## 🎮 Multiplayer Games: Client-Side Prediction

### **Estrategia: Eventual Consistency**

```
Cliente A ─→ "Mover a X" ─→ Servidor
   │                           │
   └─ Predice localmente       └─ Valida y broadcast
                                       │
Cliente B ←─ "A se movió a X" ←───────┘
```

**Técnicas:**
1. **Client Prediction**: Muestra cambios inmediatamente
2. **Server Reconciliation**: Servidor es autoridad final
3. **Lag Compensation**: Retrocede tiempo para hit detection
4. **Delta Compression**: Solo envía cambios

## 🏗️ Apache Kafka: Partitioned Parallelism

### **Estrategia: Partition-based Isolation**

```
Topic: user-events
├── Partition 0: User IDs 0-1000    → Consumer A
├── Partition 1: User IDs 1001-2000 → Consumer B
└── Partition 2: User IDs 2001-3000 → Consumer C
```

**Sin conflictos porque:**
1. Cada partición tiene un solo escritor
2. Orden garantizado dentro de partición
3. Escalabilidad horizontal

## 🔥 Firebase Realtime Database: Last-Write-Wins + Transactions

### **Estrategia Híbrida**

```javascript
// Operación normal: Last Write Wins
firebase.database().ref('users/alice').set({age: 26});

// Operación crítica: Transaction
firebase.database().ref('users/alice/balance').transaction((current) => {
  return (current || 0) + 10;  // Incremento atómico
});
```

## 📊 Elasticsearch: Versioning + Optimistic Locking

```json
// GET devuelve version
{
  "_index": "products",
  "_id": "1",
  "_version": 3,
  "_source": { "name": "Laptop", "price": 999 }
}

// UPDATE con version check
POST /products/_update/1?version=3
{
  "doc": { "price": 899 }
}
// Si version != 3, falla con 409 Conflict
```

## 🎯 Resumen: Estrategias por Caso de Uso

| Sistema | Estrategia Principal | Cuándo Usarla |
|---------|---------------------|---------------|
| **GitHub** | Branch Isolation | Cambios grandes, review necesario |
| **Google Docs** | Operational Transform | Edición en tiempo real |
| **VS Code Live** | Host-Guest | Sesiones colaborativas |
| **PostgreSQL** | MVCC | Datos transaccionales |
| **Kubernetes** | Optimistic Locking | Configuración distribuida |
| **Games** | Client Prediction | Baja latencia crítica |
| **Kafka** | Partitioning | Alto throughput |
| **Firebase** | Last-Write-Wins | Simplicidad sobre consistencia |

## 🚀 Aplicación a MIRROR SYSTEM

### **Estrategia Híbrida Recomendada:**

```python
class MirrorSystemStrategy:
    def __init__(self):
        self.strategies = {
            # Como GitHub: branches para cambios grandes
            'feature_development': BranchIsolationStrategy(),
            
            # Como Google Docs: OT para edición colaborativa
            'collaborative_edit': OperationalTransformStrategy(),
            
            # Como PostgreSQL: MVCC para datos
            'data_migration': MVCCStrategy(),
            
            # Como Kafka: particiones para paralelización masiva
            'mass_refactor': PartitionedStrategy(),
            
            # Como Kubernetes: versioning para configuración
            'config_update': OptimisticLockStrategy()
        }
    
    def select_strategy(self, task_type, scale):
        if scale > 100:  # Muchos mirrors
            return self.strategies['mass_refactor']
        elif task_type == 'realtime':
            return self.strategies['collaborative_edit']
        else:
            return self.strategies['feature_development']
```

### **Lecciones Clave de los Grandes:**

1. **No hay bala de plata**: Cada sistema usa la estrategia adecuada
2. **Embrace conflicts**: No siempre prevenir, a veces resolver
3. **Eventual consistency**: A veces "suficientemente bueno" es perfecto
4. **Partition everything**: Divide y conquista
5. **Version everything**: Tracking es esencial
6. **Human in the loop**: Para decisiones críticas

### **Para MIRROR SYSTEM:**
- **Pequeña escala** (< 10 mirrors): Branch isolation como GitHub
- **Media escala** (10-100): Partitioning como Kafka  
- **Gran escala** (> 100): MVCC + Sharding como databases
- **Tiempo real**: Operational Transform como Google Docs