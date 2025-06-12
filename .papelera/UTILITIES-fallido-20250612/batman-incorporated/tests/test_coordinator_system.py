"""
Tests for the agent coordination system.
Tests message passing, file locking, and conflict resolution.
"""

import unittest
import tempfile
import json
import time
from pathlib import Path
from datetime import datetime
import threading

from src.execution.coordinator import AgentCoordinator, AgentMessage, ConflictResolver
from src.core.task import Task, TaskType


class TestAgentCoordinator(unittest.TestCase):
    """Tests para el sistema de coordinación de agentes."""
    
    def setUp(self):
        """Setup para cada test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.coordinator = AgentCoordinator(self.temp_dir)
    
    def test_agent_registration(self):
        """Test registro de agentes en el sistema."""
        # Registrar agentes
        self.coordinator.register_agent('alfred')
        self.coordinator.register_agent('robin')
        
        # Verificar que se crearon las colas
        self.assertIn('alfred', self.coordinator.message_queues)
        self.assertIn('robin', self.coordinator.message_queues)
        
        # Verificar archivos inbox
        alfred_inbox = self.coordinator.messages_dir / 'alfred_inbox.jsonl'
        robin_inbox = self.coordinator.messages_dir / 'robin_inbox.jsonl'
        
        self.assertTrue(alfred_inbox.exists())
        self.assertTrue(robin_inbox.exists())
    
    def test_direct_message_sending(self):
        """Test envío de mensajes directos entre agentes."""
        self.coordinator.register_agent('alfred')
        self.coordinator.register_agent('robin')
        
        # Alfred envía mensaje a Robin
        message = AgentMessage(
            from_agent='alfred',
            to_agent='robin',
            message_type='task_update',
            content={
                'task': 'Arquitectura completada',
                'next_step': 'Puedes empezar con el deployment'
            }
        )
        
        self.coordinator.send_message(message)
        
        # Robin recibe el mensaje
        robin_messages = self.coordinator.get_messages('robin')
        
        self.assertEqual(len(robin_messages), 1)
        self.assertEqual(robin_messages[0].from_agent, 'alfred')
        self.assertEqual(robin_messages[0].message_type, 'task_update')
        self.assertEqual(robin_messages[0].content['task'], 'Arquitectura completada')
        
        # Alfred no debe recibir su propio mensaje
        alfred_messages = self.coordinator.get_messages('alfred')
        self.assertEqual(len(alfred_messages), 0)
    
    def test_broadcast_messages(self):
        """Test mensajes broadcast a todos los agentes."""
        # Registrar múltiples agentes
        agents = ['alfred', 'robin', 'oracle', 'batgirl']
        for agent in agents:
            self.coordinator.register_agent(agent)
        
        # Oracle hace un descubrimiento importante
        discovery_message = AgentMessage(
            from_agent='oracle',
            to_agent=None,  # Broadcast
            message_type='discovery',
            content={
                'type': 'security_vulnerability',
                'severity': 'high',
                'details': 'SQL injection en endpoint /users'
            }
        )
        
        self.coordinator.send_message(discovery_message)
        
        # Todos excepto Oracle deben recibir el mensaje
        for agent in agents:
            messages = self.coordinator.get_messages(agent)
            if agent == 'oracle':
                self.assertEqual(len(messages), 0)
            else:
                self.assertEqual(len(messages), 1)
                self.assertEqual(messages[0].message_type, 'discovery')
                self.assertEqual(messages[0].content['severity'], 'high')
    
    def test_file_locking_mechanism(self):
        """Test mecanismo de bloqueo de archivos."""
        self.coordinator.register_agent('alfred')
        self.coordinator.register_agent('batgirl')
        
        # Alfred toma lock de main.js
        lock1 = self.coordinator.request_file_lock('alfred', 'src/main.js')
        self.assertTrue(lock1)
        
        # Batgirl intenta tomar el mismo archivo
        lock2 = self.coordinator.request_file_lock('batgirl', 'src/main.js')
        self.assertFalse(lock2)
        
        # Batgirl debe recibir notificación de conflicto
        batgirl_messages = self.coordinator.get_messages('batgirl')
        conflict_messages = [m for m in batgirl_messages if m.message_type == 'file_conflict']
        
        self.assertEqual(len(conflict_messages), 1)
        self.assertEqual(conflict_messages[0].content['locked_by'], 'alfred')
        self.assertIn('Espera', conflict_messages[0].content['suggestion'])
        
        # Alfred también recibe notificación
        alfred_messages = self.coordinator.get_messages('alfred')
        notification_messages = [m for m in alfred_messages if m.message_type == 'conflict_notification']
        
        self.assertEqual(len(notification_messages), 1)
        self.assertEqual(notification_messages[0].content['requested_by'], 'batgirl')
    
    def test_file_lock_release(self):
        """Test liberación de locks de archivos."""
        self.coordinator.register_agent('alfred')
        self.coordinator.register_agent('robin')
        
        # Alfred toma y luego libera un lock
        self.coordinator.request_file_lock('alfred', 'config.yml')
        self.coordinator.release_file_lock('alfred', 'config.yml')
        
        # Robin ahora puede tomar el lock
        lock_success = self.coordinator.request_file_lock('robin', 'config.yml')
        self.assertTrue(lock_success)
        
        # Verificar mensajes de liberación
        robin_messages = self.coordinator.get_messages('robin')
        unlock_messages = [m for m in robin_messages if m.message_type == 'file_unlocked']
        
        self.assertGreater(len(unlock_messages), 0)
    
    def test_error_reporting_and_pattern_extraction(self):
        """Test reporte de errores y extracción de patrones."""
        self.coordinator.register_agent('robin')
        self.coordinator.register_agent('oracle')
        
        # Robin reporta un error
        self.coordinator.report_error(
            'robin',
            'import_error',
            'ModuleNotFoundError: No module named requests'
        )
        
        # Oracle recibe el reporte
        oracle_messages = self.coordinator.get_messages('oracle')
        error_reports = [m for m in oracle_messages if m.message_type == 'error_report']
        
        self.assertEqual(len(error_reports), 1)
        self.assertEqual(error_reports[0].content['error_type'], 'import_error')
        self.assertIn('Verificar imports', error_reports[0].content['avoid_pattern'])
    
    def test_parallel_work_coordination(self):
        """Test coordinación de trabajo paralelo."""
        # Crear tareas con dependencias de archivos
        class MockTask:
            def __init__(self, id, files):
                self.id = id
                self.files = files
        
        tasks = [
            MockTask('task1', {'src/auth.py', 'src/models.py'}),
            MockTask('task2', {'src/api.py', 'src/utils.py'}),
            MockTask('task3', {'src/auth.py', 'src/api.py'}),  # Conflicto con task1 y task2
            MockTask('task4', {'src/frontend.js'}),
            MockTask('task5', {'src/tests.py'})
        ]
        
        # Coordinar trabajo
        assignments = self.coordinator.coordinate_parallel_work(tasks)
        
        # Verificar que se asignaron todas las tareas
        total_assigned = sum(len(tasks) for tasks in assignments.values())
        self.assertEqual(total_assigned, 5)
        
        # Verificar que no hay conflictos en el mismo grupo
        for agent, agent_tasks in assignments.items():
            files_in_group = set()
            for task in agent_tasks:
                if hasattr(task, 'files'):
                    # No debe haber intersección con archivos ya en el grupo
                    self.assertEqual(len(files_in_group.intersection(task.files)), 0)
                    files_in_group.update(task.files)
    
    def test_message_persistence(self):
        """Test persistencia de mensajes en archivos."""
        self.coordinator.register_agent('alfred')
        
        # Enviar mensaje
        message = AgentMessage(
            from_agent='system',
            to_agent='alfred',
            message_type='instruction',
            content={'action': 'start_task'}
        )
        
        self.coordinator.send_message(message)
        
        # Verificar archivo de mensajes
        all_messages_file = self.coordinator.messages_dir / 'all_messages.jsonl'
        self.assertTrue(all_messages_file.exists())
        
        # Leer y verificar contenido
        with open(all_messages_file, 'r') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 1)
            
            msg_data = json.loads(lines[0])
            self.assertEqual(msg_data['from'], 'system')
            self.assertEqual(msg_data['to'], 'alfred')
            self.assertEqual(msg_data['type'], 'instruction')
    
    def test_concurrent_message_handling(self):
        """Test manejo concurrente de mensajes."""
        self.coordinator.register_agent('alfred')
        self.coordinator.register_agent('robin')
        
        messages_sent = []
        
        def send_messages(agent_from, count):
            """Enviar múltiples mensajes desde un agente."""
            for i in range(count):
                msg = AgentMessage(
                    from_agent=agent_from,
                    to_agent=None,  # Broadcast
                    message_type='update',
                    content={'index': i, 'from': agent_from}
                )
                self.coordinator.send_message(msg)
                messages_sent.append(msg)
                time.sleep(0.01)
        
        # Lanzar threads para enviar mensajes concurrentemente
        thread1 = threading.Thread(target=send_messages, args=('alfred', 5))
        thread2 = threading.Thread(target=send_messages, args=('robin', 5))
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # Verificar que todos los mensajes fueron recibidos
        time.sleep(0.1)  # Dar tiempo para procesar
        
        # Alfred debe recibir los 5 mensajes de Robin
        alfred_messages = self.coordinator.get_messages('alfred')
        alfred_from_robin = [m for m in alfred_messages if m.content['from'] == 'robin']
        self.assertEqual(len(alfred_from_robin), 5)
        
        # Robin debe recibir los 5 mensajes de Alfred
        robin_messages = self.coordinator.get_messages('robin')
        robin_from_alfred = [m for m in robin_messages if m.content['from'] == 'alfred']
        self.assertEqual(len(robin_from_alfred), 5)
    
    def test_coordination_stats(self):
        """Test estadísticas del sistema de coordinación."""
        # Configurar estado
        self.coordinator.register_agent('alfred')
        self.coordinator.register_agent('robin')
        
        self.coordinator.request_file_lock('alfred', 'src/main.py')
        self.coordinator.request_file_lock('robin', 'src/api.py')
        
        # Enviar algunos mensajes
        for i in range(3):
            self.coordinator.send_message(AgentMessage(
                from_agent='alfred',
                to_agent='robin',
                message_type='update',
                content={'index': i}
            ))
        
        # Obtener estadísticas
        stats = self.coordinator.get_coordination_stats()
        
        self.assertEqual(stats['active_locks'], 2)
        self.assertIn('src/main.py', stats['locked_files'])
        self.assertIn('src/api.py', stats['locked_files'])
        self.assertEqual(stats['message_queues']['robin'], 3)
        self.assertEqual(stats['total_messages'], 3)


class TestConflictResolver(unittest.TestCase):
    """Tests para el sistema de resolución de conflictos."""
    
    def setUp(self):
        """Setup para cada test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.coordinator = AgentCoordinator(self.temp_dir)
        self.resolver = ConflictResolver(self.coordinator)
    
    def test_merge_strategy(self):
        """Test estrategia de merge para resolver conflictos."""
        changes = [
            {
                'agent': 'alfred',
                'timestamp': '2024-01-10T10:00:00',
                'content': 'Cambio de Alfred',
                'lines': '1-50'
            },
            {
                'agent': 'robin',
                'timestamp': '2024-01-10T10:05:00',
                'content': 'Cambio de Robin',
                'lines': '100-150'
            }
        ]
        
        # Como los cambios son en diferentes líneas, deberían poder merge
        result = self.resolver.resolve_conflict('src/main.py', changes, strategy='merge')
        
        # En este caso simple, usa timestamp (el más reciente)
        self.assertEqual(result['agent'], 'robin')
    
    def test_priority_strategy(self):
        """Test estrategia de prioridad para resolver conflictos."""
        changes = [
            {
                'agent': 'robin',
                'timestamp': '2024-01-10T10:10:00',
                'content': 'Cambio de Robin'
            },
            {
                'agent': 'alfred',
                'timestamp': '2024-01-10T10:00:00',
                'content': 'Cambio de Alfred'
            },
            {
                'agent': 'oracle',
                'timestamp': '2024-01-10T10:05:00',
                'content': 'Cambio de Oracle'
            }
        ]
        
        # Resolver por prioridad de agente
        result = self.resolver.resolve_conflict('src/security.py', changes, strategy='priority')
        
        # Alfred tiene máxima prioridad (arquitectura)
        self.assertEqual(result['agent'], 'alfred')
    
    def test_timestamp_strategy(self):
        """Test estrategia de timestamp para resolver conflictos."""
        changes = [
            {
                'agent': 'batgirl',
                'timestamp': '2024-01-10T09:00:00',
                'content': 'Cambio temprano'
            },
            {
                'agent': 'lucius',
                'timestamp': '2024-01-10T11:00:00',
                'content': 'Cambio más reciente'
            }
        ]
        
        result = self.resolver.resolve_conflict('src/ui.js', changes, strategy='timestamp')
        
        # Debe elegir el más reciente
        self.assertEqual(result['agent'], 'lucius')
        self.assertEqual(result['content'], 'Cambio más reciente')
    
    def test_fallback_to_merge(self):
        """Test fallback a estrategia merge cuando la estrategia no existe."""
        changes = [
            {'agent': 'alfred', 'timestamp': '2024-01-10T10:00:00'}
        ]
        
        # Estrategia inexistente
        result = self.resolver.resolve_conflict('file.py', changes, strategy='inexistente')
        
        # Debe usar merge por defecto
        self.assertEqual(result['agent'], 'alfred')


if __name__ == '__main__':
    unittest.main()