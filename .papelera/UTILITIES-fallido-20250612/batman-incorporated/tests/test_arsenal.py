#!/usr/bin/env python3
"""
Tests para el Arsenal - Sistema de herramientas de Batman Incorporated.
"""

import unittest
from unittest.mock import patch, MagicMock, call
import sys
from pathlib import Path
import subprocess

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.arsenal import Arsenal, get_arsenal


class TestArsenal(unittest.TestCase):
    """Tests para el sistema Arsenal."""
    
    def setUp(self):
        """Setup para cada test."""
        # Clear any cached arsenal instance
        Arsenal._instance = None
        self.arsenal = Arsenal()
    
    def tearDown(self):
        """Cleanup después de cada test."""
        Arsenal._instance = None
    
    @patch('shutil.which')
    def test_tool_detection_all_available(self, mock_which):
        """Test detección cuando todas las herramientas están disponibles."""
        # Mock todas las herramientas como disponibles
        def which_side_effect(tool):
            available_tools = ['rg', 'ag', 'grep', 'fd', 'fdfind', 'find', 
                             'bat', 'batcat', 'cat', 'exa', 'eza', 'ls',
                             'sd', 'sed', 'jq', 'gh']
            return f'/usr/bin/{tool}' if tool in available_tools else None
        
        mock_which.side_effect = which_side_effect
        
        # Reinicializar arsenal para detectar herramientas
        self.arsenal._detect_available_tools()
        
        # Verificar que las mejores herramientas fueron detectadas
        self.assertEqual(self.arsenal.available_tools['search'], 'rg')
        self.assertEqual(self.arsenal.available_tools['find'], 'fd')
        self.assertEqual(self.arsenal.available_tools['view'], 'bat')
        self.assertEqual(self.arsenal.available_tools['ls'], 'exa')
        self.assertEqual(self.arsenal.available_tools['sed'], 'sd')
        self.assertEqual(self.arsenal.available_tools['json'], 'jq')
        self.assertEqual(self.arsenal.available_tools['git'], 'gh')
    
    @patch('shutil.which')
    def test_tool_detection_only_fallbacks(self, mock_which):
        """Test detección cuando solo están disponibles las herramientas de respaldo."""
        # Solo herramientas básicas disponibles
        def which_side_effect(tool):
            basic_tools = ['grep', 'find', 'cat', 'ls', 'sed']
            return f'/usr/bin/{tool}' if tool in basic_tools else None
        
        mock_which.side_effect = which_side_effect
        
        # Reinicializar arsenal
        self.arsenal._detect_available_tools()
        
        # Verificar que no están las herramientas avanzadas, pero sí las básicas
        self.assertEqual(self.arsenal.available_tools.get('search'), 'grep')
        self.assertEqual(self.arsenal.available_tools.get('find'), 'find')
        self.assertEqual(self.arsenal.available_tools.get('view'), 'cat')
        self.assertEqual(self.arsenal.available_tools.get('ls'), 'ls')
        self.assertEqual(self.arsenal.available_tools.get('sed'), 'sed')
    
    @patch('subprocess.run')
    @patch('shutil.which')
    def test_search_text_with_ripgrep(self, mock_which, mock_run):
        """Test búsqueda de texto usando ripgrep."""
        mock_which.return_value = '/usr/bin/rg'
        self.arsenal.available_tools = {'search': 'rg'}
        
        # Mock resultado de ripgrep
        mock_run.return_value = MagicMock(
            stdout='src/main.py:10:pattern found\nsrc/test.py:20:pattern here',
            stderr='',
            returncode=0
        )
        
        result = self.arsenal.search_text('pattern', path='src/')
        
        # Verificar comando ejecutado
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd[0], 'rg')
        self.assertIn('pattern', cmd)
        self.assertIn('src/', cmd)
        
        # Verificar resultado
        self.assertEqual(result.returncode, 0)
        self.assertIn('src/main.py', result.stdout)
    
    @patch('subprocess.run')
    @patch('shutil.which')
    def test_search_text_fallback_to_grep(self, mock_which, mock_run):
        """Test búsqueda de texto con fallback a grep."""
        def which_side_effect(tool):
            return '/usr/bin/grep' if tool == 'grep' else None
        
        mock_which.side_effect = which_side_effect
        self.arsenal.available_tools = {'search': 'grep'}
        
        mock_run.return_value = MagicMock(
            stdout='src/main.py:pattern found',
            stderr='',
            returncode=0
        )
        
        result = self.arsenal.search_text('pattern')
        
        # Verificar que usó grep
        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd[0], 'grep')
        self.assertIn('-r', cmd)
        self.assertIn('pattern', cmd)
    
    @patch('subprocess.run')
    @patch('shutil.which')
    def test_find_files_with_fd(self, mock_which, mock_run):
        """Test búsqueda de archivos con fd."""
        mock_which.return_value = '/usr/bin/fd'
        self.arsenal.available_tools = {'find': 'fd'}
        
        mock_run.return_value = MagicMock(
            stdout='src/main.py\nsrc/test.py\n',
            stderr='',
            returncode=0
        )
        
        result = self.arsenal.find_files('*.py', path='src/')
        
        # Verificar comando
        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd[0], 'fd')
        self.assertIn('*.py', cmd)
        self.assertIn('src/', cmd)
        
        # Verificar resultado
        self.assertEqual(result.returncode, 0)
        self.assertIn('src/main.py', result.stdout)
    
    @patch('subprocess.run')
    @patch('shutil.which')
    def test_view_file_with_bat(self, mock_which, mock_run):
        """Test visualización de archivo con bat."""
        mock_which.return_value = '/usr/bin/bat'
        self.arsenal.available_tools = {'view': 'bat'}
        
        mock_run.return_value = MagicMock(
            stdout='colored output of file.py',
            stderr='',
            returncode=0
        )
        
        result = self.arsenal.view_file('test.py')
        
        # Verificar comando
        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd[0], 'bat')
        self.assertIn('test.py', cmd)
        
        self.assertEqual(result.returncode, 0)
    
    @patch('subprocess.run')
    @patch('shutil.which')
    def test_replace_text_with_sd(self, mock_which, mock_run):
        """Test reemplazo de texto con sd."""
        mock_which.return_value = '/usr/bin/sd'
        self.arsenal.available_tools = {'sed': 'sd'}
        
        mock_run.return_value = MagicMock(returncode=0)
        
        result = self.arsenal.replace_text('old', 'new', files=['test.txt'])
        
        # Verificar comando
        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd[0], 'sd')
        self.assertIn('old', cmd)
        self.assertIn('new', cmd)
        self.assertIn('test.txt', cmd)
        
        self.assertTrue(result)
    
    @patch('subprocess.run')
    @patch('shutil.which')
    def test_process_json_with_jq(self, mock_which, mock_run):
        """Test procesamiento JSON con jq."""
        mock_which.return_value = '/usr/bin/jq'
        self.arsenal.available_tools = {'json': 'jq'}
        
        mock_run.return_value = MagicMock(
            stdout='{"key": "value"}',
            stderr='',
            returncode=0
        )
        
        # process_json espera input data, no file path
        result = self.arsenal.process_json('{"key": "value"}', '.key')
        
        # Verificar comando
        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd[0], 'jq')
        self.assertIn('.key', cmd)
        
        self.assertEqual(result, '{"key": "value"}')
    
    def test_get_best_tools_for_task(self):
        """Test selección de herramientas por tarea."""
        from core.task import Task, TaskType, TaskPriority
        
        # Simular herramientas disponibles
        self.arsenal.available_tools = {
            'search': 'rg',
            'find': 'fd', 
            'view': 'bat',
            'git': 'gh',
            'json': 'jq'
        }
        
        # Test tareas de búsqueda
        task = Task(title="buscar error", description="buscar error en logs", 
                   type=TaskType.DEVELOPMENT, priority=TaskPriority.HIGH)
        tools = self.arsenal.get_best_tools_for_task(task)
        self.assertIn('rg', tools.values())
        
        # Test tareas de archivos
        task = Task(title="encontrar archivos", description="encontrar archivos Python",
                   type=TaskType.DEVELOPMENT, priority=TaskPriority.HIGH)
        tools = self.arsenal.get_best_tools_for_task(task)
        self.assertIn('fd', tools.values())
        
        # Test tareas de GitHub
        task = Task(title="crear PR", description="crear pull request",
                   type=TaskType.DEVELOPMENT, priority=TaskPriority.HIGH)
        tools = self.arsenal.get_best_tools_for_task(task)
        self.assertIn('gh', tools.values())
        
        # Test tareas de JSON
        task = Task(title="analizar JSON", description="analizar archivo JSON",
                   type=TaskType.DEVELOPMENT, priority=TaskPriority.HIGH)
        tools = self.arsenal.get_best_tools_for_task(task)
        self.assertIn('jq', tools.values())
    
    def test_suggest_installations(self):
        """Test sugerencias de instalación."""
        # Simular pocas herramientas disponibles
        self.arsenal.available_tools = {
            'search': 'grep',
            'find': 'find',
            'view': 'cat'
        }
        
        suggestions = self.arsenal.suggest_installations()
        
        # Debe sugerir instalar herramientas avanzadas
        # Buscar en las sugerencias concatenadas
        all_suggestions = ' '.join(suggestions)
        self.assertIn('bat', all_suggestions)
        self.assertIn('jq', all_suggestions)
        self.assertTrue(any('cargo install' in s for s in suggestions))
    
    def test_singleton_pattern(self):
        """Test que Arsenal sigue el patrón singleton."""
        arsenal1 = get_arsenal()
        arsenal2 = get_arsenal()
        
        # Deben ser la misma instancia
        self.assertIs(arsenal1, arsenal2)
    
    def test_get_status_report(self):
        """Test generación de reporte de estado."""
        self.arsenal.available_tools = {'search': 'rg', 'find': 'fd', 'view': 'bat'}
        
        report = self.arsenal.get_status_report()
        
        # Verificar estructura del reporte
        self.assertIn('available', report)
        self.assertIn('missing', report)
        
        # Verificar contenido
        self.assertEqual(len(report['available']), 3)
        self.assertIn('search', report['available'])
    
    @patch('subprocess.run')
    def test_error_handling(self, mock_run):
        """Test manejo de errores en operaciones."""
        # Simular error en comando
        mock_run.side_effect = subprocess.CalledProcessError(1, ['rg', 'pattern'])
        
        self.arsenal.available_tools = {'search': 'rg'}
        
        # search_text lanza excepción, debemos manejarla
        with self.assertRaises(subprocess.CalledProcessError):
            self.arsenal.search_text('pattern')
    
    def test_get_tool_with_empty_arsenal(self):
        """Test obtener herramienta cuando no hay ninguna disponible."""
        self.arsenal.available_tools = {}
        
        # Debe devolver None cuando no hay herramientas
        tool = self.arsenal.get_tool('search')
        self.assertIsNone(tool)
    
    @patch('subprocess.run')
    @patch('shutil.which')
    def test_github_cli_operations(self, mock_which, mock_run):
        """Test operaciones con GitHub CLI."""
        mock_which.return_value = '/usr/bin/gh'
        self.arsenal.available_tools = {'git': 'gh'}
        
        mock_run.return_value = MagicMock(
            stdout='PR #123 created',
            stderr='',
            returncode=0
        )
        
        # Test crear PR
        result = self.arsenal.github_cli(['pr', 'create', '--title', 'Test PR'])
        
        # Verificar comando
        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd[0], 'gh')
        self.assertEqual(cmd[1:], ['pr', 'create', '--title', 'Test PR'])
        
        self.assertEqual(result.returncode, 0)
        self.assertIn('PR #123', result.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)