"""
Sistema unificado de tareas para Batman Incorporated.
Una sola definición de Task para todo el sistema.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


class TaskStatus(Enum):
    """Estados posibles de una tarea."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class TaskPriority(Enum):
    """Niveles de prioridad."""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    TRIVIAL = 1


class TaskType(Enum):
    """Tipos de tarea según su naturaleza."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    INFRASTRUCTURE = "infrastructure"
    SECURITY = "security"
    OPTIMIZATION = "optimization"
    RESEARCH = "research"
    MAINTENANCE = "maintenance"


@dataclass
class Task:
    """Tarea unificada para todo el sistema Batman Incorporated."""
    
    # Identificación
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    
    # Clasificación
    type: TaskType = TaskType.DEVELOPMENT
    priority: TaskPriority = TaskPriority.MEDIUM
    tags: List[str] = field(default_factory=list)
    
    # Estado
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0  # 0-100
    
    # Asignación
    assigned_to: Optional[str] = None  # Agente asignado (alfred, robin, etc.)
    created_by: str = "batman"
    
    # Tiempos
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    
    # Dependencias
    depends_on: List[str] = field(default_factory=list)  # IDs de otras tareas
    blocks: List[str] = field(default_factory=list)  # IDs de tareas bloqueadas
    
    # Ejecución
    command: Optional[str] = None  # Comando a ejecutar (si aplica)
    working_dir: Optional[str] = None  # Directorio de trabajo
    environment: Dict[str, str] = field(default_factory=dict)  # Variables de entorno
    
    # Resultados
    output: str = ""
    error: str = ""
    artifacts: List[str] = field(default_factory=list)  # Archivos generados
    metrics: Dict[str, Any] = field(default_factory=dict)  # Métricas recolectadas
    
    # Paralelización
    allow_parallel: bool = True
    max_parallel_instances: int = 1
    parallel_mode: str = "none"  # none, worktree, infinity
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validaciones y configuración inicial."""
        if not self.title:
            self.title = f"Task {self.id[:8]}"
    
    def start(self):
        """Marca la tarea como iniciada."""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()
    
    def complete(self, output: str = ""):
        """Marca la tarea como completada."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.progress = 100.0
        if output:
            self.output = output
        if self.started_at:
            self.actual_hours = (self.completed_at - self.started_at).total_seconds() / 3600
    
    def fail(self, error: str = ""):
        """Marca la tarea como fallida."""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
        if error:
            self.error = error
    
    def is_ready(self, completed_tasks: List[str]) -> bool:
        """Verifica si la tarea está lista para ejecutarse."""
        if self.status != TaskStatus.PENDING:
            return False
        return all(dep_id in completed_tasks for dep_id in self.depends_on)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la tarea a diccionario."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'type': self.type.value,
            'priority': self.priority.value,
            'status': self.status.value,
            'progress': self.progress,
            'assigned_to': self.assigned_to,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'tags': self.tags,
            'depends_on': self.depends_on,
            'output': self.output[:1000] if self.output else "",  # Limitar tamaño
            'error': self.error[:1000] if self.error else "",
            'artifacts': self.artifacts,
            'metrics': self.metrics
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Crea una tarea desde un diccionario."""
        task = cls()
        for key, value in data.items():
            if hasattr(task, key):
                if key in ['type', 'priority', 'status'] and value:
                    # Convertir strings a enums
                    if key == 'type':
                        value = TaskType(value)
                    elif key == 'priority':
                        value = TaskPriority(value)
                    elif key == 'status':
                        value = TaskStatus(value)
                elif key.endswith('_at') and value:
                    # Convertir strings a datetime
                    value = datetime.fromisoformat(value)
                setattr(task, key, value)
        return task


@dataclass
class TaskBatch:
    """Grupo de tareas relacionadas."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    tasks: List[Task] = field(default_factory=list)
    parallel: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_task(self, task: Task):
        """Añade una tarea al batch."""
        self.tasks.append(task)
    
    def get_ready_tasks(self, completed_tasks: List[str]) -> List[Task]:
        """Obtiene las tareas listas para ejecutar."""
        return [t for t in self.tasks if t.is_ready(completed_tasks)]
    
    def is_complete(self) -> bool:
        """Verifica si todas las tareas están completas."""
        return all(t.status == TaskStatus.COMPLETED for t in self.tasks)
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del batch."""
        total = len(self.tasks)
        if total == 0:
            return {'total': 0}
        
        completed = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self.tasks if t.status == TaskStatus.FAILED)
        in_progress = sum(1 for t in self.tasks if t.status == TaskStatus.IN_PROGRESS)
        
        return {
            'total': total,
            'completed': completed,
            'failed': failed,
            'in_progress': in_progress,
            'pending': total - completed - failed - in_progress,
            'progress': (completed / total) * 100,
            'success_rate': (completed / (completed + failed)) * 100 if (completed + failed) > 0 else 0
        }