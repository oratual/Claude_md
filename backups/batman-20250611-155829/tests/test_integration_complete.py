"""
Integration tests for the complete Batman Incorporated system.
Tests real agent execution, Arsenal, MCPs, Infinity Mode, and coordination.
"""

import unittest
import tempfile
import shutil
import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock, call
import subprocess

from src.core.batman import BatmanIncorporated
from src.core.config import Config
from src.core.task import Task, TaskType, TaskPriority
from src.core.arsenal import Arsenal
from src.agents import AlfredAgent, RobinAgent
from src.execution.infinity_mode import InfinityMode
from src.execution.coordinator import AgentCoordinator, AgentMessage
from src.integrations.github_integration import GitHubIntegration
from src.integrations.mcp_integration import MCPIntegration


class TestCompleteSystemIntegration(unittest.TestCase):
    """Tests completos del sistema integrado."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        # Crear directorio temporal
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = Path.cwd()
        Path(self.test_dir).mkdir(exist_ok=True)
        
        # Configuración de prueba
        self.config = Config({
            'system': {
                'name': 'Batman Test',
                'auto_mode': False
            },
            'agents': {
                'alfred': {'enabled': True},
                'robin': {'enabled': True},
                'oracle': {'enabled': True},
                'batgirl': {'enabled': True},
                'lucius': {'enabled': True}
            },
            'execution': {
                'default_mode': 'infinity',
                'use_real_agents': True,
                'infinity_mode': {
                    'auto_launch': False
                }
            },
            'arsenal': {
                'enabled': True,
                'auto_detect': True
            },
            'mcp': {
                'enabled': True,
                'servers': {
                    'memory': {'enabled': True},
                    'filesystem': {'enabled': True}
                }
            },
            'github': {
                'enabled': True
            },
            'paths': {
                'logs': self.test_dir
            }
        })
    
    def tearDown(self):
        """Limpieza después de cada test."""
        # Volver al directorio original
        import os
        os.chdir(self.original_cwd)
        
        # Limpiar directorio temporal
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_batman_initialization_with_all_features(self):
        """Test que Batman se inicializa con todas las características."""
        batman = BatmanIncorporated(self.config)
        
        # Verificar que todos los componentes estén inicializados
        self.assertIsNotNone(batman.logger)
        self.assertIsNotNone(batman.arsenal)
        self.assertIsNotNone(batman.mcp)
        self.assertEqual(len(batman.agents), 5)  # 5 agentes habilitados
        
        # Verificar que Arsenal detectó herramientas
        self.assertGreater(len(batman.arsenal.available_tools), 0)
        
        # Verificar agentes
        for agent_name in ['alfred', 'robin', 'oracle', 'batgirl', 'lucius']:
            self.assertIn(agent_name, batman.agents)
    
    @patch('subprocess.run')
    def test_real_agent_execution_with_arsenal(self, mock_run):
        """Test ejecución real de agente con herramientas Arsenal."""
        # Simular respuesta exitosa de Claude CLI
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Tarea completada exitosamente",
            stderr=""
        )
        
        batman = BatmanIncorporated(self.config)
        
        # Crear tarea de prueba
        task = Task(
            title="Refactorizar código",
            description="Usar sd para reemplazar patrones obsoletos",
            type=TaskType.DEVELOPMENT,
            assigned_to='alfred'
        )
        
        # Ejecutar con agente real
        batman._simulate_task_execution(task)
        
        # Verificar que se llamó a Claude CLI
        mock_run.assert_called()
        
        # Verificar que se pasaron las herramientas Arsenal
        call_args = mock_run.call_args[0][0]
        self.assertIn('claude', call_args)
        self.assertIn('--print', call_args)
        self.assertIn('--dangerously-skip-permissions', call_args)
        
        # Verificar estadísticas
        self.assertEqual(batman.session_stats['tasks_completed'], 1)
        self.assertIn('alfred', batman.session_stats['agents_used'])
    
    def test_mcp_context_sharing_between_agents(self):
        """Test compartir contexto entre agentes via MCP."""
        batman = BatmanIncorporated(self.config)
        
        # Simular que Alfred descubre algo importante
        alfred = batman.agents['alfred']
        discovery = {
            'type': 'architecture_pattern',
            'pattern': 'Repository Pattern',
            'files': ['src/repositories/user_repo.py'],
            'description': 'Implementar patrón Repository para acceso a datos'
        }
        
        # Compartir via MCP
        batman.mcp.share_agent_knowledge(
            'alfred',
            'pattern_discovery',
            discovery
        )
        
        # Verificar que Robin puede acceder al conocimiento
        robin_context = batman.mcp.create_agent_context('robin', None)
        
        self.assertIn('shared_knowledge', robin_context)
        self.assertIn('alfred', robin_context['shared_knowledge'])
        
        shared_knowledge = robin_context['shared_knowledge']['alfred']
        self.assertEqual(
            shared_knowledge['discoveries'][0]['pattern'],
            'Repository Pattern'
        )
    
    def test_infinity_mode_preparation(self):
        """Test preparación del modo Infinity."""
        mode = InfinityMode(self.config.get('execution.infinity_mode'), None)
        
        # Crear tareas de prueba
        tasks = [
            Task(
                title=f"Tarea {i}",
                type=TaskType.DEVELOPMENT,
                assigned_to=['alfred', 'robin', 'oracle'][i % 3]
            )
            for i in range(6)
        ]
        
        # Preparar modo infinity
        success = mode.prepare(tasks)
        self.assertTrue(success)
        
        # Verificar archivos de contexto creados
        self.assertTrue(mode.context_file.exists())
        self.assertTrue(mode.status_file.exists())
        
        # Verificar agrupación de tareas
        self.assertEqual(len(mode.agent_tasks), 3)  # 3 agentes con tareas
        self.assertEqual(len(mode.agent_tasks['alfred']), 2)
        self.assertEqual(len(mode.agent_tasks['robin']), 2)
        self.assertEqual(len(mode.agent_tasks['oracle']), 2)
    
    def test_agent_coordinator_file_locking(self):
        """Test sistema de locks para evitar conflictos."""
        shared_dir = Path(self.test_dir) / 'shared'
        coordinator = AgentCoordinator(shared_dir)
        
        # Registrar agentes
        coordinator.register_agent('alfred')
        coordinator.register_agent('robin')
        
        # Alfred toma lock de un archivo
        lock_success = coordinator.request_file_lock('alfred', 'src/main.py')
        self.assertTrue(lock_success)
        
        # Robin intenta tomar el mismo archivo
        lock_fail = coordinator.request_file_lock('robin', 'src/main.py')
        self.assertFalse(lock_fail)
        
        # Verificar que se envió notificación de conflicto
        robin_messages = coordinator.get_messages('robin')
        self.assertEqual(len(robin_messages), 1)
        self.assertEqual(robin_messages[0].message_type, 'file_conflict')
        
        # Alfred libera el lock
        coordinator.release_file_lock('alfred', 'src/main.py')
        
        # Ahora Robin puede tomarlo
        lock_success2 = coordinator.request_file_lock('robin', 'src/main.py')
        self.assertTrue(lock_success2)
    
    @patch('subprocess.run')
    def test_github_smart_pr_creation(self, mock_run):
        """Test creación inteligente de PRs."""
        # Simular git diff
        mock_run.side_effect = [
            # git diff --stat --cached
            MagicMock(
                returncode=0,
                stdout="src/main.py | 150 ++++++++++\n src/utils.py | 50 +++---\n 2 files changed, 175 insertions(+), 25 deletions(-)"
            ),
            # git diff --name-only --cached
            MagicMock(
                returncode=0,
                stdout="src/main.py\nsrc/utils.py"
            ),
            # git diff --cached
            MagicMock(
                returncode=0,
                stdout="+ feature: new authentication system\n+ fix: memory leak in utils"
            ),
            # git branch --show-current
            MagicMock(returncode=0, stdout="feature/auth"),
            # git push
            MagicMock(returncode=0),
            # gh pr create
            MagicMock(
                returncode=0,
                stdout='{"number": 42, "url": "https://github.com/test/repo/pull/42", "title": "feat: Update authentication"}'
            )
        ]
        
        github = GitHubIntegration()
        analysis_result = {'description': 'Implementar nuevo sistema de autenticación'}
        
        pr_info = github.create_smart_pr(analysis_result)
        
        self.assertIsNotNone(pr_info)
        self.assertEqual(pr_info['number'], 42)
        
        # Verificar que se detectaron los labels correctos
        pr_create_call = mock_run.call_args_list[-1]
        call_args = pr_create_call[0][0]
        
        self.assertIn('--label', call_args)
        # Debería incluir 'enhancement' por el 'feature' detectado
        label_index = call_args.index('--label') + 1
        labels = call_args[label_index].split(',')
        self.assertIn('enhancement', labels)
    
    def test_arsenal_tool_detection_for_tasks(self):
        """Test detección automática de herramientas para tareas."""
        arsenal = Arsenal()
        
        # Tarea de búsqueda
        search_task = Task(
            title="Buscar patrones de código obsoletos",
            description="Encontrar todos los usos de API deprecated",
            type=TaskType.DEVELOPMENT
        )
        
        best_tools = arsenal.get_best_tools_for_task(search_task)
        
        # Debería recomendar ripgrep para búsqueda
        self.assertIn('search', best_tools)
        self.assertTrue(
            'rg' in best_tools['search'] or 
            'ripgrep' in best_tools['search']
        )
        
        # Tarea de refactoring
        refactor_task = Task(
            title="Refactorizar nombres de variables",
            description="Cambiar camelCase a snake_case en todo el proyecto",
            type=TaskType.DEVELOPMENT
        )
        
        best_tools = arsenal.get_best_tools_for_task(refactor_task)
        
        # Debería recomendar sd para reemplazos
        self.assertIn('replace', best_tools)
        if arsenal._check_tool_available('sd'):
            self.assertIn('sd', best_tools['replace'])
    
    @patch('subprocess.Popen')
    def test_infinity_mode_auto_launch(self, mock_popen):
        """Test lanzamiento automático de instancias en Infinity Mode."""
        # Configurar auto launch
        config = self.config.get('execution.infinity_mode')
        config['auto_launch'] = True
        
        mode = InfinityMode(config, None)
        
        # Mock del proceso
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_process.poll.return_value = None  # Proceso sigue corriendo
        mock_popen.return_value = mock_process
        
        # Crear tareas
        tasks = [
            Task(title="Tarea 1", assigned_to='alfred'),
            Task(title="Tarea 2", assigned_to='robin')
        ]
        
        mode.prepare(tasks)
        
        # Generar y lanzar instancias
        instructions = mode._generate_instance_instructions()
        mode._auto_launch_instances(instructions)
        
        # Verificar que se lanzaron 2 procesos (alfred y robin)
        self.assertEqual(mock_popen.call_count, 2)
        
        # Verificar parámetros de lanzamiento
        for call in mock_popen.call_args_list:
            cmd = call[0][0]
            self.assertIn('claude', cmd)
            self.assertIn('--model', cmd)
            self.assertIn('opus', cmd)
            self.assertIn('--dangerously-skip-permissions', cmd)
    
    def test_complete_workflow_simulation(self):
        """Test simulación de flujo completo de trabajo."""
        batman = BatmanIncorporated(self.config)
        
        # Simular ejecución de tarea compleja
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Éxito",
                stderr=""
            )
            
            # Ejecutar tarea
            batman.execute_task(
                "Implementar sistema de autenticación con tests",
                mode="infinity"
            )
            
            # Verificar que se crearon tareas
            self.assertGreater(len(batman.completed_tasks), 0)
            
            # Verificar estadísticas
            stats = batman.session_stats
            self.assertGreater(stats['tasks_completed'], 0)
            self.assertGreater(len(stats['agents_used']), 0)
    
    def test_error_recovery_and_reporting(self):
        """Test recuperación de errores y reporte."""
        coordinator = AgentCoordinator(Path(self.test_dir) / 'coord')
        coordinator.register_agent('alfred')
        coordinator.register_agent('oracle')
        
        # Alfred reporta un error
        coordinator.report_error(
            'alfred',
            'import_error',
            'No se puede importar módulo inexistente'
        )
        
        # Oracle recibe la notificación
        oracle_messages = coordinator.get_messages('oracle')
        error_messages = [m for m in oracle_messages if m.message_type == 'error_report']
        
        self.assertEqual(len(error_messages), 1)
        self.assertEqual(error_messages[0].content['error_type'], 'import_error')
        self.assertIn('Verificar imports', error_messages[0].content['avoid_pattern'])


class TestAgentArsenalIntegration(unittest.TestCase):
    """Tests específicos de integración agente-arsenal."""
    
    def test_agent_uses_best_tools(self):
        """Test que los agentes usan las mejores herramientas disponibles."""
        alfred = AlfredAgent()
        arsenal = Arsenal()
        
        # Asignar herramientas al agente
        task = Task(
            title="Buscar y reemplazar código legacy",
            description="Encontrar código antiguo y modernizarlo"
        )
        
        best_tools = arsenal.get_best_tools_for_task(task)
        alfred.available_tools = best_tools
        
        # Construir prompt
        prompt = alfred._build_prompt(task)
        
        # Verificar que las herramientas están en el prompt
        self.assertIn("Arsenal de Herramientas", prompt)
        for tool_type, tool_cmd in best_tools.items():
            self.assertIn(tool_cmd, prompt)


class TestMCPCoordination(unittest.TestCase):
    """Tests de coordinación via MCP."""
    
    def test_task_completion_sharing(self):
        """Test compartir completación de tareas entre agentes."""
        mcp = MCPIntegration({})
        
        # Alfred completa una tarea
        mcp.share_task_completion(
            'alfred',
            'task-123',
            {
                'status': 'completed',
                'files_modified': ['src/auth.py'],
                'insights': 'Implementé autenticación JWT'
            }
        )
        
        # Robin consulta el estado
        shared_state = mcp.get_shared_state()
        
        self.assertIn('task_completions', shared_state)
        self.assertIn('task-123', shared_state['task_completions'])
        self.assertEqual(
            shared_state['task_completions']['task-123']['agent'],
            'alfred'
        )


if __name__ == '__main__':
    unittest.main()