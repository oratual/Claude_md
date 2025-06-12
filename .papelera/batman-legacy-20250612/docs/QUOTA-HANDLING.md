# Manejo de Cuotas y Límites en Batman

## Detección de Límites de Claude API

### Códigos de Error Comunes

1. **429 - Too Many Requests**
   - Rate limit temporal (demasiadas peticiones por minuto)
   - Headers: `X-RateLimit-Remaining`, `X-RateLimit-Reset`

2. **402 - Payment Required** 
   - Cuota mensual agotada
   - Mensaje típico: "quota exceeded" o "usage limit reached"

3. **503 - Service Unavailable**
   - Puede indicar sobrecarga o límites

### Estrategia de Batman con 5 Instancias

```python
# batman/src/quota_manager.py

class QuotaManager:
    def __init__(self):
        self.last_quota_error = None
        self.retry_after = 3600  # 1 hora por defecto
        
    def handle_api_error(self, error):
        if error.status_code == 402:
            # Cuota agotada
            self.last_quota_error = datetime.now()
            logger.error(f"QUOTA AGOTADA: Reintentando en {self.retry_after/60} minutos")
            return "quota_exceeded"
        elif error.status_code == 429:
            # Rate limit
            retry_after = error.headers.get('Retry-After', 60)
            logger.warning(f"Rate limit: esperando {retry_after} segundos")
            return "rate_limit"
        return "other_error"
```

## Arquitectura de 5 Instancias Independientes

### División de Tareas

```yaml
# batman/config/instances.yaml

instances:
  instance_1:
    name: "system_cleanup"
    tasks:
      - cleanup_logs
      - cleanup_temp
      - optimize_storage
    schedule: "00:00-02:00"
    
  instance_2:
    name: "backups"
    tasks:
      - backup_configs
      - backup_databases
      - sync_cloud
    schedule: "02:00-04:00"
    
  instance_3:
    name: "security"
    tasks:
      - security_scan
      - update_patches
      - check_intrusions
    schedule: "04:00-05:00"
    
  instance_4:
    name: "optimization"
    tasks:
      - defrag_disks
      - rebuild_indexes
      - analyze_performance
    schedule: "05:00-06:00"
    
  instance_5:
    name: "reporting"
    tasks:
      - generate_reports
      - send_summaries
      - cleanup_results
    schedule: "06:00-07:00"
```

### Sistema de Recuperación Horaria

```python
# batman/src/recovery_system.py

class RecoverySystem:
    def __init__(self):
        self.checkpoint_file = "batman_checkpoint.json"
        self.recovery_interval = 3600  # 1 hora
        
    def save_checkpoint(self, instance_id, completed_tasks):
        """Guarda progreso de cada instancia"""
        checkpoint = {
            "instance_id": instance_id,
            "timestamp": datetime.now().isoformat(),
            "completed_tasks": completed_tasks,
            "remaining_tasks": self.get_remaining_tasks(instance_id)
        }
        
    def recover_from_checkpoint(self):
        """Recupera desde último checkpoint si hay error de cuota"""
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file) as f:
                checkpoint = json.load(f)
            logger.info(f"Recuperando desde checkpoint: {checkpoint['timestamp']}")
            return checkpoint['remaining_tasks']
```

## Script Principal con Manejo de Cuotas

```python
#!/usr/bin/env python3
# batman/batman.py

import time
import sys
from datetime import datetime, timedelta

class Batman:
    def __init__(self):
        self.quota_manager = QuotaManager()
        self.recovery_system = RecoverySystem()
        self.instances = self.load_instances()
        
    def run_instance(self, instance_id):
        """Ejecuta una instancia con manejo de cuota"""
        instance = self.instances[instance_id]
        completed = []
        
        for task in instance['tasks']:
            try:
                result = self.execute_task(task)
                completed.append(task)
                self.recovery_system.save_checkpoint(instance_id, completed)
                
            except QuotaExceededError:
                logger.error(f"Cuota agotada en {instance_id}")
                # Programar reintento en 1 hora
                self.schedule_retry(instance_id, completed)
                return False
                
            except Exception as e:
                logger.error(f"Error en {task}: {e}")
                # Continuar con siguiente tarea
                continue
                
        return True
        
    def schedule_retry(self, instance_id, completed_tasks):
        """Programa reintento en 1 hora"""
        retry_time = datetime.now() + timedelta(hours=1)
        logger.info(f"Reintentando {instance_id} a las {retry_time}")
        
        # Crear cron job temporal
        cron_cmd = f"echo 'batman resume {instance_id}' | at {retry_time.strftime('%H:%M')}"
        os.system(cron_cmd)
```

## Monitoreo de Uso

```python
# batman/src/usage_monitor.py

class UsageMonitor:
    def __init__(self, monthly_limit=200):
        self.monthly_limit = monthly_limit
        self.usage_file = "batman_usage.json"
        
    def estimate_remaining_budget(self):
        """Estima presupuesto restante basado en uso"""
        usage = self.load_usage()
        current_cost = usage.get('current_month_cost', 0)
        remaining = self.monthly_limit - current_cost
        
        if remaining < 20:  # Menos de $20
            logger.warning(f"ADVERTENCIA: Solo quedan ${remaining} de cuota")
            
        return remaining
        
    def should_pause_expensive_tasks(self):
        """Decide si pausar tareas costosas"""
        remaining = self.estimate_remaining_budget()
        days_left = self.days_until_month_end()
        
        daily_budget = remaining / max(days_left, 1)
        return daily_budget < 5  # Menos de $5 por día
```

## Configuración Recomendada

```yaml
# batman/config/batman.yaml

quota:
  monthly_limit: 200
  warning_threshold: 20
  daily_safety_margin: 5
  
recovery:
  retry_interval: 3600  # 1 hora
  max_retries: 3
  checkpoint_frequency: 300  # 5 minutos
  
instances:
  parallel: false  # Ejecutar secuencialmente
  isolation: true  # Cada instancia independiente
  continue_on_failure: true
```

## Ventajas de 5 Instancias Separadas

1. **Aislamiento de Fallos**: Si una instancia falla, las otras continúan
2. **Checkpoints Granulares**: Cada instancia guarda su progreso
3. **Recuperación Específica**: Solo reintentar lo que falló
4. **Presupuesto Distribuido**: Cada instancia tiene su cuota
5. **Logs Separados**: Más fácil debuggear problemas

## Comando de Recuperación Manual

```bash
# Retomar desde checkpoint
batman resume instance_3

# Ver estado de todas las instancias
batman status

# Verificar cuota restante
batman quota

# Ejecutar solo tareas baratas si queda poca cuota
batman run --low-cost-only
```