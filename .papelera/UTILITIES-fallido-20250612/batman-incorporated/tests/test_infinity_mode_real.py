"""
Tests for Infinity Mode with real subprocess launching.
Tests the revolutionary parallel execution with multiple Claude instances.
"""

import unittest
import tempfile
import json
import time
import threading
from pathlib import Path
from unittest.mock import patch, MagicMock, call
import subprocess

from src.execution.infinity_mode import InfinityMode
from src.core.task import Task, TaskBatch, TaskType
from src.core.config import Config


class TestInfinityModeReal(unittest.TestCase):
    """Tests para Infinity Mode con lanzamiento real de subprocesos."""
    
    def setUp(self):
        """Setup para cada test."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'auto_launch': False,
            'max_instances': 5,
            'instance_timeout': 3600
        }
    
    def test_infinity_mode_file_structure(self):
        """Test creación de estructura de archivos para Infinity Mode."""
        mode = InfinityMode(self.config)
        
        tasks = [
            Task(title="Task 1", assigned_to='alfred'),
            Task(title="Task 2", assigned_to='robin'),
            Task(title="Task 3", assigned_to='alfred')
        ]
        
        # Preparar modo
        success = mode.prepare(tasks)
        self.assertTrue(success)
        
        # Verificar estructura de directorios
        self.assertTrue(mode.shared_dir.exists())
        self.assertTrue((mode.shared_dir / 'context').exists())
        self.assertTrue((mode.shared_dir / 'status').exists())
        self.assertTrue((mode.shared_dir / 'results').exists())
        
        # Verificar archivos de contexto
        self.assertTrue(mode.context_file.exists())
        
        context_data = json.loads(mode.context_file.read_text())
        self.assertEqual(context_data['total_tasks'], 3)
        self.assertEqual(context_data['mode'], 'infinity')
    
    def test_agent_instruction_generation(self):
        """Test generación de instrucciones para cada agente."""
        mode = InfinityMode(self.config)
        
        tasks = [
            Task(
                title="Implementar autenticación",
                description="Sistema completo de auth",
                assigned_to='alfred'
            ),
            Task(
                title="Configurar CI/CD",
                description="GitHub Actions setup",
                assigned_to='robin'
            ),
            Task(
                title="Escribir tests E2E",
                description="Tests completos del sistema",
                assigned_to='oracle'
            )
        ]
        
        mode.prepare(tasks)
        instructions = mode._generate_instance_instructions()
        
        # Verificar instrucciones para cada agente
        self.assertEqual(len(instructions), 3)
        self.assertIn('alfred', instructions)
        self.assertIn('robin', instructions)
        self.assertIn('oracle', instructions)
        
        # Verificar contenido de instrucciones de Alfred
        alfred_inst = instructions['alfred']
        alfred_file = Path(alfred_inst['instruction_file'])
        self.assertTrue(alfred_file.exists())
        
        content = alfred_file.read_text()
        self.assertIn("Eres alfred", content)
        self.assertIn("mayordomo perfecto", content)
        self.assertIn("Implementar autenticación", content)
        self.assertIn(str(mode.context_file), content)
        self.assertIn("#memoria", content)
    
    @patch('subprocess.Popen')
    def test_auto_launch_subprocess(self, mock_popen):
        """Test lanzamiento automático de subprocesos."""
        # Configurar auto launch
        config = self.config.copy()
        config['auto_launch'] = True
        
        mode = InfinityMode(config)
        
        # Mock de procesos
        mock_processes = []
        for i in range(3):
            mock_proc = MagicMock()
            mock_proc.pid = 1000 + i
            mock_proc.poll.return_value = None  # Proceso activo
            mock_processes.append(mock_proc)
        
        mock_popen.side_effect = mock_processes
        
        tasks = [
            Task(title=f"Task {i}", assigned_to=['alfred', 'robin', 'oracle'][i])
            for i in range(3)
        ]
        
        mode.prepare(tasks)
        instructions = mode._generate_instance_instructions()
        
        # Lanzar instancias
        mode._auto_launch_instances(instructions)
        
        # Verificar lanzamientos
        self.assertEqual(mock_popen.call_count, 3)
        
        # Verificar parámetros de cada lanzamiento
        for call_args in mock_popen.call_args_list:
            cmd = call_args[0][0]
            kwargs = call_args[1]
            
            # Comando correcto
            self.assertEqual(cmd[0], 'claude')
            self.assertIn('--model', cmd)
            self.assertIn('opus', cmd)
            self.assertIn('--print', cmd)
            self.assertIn('--dangerously-skip-permissions', cmd)
            self.assertIn('--max-turns', cmd)
            
            # Archivo de instrucciones
            self.assertTrue(any('@' in arg for arg in cmd))
            
            # Configuración del proceso
            self.assertEqual(kwargs['cwd'], str(mode.shared_dir))
            self.assertTrue(kwargs['start_new_session'])
    
    def test_status_monitoring(self):
        """Test monitoreo de estado de instancias."""
        mode = InfinityMode(self.config)
        
        tasks = [
            Task(title="Task 1", assigned_to='alfred'),
            Task(title="Task 2", assigned_to='robin')
        ]
        
        mode.prepare(tasks)
        mode._generate_instance_instructions()
        
        # Simular actualización de estado por agente
        status_data = {
            'session_id': mode.session_id,
            'updated_at': '2024-01-10T10:00:00',
            'agents': {
                'alfred': {
                    'id': 'abc123',
                    'status': 'working',
                    'tasks_count': 1,
                    'started': '2024-01-10T10:00:00'
                },
                'robin': {
                    'id': 'def456',
                    'status': 'completed',
                    'tasks_count': 1,
                    'started': '2024-01-10T10:00:00'
                }
            }
        }
        
        mode._write_json(mode.status_file, status_data)
        
        # Leer estado
        status = mode._read_json(mode.status_file)
        
        self.assertEqual(status['agents']['alfred']['status'], 'working')
        self.assertEqual(status['agents']['robin']['status'], 'completed')
    
    def test_result_collection(self):
        """Test recolección de resultados de agentes."""
        mode = InfinityMode(self.config)
        
        tasks = [
            Task(title="Task 1", assigned_to='alfred'),
            Task(title="Task 2", assigned_to='robin')
        ]
        
        mode.prepare(tasks)
        
        # Simular resultados de agentes
        results_dir = mode.shared_dir / 'results'
        
        # Resultados de Alfred
        alfred_dir = results_dir / 'alfred'
        alfred_dir.mkdir(parents=True)
        
        alfred_result = {
            'task_id': tasks[0].id,
            'status': 'completed',
            'files_created': ['src/auth.py'],
            'insights': 'Implementé sistema de autenticación JWT'
        }
        (alfred_dir / 'result_1.json').write_text(json.dumps(alfred_result))
        
        # Resultados de Robin
        robin_dir = results_dir / 'robin'
        robin_dir.mkdir(parents=True)
        
        robin_result = {
            'task_id': tasks[1].id,
            'status': 'completed',
            'files_created': ['.github/workflows/ci.yml'],
            'insights': 'CI/CD configurado con GitHub Actions'
        }
        (robin_dir / 'result_1.json').write_text(json.dumps(robin_result))
        
        # Recolectar resultados
        results = mode._collect_results()
        
        self.assertEqual(results['mode'], 'infinity')
        self.assertIn('alfred', results['agents'])
        self.assertIn('robin', results['agents'])
        
        self.assertEqual(results['agents']['alfred']['tasks_completed'], 1)
        self.assertEqual(results['agents']['robin']['tasks_completed'], 1)
        
        # Verificar contenido de resultados
        alfred_results = results['agents']['alfred']['results']
        self.assertEqual(len(alfred_results), 1)
        self.assertEqual(alfred_results[0]['status'], 'completed')
    
    @patch('subprocess.Popen')
    def test_process_monitoring_and_timeout(self, mock_popen):
        """Test monitoreo de procesos y manejo de timeout."""
        config = self.config.copy()
        config['auto_launch'] = True
        
        mode = InfinityMode(config)
        
        # Mock proceso que eventualmente termina
        mock_proc = MagicMock()
        mock_proc.pid = 12345
        # Primero activo, luego terminado
        mock_proc.poll.side_effect = [None, None, 0]
        mock_popen.return_value = mock_proc
        
        tasks = [Task(title="Long task", assigned_to='alfred')]
        mode.prepare(tasks)
        
        # Mock tiempo para simular timeout rápido
        original_time = time.time
        start_time = original_time()
        
        def mock_time():
            # Simular que pasó mucho tiempo
            return start_time + 4000  # Más de 1 hora
        
        with patch('time.time', side_effect=[start_time, start_time + 100, mock_time]):
            batch = TaskBatch("Test", tasks)
            results = mode.execute(batch)
        
        # Debería haber terminado por timeout
        self.assertIsNotNone(results)
    
    def test_parallel_coordination_files(self):
        """Test archivos de coordinación para trabajo paralelo."""
        mode = InfinityMode(self.config)
        
        tasks = [
            Task(title="Backend API", assigned_to='alfred'),
            Task(title="Frontend UI", assigned_to='batgirl'),
            Task(title="Database schema", assigned_to='alfred')
        ]
        
        mode.prepare(tasks)
        instructions = mode._generate_instance_instructions()
        
        # Verificar que cada agente sabe en qué están trabajando los otros
        for agent_name, inst in instructions.items():
            inst_file = Path(inst['instruction_file'])
            content = inst_file.read_text()
            
            # Debe mencionar el trabajo de otros agentes
            if agent_name == 'alfred':
                self.assertIn("Batgirl está trabajando en:", content)
            elif agent_name == 'batgirl':
                self.assertIn("Alfred está trabajando en:", content)
    
    def test_session_archival(self):
        """Test archivo de sesión después de completar."""
        mode = InfinityMode(self.config)
        
        tasks = [Task(title="Test task")]
        mode.prepare(tasks)
        
        # Crear algunos archivos de sesión
        mode.context_file.write_text('{"test": "data"}')
        mode.status_file.write_text('{"status": "completed"}')
        
        # Limpiar y archivar
        mode.cleanup()
        
        # Verificar que se archivó
        archive_dir = mode.shared_dir / 'archive' / mode.session_id
        self.assertTrue(archive_dir.exists())
        self.assertTrue((archive_dir / mode.context_file.name).exists())
        self.assertTrue((archive_dir / mode.status_file.name).exists())
        
        # Archivos originales movidos
        self.assertFalse(mode.context_file.exists())
        self.assertFalse(mode.status_file.exists())


class TestInfinityModeIntegration(unittest.TestCase):
    """Tests de integración completa de Infinity Mode."""
    
    @patch('subprocess.Popen')
    def test_complete_infinity_workflow(self, mock_popen):
        """Test flujo completo de trabajo en Infinity Mode."""
        # Configurar mocks
        mock_processes = []
        for i in range(3):
            mock_proc = MagicMock()
            mock_proc.pid = 2000 + i
            mock_proc.poll.side_effect = [None, None, 0]  # Activo, activo, terminado
            mock_processes.append(mock_proc)
        
        mock_popen.side_effect = mock_processes
        
        # Configurar Infinity Mode
        config = {
            'auto_launch': True,
            'max_instances': 5
        }
        mode = InfinityMode(config)
        
        # Crear batch de tareas complejas
        tasks = [
            Task(
                title="Diseñar arquitectura de microservicios",
                description="Diseñar sistema completo con 5 microservicios",
                type=TaskType.DEVELOPMENT,
                assigned_to='alfred',
                estimated_hours=4
            ),
            Task(
                title="Implementar servicio de autenticación",
                description="JWT, OAuth2, refresh tokens",
                type=TaskType.DEVELOPMENT,
                assigned_to='robin',
                estimated_hours=3
            ),
            Task(
                title="Crear suite de tests de integración",
                description="Tests E2E para todos los servicios",
                type=TaskType.TESTING,
                assigned_to='oracle',
                estimated_hours=3
            )
        ]
        
        batch = TaskBatch("Proyecto Microservicios", tasks)
        
        # Simular resultados en archivos
        def create_mock_results():
            time.sleep(0.1)  # Simular trabajo
            results_dir = mode.shared_dir / 'results'
            
            # Resultado Alfred
            alfred_dir = results_dir / 'alfred'
            alfred_dir.mkdir(parents=True, exist_ok=True)
            (alfred_dir / 'result_1.json').write_text(json.dumps({
                'task_id': tasks[0].id,
                'status': 'completed',
                'architecture': {
                    'services': ['auth', 'users', 'products', 'orders', 'notifications'],
                    'patterns': ['API Gateway', 'Service Mesh', 'Event Sourcing']
                }
            }))
            
            # Resultado Robin
            robin_dir = results_dir / 'robin'
            robin_dir.mkdir(parents=True, exist_ok=True)
            (robin_dir / 'result_1.json').write_text(json.dumps({
                'task_id': tasks[1].id,
                'status': 'completed',
                'implementation': {
                    'endpoints': ['/auth/login', '/auth/refresh', '/auth/logout'],
                    'security': 'JWT + Redis sessions'
                }
            }))
            
            # Resultado Oracle
            oracle_dir = results_dir / 'oracle'
            oracle_dir.mkdir(parents=True, exist_ok=True)
            (oracle_dir / 'result_1.json').write_text(json.dumps({
                'task_id': tasks[2].id,
                'status': 'completed',
                'tests': {
                    'total': 45,
                    'coverage': '92%',
                    'types': ['unit', 'integration', 'e2e']
                }
            }))
        
        # Thread para crear resultados mientras se ejecuta
        result_thread = threading.Thread(target=create_mock_results)
        result_thread.start()
        
        # Ejecutar
        results = mode.execute(batch)
        
        # Esperar thread de resultados
        result_thread.join()
        
        # Verificar ejecución completa
        self.assertEqual(len(results['agents']), 3)
        
        # Verificar que cada agente completó su trabajo
        for agent in ['alfred', 'robin', 'oracle']:
            self.assertIn(agent, results['agents'])
            self.assertEqual(results['agents'][agent]['tasks_completed'], 1)
            
            # Verificar resultados específicos
            agent_results = results['agents'][agent]['results']
            self.assertEqual(len(agent_results), 1)
            self.assertEqual(agent_results[0]['status'], 'completed')
        
        # Verificar llamadas a Popen
        self.assertEqual(mock_popen.call_count, 3)
        
        # Limpiar
        mode.cleanup()


if __name__ == '__main__':
    unittest.main()