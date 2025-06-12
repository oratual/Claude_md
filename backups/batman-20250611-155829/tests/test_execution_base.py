"""
Tests para la clase base ExecutionMode.
Verifica la interfaz abstracta y métodos comunes.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import subprocess

from src.execution.base import ExecutionMode
from src.core.task import Task
from src.features.chapter_logger import ChapterLogger


class ConcreteExecutionMode(ExecutionMode):
    """Implementación concreta para testing."""
    
    def prepare(self, tasks):
        return True
    
    def execute(self, task, agent):
        return True
    
    def cleanup(self):
        return True


class TestExecutionModeBase(unittest.TestCase):
    """Tests para la clase base ExecutionMode."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.config = {
            "test_key": "test_value",
            "parallel": False
        }
        self.logger = Mock(spec=ChapterLogger)
        self.mode = ConcreteExecutionMode("test", self.config, self.logger)
    
    def test_initialization(self):
        """Verifica la inicialización correcta."""
        # Sin logger
        mode = ConcreteExecutionMode("test", self.config)
        self.assertEqual(mode.name, "test")
        self.assertEqual(mode.config, self.config)
        self.assertIsNone(mode.logger)
        self.assertEqual(mode.working_dir, Path.cwd())
        
        # Con logger
        mode = ConcreteExecutionMode("test", self.config, self.logger)
        self.assertEqual(mode.logger, self.logger)
    
    def test_abstract_methods_required(self):
        """Verifica que las clases hijas deben implementar métodos abstractos."""
        # Clase incompleta
        class IncompleteMode(ExecutionMode):
            pass
        
        # No se puede instanciar sin implementar métodos abstractos
        with self.assertRaises(TypeError):
            IncompleteMode("incomplete", {})
    
    def test_can_parallelize_default(self):
        """Verifica el comportamiento por defecto de can_parallelize."""
        self.assertFalse(self.mode.can_parallelize())
    
    def test_max_parallel_tasks_default(self):
        """Verifica el valor por defecto de max_parallel_tasks."""
        self.assertEqual(self.mode.max_parallel_tasks(), 1)
    
    def test_log_with_logger(self):
        """Verifica el logging cuando hay logger disponible."""
        self.mode._log("Test message")
        self.logger.log.assert_called_once_with("[TEST] Test message")
    
    @patch('builtins.print')
    def test_log_without_logger(self, mock_print):
        """Verifica el logging cuando no hay logger."""
        mode = ConcreteExecutionMode("test", self.config)
        mode._log("Test message")
        mock_print.assert_called_once_with("[TEST] Test message")
    
    @patch('subprocess.run')
    def test_run_command_success(self, mock_run):
        """Verifica ejecución exitosa de comandos."""
        # Configurar mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        # Ejecutar
        success, stdout, stderr = self.mode._run_command("echo test")
        
        # Verificar
        self.assertTrue(success)
        self.assertEqual(stdout, "output")
        self.assertEqual(stderr, "")
        mock_run.assert_called_once_with(
            "echo test",
            shell=True,
            cwd=str(self.mode.working_dir),
            capture_output=True,
            text=True,
            timeout=300
        )
    
    @patch('subprocess.run')
    def test_run_command_failure(self, mock_run):
        """Verifica manejo de fallo en comandos."""
        # Configurar mock
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "error"
        mock_run.return_value = mock_result
        
        # Ejecutar
        success, stdout, stderr = self.mode._run_command("false")
        
        # Verificar
        self.assertFalse(success)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "error")
    
    @patch('subprocess.run')
    def test_run_command_with_cwd(self, mock_run):
        """Verifica ejecución de comando con directorio específico."""
        # Configurar mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        # Ejecutar con cwd específico
        test_dir = Path("/tmp/test")
        success, stdout, stderr = self.mode._run_command("ls", cwd=test_dir)
        
        # Verificar
        self.assertTrue(success)
        mock_run.assert_called_once_with(
            "ls",
            shell=True,
            cwd=str(test_dir),
            capture_output=True,
            text=True,
            timeout=300
        )
    
    @patch('subprocess.run')
    def test_run_command_timeout(self, mock_run):
        """Verifica manejo de timeout en comandos."""
        # Configurar mock para lanzar timeout
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 300)
        
        # Ejecutar
        success, stdout, stderr = self.mode._run_command("long_command")
        
        # Verificar
        self.assertFalse(success)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "Command timed out")
    
    @patch('subprocess.run')
    def test_run_command_exception(self, mock_run):
        """Verifica manejo de excepciones en comandos."""
        # Configurar mock para lanzar excepción
        mock_run.side_effect = Exception("Test exception")
        
        # Ejecutar
        success, stdout, stderr = self.mode._run_command("bad_command")
        
        # Verificar
        self.assertFalse(success)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "Test exception")
    
    def test_inheritance_pattern(self):
        """Verifica que la herencia funciona correctamente."""
        # Crear una subclase con implementación personalizada
        class CustomMode(ExecutionMode):
            def prepare(self, tasks):
                self._log(f"Preparing {len(tasks)} tasks")
                return len(tasks) > 0
            
            def execute(self, task, agent):
                self._log(f"Executing task: {task.description}")
                return True
            
            def cleanup(self):
                self._log("Cleaning up")
                return True
            
            def can_parallelize(self):
                return True
            
            def max_parallel_tasks(self):
                return 4
        
        # Crear instancia y verificar
        mode = CustomMode("custom", {"parallel": True}, self.logger)
        
        # Verificar métodos base
        self.assertEqual(mode.name, "custom")
        self.assertEqual(mode.config["parallel"], True)
        
        # Verificar métodos personalizados
        self.assertTrue(mode.can_parallelize())
        self.assertEqual(mode.max_parallel_tasks(), 4)
        
        # Verificar prepare
        tasks = [Mock(spec=Task), Mock(spec=Task)]
        self.assertTrue(mode.prepare(tasks))
        self.logger.log.assert_called_with("[CUSTOM] Preparing 2 tasks")
        
        # Verificar execute
        task = Mock(spec=Task)
        task.description = "Test task"
        self.assertTrue(mode.execute(task, Mock()))
        
        # Verificar cleanup
        self.assertTrue(mode.cleanup())
    
    def test_edge_cases(self):
        """Prueba casos edge y valores límite."""
        # Config vacío
        mode = ConcreteExecutionMode("empty", {})
        self.assertEqual(mode.config, {})
        
        # Nombre con caracteres especiales
        mode = ConcreteExecutionMode("test-mode_123", self.config)
        mode._log("Test")
        self.logger.log.assert_called_with("[TEST-MODE_123] Test")
        
        # Comando vacío
        success, stdout, stderr = mode._run_command("")
        # Comando vacío puede tener comportamiento variable según el shell
        # Verificamos que no lance excepción
        self.assertIsInstance(success, bool)
        self.assertIsInstance(stdout, str)
        self.assertIsInstance(stderr, str)


class TestExecutionModeIntegration(unittest.TestCase):
    """Tests de integración para ExecutionMode."""
    
    def test_full_execution_cycle(self):
        """Verifica un ciclo completo de ejecución."""
        # Crear modo con comportamiento específico
        class TestMode(ExecutionMode):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.prepared = False
                self.executed_tasks = []
                self.cleaned = False
            
            def prepare(self, tasks):
                self.prepared = True
                return True
            
            def execute(self, task, agent):
                self.executed_tasks.append(task)
                return True
            
            def cleanup(self):
                self.cleaned = True
                return True
        
        # Crear instancia y ejecutar ciclo
        mode = TestMode("test", {})
        tasks = [Mock(spec=Task) for _ in range(3)]
        
        # Preparar
        self.assertTrue(mode.prepare(tasks))
        self.assertTrue(mode.prepared)
        
        # Ejecutar tareas
        for task in tasks:
            self.assertTrue(mode.execute(task, Mock()))
        self.assertEqual(len(mode.executed_tasks), 3)
        
        # Limpiar
        self.assertTrue(mode.cleanup())
        self.assertTrue(mode.cleaned)


if __name__ == "__main__":
    unittest.main()