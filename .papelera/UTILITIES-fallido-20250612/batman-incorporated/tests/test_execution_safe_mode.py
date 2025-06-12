"""
Tests para SafeMode - Ejecución con Git worktrees.
Verifica aislamiento, paralelización y merge de cambios.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
import tempfile

from src.execution.safe_mode import SafeMode
from src.core.task import Task
from src.features.chapter_logger import ChapterLogger


class TestSafeMode(unittest.TestCase):
    """Tests para el modo seguro con Git worktrees."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.config = {
            'worktree_base': '/tmp/test-batman-worktrees',
            'max_parallel': 3
        }
        self.logger = Mock(spec=ChapterLogger)
        self.mode = SafeMode(self.config, self.logger)
        
        # Mock de tareas
        self.tasks = [
            Mock(spec=Task, id="task1", title="Task 1", assigned_to="alfred"),
            Mock(spec=Task, id="task2", title="Task 2", assigned_to="robin"),
            Mock(spec=Task, id="task3", title="Task 3", assigned_to="alfred"),
        ]
    
    def test_initialization(self):
        """Verifica la inicialización correcta."""
        self.assertEqual(self.mode.name, "Safe Mode")
        self.assertEqual(self.mode.config, self.config)
        self.assertEqual(self.mode.worktree_base, Path('/tmp/test-batman-worktrees'))
        self.assertEqual(self.mode.worktrees, {})
        self.assertEqual(self.mode.branches, {})
    
    def test_initialization_default_worktree_base(self):
        """Verifica el valor por defecto de worktree_base."""
        mode = SafeMode({}, self.logger)
        self.assertEqual(mode.worktree_base, Path('/tmp/batman-worktrees'))
    
    @patch.object(SafeMode, '_run_command')
    @patch('pathlib.Path.mkdir')
    def test_prepare_not_git_repo(self, mock_mkdir, mock_run):
        """Verifica manejo cuando no estamos en un repo git."""
        # No es un repo git
        mock_run.return_value = (False, "", "fatal: not a git repository")
        
        result = self.mode.prepare(self.tasks)
        
        self.assertFalse(result)
        self.logger.log.assert_any_call(
            "[SAFE MODE] ❌ No estamos en un repositorio Git"
        )
    
    @patch.object(SafeMode, '_run_command')
    @patch('pathlib.Path.mkdir')
    def test_prepare_cannot_get_branch(self, mock_mkdir, mock_run):
        """Verifica manejo cuando no se puede obtener el branch actual."""
        # Es un repo git pero no puede obtener branch
        mock_run.side_effect = [
            (True, ".git", ""),  # git rev-parse
            (False, "", "error")  # git branch --show-current
        ]
        
        result = self.mode.prepare(self.tasks)
        
        self.assertFalse(result)
        self.logger.log.assert_any_call(
            "[SAFE MODE] ❌ No se pudo obtener el branch actual"
        )
    
    @patch.object(SafeMode, '_create_worktree_for_agent')
    @patch.object(SafeMode, '_run_command')
    @patch('pathlib.Path.mkdir')
    def test_prepare_success(self, mock_mkdir, mock_run, mock_create_worktree):
        """Verifica preparación exitosa con múltiples agentes."""
        # Configurar mocks
        mock_run.side_effect = [
            (True, ".git", ""),      # git rev-parse
            (True, "main\n", "")     # git branch --show-current
        ]
        mock_create_worktree.return_value = True
        
        result = self.mode.prepare(self.tasks)
        
        # Verificar
        self.assertTrue(result)
        self.assertEqual(self.mode.main_branch, "main")
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        
        # Debe crear worktrees para alfred y robin (únicos)
        self.assertEqual(mock_create_worktree.call_count, 2)
        mock_create_worktree.assert_any_call("alfred")
        mock_create_worktree.assert_any_call("robin")
    
    @patch.object(SafeMode, '_create_worktree_for_agent')
    @patch.object(SafeMode, '_run_command')
    @patch('pathlib.Path.mkdir')
    def test_prepare_worktree_creation_failure(self, mock_mkdir, mock_run, mock_create_worktree):
        """Verifica manejo de fallo al crear worktree."""
        # Configurar mocks
        mock_run.side_effect = [
            (True, ".git", ""),      # git rev-parse
            (True, "main\n", "")     # git branch --show-current
        ]
        mock_create_worktree.side_effect = [True, False]  # Falla en el segundo
        
        result = self.mode.prepare(self.tasks)
        
        self.assertFalse(result)
        self.logger.log.assert_any_call(
            "[SAFE MODE] ❌ Error creando worktree para robin"
        )
    
    @patch('tempfile.mktemp')
    @patch.object(SafeMode, '_run_command')
    def test_create_worktree_for_agent_success(self, mock_run, mock_mktemp):
        """Verifica creación exitosa de worktree para un agente."""
        # Configurar mocks
        mock_mktemp.return_value = "/tmp/temp12345678"
        mock_run.return_value = (True, "", "")
        
        result = self.mode._create_worktree_for_agent("alfred")
        
        # Verificar
        self.assertTrue(result)
        self.assertIn("alfred", self.mode.worktrees)
        self.assertIn("alfred", self.mode.branches)
        
        # Verificar comando git
        expected_branch = "batman/alfred-12345678"
        expected_path = self.mode.worktree_base / "alfred-12345678"
        mock_run.assert_called_once_with(
            f"git worktree add -b {expected_branch} {expected_path} HEAD"
        )
    
    @patch('tempfile.mktemp')
    @patch.object(SafeMode, '_run_command')
    def test_create_worktree_for_agent_failure(self, mock_run, mock_mktemp):
        """Verifica manejo de fallo al crear worktree."""
        # Configurar mocks
        mock_mktemp.return_value = "/tmp/temp12345678"
        mock_run.return_value = (False, "", "fatal: worktree error")
        
        result = self.mode._create_worktree_for_agent("alfred")
        
        # Verificar
        self.assertFalse(result)
        self.assertNotIn("alfred", self.mode.worktrees)
        self.assertNotIn("alfred", self.mode.branches)
    
    def test_execute_no_worktree(self):
        """Verifica ejecución cuando no hay worktree para el agente."""
        task = Mock(spec=Task, assigned_to="oracle")
        agent = Mock()
        
        result = self.mode.execute(task, agent)
        
        self.assertFalse(result)
        self.logger.log.assert_any_call(
            "[SAFE MODE] ❌ No hay worktree para oracle"
        )
    
    @patch.object(SafeMode, '_commit_changes')
    def test_execute_success(self, mock_commit):
        """Verifica ejecución exitosa de tarea."""
        # Preparar
        task = Mock(spec=Task, assigned_to="alfred")
        agent = Mock()
        agent.working_dir = Path("/original/dir")
        agent.execute_task.return_value = True
        
        worktree_path = Path("/tmp/test-worktree")
        self.mode.worktrees["alfred"] = worktree_path
        
        # Ejecutar
        result = self.mode.execute(task, agent)
        
        # Verificar
        self.assertTrue(result)
        agent.execute_task.assert_called_once_with(task)
        mock_commit.assert_called_once_with("alfred", task)
        # Verificar que se restauró el directorio original
        self.assertEqual(agent.working_dir, Path("/original/dir"))
    
    @patch.object(SafeMode, '_commit_changes')
    def test_execute_failure(self, mock_commit):
        """Verifica manejo de fallo en ejecución."""
        # Preparar
        task = Mock(spec=Task, assigned_to="alfred")
        agent = Mock()
        agent.working_dir = Path("/original/dir")
        agent.execute_task.return_value = False
        
        worktree_path = Path("/tmp/test-worktree")
        self.mode.worktrees["alfred"] = worktree_path
        
        # Ejecutar
        result = self.mode.execute(task, agent)
        
        # Verificar
        self.assertFalse(result)
        agent.execute_task.assert_called_once_with(task)
        mock_commit.assert_not_called()  # No debe commitear si falla
        # Verificar que se restauró el directorio original
        self.assertEqual(agent.working_dir, Path("/original/dir"))
    
    @patch.object(SafeMode, '_commit_changes')
    def test_execute_exception_handling(self, mock_commit):
        """Verifica que se restaura el directorio incluso con excepciones."""
        # Preparar
        task = Mock(spec=Task, assigned_to="alfred")
        agent = Mock()
        agent.working_dir = Path("/original/dir")
        agent.execute_task.side_effect = Exception("Test error")
        
        worktree_path = Path("/tmp/test-worktree")
        self.mode.worktrees["alfred"] = worktree_path
        
        # Ejecutar y verificar excepción
        with self.assertRaises(Exception):
            self.mode.execute(task, agent)
        
        # Verificar que se restauró el directorio original
        self.assertEqual(agent.working_dir, Path("/original/dir"))
    
    @patch.object(SafeMode, '_run_command')
    def test_commit_changes_with_changes(self, mock_run):
        """Verifica commit cuando hay cambios."""
        # Configurar mocks
        mock_run.side_effect = [
            (True, "", ""),  # git add
            (True, "M file.py\n", ""),  # git status
            (True, "", "")  # git commit
        ]
        
        task = Mock(spec=Task, id="task1", title="Fix bug")
        worktree_path = Path("/tmp/worktree")
        self.mode.worktrees["alfred"] = worktree_path
        
        # Ejecutar
        self.mode._commit_changes("alfred", task)
        
        # Verificar llamadas
        expected_calls = [
            call("git add -A", cwd=worktree_path),
            call("git status --porcelain", cwd=worktree_path),
            call('git commit -m "alfred: Fix bug\n\nTask ID: task1"', cwd=worktree_path)
        ]
        mock_run.assert_has_calls(expected_calls)
    
    @patch.object(SafeMode, '_run_command')
    def test_commit_changes_no_changes(self, mock_run):
        """Verifica que no hace commit si no hay cambios."""
        # Configurar mocks
        mock_run.side_effect = [
            (True, "", ""),  # git add
            (True, "", ""),  # git status (sin cambios)
        ]
        
        task = Mock(spec=Task, id="task1", title="Fix bug")
        worktree_path = Path("/tmp/worktree")
        self.mode.worktrees["alfred"] = worktree_path
        
        # Ejecutar
        self.mode._commit_changes("alfred", task)
        
        # Verificar que no se hizo commit
        self.assertEqual(mock_run.call_count, 2)  # Solo add y status
    
    @patch('pathlib.Path.exists')
    @patch.object(SafeMode, '_run_command')
    def test_cleanup_success(self, mock_run, mock_exists):
        """Verifica cleanup exitoso con merge automático."""
        # Preparar estado
        self.mode.main_branch = "main"
        self.mode.branches = {"alfred": "batman/alfred-123", "robin": "batman/robin-456"}
        self.mode.worktrees = {
            "alfred": Path("/tmp/alfred-123"),
            "robin": Path("/tmp/robin-456")
        }
        
        # Configurar mocks
        mock_exists.return_value = True
        mock_run.return_value = (True, "", "")  # Todos los comandos exitosos
        
        # Ejecutar
        result = self.mode.cleanup()
        
        # Verificar
        self.assertTrue(result)
        
        # Verificar llamadas esperadas
        expected_calls = [
            call("git checkout main"),
            call("git merge --no-ff batman/alfred-123"),
            call("git merge --no-ff batman/robin-456"),
            call("git worktree remove --force /tmp/alfred-123"),
            call("git branch -d batman/alfred-123"),
            call("git worktree remove --force /tmp/robin-456"),
            call("git branch -d batman/robin-456")
        ]
        
        for expected_call in expected_calls:
            self.assertIn(expected_call, mock_run.call_args_list)
    
    @patch('pathlib.Path.exists')
    @patch.object(SafeMode, '_run_command')
    def test_cleanup_with_merge_conflict(self, mock_run, mock_exists):
        """Verifica manejo de conflictos en merge."""
        # Preparar estado
        self.mode.main_branch = "main"
        self.mode.branches = {"alfred": "batman/alfred-123"}
        self.mode.worktrees = {"alfred": Path("/tmp/alfred-123")}
        
        # Configurar mocks
        mock_exists.return_value = True
        
        # Simular conflicto en merge
        def side_effect(cmd, cwd=None):
            if "merge" in cmd:
                return (False, "", "CONFLICT")
            return (True, "", "")
        
        mock_run.side_effect = side_effect
        
        # Ejecutar
        result = self.mode.cleanup()
        
        # Verificar
        self.assertTrue(result)  # Cleanup continúa a pesar del conflicto
        
        # No debe eliminar worktree si hay conflicto
        worktree_remove_calls = [
            call for call in mock_run.call_args_list 
            if "worktree remove" in str(call)
        ]
        self.assertEqual(len(worktree_remove_calls), 0)
    
    def test_can_parallelize(self):
        """Verifica que SafeMode soporta paralelización."""
        self.assertTrue(self.mode.can_parallelize())
    
    def test_max_parallel_tasks(self):
        """Verifica el límite de tareas paralelas."""
        self.assertEqual(self.mode.max_parallel_tasks(), 3)
        
        # Probar valor por defecto
        mode = SafeMode({}, self.logger)
        self.assertEqual(mode.max_parallel_tasks(), 5)
    
    def test_edge_cases(self):
        """Prueba casos edge y valores límite."""
        # Tareas sin asignación
        tasks_no_assignment = [
            Mock(spec=Task, assigned_to=None),
            Mock(spec=Task, assigned_to=""),
        ]
        
        # Execute sin asignación usa "batman" por defecto
        task = Mock(spec=Task, assigned_to=None)
        agent = Mock()
        result = self.mode.execute(task, agent)
        self.assertFalse(result)  # No hay worktree para "batman"
        
        # Preparar con tareas vacías
        with patch.object(self.mode, '_run_command') as mock_run:
            mock_run.side_effect = [
                (True, ".git", ""),
                (True, "main\n", "")
            ]
            with patch('pathlib.Path.mkdir'):
                result = self.mode.prepare([])
                self.assertTrue(result)  # Debe funcionar con lista vacía


class TestSafeModeIntegration(unittest.TestCase):
    """Tests de integración para SafeMode."""
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.mkdir')
    @patch.object(SafeMode, '_run_command')
    def test_full_workflow(self, mock_run, mock_mkdir, mock_exists):
        """Verifica flujo completo: prepare -> execute -> cleanup."""
        # Configurar
        config = {'worktree_base': '/tmp/test-worktrees'}
        mode = SafeMode(config)
        
        tasks = [
            Mock(spec=Task, id="t1", title="Task 1", assigned_to="alfred"),
            Mock(spec=Task, id="t2", title="Task 2", assigned_to="robin"),
        ]
        
        agents = {
            "alfred": Mock(execute_task=Mock(return_value=True)),
            "robin": Mock(execute_task=Mock(return_value=True))
        }
        
        # Mock de comandos git
        mock_exists.return_value = True
        git_responses = {
            "git rev-parse": (True, ".git", ""),
            "git branch --show-current": (True, "main\n", ""),
            "git worktree add": (True, "", ""),
            "git add": (True, "", ""),
            "git status": (True, "M file.py", ""),
            "git commit": (True, "", ""),
            "git checkout": (True, "", ""),
            "git merge": (True, "", ""),
            "git worktree remove": (True, "", ""),
            "git branch -d": (True, "", "")
        }
        
        def run_command_side_effect(cmd, cwd=None):
            for key, response in git_responses.items():
                if key in cmd:
                    return response
            return (True, "", "")
        
        mock_run.side_effect = run_command_side_effect
        
        # Ejecutar flujo completo
        # 1. Preparar
        self.assertTrue(mode.prepare(tasks))
        self.assertEqual(len(mode.worktrees), 2)
        
        # 2. Ejecutar tareas
        for task in tasks:
            agent = agents[task.assigned_to]
            self.assertTrue(mode.execute(task, agent))
        
        # 3. Limpiar
        self.assertTrue(mode.cleanup())


if __name__ == "__main__":
    unittest.main()