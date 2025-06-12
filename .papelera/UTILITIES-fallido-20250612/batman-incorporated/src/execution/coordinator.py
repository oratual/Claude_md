"""
Sistema de coordinación avanzado para agentes paralelos.
Maneja comunicación, sincronización y resolución de conflictos.
"""

import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from queue import Queue, Empty
from enum import Enum
from dataclasses import dataclass, field


@dataclass
class AgentMessage:
    """Mensaje entre agentes."""
    from_agent: str
    to_agent: Optional[str]  # None = broadcast
    message_type: str
    content: Any
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'from': self.from_agent,
            'to': self.to_agent,
            'type': self.message_type,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }


class AgentCoordinator:
    """
    Coordina comunicación y sincronización entre agentes.
    
    Características:
    - Sistema de mensajería pub/sub
    - Detección y resolución de conflictos
    - Sincronización de archivos
    - Broadcast de eventos importantes
    """
    
    def __init__(self, shared_dir: Path):
        self.shared_dir = shared_dir
        self.messages_dir = shared_dir / 'messages'
        self.messages_dir.mkdir(exist_ok=True)
        
        # Colas de mensajes por agente
        self.message_queues: Dict[str, Queue] = {}
        
        # Estado de archivos para detectar conflictos
        self.file_locks: Dict[str, str] = {}  # archivo -> agente
        self.file_versions: Dict[str, int] = {}  # archivo -> versión
        
        # Thread para procesar mensajes
        self.running = False
        self.processor_thread = None
        
    def register_agent(self, agent_name: str):
        """Registra un nuevo agente en el sistema."""
        if agent_name not in self.message_queues:
            self.message_queues[agent_name] = Queue()
            
            # Archivo de inbox del agente
            inbox_file = self.messages_dir / f'{agent_name}_inbox.jsonl'
            inbox_file.touch()
    
    def send_message(self, message: AgentMessage):
        """Envía un mensaje a uno o todos los agentes."""
        # Guardar en archivo para persistencia
        self._persist_message(message)
        
        # Distribuir a las colas
        if message.to_agent:
            # Mensaje directo
            if message.to_agent in self.message_queues:
                self.message_queues[message.to_agent].put(message)
        else:
            # Broadcast
            for agent_name, queue in self.message_queues.items():
                if agent_name != message.from_agent:
                    queue.put(message)
    
    def get_messages(self, agent_name: str, timeout: float = 0.1) -> List[AgentMessage]:
        """Obtiene mensajes pendientes para un agente."""
        messages = []
        if agent_name not in self.message_queues:
            return messages
            
        queue = self.message_queues[agent_name]
        
        # Obtener todos los mensajes disponibles
        while True:
            try:
                message = queue.get(timeout=timeout)
                messages.append(message)
            except Empty:
                break
                
        return messages
    
    def request_file_lock(self, agent_name: str, file_path: str) -> bool:
        """
        Solicita un lock exclusivo sobre un archivo.
        
        Returns:
            True si se obtuvo el lock, False si ya está tomado
        """
        if file_path in self.file_locks:
            current_owner = self.file_locks[file_path]
            if current_owner != agent_name:
                # Archivo bloqueado por otro agente
                self._notify_conflict(agent_name, current_owner, file_path)
                return False
        
        # Otorgar lock
        self.file_locks[file_path] = agent_name
        self.file_versions[file_path] = self.file_versions.get(file_path, 0) + 1
        
        # Notificar a otros agentes
        self.send_message(AgentMessage(
            from_agent=agent_name,
            to_agent=None,
            message_type='file_locked',
            content={
                'file': file_path,
                'version': self.file_versions[file_path]
            }
        ))
        
        return True
    
    def release_file_lock(self, agent_name: str, file_path: str):
        """Libera el lock de un archivo."""
        if file_path in self.file_locks and self.file_locks[file_path] == agent_name:
            del self.file_locks[file_path]
            
            # Notificar liberación
            self.send_message(AgentMessage(
                from_agent=agent_name,
                to_agent=None,
                message_type='file_unlocked',
                content={'file': file_path}
            ))
    
    def broadcast_discovery(self, agent_name: str, discovery_type: str, details: Any):
        """Broadcast un descubrimiento importante a todos los agentes."""
        self.send_message(AgentMessage(
            from_agent=agent_name,
            to_agent=None,
            message_type='discovery',
            content={
                'type': discovery_type,
                'details': details
            }
        ))
    
    def report_error(self, agent_name: str, error_type: str, details: str):
        """Reporta un error para que otros agentes lo eviten."""
        self.send_message(AgentMessage(
            from_agent=agent_name,
            to_agent=None,
            message_type='error_report',
            content={
                'error_type': error_type,
                'details': details,
                'avoid_pattern': self._extract_error_pattern(error_type, details)
            }
        ))
    
    def coordinate_parallel_work(self, tasks: List[Any]) -> Dict[str, List[Any]]:
        """
        Distribuye tareas entre agentes evitando conflictos.
        
        Args:
            tasks: Lista de tareas a distribuir
            
        Returns:
            Diccionario agente -> tareas asignadas
        """
        # Analizar dependencias de archivos
        file_dependencies = self._analyze_file_dependencies(tasks)
        
        # Agrupar tareas que no tienen conflictos
        task_groups = self._group_non_conflicting_tasks(tasks, file_dependencies)
        
        # Asignar grupos a agentes
        agent_assignments = self._assign_task_groups(task_groups)
        
        return agent_assignments
    
    def _persist_message(self, message: AgentMessage):
        """Persiste un mensaje en el sistema de archivos."""
        # Archivo general de mensajes
        all_messages_file = self.messages_dir / 'all_messages.jsonl'
        with open(all_messages_file, 'a') as f:
            f.write(json.dumps(message.to_dict()) + '\n')
        
        # Archivo específico del destinatario
        if message.to_agent:
            inbox_file = self.messages_dir / f'{message.to_agent}_inbox.jsonl'
            with open(inbox_file, 'a') as f:
                f.write(json.dumps(message.to_dict()) + '\n')
    
    def _notify_conflict(self, requesting_agent: str, current_owner: str, file_path: str):
        """Notifica un conflicto de archivo."""
        # Notificar al agente que solicita
        self.send_message(AgentMessage(
            from_agent='coordinator',
            to_agent=requesting_agent,
            message_type='file_conflict',
            content={
                'file': file_path,
                'locked_by': current_owner,
                'suggestion': f'Espera a que {current_owner} termine o trabaja en otro archivo'
            }
        ))
        
        # Notificar al dueño actual
        self.send_message(AgentMessage(
            from_agent='coordinator',
            to_agent=current_owner,
            message_type='conflict_notification',
            content={
                'file': file_path,
                'requested_by': requesting_agent,
                'suggestion': f'Considera liberar {file_path} pronto para {requesting_agent}'
            }
        ))
    
    def _extract_error_pattern(self, error_type: str, details: str) -> str:
        """Extrae un patrón del error para que otros lo eviten."""
        patterns = {
            'import_error': 'Verificar imports antes de usar',
            'syntax_error': 'Validar sintaxis con linter',
            'type_error': 'Verificar tipos de datos',
            'file_not_found': 'Verificar existencia de archivos',
            'permission_error': 'Verificar permisos de archivos'
        }
        
        return patterns.get(error_type, 'Verificar condiciones previas')
    
    def _analyze_file_dependencies(self, tasks: List[Any]) -> Dict[str, Set[str]]:
        """Analiza qué archivos necesita cada tarea."""
        dependencies = {}
        
        for task in tasks:
            task_files = set()
            
            # Extraer archivos mencionados en la descripción
            # (En implementación real, sería más sofisticado)
            if hasattr(task, 'files'):
                task_files.update(task.files)
            
            dependencies[task.id] = task_files
        
        return dependencies
    
    def _group_non_conflicting_tasks(self, tasks: List[Any], dependencies: Dict[str, Set[str]]) -> List[List[Any]]:
        """Agrupa tareas que no tienen conflictos de archivos."""
        groups = []
        assigned = set()
        
        for task in tasks:
            if task.id in assigned:
                continue
                
            # Crear nuevo grupo con esta tarea
            group = [task]
            group_files = dependencies.get(task.id, set())
            assigned.add(task.id)
            
            # Agregar tareas que no conflictúan
            for other_task in tasks:
                if other_task.id in assigned:
                    continue
                    
                other_files = dependencies.get(other_task.id, set())
                
                # Si no hay archivos en común, pueden ir juntas
                if not group_files.intersection(other_files):
                    group.append(other_task)
                    group_files.update(other_files)
                    assigned.add(other_task.id)
            
            groups.append(group)
        
        return groups
    
    def _assign_task_groups(self, groups: List[List[Any]]) -> Dict[str, List[Any]]:
        """Asigna grupos de tareas a agentes."""
        agents = ['alfred', 'robin', 'oracle', 'batgirl', 'lucius']
        assignments = {agent: [] for agent in agents}
        
        # Distribuir grupos entre agentes
        for i, group in enumerate(groups):
            agent = agents[i % len(agents)]
            assignments[agent].extend(group)
        
        return assignments
    
    def get_coordination_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema de coordinación."""
        return {
            'active_locks': len(self.file_locks),
            'locked_files': list(self.file_locks.keys()),
            'message_queues': {
                agent: queue.qsize() 
                for agent, queue in self.message_queues.items()
            },
            'total_messages': sum(
                q.qsize() for q in self.message_queues.values()
            )
        }


class ConflictResolver:
    """
    Resuelve conflictos entre cambios de diferentes agentes.
    """
    
    def __init__(self, coordinator: AgentCoordinator):
        self.coordinator = coordinator
        self.resolution_strategies = {
            'merge': self._merge_changes,
            'priority': self._apply_by_priority,
            'timestamp': self._apply_by_timestamp,
            'interactive': self._interactive_resolution
        }
    
    def resolve_conflict(self, file_path: str, changes: List[Dict[str, Any]], 
                        strategy: str = 'merge') -> Dict[str, Any]:
        """
        Resuelve conflictos entre múltiples cambios.
        
        Args:
            file_path: Archivo en conflicto
            changes: Lista de cambios de diferentes agentes
            strategy: Estrategia de resolución
            
        Returns:
            Cambio resuelto final
        """
        if strategy not in self.resolution_strategies:
            strategy = 'merge'
        
        resolver = self.resolution_strategies[strategy]
        return resolver(file_path, changes)
    
    def _merge_changes(self, file_path: str, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Intenta hacer merge automático de cambios no conflictivos."""
        # Implementación simplificada
        # En producción, usaría git merge o algoritmos más sofisticados
        
        if len(changes) == 1:
            return changes[0]
        
        # Si los cambios son en diferentes partes del archivo, merge
        # Si son en la misma parte, usar el más reciente
        return self._apply_by_timestamp(file_path, changes)
    
    def _apply_by_priority(self, file_path: str, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aplica cambios según prioridad del agente."""
        agent_priority = {
            'alfred': 5,  # Máxima prioridad - arquitectura
            'oracle': 4,  # Alta - testing y seguridad
            'batgirl': 3,  # Media - frontend
            'robin': 2,   # Media-baja - devops
            'lucius': 1   # Baja - experimental
        }
        
        # Ordenar por prioridad
        sorted_changes = sorted(
            changes,
            key=lambda c: agent_priority.get(c.get('agent', ''), 0),
            reverse=True
        )
        
        return sorted_changes[0]
    
    def _apply_by_timestamp(self, file_path: str, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aplica el cambio más reciente."""
        return max(changes, key=lambda c: c.get('timestamp', ''))
    
    def _interactive_resolution(self, file_path: str, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Resuelve conflictos de forma interactiva (placeholder)."""
        # En producción, esto abriría una UI o prompt para el usuario
        # Por ahora, usa merge automático
        return self._merge_changes(file_path, changes)