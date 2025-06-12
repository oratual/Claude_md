"""
Tests for real agent execution with Claude CLI.
These tests verify the actual execution flow without running Claude.
"""

import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, ANY
import subprocess

from src.agents import AlfredAgent, RobinAgent, OracleAgent
from src.core.task import Task, TaskType, TaskPriority
from src.core.arsenal import Arsenal
from src.integrations.mcp_integration import MCPIntegration


class TestRealAgentExecution(unittest.TestCase):
    """Tests para ejecución real de agentes."""
    
    def setUp(self):
        """Setup para cada test."""
        self.temp_dir = tempfile.mkdtemp()
        self.arsenal = Arsenal()
        self.mcp = MCPIntegration({})
    
    @patch('subprocess.run')
    def test_alfred_executes_architecture_task(self, mock_run):
        """Test Alfred ejecutando tarea de arquitectura."""
        # Simular respuesta exitosa
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="""
            Analizando arquitectura del proyecto...
            ✅ Estructura de directorios creada
            ✅ Interfaces definidas
            ✅ Patrón Repository implementado
            
            Archivos creados:
            - src/domain/entities/user.py
            - src/infrastructure/repositories/user_repository.py
            - src/application/services/user_service.py
            """,
            stderr=""
        )
        
        alfred = AlfredAgent()
        
        # Asignar herramientas del Arsenal
        task = Task(
            title="Diseñar arquitectura del sistema",
            description="Implementar arquitectura hexagonal con DDD",
            type=TaskType.DEVELOPMENT,
            priority=TaskPriority.HIGH
        )
        
        alfred.available_tools = self.arsenal.get_best_tools_for_task(task)
        
        # Ejecutar tarea
        success = alfred.execute_task(task, context_files=['README.md'])
        
        self.assertTrue(success)
        self.assertEqual(alfred.stats['tasks_completed'], 1)
        
        # Verificar que se llamó a Claude con los parámetros correctos
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        
        self.assertEqual(call_args[0], 'claude')
        self.assertIn('--print', call_args)
        self.assertIn('--dangerously-skip-permissions', call_args)
        self.assertIn('--max-turns', call_args)
        
        # Verificar que el prompt incluye la personalidad de Alfred
        prompt_arg = call_args[-1]
        self.assertIn("mayordomo perfecto", prompt_arg)
        self.assertIn("arquitectura impecable", prompt_arg)
    
    @patch('subprocess.run')
    def test_robin_devops_automation(self, mock_run):
        """Test Robin automatizando DevOps."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="""
            Setting up CI/CD pipeline...
            ✅ GitHub Actions workflow created
            ✅ Docker configuration added
            ✅ Deployment scripts ready
            
            Files modified:
            - .github/workflows/ci.yml
            - Dockerfile
            - scripts/deploy.sh
            """,
            stderr=""
        )
        
        robin = RobinAgent()
        
        task = Task(
            title="Configurar CI/CD",
            description="Setup GitHub Actions con tests y deployment automático",
            type=TaskType.INFRASTRUCTURE,
            priority=TaskPriority.HIGH
        )
        
        # Herramientas especiales para DevOps
        robin.available_tools = {
            'container': 'docker',
            'ci': 'gh',
            'automation': 'make'
        }
        
        success = robin.execute_task(task)
        
        self.assertTrue(success)
        
        # Verificar prompt de Robin
        prompt = mock_run.call_args[0][0][-1]
        self.assertIn("Entusiasta del DevOps", prompt)
        self.assertIn("automatización", prompt)
    
    @patch('subprocess.run')
    def test_oracle_testing_with_mcp(self, mock_run):
        """Test Oracle escribiendo tests con contexto MCP."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="""
            Analizando cobertura de tests...
            ✅ Tests unitarios creados
            ✅ Tests de integración añadidos
            ✅ Cobertura: 85%
            
            Tests creados:
            - tests/unit/test_user_service.py
            - tests/integration/test_api.py
            """,
            stderr=""
        )
        
        oracle = OracleAgent()
        
        # Simular contexto MCP compartido
        mcp_context = {
            'shared_knowledge': {
                'alfred': {
                    'discoveries': [{
                        'type': 'api_endpoints',
                        'endpoints': ['/users', '/auth/login'],
                        'timestamp': '2024-01-10T10:00:00'
                    }]
                }
            }
        }
        
        oracle.mcp_context = mcp_context
        oracle.mcp_prompt_section = """
        ## Contexto Compartido (MCP)
        Alfred descubrió los siguientes endpoints:
        - /users
        - /auth/login
        """
        
        task = Task(
            title="Escribir tests completos",
            description="Crear tests para los nuevos endpoints",
            type=TaskType.TESTING
        )
        
        success = oracle.execute_task(task)
        
        self.assertTrue(success)
        
        # Verificar que el prompt incluye contexto MCP
        prompt = mock_run.call_args[0][0][-1]
        self.assertIn("Contexto Compartido (MCP)", prompt)
        self.assertIn("/users", prompt)
    
    @patch('subprocess.run')
    def test_agent_timeout_handling(self, mock_run):
        """Test manejo de timeout en ejecución."""
        # Simular timeout
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd=['claude'],
            timeout=600
        )
        
        agent = AlfredAgent()
        task = Task(
            title="Tarea muy compleja",
            description="Algo que toma demasiado tiempo"
        )
        
        success = agent.execute_task(task)
        
        self.assertFalse(success)
        self.assertEqual(agent.stats['tasks_failed'], 1)
        self.assertEqual(task.status.value, 'failed')
        self.assertIn("Timeout", task.result)
    
    @patch('subprocess.run')
    def test_agent_error_handling(self, mock_run):
        """Test manejo de errores en ejecución."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="Partial output",
            stderr="Error: No se pudo completar la tarea"
        )
        
        agent = RobinAgent()
        task = Task(title="Tarea que falla")
        
        success = agent.execute_task(task)
        
        self.assertFalse(success)
        self.assertEqual(agent.stats['tasks_failed'], 1)
        self.assertIn("Error", task.result)
    
    def test_agent_prompt_building_with_all_features(self):
        """Test construcción completa del prompt con todas las características."""
        agent = AlfredAgent()
        
        # Configurar todas las características
        task = Task(
            title="Tarea compleja",
            description="Implementar feature con todas las herramientas",
            type=TaskType.DEVELOPMENT,
            priority=TaskPriority.CRITICAL,
            tags=['backend', 'api', 'performance']
        )
        
        # Arsenal tools
        agent.available_tools = {
            'search': 'rg --type py',
            'replace': 'sd',
            'format': 'black'
        }
        
        # MCP context
        agent.mcp_prompt_section = """
        ## Conocimiento Compartido
        - Robin: CI/CD configurado en .github/workflows
        - Oracle: Tests en tests/
        """
        
        # Context files
        context_files = ['README.md', 'src/main.py']
        
        # Crear archivos temporales
        for file in context_files:
            Path(file).parent.mkdir(parents=True, exist_ok=True)
            Path(file).write_text(f"# Contenido de {file}")
        
        try:
            prompt = agent._build_prompt(task, context_files)
            
            # Verificar todas las secciones
            self.assertIn("Tarea Actual", prompt)
            self.assertIn("CRITICAL", prompt)
            self.assertIn("backend", prompt)
            self.assertIn("Arsenal de Herramientas", prompt)
            self.assertIn("rg --type py", prompt)
            self.assertIn("MCPs Disponibles", prompt)
            self.assertIn("Conocimiento Compartido", prompt)
            self.assertIn("Contexto del Proyecto", prompt)
            self.assertIn("README.md", prompt)
            
        finally:
            # Limpiar
            for file in context_files:
                Path(file).unlink(missing_ok=True)
    
    @patch('subprocess.run')
    def test_multiple_agents_sequential_execution(self, mock_run):
        """Test ejecución secuencial de múltiples agentes."""
        # Respuestas diferentes para cada agente
        responses = [
            MagicMock(returncode=0, stdout="Alfred: Arquitectura lista"),
            MagicMock(returncode=0, stdout="Robin: CI/CD configurado"),
            MagicMock(returncode=0, stdout="Oracle: Tests escritos")
        ]
        mock_run.side_effect = responses
        
        agents = [AlfredAgent(), RobinAgent(), OracleAgent()]
        tasks = [
            Task(title="Diseñar", assigned_to='alfred'),
            Task(title="Automatizar", assigned_to='robin'),
            Task(title="Testear", assigned_to='oracle')
        ]
        
        results = []
        for agent, task in zip(agents, tasks):
            success = agent.execute_task(task)
            results.append(success)
        
        # Todos deberían ser exitosos
        self.assertTrue(all(results))
        
        # Verificar que cada agente completó su tarea
        for agent in agents:
            self.assertEqual(agent.stats['tasks_completed'], 1)
        
        # Verificar que se llamó 3 veces a Claude
        self.assertEqual(mock_run.call_count, 3)


class TestArsenalRealIntegration(unittest.TestCase):
    """Tests de integración real con Arsenal."""
    
    def test_arsenal_detects_actual_tools(self):
        """Test que Arsenal detecta herramientas reales del sistema."""
        arsenal = Arsenal()
        
        # Verificar que detectó al menos algunas herramientas básicas
        tools = arsenal.available_tools
        
        # Herramientas que deberían estar en cualquier sistema
        basic_tools = ['grep', 'find', 'ls', 'cat']
        
        detected_basics = sum(1 for tool in basic_tools if tool in tools)
        self.assertGreater(detected_basics, 0, "No se detectaron herramientas básicas")
        
        # Si está en el sistema de desarrollo, debería tener más
        if arsenal._check_tool_available('rg'):
            self.assertIn('rg', tools)
            self.assertEqual(arsenal.tool_categories['search']['preferred'], 'rg')


if __name__ == '__main__':
    unittest.main()