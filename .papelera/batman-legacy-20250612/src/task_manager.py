#!/usr/bin/env python3
"""
Task Manager - Sistema completo de gestión de tareas para Batman
Maneja persistencia, priorización, dependencias y estado
"""

import json
import sqlite3
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import networkx as nx
import yaml
import logging
from collections import defaultdict
import hashlib


class TaskType(Enum):
    """Tipos de tareas soportadas"""
    COMMAND = "command"           # Comando shell/bash
    AI_PROMPT = "ai_prompt"       # Prompt para Claude
    CODE_GENERATION = "code"      # Generación de código
    ANALYSIS = "analysis"         # Análisis de sistema/código
    MAINTENANCE = "maintenance"   # Mantenimiento del sistema
    EXPERIMENTAL = "experimental" # Tareas experimentales/creativas


@dataclass
class TaskMetadata:
    """Metadatos adicionales de una tarea"""
    estimated_duration: int = 300  # segundos
    requires_internet: bool = False
    requires_sudo: bool = False
    safe_to_retry: bool = True
    max_retries: int = 3
    retry_delay: int = 60
    tags: List[str] = field(default_factory=list)
    created_by: str = "batman"
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_for: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    
@dataclass
class TaskDependency:
    """Define una dependencia entre tareas"""
    task_id: str
    depends_on: str
    dependency_type: str = "completion"  # completion, success, partial
    optional: bool = False
    
    
class TaskGraph:
    """Grafo de dependencias de tareas usando NetworkX"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        
    def add_task(self, task_id: str, task_data: Dict):
        """Agrega una tarea al grafo"""
        self.graph.add_node(task_id, **task_data)
        
    def add_dependency(self, from_task: str, to_task: str, dep_type: str = "completion"):
        """Agrega dependencia: from_task depende de to_task"""
        self.graph.add_edge(to_task, from_task, type=dep_type)
        
    def get_ready_tasks(self, completed_tasks: Set[str]) -> List[str]:
        """Obtiene tareas listas para ejecutar (sin dependencias pendientes)"""
        ready = []
        
        for node in self.graph.nodes():
            if node in completed_tasks:
                continue
                
            # Verificar si todas las dependencias están completas
            predecessors = list(self.graph.predecessors(node))
            if all(pred in completed_tasks for pred in predecessors):
                ready.append(node)
                
        return ready
        
    def get_execution_order(self) -> List[str]:
        """Obtiene orden óptimo de ejecución respetando dependencias"""
        try:
            return list(nx.topological_sort(self.graph))
        except nx.NetworkXUnfeasible:
            # Hay ciclos, intentar resolverlos
            cycles = list(nx.simple_cycles(self.graph))
            raise ValueError(f"Ciclos detectados en dependencias: {cycles}")
            
    def visualize(self, output_path: str = None):
        """Genera visualización del grafo de tareas"""
        try:
            import matplotlib.pyplot as plt
            
            pos = nx.spring_layout(self.graph)
            plt.figure(figsize=(12, 8))
            
            # Dibujar nodos
            nx.draw_networkx_nodes(self.graph, pos, node_size=500)
            nx.draw_networkx_labels(self.graph, pos)
            nx.draw_networkx_edges(self.graph, pos, edge_color='gray', arrows=True)
            
            if output_path:
                plt.savefig(output_path)
            else:
                plt.show()
                
        except ImportError:
            logging.warning("matplotlib no disponible para visualización")


class TaskPersistence:
    """Maneja persistencia de tareas en SQLite"""
    
    def __init__(self, db_path: str = "~/.batman/tasks.db"):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        
    def _init_db(self):
        """Inicializa esquema de base de datos"""
        with sqlite3.connect(self.db_path) as conn:
            # Tabla principal de tareas
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    type TEXT NOT NULL,
                    priority INTEGER DEFAULT 3,
                    status TEXT DEFAULT 'pending',
                    data JSON NOT NULL,
                    metadata JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    scheduled_for TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)
            
            # Tabla de dependencias
            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_dependencies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    depends_on TEXT NOT NULL,
                    dependency_type TEXT DEFAULT 'completion',
                    optional BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                    FOREIGN KEY (depends_on) REFERENCES tasks(id) ON DELETE CASCADE,
                    UNIQUE(task_id, depends_on)
                )
            """)
            
            # Tabla de resultados/historial
            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    attempt_number INTEGER DEFAULT 1,
                    status TEXT NOT NULL,
                    started_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP NOT NULL,
                    duration_seconds REAL,
                    output TEXT,
                    error TEXT,
                    artifacts JSON,
                    metrics JSON,
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
                )
            """)
            
            # Tabla de eventos/logs
            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_data JSON,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
                )
            """)
            
            # Índices para performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_scheduled ON tasks(scheduled_for)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_results_task ON task_results(task_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_task ON task_events(task_id)")
            
    def save_task(self, task: Dict) -> str:
        """Guarda o actualiza una tarea"""
        task_id = task.get('id') or str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            # Verificar si existe
            existing = conn.execute(
                "SELECT id FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
            
            if existing:
                # Actualizar
                conn.execute("""
                    UPDATE tasks SET
                        title = ?, description = ?, type = ?, priority = ?,
                        status = ?, data = ?, metadata = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    task['title'], task.get('description'), task['type'],
                    task.get('priority', 3), task.get('status', 'pending'),
                    json.dumps(task), json.dumps(task.get('metadata', {})),
                    task_id
                ))
            else:
                # Insertar
                conn.execute("""
                    INSERT INTO tasks (id, title, description, type, priority, status, data, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    task_id, task['title'], task.get('description'), task['type'],
                    task.get('priority', 3), task.get('status', 'pending'),
                    json.dumps(task), json.dumps(task.get('metadata', {}))
                ))
                
            # Guardar dependencias
            if 'dependencies' in task:
                # Eliminar dependencias antiguas
                conn.execute("DELETE FROM task_dependencies WHERE task_id = ?", (task_id,))
                
                # Insertar nuevas
                for dep in task['dependencies']:
                    if isinstance(dep, dict):
                        conn.execute("""
                            INSERT INTO task_dependencies (task_id, depends_on, dependency_type, optional)
                            VALUES (?, ?, ?, ?)
                        """, (task_id, dep['depends_on'], dep.get('type', 'completion'), dep.get('optional', False)))
                    else:
                        # Dependencia simple (solo ID)
                        conn.execute("""
                            INSERT INTO task_dependencies (task_id, depends_on)
                            VALUES (?, ?)
                        """, (task_id, dep))
                        
            # Log evento
            self._log_event(conn, task_id, 'created' if not existing else 'updated', task)
            
        return task_id
        
    def get_task(self, task_id: str) -> Optional[Dict]:
        """Obtiene una tarea por ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            row = conn.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
            
            if not row:
                return None
                
            task = json.loads(row['data'])
            
            # Agregar dependencias
            deps = conn.execute("""
                SELECT depends_on, dependency_type, optional
                FROM task_dependencies WHERE task_id = ?
            """, (task_id,)).fetchall()
            
            task['dependencies'] = [
                {'depends_on': d['depends_on'], 'type': d['dependency_type'], 'optional': bool(d['optional'])}
                for d in deps
            ]
            
            return task
            
    def get_pending_tasks(self, limit: int = None) -> List[Dict]:
        """Obtiene tareas pendientes ordenadas por prioridad"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            query = """
                SELECT * FROM tasks
                WHERE status = 'pending'
                AND (scheduled_for IS NULL OR scheduled_for <= CURRENT_TIMESTAMP)
                ORDER BY priority ASC, created_at ASC
            """
            
            if limit:
                query += f" LIMIT {limit}"
                
            rows = conn.execute(query).fetchall()
            
            tasks = []
            for row in rows:
                task = json.loads(row['data'])
                
                # Agregar dependencias
                deps = conn.execute("""
                    SELECT depends_on, dependency_type, optional
                    FROM task_dependencies WHERE task_id = ?
                """, (row['id'],)).fetchall()
                
                task['dependencies'] = [dict(d) for d in deps]
                tasks.append(task)
                
            return tasks
            
    def update_task_status(self, task_id: str, status: str, **kwargs):
        """Actualiza el estado de una tarea"""
        with sqlite3.connect(self.db_path) as conn:
            updates = ["status = ?", "updated_at = CURRENT_TIMESTAMP"]
            values = [status]
            
            if status == 'in_progress' and 'started_at' not in kwargs:
                updates.append("started_at = CURRENT_TIMESTAMP")
            elif status in ['completed', 'failed'] and 'completed_at' not in kwargs:
                updates.append("completed_at = CURRENT_TIMESTAMP")
                
            for key, value in kwargs.items():
                if key in ['started_at', 'completed_at']:
                    updates.append(f"{key} = ?")
                    values.append(value)
                    
            values.append(task_id)
            
            conn.execute(
                f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?",
                values
            )
            
            # Log evento
            self._log_event(conn, task_id, f'status_changed_to_{status}', kwargs)
            
    def save_task_result(self, task_id: str, result: Dict):
        """Guarda el resultado de ejecutar una tarea"""
        with sqlite3.connect(self.db_path) as conn:
            # Obtener número de intento
            attempt = conn.execute("""
                SELECT MAX(attempt_number) FROM task_results WHERE task_id = ?
            """, (task_id,)).fetchone()[0]
            
            attempt = (attempt or 0) + 1
            
            conn.execute("""
                INSERT INTO task_results 
                (task_id, attempt_number, status, started_at, completed_at, 
                 duration_seconds, output, error, artifacts, metrics)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task_id, attempt, result['status'],
                result['started_at'], result['completed_at'],
                result.get('duration'), result.get('output'),
                result.get('error'), json.dumps(result.get('artifacts', [])),
                json.dumps(result.get('metrics', {}))
            ))
            
            # Log evento
            self._log_event(conn, task_id, 'result_saved', {
                'attempt': attempt,
                'status': result['status']
            })
            
    def get_task_history(self, task_id: str) -> List[Dict]:
        """Obtiene historial de ejecuciones de una tarea"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            rows = conn.execute("""
                SELECT * FROM task_results 
                WHERE task_id = ?
                ORDER BY attempt_number DESC
            """, (task_id,)).fetchall()
            
            return [dict(row) for row in rows]
            
    def get_statistics(self) -> Dict:
        """Obtiene estadísticas generales"""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            
            # Conteo por estado
            status_counts = conn.execute("""
                SELECT status, COUNT(*) as count
                FROM tasks GROUP BY status
            """).fetchall()
            
            stats['by_status'] = dict(status_counts)
            
            # Conteo por tipo
            type_counts = conn.execute("""
                SELECT type, COUNT(*) as count
                FROM tasks GROUP BY type
            """).fetchall()
            
            stats['by_type'] = dict(type_counts)
            
            # Tasas de éxito
            success_rate = conn.execute("""
                SELECT 
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) * 100.0 / COUNT(*) as success_rate
                FROM task_results
            """).fetchone()[0]
            
            stats['success_rate'] = success_rate or 0
            
            # Tiempo promedio de ejecución
            avg_duration = conn.execute("""
                SELECT AVG(duration_seconds) FROM task_results
                WHERE status = 'completed'
            """).fetchone()[0]
            
            stats['avg_duration_seconds'] = avg_duration or 0
            
            return stats
            
    def cleanup_old_tasks(self, days: int = 30):
        """Limpia tareas antiguas completadas"""
        with sqlite3.connect(self.db_path) as conn:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            deleted = conn.execute("""
                DELETE FROM tasks
                WHERE status IN ('completed', 'failed', 'cancelled')
                AND completed_at < ?
            """, (cutoff_date,)).rowcount
            
            logging.info(f"Eliminadas {deleted} tareas antiguas")
            
            # Vacuum para recuperar espacio
            conn.execute("VACUUM")
            
    def _log_event(self, conn: sqlite3.Connection, task_id: str, event_type: str, data: Dict = None):
        """Registra un evento de tarea"""
        conn.execute("""
            INSERT INTO task_events (task_id, event_type, event_data)
            VALUES (?, ?, ?)
        """, (task_id, event_type, json.dumps(data or {})))


class TaskManager:
    """Manager principal que coordina todo el sistema de tareas"""
    
    def __init__(self, db_path: str = None):
        self.persistence = TaskPersistence(db_path)
        self.graph = TaskGraph()
        self.logger = logging.getLogger(__name__)
        self._rebuild_graph()
        
    def _rebuild_graph(self):
        """Reconstruye el grafo de dependencias desde la DB"""
        tasks = self.persistence.get_pending_tasks()
        
        for task in tasks:
            self.graph.add_task(task['id'], task)
            
            for dep in task.get('dependencies', []):
                if isinstance(dep, dict):
                    self.graph.add_dependency(task['id'], dep['depends_on'], dep.get('type', 'completion'))
                else:
                    self.graph.add_dependency(task['id'], dep)
                    
    def add_task(self, task: Dict) -> str:
        """Agrega una nueva tarea"""
        # Validar tarea
        self._validate_task(task)
        
        # Generar ID si no tiene
        if 'id' not in task:
            task['id'] = self._generate_task_id(task)
            
        # Guardar en DB
        task_id = self.persistence.save_task(task)
        
        # Actualizar grafo
        self.graph.add_task(task_id, task)
        for dep in task.get('dependencies', []):
            if isinstance(dep, dict):
                self.graph.add_dependency(task_id, dep['depends_on'], dep.get('type', 'completion'))
            else:
                self.graph.add_dependency(task_id, dep)
                
        self.logger.info(f"Tarea agregada: {task_id} - {task['title']}")
        return task_id
        
    def get_ready_tasks(self, completed_tasks: Set[str] = None) -> List[Dict]:
        """Obtiene tareas listas para ejecutar"""
        if completed_tasks is None:
            # Obtener de DB
            with sqlite3.connect(self.persistence.db_path) as conn:
                rows = conn.execute("""
                    SELECT id FROM tasks WHERE status IN ('completed', 'skipped')
                """).fetchall()
                completed_tasks = {row[0] for row in rows}
                
        # Obtener IDs listos del grafo
        ready_ids = self.graph.get_ready_tasks(completed_tasks)
        
        # Obtener datos completos
        ready_tasks = []
        for task_id in ready_ids:
            task = self.persistence.get_task(task_id)
            if task and task.get('status') == 'pending':
                ready_tasks.append(task)
                
        # Ordenar por prioridad
        ready_tasks.sort(key=lambda t: (t.get('priority', 3), t.get('created_at')))
        
        return ready_tasks
        
    def mark_task_completed(self, task_id: str, result: Dict):
        """Marca una tarea como completada"""
        self.persistence.update_task_status(task_id, 'completed')
        self.persistence.save_task_result(task_id, result)
        
        # Verificar si esto desbloquea otras tareas
        newly_ready = self.get_ready_tasks()
        if newly_ready:
            self.logger.info(f"Tareas desbloqueadas: {[t['id'] for t in newly_ready]}")
            
    def mark_task_failed(self, task_id: str, result: Dict):
        """Marca una tarea como fallida"""
        self.persistence.update_task_status(task_id, 'failed')
        self.persistence.save_task_result(task_id, result)
        
        # Verificar si hay tareas que dependen de esta
        dependent_tasks = list(self.graph.graph.successors(task_id))
        if dependent_tasks:
            self.logger.warning(f"Tareas bloqueadas por fallo: {dependent_tasks}")
            
    def load_tasks_from_yaml(self, file_path: str):
        """Carga tareas desde archivo YAML"""
        with open(file_path) as f:
            data = yaml.safe_load(f)
            
        for task_data in data.get('tasks', []):
            self.add_task(task_data)
            
        self.logger.info(f"Cargadas {len(data.get('tasks', []))} tareas desde {file_path}")
        
    def get_execution_plan(self) -> List[List[str]]:
        """Obtiene plan de ejecución en fases"""
        try:
            # Orden topológico
            order = self.graph.get_execution_order()
            
            # Agrupar por niveles (tareas que pueden ejecutarse en paralelo)
            levels = []
            remaining = set(order)
            completed = set()
            
            while remaining:
                # Encontrar tareas sin dependencias pendientes
                current_level = []
                for task_id in remaining:
                    predecessors = set(self.graph.graph.predecessors(task_id))
                    if predecessors.issubset(completed):
                        current_level.append(task_id)
                        
                if not current_level:
                    # No se puede avanzar, hay ciclos
                    break
                    
                levels.append(current_level)
                completed.update(current_level)
                remaining.difference_update(current_level)
                
            return levels
            
        except ValueError as e:
            self.logger.error(f"Error generando plan: {e}")
            return []
            
    def _validate_task(self, task: Dict):
        """Valida que una tarea tenga los campos requeridos"""
        required = ['title', 'type']
        for field in required:
            if field not in task:
                raise ValueError(f"Campo requerido faltante: {field}")
                
        # Validar tipo
        valid_types = [t.value for t in TaskType]
        if task['type'] not in valid_types:
            raise ValueError(f"Tipo inválido: {task['type']}. Debe ser uno de: {valid_types}")
            
    def _generate_task_id(self, task: Dict) -> str:
        """Genera ID único para una tarea"""
        # Usar hash del título + timestamp para evitar duplicados
        content = f"{task['title']}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]


# Ejemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Crear manager
    manager = TaskManager()
    
    # Agregar algunas tareas de ejemplo
    task1 = {
        'title': 'Analizar logs del sistema',
        'type': TaskType.ANALYSIS.value,
        'priority': 2,
        'description': 'Revisar logs en busca de errores o anomalías'
    }
    
    task2 = {
        'title': 'Limpiar archivos temporales',
        'type': TaskType.MAINTENANCE.value,
        'priority': 3,
        'dependencies': [task1['title']],  # Depende de análisis
        'description': 'Eliminar archivos temporales antiguos'
    }
    
    id1 = manager.add_task(task1)
    id2 = manager.add_task(task2)
    
    # Obtener tareas listas
    ready = manager.get_ready_tasks()
    print(f"Tareas listas: {[t['title'] for t in ready]}")
    
    # Obtener plan de ejecución
    plan = manager.get_execution_plan()
    print(f"Plan de ejecución: {plan}")
    
    # Estadísticas
    stats = manager.persistence.get_statistics()
    print(f"Estadísticas: {stats}")