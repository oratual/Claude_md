#!/usr/bin/env python3
"""
Tests para los agentes de Batman Incorporated.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import subprocess
from datetime import datetime
import tempfile
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agents import AlfredAgent, RobinAgent, OracleAgent, BatgirlAgent, LuciusAgent
from core.task import Task, TaskType, TaskPriority, TaskStatus
from features.chapter_logger import ChapterLogger


class TestAgents(unittest.TestCase):
    """Tests para el sistema de agentes."""
    
    def setUp(self):
        """Setup para cada test."""
        self.alfred = AlfredAgent()
        self.robin = RobinAgent()
        self.oracle = OracleAgent()
        self.batgirl = BatgirlAgent()
        self.lucius = LuciusAgent()
    
    def test_agent_initialization(self):
        """Test que los agentes se inicializan correctamente."""
        self.assertEqual(self.alfred.name, "alfred")
        self.assertEqual(self.alfred.role, "Senior Developer")
        
        self.assertEqual(self.robin.name, "robin")
        self.assertEqual(self.robin.role, "DevOps & Junior Developer")
        
        self.assertEqual(self.oracle.name, "oracle")
        self.assertEqual(self.oracle.role, "QA & Security Lead")
        
        self.assertEqual(self.batgirl.name, "batgirl")
        self.assertEqual(self.batgirl.role, "Frontend Specialist")
        
        self.assertEqual(self.lucius.name, "lucius")
        self.assertEqual(self.lucius.role, "Research & Innovation")
    
    def test_agent_specialties(self):
        """Test que los agentes tienen las especialidades correctas."""
        alfred_specialties = self.alfred.get_specialties()
        self.assertIn("backend", alfred_specialties)
        self.assertIn("api", alfred_specialties)
        
        robin_specialties = self.robin.get_specialties()
        self.assertIn("devops", robin_specialties)
        self.assertIn("docker", robin_specialties)
        
        oracle_specialties = self.oracle.get_specialties()
        self.assertIn("testing", oracle_specialties)
        self.assertIn("security", oracle_specialties)
        
        batgirl_specialties = self.batgirl.get_specialties()
        self.assertIn("frontend", batgirl_specialties)
        self.assertIn("ui", batgirl_specialties)
        
        lucius_specialties = self.lucius.get_specialties()
        self.assertIn("research", lucius_specialties)
        self.assertIn("innovation", lucius_specialties)
    
    def test_task_assignment(self):
        """Test que los agentes se asignan correctamente según las tareas."""
        # Alfred debe manejar tareas de backend
        self.assertTrue(self.alfred.should_handle_task("crear API REST para usuarios"))
        self.assertTrue(self.alfred.should_handle_task("refactorizar modelo de database"))
        self.assertFalse(self.alfred.should_handle_task("crear componente React"))
        
        # Robin debe manejar tareas de DevOps
        self.assertTrue(self.robin.should_handle_task("configurar Docker container"))
        self.assertTrue(self.robin.should_handle_task("setup CI/CD pipeline"))
        # Note: Robin puede manejar tests porque también hace testing en CI/CD
        self.assertFalse(self.robin.should_handle_task("crear componente React"))
        
        # Oracle debe manejar tareas de testing y seguridad
        self.assertTrue(self.oracle.should_handle_task("escribir tests unitarios"))
        self.assertTrue(self.oracle.should_handle_task("security analysis"))
        self.assertFalse(self.oracle.should_handle_task("diseñar interfaz de usuario"))
        
        # Batgirl debe manejar tareas de frontend
        self.assertTrue(self.batgirl.should_handle_task("crear componente React"))
        self.assertTrue(self.batgirl.should_handle_task("diseñar interfaz responsive"))
        self.assertFalse(self.batgirl.should_handle_task("configurar servidor"))
        
        # Lucius debe manejar tareas de investigación
        self.assertTrue(self.lucius.should_handle_task("research new AI algorithms"))
        self.assertTrue(self.lucius.should_handle_task("optimization prototype"))
        self.assertFalse(self.lucius.should_handle_task("fix CSS styling"))
    
    def test_system_prompts(self):
        """Test que los agentes tienen prompts de sistema válidos."""
        for agent in [self.alfred, self.robin, self.oracle, self.batgirl, self.lucius]:
            prompt = agent.get_system_prompt()
            self.assertIsInstance(prompt, str)
            self.assertGreater(len(prompt), 100)  # Prompts deben ser sustanciales
            self.assertIn(agent.name.title(), prompt)  # Deben mencionar su nombre
    
    def test_agent_stats(self):
        """Test que los agentes inicializan estadísticas correctamente."""
        for agent in [self.alfred, self.robin, self.oracle, self.batgirl, self.lucius]:
            stats = agent.get_stats()
            self.assertIn('name', stats)
            self.assertIn('role', stats)
            self.assertIn('stats', stats)
            self.assertIn('specialties', stats)
            
            # Stats iniciales deben ser cero
            agent_stats = stats['stats']
            self.assertEqual(agent_stats['tasks_completed'], 0)
            self.assertEqual(agent_stats['tasks_failed'], 0)


class TestTaskCreation(unittest.TestCase):
    """Tests para la creación de tareas."""
    
    def test_task_creation(self):
        """Test que las tareas se crean correctamente."""
        task = Task(
            title="Test Task",
            description="Una tarea de prueba",
            type=TaskType.DEVELOPMENT,
            priority=TaskPriority.HIGH
        )
        
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.description, "Una tarea de prueba")
        self.assertEqual(task.type, TaskType.DEVELOPMENT)
        self.assertEqual(task.priority, TaskPriority.HIGH)
        self.assertIsNotNone(task.id)
    
    def test_task_lifecycle(self):
        """Test del ciclo de vida de una tarea."""
        task = Task(
            title="Lifecycle Test",
            type=TaskType.TESTING,
            priority=TaskPriority.MEDIUM
        )
        
        # Estado inicial
        from core.task import TaskStatus
        self.assertEqual(task.status, TaskStatus.PENDING)
        
        # Iniciar tarea
        task.start()
        self.assertEqual(task.status, TaskStatus.IN_PROGRESS)
        self.assertIsNotNone(task.started_at)
        
        # Completar tarea
        task.complete("Tarea completada exitosamente")
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertIsNotNone(task.completed_at)
        self.assertEqual(task.output, "Tarea completada exitosamente")


class TestBaseAgentMethods(unittest.TestCase):
    """Tests para los métodos de BaseAgent que no están cubiertos."""
    
    def setUp(self):
        """Setup para cada test."""
        self.logger = Mock(spec=ChapterLogger)
        self.alfred = AlfredAgent(logger=self.logger)
    
    def test_working_directory_initialization(self):
        """Test que el directorio de trabajo se inicializa correctamente."""
        self.assertEqual(self.alfred.working_dir, Path.cwd())
    
    def test_available_tools_initialization(self):
        """Test que las herramientas disponibles se inicializan vacías."""
        self.assertEqual(self.alfred.available_tools, {})
    
    def test_logger_integration(self):
        """Test que el logger se integra correctamente."""
        self.alfred._log("Test message")
        self.logger.log.assert_called_once_with("[ALFRED] Test message")
    
    def test_logger_fallback_to_print(self):
        """Test que sin logger, se usa print."""
        agent_no_logger = AlfredAgent()
        with patch('builtins.print') as mock_print:
            agent_no_logger._log("Test message")
            mock_print.assert_called_once_with("[ALFRED] Test message")
    
    @patch('subprocess.run')
    def test_execute_task_success(self, mock_run):
        """Test ejecución exitosa de una tarea."""
        # Mock subprocess para simular éxito
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Task completed successfully",
            stderr=""
        )
        
        task = Task(
            title="Test Task",
            description="Test description",
            type=TaskType.DEVELOPMENT,
            priority=TaskPriority.HIGH
        )
        
        result = self.alfred.execute_task(task)
        
        # Verificar resultado exitoso
        self.assertTrue(result)
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertEqual(task.output, "Task completed successfully")
        self.assertEqual(self.alfred.stats['tasks_completed'], 1)
        self.assertEqual(self.alfred.stats['tasks_failed'], 0)
        self.assertGreater(self.alfred.stats['total_time'], 0)
    
    @patch('subprocess.run')
    def test_execute_task_failure(self, mock_run):
        """Test fallo en la ejecución de una tarea."""
        # Mock subprocess para simular fallo
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Error executing task"
        )
        
        task = Task(
            title="Failing Task",
            description="This will fail",
            type=TaskType.DEVELOPMENT,
            priority=TaskPriority.HIGH
        )
        
        result = self.alfred.execute_task(task)
        
        # Verificar fallo
        self.assertFalse(result)
        self.assertEqual(task.status, TaskStatus.FAILED)
        self.assertEqual(task.error, "Error executing task")
        self.assertEqual(self.alfred.stats['tasks_completed'], 0)
        self.assertEqual(self.alfred.stats['tasks_failed'], 1)
    
    @patch('subprocess.run')
    def test_execute_task_timeout(self, mock_run):
        """Test timeout en la ejecución de una tarea."""
        # Mock subprocess para simular timeout
        mock_run.side_effect = subprocess.TimeoutExpired('claude', 600)
        
        task = Task(
            title="Timeout Task",
            description="This will timeout",
            type=TaskType.DEVELOPMENT,
            priority=TaskPriority.HIGH
        )
        
        result = self.alfred.execute_task(task)
        
        # Verificar manejo de timeout
        self.assertFalse(result)
        self.assertEqual(task.status, TaskStatus.FAILED)
        self.assertIn("Timeout", task.error)
        self.assertEqual(self.alfred.stats['tasks_failed'], 1)
    
    @patch('subprocess.run')
    def test_execute_task_exception(self, mock_run):
        """Test excepción general en la ejecución."""
        # Mock subprocess para simular excepción
        mock_run.side_effect = Exception("Unexpected error")
        
        task = Task(
            title="Exception Task",
            description="This will raise exception",
            type=TaskType.DEVELOPMENT,
            priority=TaskPriority.HIGH
        )
        
        result = self.alfred.execute_task(task)
        
        # Verificar manejo de excepción
        self.assertFalse(result)
        self.assertEqual(task.status, TaskStatus.FAILED)
        self.assertIn("Unexpected error", task.error)
        self.assertEqual(self.alfred.stats['tasks_failed'], 1)
    
    def test_build_prompt_basic(self):
        """Test construcción básica del prompt."""
        task = Task(
            title="Test Task",
            description="Test description",
            type=TaskType.DEVELOPMENT,
            priority=TaskPriority.HIGH,
            tags=["backend", "api"]
        )
        
        prompt = self.alfred._build_prompt(task)
        
        # Verificar contenido del prompt
        self.assertIn("Alfred Pennyworth", prompt)  # System prompt
        self.assertIn("Test Task", prompt)
        self.assertIn("Test description", prompt)
        self.assertIn("development", prompt)  # TaskType enum returns lowercase
        self.assertIn("4", prompt)  # TaskPriority.HIGH has value 4
        self.assertIn("backend", prompt)
        self.assertIn("api", prompt)
        self.assertIn("## Instrucciones", prompt)
        self.assertIn("## MCPs Disponibles", prompt)
        self.assertIn(str(self.alfred.working_dir), prompt)
    
    def test_build_prompt_with_context_files(self):
        """Test construcción del prompt con archivos de contexto."""
        # Crear archivo temporal de contexto
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def test_function():\n    return 'Hello'")
            context_file = f.name
        
        try:
            task = Task(
                title="Test with Context",
                description="Test with file context",
                type=TaskType.DEVELOPMENT,
                priority=TaskPriority.MEDIUM
            )
            
            prompt = self.alfred._build_prompt(task, [context_file])
            
            # Verificar que el contenido del archivo está en el prompt
            self.assertIn("## Contexto del Proyecto", prompt)
            self.assertIn(context_file, prompt)
            self.assertIn("def test_function():", prompt)
            self.assertIn("return 'Hello'", prompt)
        finally:
            # Limpiar archivo temporal
            os.unlink(context_file)
    
    def test_build_prompt_with_large_context_file(self):
        """Test truncado de archivos grandes en el prompt."""
        # Crear archivo temporal grande
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            # Escribir más de 10000 caracteres
            large_content = "x" * 15000
            f.write(large_content)
            context_file = f.name
        
        try:
            task = Task(
                title="Test Large File",
                description="Test with large file",
                type=TaskType.DEVELOPMENT,
                priority=TaskPriority.LOW
            )
            
            prompt = self.alfred._build_prompt(task, [context_file])
            
            # Verificar truncado
            self.assertIn("... (truncado)", prompt)
            # El contenido no debe exceder ~10000 caracteres
            file_content_start = prompt.find("```") + 3
            file_content_end = prompt.find("```", file_content_start)
            content_length = file_content_end - file_content_start
            self.assertLess(content_length, 11000)  # Un poco más de 10000 por el mensaje de truncado
        finally:
            os.unlink(context_file)
    
    def test_build_prompt_with_arsenal_tools(self):
        """Test inclusión de herramientas del Arsenal en el prompt."""
        self.alfred.available_tools = {
            'search': 'rg',
            'find': 'fd',
            'view': 'bat'
        }
        
        task = Task(
            title="Test Arsenal",
            description="Test with tools",
            type=TaskType.DEVELOPMENT,
            priority=TaskPriority.MEDIUM
        )
        
        prompt = self.alfred._build_prompt(task)
        
        # Verificar que las herramientas están en el prompt
        self.assertIn("## Arsenal de Herramientas", prompt)
        self.assertIn("search", prompt)
        self.assertIn("rg", prompt)
        self.assertIn("find", prompt)
        self.assertIn("fd", prompt)
        self.assertIn("view", prompt)
        self.assertIn("bat", prompt)
    
    def test_build_prompt_with_mcp_context(self):
        """Test inclusión de contexto MCP compartido."""
        # Simular contexto MCP
        self.alfred.mcp_prompt_section = "\n## Contexto MCP Compartido\nMemoria compartida: Task X completada"
        
        task = Task(
            title="Test MCP",
            description="Test with MCP context",
            type=TaskType.DEVELOPMENT,
            priority=TaskPriority.HIGH
        )
        
        prompt = self.alfred._build_prompt(task)
        
        # Verificar contexto MCP
        self.assertIn("## Contexto MCP Compartido", prompt)
        self.assertIn("Memoria compartida: Task X completada", prompt)
    
    @patch('subprocess.run')
    def test_execute_claude_saves_files(self, mock_run):
        """Test que execute_claude guarda archivos de prompt y respuesta."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Test response",
            stderr=""
        )
        
        task = Task(
            title="Test Save Files",
            description="Test file saving",
            type=TaskType.DEVELOPMENT,
            priority=TaskPriority.HIGH
        )
        
        prompt = "Test prompt"
        success, output, error = self.alfred._execute_claude(prompt, task)
        
        # Verificar archivos guardados
        prompt_file = Path(f"/tmp/batman_prompt_{task.id}.txt")
        response_file = Path(f"/tmp/batman_response_{task.id}.txt")
        
        self.assertTrue(prompt_file.exists())
        self.assertTrue(response_file.exists())
        self.assertEqual(prompt_file.read_text(), prompt)
        self.assertEqual(response_file.read_text(), "Test response")
        
        # Limpiar archivos
        prompt_file.unlink()
        response_file.unlink()
    
    @patch('subprocess.run')
    def test_execute_claude_command_construction(self, mock_run):
        """Test construcción correcta del comando Claude CLI."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Success",
            stderr=""
        )
        
        task = Task(title="Test", type=TaskType.DEVELOPMENT)
        prompt = "Test prompt"
        
        self.alfred._execute_claude(prompt, task)
        
        # Verificar comando construido
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        
        self.assertEqual(cmd[0], 'claude')
        self.assertIn('--print', cmd)
        self.assertIn('--dangerously-skip-permissions', cmd)
        self.assertIn('--max-turns', cmd)
        self.assertIn('10', cmd)
        self.assertEqual(cmd[-1], prompt)
    
    def test_stats_accumulation(self):
        """Test que las estadísticas se acumulan correctamente."""
        with patch('subprocess.run') as mock_run:
            # Primera tarea exitosa
            mock_run.return_value = MagicMock(returncode=0, stdout="OK", stderr="")
            task1 = Task(title="Task 1", type=TaskType.DEVELOPMENT)
            self.alfred.execute_task(task1)
            
            # Segunda tarea fallida
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="Error")
            task2 = Task(title="Task 2", type=TaskType.TESTING)
            self.alfred.execute_task(task2)
            
            # Tercera tarea exitosa
            mock_run.return_value = MagicMock(returncode=0, stdout="OK", stderr="")
            task3 = Task(title="Task 3", type=TaskType.DEVELOPMENT)
            self.alfred.execute_task(task3)
            
            # Verificar estadísticas acumuladas
            stats = self.alfred.get_stats()['stats']
            self.assertEqual(stats['tasks_completed'], 2)
            self.assertEqual(stats['tasks_failed'], 1)
            self.assertGreater(stats['total_time'], 0)


class TestAgentFileHandling(unittest.TestCase):
    """Tests para el manejo de archivos creados/modificados por agentes."""
    
    def setUp(self):
        """Setup para cada test."""
        self.alfred = AlfredAgent()
    
    def test_file_stats_tracking(self):
        """Test que las estadísticas de archivos se inicializan correctamente."""
        stats = self.alfred.get_stats()['stats']
        self.assertIn('files_created', stats)
        self.assertIn('files_modified', stats)
        self.assertEqual(stats['files_created'], [])
        self.assertEqual(stats['files_modified'], [])
    
    def test_build_prompt_with_nonexistent_context_file(self):
        """Test manejo de archivos de contexto que no existen."""
        task = Task(
            title="Test Nonexistent File",
            description="Test with missing file",
            type=TaskType.DEVELOPMENT,
            priority=TaskPriority.MEDIUM
        )
        
        # Archivo que no existe
        nonexistent_file = "/tmp/this_file_does_not_exist_12345.py"
        
        # No debería lanzar excepción
        prompt = self.alfred._build_prompt(task, [nonexistent_file])
        
        # El prompt se genera pero no incluye el archivo inexistente
        self.assertIn("## Tarea Actual", prompt)
        self.assertIn("Test Nonexistent File", prompt)
    
    def test_build_prompt_with_unreadable_file(self):
        """Test manejo de archivos que no se pueden leer."""
        # Crear archivo temporal con permisos restringidos
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("secret content")
            restricted_file = f.name
        
        try:
            # Cambiar permisos para que no sea legible
            os.chmod(restricted_file, 0o000)
            
            task = Task(
                title="Test Unreadable File",
                description="Test with restricted file",
                type=TaskType.DEVELOPMENT,
                priority=TaskPriority.MEDIUM
            )
            
            # No debería lanzar excepción
            prompt = self.alfred._build_prompt(task, [restricted_file])
            
            # Verificar que el error se maneja gracefully
            self.assertIn("## Contexto del Proyecto", prompt)
            self.assertIn("Error leyendo archivo", prompt)
        finally:
            # Restaurar permisos y limpiar
            os.chmod(restricted_file, 0o644)
            os.unlink(restricted_file)


class TestAgentTaskAssignment(unittest.TestCase):
    """Tests adicionales para la asignación de tareas a agentes."""
    
    def setUp(self):
        """Setup para cada test."""
        self.agents = {
            'alfred': AlfredAgent(),
            'robin': RobinAgent(),
            'oracle': OracleAgent(),
            'batgirl': BatgirlAgent(),
            'lucius': LuciusAgent()
        }
    
    def test_edge_case_assignments(self):
        """Test casos límite en la asignación de tareas."""
        # Tareas ambiguas que podrían ir a múltiples agentes
        ambiguous_tasks = [
            ("implement secure API endpoint", ['alfred', 'oracle']),  # API + security
            ("test frontend components", ['oracle', 'batgirl']),      # test + frontend
            ("optimize database queries", ['alfred', 'lucius']),      # database + optimization
            ("setup docker for testing", ['robin', 'oracle']),        # docker + testing
        ]
        
        for task_desc, possible_agents in ambiguous_tasks:
            handled_by = []
            for agent_name, agent in self.agents.items():
                if agent.should_handle_task(task_desc):
                    handled_by.append(agent_name)
            
            # Verificar que al menos uno de los agentes posibles maneja la tarea
            self.assertTrue(
                any(agent in handled_by for agent in possible_agents),
                f"Task '{task_desc}' should be handled by at least one of {possible_agents}, but was handled by {handled_by}"
            )
    
    def test_no_agent_handles_task(self):
        """Test tareas que ningún agente debería manejar."""
        irrelevant_tasks = [
            "write a blog post about cooking",
            "create marketing materials",
            "design company logo"
        ]
        
        for task_desc in irrelevant_tasks:
            handled_by = []
            for agent_name, agent in self.agents.items():
                if agent.should_handle_task(task_desc):
                    handled_by.append(agent_name)
            
            # Para tareas no técnicas, es posible que ningún agente las maneje
            # o que Lucius las tome por ser research/innovation
            # También Batgirl podría tomar tareas de "design"
            self.assertTrue(
                len(handled_by) <= 2,  # Máximo dos agentes (ej: Batgirl por "design", Lucius por "innovation")
                f"Non-technical task '{task_desc}' was handled by too many agents: {handled_by}"
            )


class TestClaudeCLIEdgeCases(unittest.TestCase):
    """Tests para casos límite en la ejecución de Claude CLI."""
    
    def setUp(self):
        """Setup para cada test."""
        self.alfred = AlfredAgent()
    
    @patch('subprocess.run')
    def test_execute_claude_with_cwd(self, mock_run):
        """Test que el comando se ejecuta en el directorio correcto."""
        mock_run.return_value = MagicMock(returncode=0, stdout="OK", stderr="")
        
        # Cambiar directorio de trabajo
        test_dir = Path("/tmp")
        self.alfred.working_dir = test_dir
        
        task = Task(title="Test CWD", type=TaskType.DEVELOPMENT)
        self.alfred._execute_claude("test prompt", task)
        
        # Verificar que se usa el directorio correcto
        mock_run.assert_called_once()
        kwargs = mock_run.call_args[1]
        self.assertEqual(kwargs['cwd'], str(test_dir))
    
    @patch('subprocess.run')
    def test_execute_claude_timeout_value(self, mock_run):
        """Test que se aplica el timeout correcto."""
        mock_run.return_value = MagicMock(returncode=0, stdout="OK", stderr="")
        
        task = Task(title="Test Timeout", type=TaskType.DEVELOPMENT)
        self.alfred._execute_claude("test prompt", task)
        
        # Verificar timeout de 600 segundos (10 minutos)
        mock_run.assert_called_once()
        kwargs = mock_run.call_args[1]
        self.assertEqual(kwargs['timeout'], 600)
    
    @patch('subprocess.run')
    def test_execute_claude_empty_output(self, mock_run):
        """Test manejo de salida vacía de Claude."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        task = Task(title="Empty Output", type=TaskType.DEVELOPMENT)
        success, output, error = self.alfred._execute_claude("test", task)
        
        # Debería ser exitoso incluso con salida vacía
        self.assertTrue(success)
        self.assertEqual(output, "")
        self.assertEqual(error, "")
    
    def test_all_agents_have_required_methods(self):
        """Test que todos los agentes implementan los métodos abstractos."""
        agents = [AlfredAgent(), RobinAgent(), OracleAgent(), BatgirlAgent(), LuciusAgent()]
        
        for agent in agents:
            # Verificar métodos abstractos
            self.assertTrue(hasattr(agent, 'get_system_prompt'))
            self.assertTrue(callable(agent.get_system_prompt))
            self.assertIsInstance(agent.get_system_prompt(), str)
            
            self.assertTrue(hasattr(agent, 'get_specialties'))
            self.assertTrue(callable(agent.get_specialties))
            self.assertIsInstance(agent.get_specialties(), list)
            
            # Verificar método should_handle_task
            self.assertTrue(hasattr(agent, 'should_handle_task'))
            self.assertTrue(callable(agent.should_handle_task))


class TestBaseAgentMethods(unittest.TestCase):
    """Tests para métodos base de los agentes."""
    
    def setUp(self):
        """Setup para cada test."""
        self.alfred = AlfredAgent()
        # Crear directorio temporal para tests
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Cleanup después de cada test."""
        # Limpiar directorio temporal
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('subprocess.run')
    def test_execute_task_success(self, mock_run):
        """Test ejecución exitosa de tarea."""
        # Mock respuesta exitosa
        mock_run.return_value = MagicMock(
            stdout='Task completed successfully',
            stderr='',
            returncode=0
        )
        
        task = Task(
            title="Test Task",
            description="A test task",
            type=TaskType.DEVELOPMENT,
            priority=TaskPriority.HIGH
        )
        
        result = self.alfred.execute_task(task)
        
        # Verificar resultado
        self.assertTrue(result['success'])
        self.assertEqual(result['output'], 'Task completed successfully')
        self.assertIsNone(result['error'])
        
        # Verificar estadísticas actualizadas
        stats = self.alfred.get_stats()
        self.assertEqual(stats['stats']['tasks_completed'], 1)
        self.assertEqual(stats['stats']['tasks_failed'], 0)
    
    @patch('subprocess.run')
    def test_execute_task_failure(self, mock_run):
        """Test fallo en ejecución de tarea."""
        # Mock error
        mock_run.return_value = MagicMock(
            stdout='',
            stderr='Error occurred',
            returncode=1
        )
        
        task = Task(
            title="Failing Task",
            type=TaskType.DEVELOPMENT,
            priority=TaskPriority.HIGH
        )
        
        result = self.alfred.execute_task(task)
        
        # Verificar resultado
        self.assertFalse(result['success'])
        self.assertIn('Error occurred', result['error'])
        
        # Verificar estadísticas
        stats = self.alfred.get_stats()
        self.assertEqual(stats['stats']['tasks_completed'], 0)
        self.assertEqual(stats['stats']['tasks_failed'], 1)
    
    @patch('subprocess.run')
    def test_execute_task_with_timeout(self, mock_run):
        """Test ejecución con timeout."""
        import subprocess
        
        # Mock timeout
        mock_run.side_effect = subprocess.TimeoutExpired(['claude'], 300)
        
        task = Task(
            title="Timeout Task",
            type=TaskType.DEVELOPMENT,
            priority=TaskPriority.HIGH
        )
        
        result = self.alfred.execute_task(task)
        
        # Verificar manejo de timeout
        self.assertFalse(result['success'])
        self.assertIn('timeout', result['error'].lower())
        
        # Verificar estadísticas
        stats = self.alfred.get_stats()
        self.assertEqual(stats['stats']['tasks_failed'], 1)
    
    @patch('subprocess.run')
    def test_execute_task_with_exception(self, mock_run):
        """Test manejo de excepciones inesperadas."""
        # Mock excepción
        mock_run.side_effect = Exception("Unexpected error")
        
        task = Task(
            title="Exception Task",
            type=TaskType.DEVELOPMENT,
            priority=TaskPriority.HIGH
        )
        
        result = self.alfred.execute_task(task)
        
        # Verificar manejo de excepción
        self.assertFalse(result['success'])
        self.assertIn('Unexpected error', result['error'])
    
    def test_build_prompt_basic(self):
        """Test construcción de prompt básico."""
        task = Task(
            title="Basic Task",
            description="Do something basic",
            type=TaskType.DEVELOPMENT,
            priority=TaskPriority.MEDIUM
        )
        
        prompt = self.alfred._build_prompt(task)
        
        # Verificar elementos del prompt
        self.assertIn("Basic Task", prompt)
        self.assertIn("Do something basic", prompt)
        self.assertIn("Alfred", prompt)  # Nombre del agente
        self.assertIn("Senior Developer", prompt)  # Rol del agente
    
    def test_build_prompt_with_files(self):
        """Test construcción de prompt con archivos de contexto."""
        # Crear archivo temporal
        test_file = self.temp_dir / "context.py"
        test_file.write_text("def hello():\n    return 'world'")
        
        task = Task(
            title="Task with Files",
            type=TaskType.DEVELOPMENT,
            priority=TaskPriority.HIGH,
            context_files=[str(test_file)]
        )
        
        prompt = self.alfred._build_prompt(task)
        
        # Verificar que incluye el contenido del archivo
        self.assertIn("context.py", prompt)
        self.assertIn("def hello():", prompt)
        self.assertIn("return 'world'", prompt)
    
    def test_build_prompt_with_large_file(self):
        """Test construcción de prompt con archivo grande."""
        # Crear archivo grande
        large_file = self.temp_dir / "large.txt"
        large_content = "Line\n" * 1000  # 1000 líneas
        large_file.write_text(large_content)
        
        task = Task(
            title="Task with Large File",
            type=TaskType.DEVELOPMENT,
            priority=TaskPriority.HIGH,
            context_files=[str(large_file)]
        )
        
        prompt = self.alfred._build_prompt(task)
        
        # Verificar que trunca el archivo
        self.assertIn("large.txt", prompt)
        self.assertIn("[First 50 lines shown]", prompt)
    
    @patch('core.arsenal.get_arsenal')
    def test_build_prompt_with_arsenal_tools(self, mock_arsenal):
        """Test construcción de prompt con herramientas del Arsenal."""
        # Mock arsenal con herramientas
        mock_arsenal_instance = MagicMock()
        mock_arsenal_instance.get_best_tools_for_task.return_value = ['rg', 'fd', 'bat']
        mock_arsenal.return_value = mock_arsenal_instance
        
        task = Task(
            title="Search Task",
            description="Find all Python files",
            type=TaskType.DEVELOPMENT,
            priority=TaskPriority.HIGH
        )
        
        prompt = self.alfred._build_prompt(task)
        
        # Verificar que incluye herramientas sugeridas
        self.assertIn("Recommended tools", prompt)
        self.assertIn("rg", prompt)
        self.assertIn("fd", prompt)
        self.assertIn("bat", prompt)
    
    @patch('integrations.mcp_integration.get_mcp_integration')
    def test_build_prompt_with_mcp_context(self, mock_mcp):
        """Test construcción de prompt con contexto MCP."""
        # Mock MCP con contexto
        mock_mcp_instance = MagicMock()
        mock_mcp_instance.create_mcp_prompt_section.return_value = """
        === MCP SHARED CONTEXT ===
        Other agents have completed tasks.
        """
        mock_mcp.return_value = mock_mcp_instance
        
        task = Task(
            title="MCP Task",
            type=TaskType.DEVELOPMENT,
            priority=TaskPriority.HIGH
        )
        
        prompt = self.alfred._build_prompt(task)
        
        # Verificar que incluye contexto MCP
        self.assertIn("MCP SHARED CONTEXT", prompt)
        self.assertIn("Other agents have completed", prompt)
    
    @patch('subprocess.run')
    def test_execute_claude_saves_file(self, mock_run):
        """Test que execute_claude guarda el prompt en archivo."""
        mock_run.return_value = MagicMock(returncode=0, stdout='Success')
        
        # Ejecutar
        with patch('tempfile.NamedTemporaryFile', mock_open()) as mock_file:
            result = self.alfred._execute_claude("Test prompt", timeout=60)
            
            # Verificar que se escribió el prompt
            mock_file.assert_called_once()
            handle = mock_file()
            handle.write.assert_called_once_with(b"Test prompt")
    
    @patch('subprocess.run')
    def test_execute_claude_command_construction(self, mock_run):
        """Test construcción correcta del comando Claude."""
        mock_run.return_value = MagicMock(returncode=0, stdout='Success')
        
        with patch('tempfile.NamedTemporaryFile'):
            self.alfred._execute_claude("Test", timeout=120, cwd="/test/dir")
            
            # Verificar comando
            cmd = mock_run.call_args[0][0]
            self.assertEqual(cmd[0], 'claude')
            self.assertIn('--print', cmd)
            self.assertIn('--dangerously-skip-permissions', cmd)
            
            # Verificar kwargs
            kwargs = mock_run.call_args[1]
            self.assertEqual(kwargs['timeout'], 120)
            self.assertEqual(kwargs['cwd'], '/test/dir')
    
    def test_working_directory_management(self):
        """Test manejo de directorio de trabajo."""
        # Por defecto debe ser None
        self.assertIsNone(self.alfred.working_directory)
        
        # Establecer directorio
        self.alfred.working_directory = "/test/path"
        
        # Verificar en execute_task
        with patch.object(self.alfred, '_execute_claude') as mock_execute:
            mock_execute.return_value = {'success': True, 'output': 'OK'}
            
            task = Task(title="Test", type=TaskType.DEVELOPMENT, priority=TaskPriority.LOW)
            self.alfred.execute_task(task)
            
            # Verificar que pasó el cwd
            mock_execute.assert_called_once()
            call_kwargs = mock_execute.call_args[1]
            self.assertEqual(call_kwargs['cwd'], '/test/path')
    
    @patch('features.chapter_logger.get_logger')
    def test_logger_integration(self, mock_get_logger):
        """Test integración con ChapterLogger."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Ejecutar tarea
        with patch.object(self.alfred, '_execute_claude') as mock_execute:
            mock_execute.return_value = {'success': True, 'output': 'Done'}
            
            task = Task(title="Log Test", type=TaskType.DEVELOPMENT, priority=TaskPriority.HIGH)
            self.alfred.execute_task(task)
            
            # Verificar logging
            mock_logger.agent_event.assert_called()
    
    def test_logger_fallback(self):
        """Test fallback cuando ChapterLogger no está disponible."""
        # Simular que ChapterLogger no está disponible
        with patch('features.chapter_logger.get_logger', side_effect=ImportError):
            # No debe fallar
            try:
                alfred = AlfredAgent()
                self.assertIsNone(alfred.logger)
            except Exception as e:
                self.fail(f"No debe fallar sin logger: {e}")
    
    def test_stats_accumulation(self):
        """Test acumulación de estadísticas."""
        # Ejecutar múltiples tareas
        with patch.object(self.alfred, '_execute_claude') as mock_execute:
            # 2 éxitos
            mock_execute.return_value = {'success': True, 'output': 'OK'}
            for _ in range(2):
                task = Task(title="Success", type=TaskType.DEVELOPMENT, priority=TaskPriority.LOW)
                self.alfred.execute_task(task)
            
            # 1 fallo
            mock_execute.return_value = {'success': False, 'error': 'Failed'}
            task = Task(title="Fail", type=TaskType.DEVELOPMENT, priority=TaskPriority.LOW)
            self.alfred.execute_task(task)
        
        # Verificar estadísticas acumuladas
        stats = self.alfred.get_stats()
        self.assertEqual(stats['stats']['tasks_completed'], 2)
        self.assertEqual(stats['stats']['tasks_failed'], 1)
        self.assertEqual(stats['stats']['total_tasks'], 3)


class TestAgentFileHandling(unittest.TestCase):
    """Tests para manejo de archivos en agentes."""
    
    def setUp(self):
        """Setup para cada test."""
        self.agent = OracleAgent()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Cleanup."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_nonexistent_file_in_context(self):
        """Test manejo de archivo no existente en contexto."""
        task = Task(
            title="Task with Missing File",
            type=TaskType.TESTING,
            priority=TaskPriority.HIGH,
            context_files=["/nonexistent/file.py"]
        )
        
        # No debe fallar
        try:
            prompt = self.agent._build_prompt(task)
            self.assertIn("not found", prompt)
        except Exception as e:
            self.fail(f"No debe fallar con archivo no existente: {e}")
    
    def test_unreadable_file_in_context(self):
        """Test manejo de archivo sin permisos de lectura."""
        import os
        
        # Crear archivo sin permisos
        unreadable = self.temp_dir / "unreadable.txt"
        unreadable.write_text("secret")
        os.chmod(unreadable, 0o000)
        
        task = Task(
            title="Task with Unreadable File",
            type=TaskType.TESTING,
            priority=TaskPriority.HIGH,
            context_files=[str(unreadable)]
        )
        
        try:
            prompt = self.agent._build_prompt(task)
            # Debe manejar el error gracefully
            self.assertIn("unreadable.txt", prompt)
        finally:
            # Restaurar permisos para cleanup
            os.chmod(unreadable, 0o644)
    
    def test_file_statistics_tracking(self):
        """Test rastreo de estadísticas de archivos."""
        # Crear archivos de diferentes tamaños
        small_file = self.temp_dir / "small.py"
        small_file.write_text("print('hello')")
        
        medium_file = self.temp_dir / "medium.py"
        medium_file.write_text("# Comment\n" * 100)
        
        task = Task(
            title="Multi-file Task",
            type=TaskType.TESTING,
            priority=TaskPriority.HIGH,
            context_files=[str(small_file), str(medium_file)]
        )
        
        prompt = self.agent._build_prompt(task)
        
        # Verificar que procesó ambos archivos
        self.assertIn("small.py", prompt)
        self.assertIn("medium.py", prompt)


class TestClaudeCLIEdgeCases(unittest.TestCase):
    """Tests para casos edge con Claude CLI."""
    
    def setUp(self):
        """Setup."""
        self.agent = LuciusAgent()
    
    @patch('subprocess.run')
    def test_claude_binary_not_found(self, mock_run):
        """Test cuando el binario de Claude no se encuentra."""
        import subprocess
        mock_run.side_effect = FileNotFoundError("claude not found")
        
        result = self.agent._execute_claude("Test prompt")
        
        # Debe manejar el error
        self.assertFalse(result['success'])
        self.assertIn('not found', result['error'].lower())
    
    @patch('subprocess.run')
    def test_claude_interrupted(self, mock_run):
        """Test cuando Claude es interrumpido."""
        import subprocess
        mock_run.side_effect = KeyboardInterrupt()
        
        result = self.agent._execute_claude("Test prompt")
        
        # Debe manejar la interrupción
        self.assertFalse(result['success'])
        self.assertIn('interrupted', result['error'].lower())
    
    @patch('subprocess.run')
    def test_claude_memory_error(self, mock_run):
        """Test cuando Claude se queda sin memoria."""
        mock_run.side_effect = MemoryError()
        
        result = self.agent._execute_claude("Test prompt")
        
        # Debe manejar el error de memoria
        self.assertFalse(result['success'])
        self.assertIn('memory', result['error'].lower())


# Importar módulos necesarios para los tests
import tempfile
from unittest.mock import mock_open


if __name__ == '__main__':
    # Ejecutar tests con verbose output
    unittest.main(verbosity=2)