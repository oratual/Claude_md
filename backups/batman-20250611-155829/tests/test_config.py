#!/usr/bin/env python3
"""
Tests para el sistema de configuración de Batman Incorporated.
"""

import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os
import yaml
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.config import Config


class TestConfig(unittest.TestCase):
    """Tests para el sistema de configuración."""
    
    def setUp(self):
        """Setup para cada test."""
        # Crear configuración temporal para tests
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / "config"
        self.config_dir.mkdir(exist_ok=True)
        
        # Configuración de ejemplo
        self.default_config = {
            'batman': {
                'name': 'Batman Incorporated',
                'version': '1.0.0'
            },
            'paths': {
                'base': '~/glados/batman-incorporated',
                'logs': '${paths.base}/logs',
                'tasks': '${paths.base}/tasks'
            },
            'agents': {
                'alfred': {
                    'enabled': True,
                    'role': 'Senior Developer'
                },
                'robin': {
                    'enabled': True,
                    'role': 'DevOps'
                }
            },
            'execution': {
                'mode': 'safe',
                'max_retries': 3
            }
        }
        
        # Escribir config por defecto
        default_path = self.config_dir / "default_config.yaml"
        with open(default_path, 'w') as f:
            yaml.dump(self.default_config, f)
    
    def tearDown(self):
        """Cleanup después de cada test."""
        # Limpiar directorio temporal
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_load_default_config(self):
        """Test carga de configuración por defecto."""
        # Crear un archivo de config temporal
        with patch('core.config.Path.__file__', new=self.temp_dir):
            with patch.object(Config, 'default_config_path', self.config_dir / "default_config.yaml"):
                with patch.object(Config, '_create_directories'):
                    config = Config()
                    
                    # Verificar que se cargó correctamente
                    self.assertEqual(config.get('batman.name'), 'Batman Incorporated')
                    self.assertEqual(config.get('batman.version'), '1.0.0')
                    self.assertEqual(config.get('execution.mode'), 'safe')
    
    def test_variable_expansion(self):
        """Test expansión de variables en configuración."""
        with patch.object(Config, 'default_config_path', self.config_dir / "default_config.yaml"):
            with patch.object(Config, '_create_directories'):
                config = Config()
                config.config = {
                    'paths': {
                        'base': '~/test/batman',
                        'logs': '${paths.base}/logs',
                        'nested': '${paths.logs}/daily'
                    }
                }
                
                config._expand_variables()
                
                # Verificar expansión
                base_expanded = os.path.expanduser('~/test/batman')
                self.assertEqual(config.get('paths.base'), base_expanded)
                self.assertEqual(config.get('paths.logs'), f'{base_expanded}/logs')
                self.assertEqual(config.get('paths.nested'), f'{base_expanded}/logs/daily')
    
    def test_deep_merge(self):
        """Test fusión profunda de configuraciones."""
        with patch.object(Config, 'default_config_path', self.config_dir / "default_config.yaml"):
            with patch.object(Config, '_create_directories'):
                config = Config()
        
        base = {
            'agents': {
                'alfred': {'role': 'Developer', 'level': 'senior'},
                'robin': {'role': 'DevOps'}
            },
            'execution': {'mode': 'safe'}
        }
        
        override = {
            'agents': {
                'alfred': {'level': 'expert'},  # Sobrescribir level
                'oracle': {'role': 'QA'}  # Nuevo agente
            },
            'execution': {'timeout': 300}  # Nueva configuración
        }
        
        # _deep_merge modifica in-place
        config._deep_merge(base, override)
        
        # Verificar fusión correcta
        self.assertEqual(base['agents']['alfred']['role'], 'Developer')  # Original
        self.assertEqual(base['agents']['alfred']['level'], 'expert')  # Sobrescrito
        self.assertEqual(base['agents']['robin']['role'], 'DevOps')  # Original
        self.assertEqual(base['agents']['oracle']['role'], 'QA')  # Nuevo
        self.assertEqual(base['execution']['mode'], 'safe')  # Original
        self.assertEqual(base['execution']['timeout'], 300)  # Nuevo
    
    def test_get_nested_value(self):
        """Test obtención de valores anidados con notación de punto."""
        with patch.object(Config, 'default_config_path', self.config_dir / "default_config.yaml"):
            with patch.object(Config, '_create_directories'):
                config = Config()
                config.config = {
                    'level1': {
                        'level2': {
                            'level3': 'value'
                        },
                        'array': [1, 2, 3]
                    }
                }
        
        # Test valores existentes
        self.assertEqual(config.get('level1.level2.level3'), 'value')
        self.assertEqual(config.get('level1.array'), [1, 2, 3])
        
        # Test valores no existentes
        self.assertIsNone(config.get('level1.nonexistent'))
        self.assertEqual(config.get('level1.nonexistent', 'default'), 'default')
    
    def test_set_nested_value(self):
        """Test establecer valores anidados con notación de punto."""
        with patch.object(Config, 'default_config_path', self.config_dir / "default_config.yaml"):
            with patch.object(Config, '_create_directories'):
                config = Config()
                config.config = {}
                
                # Establecer valor anidado
                config.set('agents.batman.role', 'Detective')
        
        # Verificar
        self.assertEqual(config.get('agents.batman.role'), 'Detective')
        
        # Sobrescribir valor existente
        config.set('agents.batman.role', 'Vigilante')
        self.assertEqual(config.get('agents.batman.role'), 'Vigilante')
        
        # Establecer en estructura existente
        config.set('agents.robin.role', 'Sidekick')
        self.assertEqual(config.get('agents.robin.role'), 'Sidekick')
        self.assertEqual(config.get('agents.batman.role'), 'Vigilante')
    
    def test_get_agent_config(self):
        """Test obtención de configuración específica de agente."""
        with patch.object(Config, 'default_config_path', self.config_dir / "default_config.yaml"):
            with patch.object(Config, '_create_directories'):
                config = Config()
                config.config = {
                    'agents': {
                        'alfred': {
                            'enabled': True,
                            'role': 'Senior Developer',
                            'specialties': ['backend', 'architecture']
                        }
                    }
                }
        
        alfred_config = config.get_agent_config('alfred')
        
        self.assertIsNotNone(alfred_config)
        self.assertEqual(alfred_config['role'], 'Senior Developer')
        self.assertIn('backend', alfred_config['specialties'])
        
        # Test agente no existente
        batman_config = config.get_agent_config('batman')
        self.assertEqual(batman_config, {})
    
    def test_is_agent_enabled(self):
        """Test verificación de agentes habilitados."""
        with patch.object(Config, 'default_config_path', self.config_dir / "default_config.yaml"):
            with patch.object(Config, '_create_directories'):
                config = Config()
                config.config = {
                    'agents': {
                        'alfred': {'enabled': True},
                        'robin': {'enabled': False},
                        'oracle': {}  # Sin campo enabled
                    }
                }
                
                self.assertTrue(config.is_agent_enabled('alfred'))
                self.assertFalse(config.is_agent_enabled('robin'))
                self.assertFalse(config.is_agent_enabled('oracle'))  # Por defecto False
                self.assertFalse(config.is_agent_enabled('batman'))  # No existe, por defecto False
    
    def test_get_execution_mode(self):
        """Test obtención de modo de ejecución."""
        with patch.object(Config, 'default_config_path', self.config_dir / "default_config.yaml"):
            with patch.object(Config, '_create_directories'):
                config = Config()
                
                # Con modo establecido
                config.config = {'execution': {'mode': 'fast'}}
                self.assertEqual(config.get_execution_mode(), 'fast')
                
                # Sin modo establecido (default)
                config.config = {}
                self.assertEqual(config.get_execution_mode(), 'auto')
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    def test_save_config(self, mock_makedirs, mock_file):
        """Test guardar configuración a archivo."""
        with patch.object(Config, 'default_config_path', self.config_dir / "default_config.yaml"):
            with patch.object(Config, '_create_directories'):
                config = Config()
                config.config = {'test': 'value'}
        
        # Guardar con ruta específica
        config.save('/tmp/test_config.yaml')
        
        # Verificar que se escribió
        mock_file.assert_called_once_with('/tmp/test_config.yaml', 'w')
        handle = mock_file()
        
        # Verificar que se escribió YAML
        written_content = ''.join([str(call[0][0]) for call in handle.write.call_args_list])
        self.assertIn('test: value', written_content)
    
    @patch('os.makedirs')
    def test_create_directories(self, mock_makedirs):
        """Test creación de directorios requeridos."""
        with patch.object(Config, 'default_config_path', self.config_dir / "default_config.yaml"):
            config = Config()
            config.config = {
                'paths': {
                    'logs': '/tmp/batman/logs',
                    'tasks': '/tmp/batman/tasks',
                    'temp': '/tmp/batman/temp'
                }
            }
        
        config._create_directories()
        
        # Verificar que se intentó crear los directorios
        # La función _create_directories crea paths específicos, no todos los del config
        calls = mock_makedirs.call_args_list
        created_paths = [call[0][0].as_posix() if hasattr(call[0][0], 'as_posix') else str(call[0][0]) for call in calls]
        
        # Verificar que se crearon los directorios logs y tasks
        self.assertIn('/tmp/batman/logs', created_paths)
        self.assertIn('/tmp/batman/tasks', created_paths)
    
    def test_to_dict(self):
        """Test conversión a diccionario."""
        with patch.object(Config, 'default_config_path', self.config_dir / "default_config.yaml"):
            with patch.object(Config, '_create_directories'):
                config = Config()
                config.config = {
                    'agents': {'alfred': {'role': 'Developer'}},
                    'paths': {'base': '/home/user'}
                }
        
        result = config.to_dict()
        
        # Debe ser una copia, no referencia
        self.assertEqual(result, config.config)
        self.assertIsNot(result, config.config)
        
        # Modificar copia no debe afectar original
        result['agents']['alfred']['role'] = 'Modified'
        self.assertEqual(config.get('agents.alfred.role'), 'Developer')
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.read_text')
    def test_merge_user_config(self, mock_read, mock_exists):
        """Test fusión con configuración de usuario."""
        # Simular archivo de usuario
        user_config = {
            'agents': {
                'alfred': {'specialties': ['custom', 'specialty']}
            },
            'custom_setting': 'value'
        }
        
        mock_exists.return_value = True
        mock_read.return_value = yaml.dump(user_config)
        
        with patch.object(Config, 'default_config_path', self.config_dir / "default_config.yaml"):
            with patch.object(Config, '_create_directories'):
                config = Config()
                config.config = {
                    'agents': {
                        'alfred': {'role': 'Developer'}
                    }
                }
        
        # Aplicar configuración de usuario
        config._merge_user_config('/tmp/user_config.yaml')
        
        # Verificar fusión
        self.assertEqual(config.get('agents.alfred.role'), 'Developer')  # Original
        self.assertEqual(config.get('agents.alfred.specialties'), ['custom', 'specialty'])  # Usuario
        self.assertEqual(config.get('custom_setting'), 'value')  # Usuario
    
    def test_config_validation(self):
        """Test validación básica de configuración."""
        with patch.object(Config, 'default_config_path', self.config_dir / "default_config.yaml"):
            with patch.object(Config, '_create_directories'):
                config = Config()
                
                # Configuración mínima válida
                config.config = {
                    'batman': {'name': 'Test'},
                    'agents': {},
                    'paths': {'base': '/tmp'}
                }
        
        # No debe lanzar excepciones
        try:
            config.get('batman.name')
            config.get_agent_config('alfred')
            config.get_execution_mode()
        except Exception as e:
            self.fail(f"La configuración válida lanzó excepción: {e}")
    
    def test_environment_variable_expansion(self):
        """Test expansión de variables de entorno (feature no implementada)."""
        # Esta funcionalidad no está implementada en la configuración actual
        # Se podría agregar en el futuro si es necesaria
        pass


if __name__ == '__main__':
    unittest.main(verbosity=2)