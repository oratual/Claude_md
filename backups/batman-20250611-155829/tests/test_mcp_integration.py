#!/usr/bin/env python3
"""
Tests para el sistema de integración MCP de Batman Incorporated.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
import json
from datetime import datetime, timedelta
import tempfile
import os
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from integrations.mcp_integration import MCPIntegration, MCPFileSystemIntegration, get_mcp_integration
from core.task import Task, TaskType, TaskPriority, TaskStatus


class TestMCPIntegration(unittest.TestCase):
    """Tests para el sistema de integración MCP."""
    
    def setUp(self):
        """Setup para cada test."""
        # Reset singleton
        import integrations.mcp_integration
        integrations.mcp_integration._mcp_instance = None
        
        # Create temp directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.test_state_file = Path(self.temp_dir) / ".batman" / "mcp_memory" / "shared_state.json"
        
        # Create minimal config
        self.config = {
            'mcp': {
                'enabled': True,
                'memory_path': self.temp_dir
            }
        }
        
        # Patch home directory to use temp dir
        self.home_patcher = patch('pathlib.Path.home')
        self.mock_home = self.home_patcher.start()
        self.mock_home.return_value = Path(self.temp_dir)
        
        self.mcp = MCPIntegration(self.config)
    
    def tearDown(self):
        """Cleanup después de cada test."""
        self.home_patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        # Reset singleton
        import integrations.mcp_integration
        integrations.mcp_integration._mcp_instance = None
    
    def test_singleton_pattern(self):
        """Test que MCP usa patrón singleton correctamente."""
        config = {'mcp': {'enabled': True}}
        mcp1 = get_mcp_integration(config)
        mcp2 = get_mcp_integration()
        self.assertIs(mcp1, mcp2)
    
    def test_share_task_completion(self):
        """Test compartir completación de tarea."""
        result = {
            "success": True,
            "files_modified": ["file1.py", "file2.py"],
            "message": "Task completed successfully"
        }
        
        with patch.object(self.mcp, '_save_shared_state') as mock_save:
            self.mcp.share_task_completion("alfred", "task-001", result)
            
            # Verificar que se guardó el estado
            mock_save.assert_called_once()
            
            # Verificar el contenido
            self.assertEqual(len(self.mcp.shared_state["tasks_completed"]), 1)
            completion = self.mcp.shared_state["tasks_completed"][0]
            self.assertEqual(completion["agent"], "alfred")
            self.assertEqual(completion["task_id"], "task-001")
            self.assertEqual(completion["result"], result)
            
            # Verificar que se actualizaron los archivos modificados
            self.assertIn("file1.py", self.mcp.shared_state["files_modified"])
            self.assertIn("file2.py", self.mcp.shared_state["files_modified"])
    
    def test_share_agent_knowledge(self):
        """Test compartir conocimiento entre agentes."""
        with patch.object(self.mcp, '_save_shared_state') as mock_save:
            self.mcp.share_agent_knowledge("robin", "database", {"type": "postgres", "version": "14"})
            
            mock_save.assert_called_once()
            self.assertIn("robin", self.mcp.shared_state["agent_knowledge"])
            self.assertIn("database", self.mcp.shared_state["agent_knowledge"]["robin"])
            knowledge = self.mcp.shared_state["agent_knowledge"]["robin"]["database"]
            self.assertEqual(knowledge["data"]["type"], "postgres")
            self.assertEqual(knowledge["data"]["version"], "14")
    
    def test_get_agent_knowledge(self):
        """Test obtener conocimiento compartido."""
        # Preparar datos
        self.mcp.shared_state["agent_knowledge"] = {
            "alfred": {
                "api_design": {
                    "data": {"pattern": "REST", "version": "v2"},
                    "timestamp": datetime.now().isoformat()
                }
            }
        }
        
        # Test obtener todo el conocimiento de un agente
        knowledge = self.mcp.get_agent_knowledge("alfred")
        self.assertIn("api_design", knowledge)
        
        # Test obtener conocimiento específico
        api_knowledge = self.mcp.get_agent_knowledge("alfred", "api_design")
        self.assertEqual(api_knowledge["data"]["pattern"], "REST")
        
        # Test agente no existente
        self.assertEqual(self.mcp.get_agent_knowledge("batman"), {})
    
    def test_share_error(self):
        """Test compartir errores para aprendizaje."""
        with patch.object(self.mcp, '_save_shared_state') as mock_save:
            self.mcp.share_error("oracle", "TypeError", "undefined is not a function in component.js")
            
            mock_save.assert_called_once()
            self.assertEqual(len(self.mcp.shared_state["errors_found"]), 1)
            error = self.mcp.shared_state["errors_found"][0]
            self.assertEqual(error["agent"], "oracle")
            self.assertEqual(error["type"], "TypeError")
            self.assertEqual(error["details"], "undefined is not a function in component.js")
    
    def test_share_decision(self):
        """Test compartir decisiones importantes."""
        with patch.object(self.mcp, '_save_shared_state') as mock_save:
            self.mcp.share_decision("lucius", "Use TypeScript", "Better type safety")
            
            mock_save.assert_called_once()
            self.assertEqual(len(self.mcp.shared_state["decisions_made"]), 1)
            decision = self.mcp.shared_state["decisions_made"][0]
            self.assertEqual(decision["agent"], "lucius")
            self.assertEqual(decision["decision"], "Use TypeScript")
            self.assertEqual(decision["reasoning"], "Better type safety")
    
    def test_get_files_modified(self):
        """Test obtener archivos modificados."""
        # Añadir archivos
        self.mcp.shared_state["files_modified"] = {"file1.py", "file2.js", "file3.tsx"}
        
        files = self.mcp.get_files_modified()
        self.assertEqual(len(files), 3)
        self.assertIn("file1.py", files)
        self.assertIn("file2.js", files)
        self.assertIn("file3.tsx", files)
    
    def test_get_recent_errors(self):
        """Test obtener errores recientes."""
        # Añadir varios errores
        for i in range(15):
            self.mcp.shared_state["errors_found"].append({
                "agent": f"agent{i}",
                "type": f"Error{i}",
                "details": f"Details {i}",
                "timestamp": datetime.now().isoformat()
            })
        
        # Test límite por defecto (10)
        errors = self.mcp.get_recent_errors()
        self.assertEqual(len(errors), 10)
        self.assertEqual(errors[0]["type"], "Error5")  # Debe ser desde el índice 5
        self.assertEqual(errors[-1]["type"], "Error14")  # Hasta el índice 14
        
        # Test límite personalizado
        errors = self.mcp.get_recent_errors(limit=5)
        self.assertEqual(len(errors), 5)
        self.assertEqual(errors[0]["type"], "Error10")
        self.assertEqual(errors[-1]["type"], "Error14")
    
    def test_integration_with_task_object(self):
        """Test integración con objetos Task del sistema."""
        # Crear una tarea real
        from core.task import Task, TaskType, TaskPriority
        
        task = Task(
            id="task-test",
            title="Test Task",
            description="This is a test task",
            type=TaskType.TESTING,
            priority=TaskPriority.HIGH
        )
        
        result = {
            "success": True,
            "files_modified": ["test_file.py"],
            "tests_passed": 10
        }
        
        with patch.object(self.mcp, '_save_shared_state') as mock_save:
            self.mcp.share_task_completion("oracle", task.id, result)
            
            # Verificar que se guardó correctamente
            self.assertEqual(len(self.mcp.shared_state["tasks_completed"]), 1)
            completion = self.mcp.shared_state["tasks_completed"][0]
            self.assertEqual(completion["task_id"], "task-test")
            self.assertEqual(completion["result"]["tests_passed"], 10)
    
    def test_knowledge_sharing_between_agents(self):
        """Test compartir conocimiento complejo entre agentes."""
        # Alfred descubre la arquitectura
        alfred_knowledge = {
            "api_structure": {
                "endpoints": ["/users", "/posts", "/comments"],
                "auth": "JWT",
                "database": "PostgreSQL"
            }
        }
        
        self.mcp.share_agent_knowledge("alfred", "architecture", alfred_knowledge)
        
        # Robin necesita acceder a ese conocimiento
        knowledge = self.mcp.get_agent_knowledge("alfred", "architecture")
        self.assertEqual(knowledge["data"]["api_structure"]["auth"], "JWT")
        
        # Oracle añade conocimiento de testing
        oracle_knowledge = {
            "test_coverage": "85%",
            "failing_tests": [],
            "test_framework": "pytest"
        }
        
        self.mcp.share_agent_knowledge("oracle", "testing", oracle_knowledge)
        
        # Verificar que ambos conocimientos están disponibles
        all_knowledge = self.mcp.get_agent_knowledge()
        self.assertIn("alfred", all_knowledge)
        self.assertIn("oracle", all_knowledge)
    
    def test_concurrent_access_simulation(self):
        """Test simular acceso concurrente de múltiples agentes."""
        # Simular múltiples agentes trabajando al mismo tiempo
        agents = ["alfred", "robin", "oracle", "batgirl", "lucius"]
        
        with patch.object(self.mcp, '_save_shared_state') as mock_save:
            for i, agent in enumerate(agents):
                # Cada agente completa una tarea
                result = {
                    "success": True,
                    "files_modified": [f"{agent}_file_{i}.py"]
                }
                self.mcp.share_task_completion(agent, f"task-{i:03d}", result)
                
                # Cada agente comparte un error
                self.mcp.share_error(agent, f"Error{i}", f"Details from {agent}")
            
            # Verificar que se guardó el estado múltiples veces
            self.assertEqual(mock_save.call_count, 10)  # 5 tareas + 5 errores
            
            # Verificar que todos los datos están presentes
            self.assertEqual(len(self.mcp.shared_state["tasks_completed"]), 5)
            self.assertEqual(len(self.mcp.shared_state["errors_found"]), 5)
            self.assertEqual(len(self.mcp.shared_state["files_modified"]), 5)
    
    @patch('subprocess.run')
    def test_mcp_filesystem_integration(self, mock_run):
        """Test integración con MCP filesystem."""
        fs_integration = MCPFileSystemIntegration()
        
        # Test siempre devuelve True por ahora
        self.assertTrue(fs_integration.mcp_available)
        
        # Test sugerencia de operación
        suggestion = fs_integration.suggest_file_operation("read", "/path/to/file.py")
        self.assertIn("MCP filesystem", suggestion)
        self.assertIn("leer", suggestion)
        self.assertIn("/path/to/file.py", suggestion)
        
        # Test operación desconocida
        suggestion = fs_integration.suggest_file_operation("unknown", "/path/to/file.py")
        self.assertIn("MCP", suggestion)
        self.assertIn("unknown", suggestion)
    
    def test_load_save_state(self):
        """Test guardar y cargar estado desde disco."""
        # Añadir datos y guardar
        self.mcp.shared_state["tasks_completed"].append({
            "agent": "test",
            "task_id": "test-001",
            "timestamp": datetime.now().isoformat()
        })
        self.mcp.shared_state["files_modified"].add("test.py")
        
        self.mcp._save_shared_state()
        
        # Verificar que se guardó
        state_file = self.mcp.mcp_memory_path / "shared_state.json"
        self.assertTrue(state_file.exists())
        
        # Crear nueva instancia y verificar que carga el estado
        mcp2 = MCPIntegration(self.config)
        
        self.assertEqual(len(mcp2.shared_state["tasks_completed"]), 1)
        self.assertEqual(mcp2.shared_state["tasks_completed"][0]["task_id"], "test-001")
        self.assertIn("test.py", mcp2.shared_state["files_modified"])
    
    def test_error_handling_in_save(self):
        """Test manejo de errores al guardar estado."""
        # Hacer que el directorio sea de solo lectura
        self.mcp.mcp_memory_path.chmod(0o444)
        
        # No debe lanzar excepción, solo imprimir error
        try:
            self.mcp._save_shared_state()
        except Exception:
            self.fail("_save_shared_state should not raise exceptions")
        finally:
            # Restaurar permisos
            self.mcp.mcp_memory_path.chmod(0o755)
    
    def test_error_handling_in_load(self):
        """Test manejo de errores al cargar estado corrupto."""
        # Crear archivo con JSON inválido
        state_file = self.mcp.mcp_memory_path / "shared_state.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(state_file, 'w') as f:
            f.write("{ invalid json }")
        
        # No debe lanzar excepción al crear instancia
        try:
            mcp = MCPIntegration(self.config)
            # Debe tener estado por defecto
            self.assertIsInstance(mcp.shared_state["tasks_completed"], list)
            self.assertIsInstance(mcp.shared_state["files_modified"], set)
        except Exception:
            self.fail("MCPIntegration should handle corrupt state files gracefully")


if __name__ == "__main__":
    unittest.main()