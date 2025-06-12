#!/usr/bin/env python3
"""
Batman MCP Manager - Gestor de Model Context Protocols para Batman
Integra y gestiona MCPs disponibles en el sistema
"""

import os
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import yaml
import tempfile
import shutil
from dataclasses import dataclass
from enum import Enum


class MCPType(Enum):
    """Tipos de MCPs soportados"""
    FILESYSTEM = "filesystem"
    MEMORY = "memory"
    GIT = "git"
    TIME = "time"
    SEQUENTIAL_THINKING = "sequentialthinking"
    CUSTOM = "custom"


@dataclass
class MCPConfig:
    """Configuración de un MCP"""
    name: str
    type: MCPType
    command: List[str]
    args: List[str] = None
    env: Dict[str, str] = None
    capabilities: List[str] = None
    enabled: bool = True
    
    def __post_init__(self):
        if self.args is None:
            self.args = []
        if self.env is None:
            self.env = {}
        if self.capabilities is None:
            self.capabilities = []


class MCPManager:
    """Gestor principal de MCPs para Batman"""
    
    def __init__(self, config_path: str = "~/.batman/mcp_config.yaml"):
        self.config_path = Path(config_path).expanduser()
        self.logger = logging.getLogger(__name__)
        self.mcps = self.load_mcps()
        self.mcp_base_path = Path.home() / "glados" / "MCP"
        
    def load_mcps(self) -> Dict[str, MCPConfig]:
        """Carga configuración de MCPs"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                data = yaml.safe_load(f)
                
            mcps = {}
            for mcp_data in data.get('mcps', []):
                mcp_data['type'] = MCPType(mcp_data['type'])
                mcp = MCPConfig(**mcp_data)
                mcps[mcp.name] = mcp
                
            return mcps
        else:
            # Configuración por defecto con MCPs conocidos
            default_mcps = self._get_default_mcps()
            self.save_config(default_mcps)
            return default_mcps
            
    def _get_default_mcps(self) -> Dict[str, MCPConfig]:
        """Retorna configuración por defecto de MCPs conocidos"""
        return {
            'filesystem': MCPConfig(
                name='filesystem',
                type=MCPType.FILESYSTEM,
                command=['node', '/home/lauta/glados/MCP/built/node/mcp-filesystem.js'],
                capabilities=['read', 'write', 'list', 'search'],
                args=['--workspace', '/home/lauta']
            ),
            'memory': MCPConfig(
                name='memory',
                type=MCPType.MEMORY,
                command=['node', '/home/lauta/glados/MCP/built/node/mcp-memory.js'],
                capabilities=['store', 'retrieve', 'list', 'clear']
            ),
            'git': MCPConfig(
                name='git',
                type=MCPType.GIT,
                command=['node', '/home/lauta/glados/MCP/built/node/mcp-git.js'],
                capabilities=['status', 'diff', 'commit', 'log', 'branch']
            ),
            'time': MCPConfig(
                name='time',
                type=MCPType.TIME,
                command=['node', '/home/lauta/glados/MCP/built/node/mcp-time.js'],
                capabilities=['now', 'schedule', 'timer', 'timezone']
            ),
            'sequentialthinking': MCPConfig(
                name='sequentialthinking',
                type=MCPType.SEQUENTIAL_THINKING,
                command=['node', '/home/lauta/glados/MCP/built/node/mcp-thinking.js'],
                capabilities=['think', 'reason', 'plan', 'reflect']
            )
        }
        
    def save_config(self, mcps: Dict[str, MCPConfig]):
        """Guarda configuración de MCPs"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'mcps': [
                {
                    'name': mcp.name,
                    'type': mcp.type.value,
                    'command': mcp.command,
                    'args': mcp.args,
                    'env': mcp.env,
                    'capabilities': mcp.capabilities,
                    'enabled': mcp.enabled
                }
                for mcp in mcps.values()
            ]
        }
        
        with open(self.config_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
            
    def check_mcp_availability(self, mcp_name: str) -> bool:
        """Verifica si un MCP está disponible y funcional"""
        if mcp_name not in self.mcps:
            return False
            
        mcp = self.mcps[mcp_name]
        
        # Verificar que el comando existe
        if mcp.command[0] == 'node':
            # Verificar archivo JS
            js_file = Path(mcp.command[1])
            if not js_file.exists():
                self.logger.warning(f"MCP {mcp_name} archivo no encontrado: {js_file}")
                return False
                
        # Intentar ejecutar con --version o similar
        try:
            test_cmd = mcp.command + ['--version']
            result = subprocess.run(test_cmd, capture_output=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
            
    def get_available_mcps(self) -> List[str]:
        """Obtiene lista de MCPs disponibles y funcionales"""
        available = []
        
        for mcp_name in self.mcps:
            if self.mcps[mcp_name].enabled and self.check_mcp_availability(mcp_name):
                available.append(mcp_name)
                
        return available
        
    def install_mcp(self, mcp_url: str, mcp_name: str) -> bool:
        """Instala un nuevo MCP desde una URL de GitHub"""
        install_dir = self.mcp_base_path / "source" / "custom" / mcp_name
        
        try:
            # Clonar repositorio
            self.logger.info(f"Instalando MCP {mcp_name} desde {mcp_url}")
            
            install_dir.parent.mkdir(parents=True, exist_ok=True)
            
            subprocess.run([
                'git', 'clone', mcp_url, str(install_dir)
            ], check=True)
            
            # Instalar dependencias si hay package.json
            package_json = install_dir / "package.json"
            if package_json.exists():
                self.logger.info("Instalando dependencias npm...")
                subprocess.run(['npm', 'install'], cwd=install_dir, check=True)
                
                # Compilar si es necesario
                if (install_dir / "tsconfig.json").exists():
                    self.logger.info("Compilando TypeScript...")
                    subprocess.run(['npm', 'run', 'build'], cwd=install_dir, check=True)
                    
            # Buscar archivo principal
            main_file = self._find_mcp_main_file(install_dir)
            
            if main_file:
                # Agregar a configuración
                new_mcp = MCPConfig(
                    name=mcp_name,
                    type=MCPType.CUSTOM,
                    command=['node', str(main_file)],
                    capabilities=['custom']
                )
                
                self.mcps[mcp_name] = new_mcp
                self.save_config(self.mcps)
                
                self.logger.info(f"MCP {mcp_name} instalado exitosamente")
                return True
            else:
                self.logger.error(f"No se encontró archivo principal para MCP {mcp_name}")
                return False
                
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error instalando MCP: {e}")
            return False
            
    def _find_mcp_main_file(self, install_dir: Path) -> Optional[Path]:
        """Encuentra el archivo principal de un MCP"""
        # Buscar en package.json
        package_json = install_dir / "package.json"
        if package_json.exists():
            with open(package_json) as f:
                data = json.load(f)
                
            if 'main' in data:
                return install_dir / data['main']
                
        # Buscar archivos comunes
        common_names = ['index.js', 'main.js', 'dist/index.js', 'build/index.js']
        for name in common_names:
            file_path = install_dir / name
            if file_path.exists():
                return file_path
                
        # Buscar cualquier .js en raíz
        js_files = list(install_dir.glob('*.js'))
        if js_files:
            return js_files[0]
            
        return None


class BatmanMCPInterface:
    """Interfaz de Batman para usar MCPs"""
    
    def __init__(self, mcp_manager: MCPManager):
        self.manager = mcp_manager
        self.logger = logging.getLogger(__name__)
        self.memory_cache = {}
        
    def use_filesystem_mcp(self, operation: str, **kwargs) -> Dict:
        """Usa el MCP de filesystem para operaciones de archivos"""
        if 'filesystem' not in self.manager.get_available_mcps():
            return {'error': 'Filesystem MCP no disponible'}
            
        mcp = self.manager.mcps['filesystem']
        
        # Construir comando según operación
        if operation == 'search':
            pattern = kwargs.get('pattern', '')
            path = kwargs.get('path', '.')
            cmd = mcp.command + ['search', pattern, path]
            
        elif operation == 'read':
            file_path = kwargs.get('file_path')
            if not file_path:
                return {'error': 'file_path requerido'}
            cmd = mcp.command + ['read', file_path]
            
        elif operation == 'write':
            file_path = kwargs.get('file_path')
            content = kwargs.get('content')
            if not file_path or content is None:
                return {'error': 'file_path y content requeridos'}
                
            # Escribir contenido a archivo temporal
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
                tmp.write(content)
                tmp_path = tmp.name
                
            cmd = mcp.command + ['write', file_path, tmp_path]
            
        else:
            return {'error': f'Operación no soportada: {operation}'}
            
        # Ejecutar comando
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return {'success': True, 'output': result.stdout}
            else:
                return {'success': False, 'error': result.stderr}
                
        except subprocess.TimeoutExpired:
            return {'error': 'Timeout ejecutando MCP'}
        except Exception as e:
            return {'error': str(e)}
        finally:
            # Limpiar archivo temporal si existe
            if operation == 'write' and 'tmp_path' in locals():
                Path(tmp_path).unlink(missing_ok=True)
                
    def use_memory_mcp(self, operation: str, **kwargs) -> Dict:
        """Usa el MCP de memoria para persistencia"""
        if 'memory' not in self.manager.get_available_mcps():
            # Fallback a memoria local
            return self._local_memory_fallback(operation, **kwargs)
            
        mcp = self.manager.mcps['memory']
        
        if operation == 'store':
            key = kwargs.get('key')
            value = kwargs.get('value')
            if not key or value is None:
                return {'error': 'key y value requeridos'}
                
            # Serializar valor a JSON
            value_json = json.dumps(value)
            cmd = mcp.command + ['store', key, value_json]
            
        elif operation == 'retrieve':
            key = kwargs.get('key')
            if not key:
                return {'error': 'key requerido'}
            cmd = mcp.command + ['retrieve', key]
            
        elif operation == 'list':
            cmd = mcp.command + ['list']
            
        else:
            return {'error': f'Operación no soportada: {operation}'}
            
        # Ejecutar
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                
                # Parsear resultado si es JSON
                if operation == 'retrieve' and output:
                    try:
                        output = json.loads(output)
                    except json.JSONDecodeError:
                        pass
                        
                return {'success': True, 'output': output}
            else:
                return {'success': False, 'error': result.stderr}
                
        except Exception as e:
            return {'error': str(e)}
            
    def _local_memory_fallback(self, operation: str, **kwargs) -> Dict:
        """Fallback local para operaciones de memoria"""
        if operation == 'store':
            key = kwargs.get('key')
            value = kwargs.get('value')
            self.memory_cache[key] = value
            return {'success': True, 'output': 'Stored locally'}
            
        elif operation == 'retrieve':
            key = kwargs.get('key')
            value = self.memory_cache.get(key)
            return {'success': True, 'output': value}
            
        elif operation == 'list':
            return {'success': True, 'output': list(self.memory_cache.keys())}
            
        return {'error': f'Operación no soportada: {operation}'}
        
    def use_git_mcp(self, operation: str, **kwargs) -> Dict:
        """Usa el MCP de Git para operaciones de repositorio"""
        if 'git' not in self.manager.get_available_mcps():
            # Fallback a comandos git directos
            return self._git_command_fallback(operation, **kwargs)
            
        mcp = self.manager.mcps['git']
        repo_path = kwargs.get('repo_path', '.')
        
        if operation == 'status':
            cmd = mcp.command + ['status', repo_path]
            
        elif operation == 'diff':
            cmd = mcp.command + ['diff', repo_path]
            
        elif operation == 'commit':
            message = kwargs.get('message', 'Batman auto-commit')
            cmd = mcp.command + ['commit', repo_path, '-m', message]
            
        elif operation == 'log':
            limit = kwargs.get('limit', '10')
            cmd = mcp.command + ['log', repo_path, '--limit', str(limit)]
            
        else:
            return {'error': f'Operación no soportada: {operation}'}
            
        # Ejecutar
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return {'success': True, 'output': result.stdout}
            else:
                return {'success': False, 'error': result.stderr}
                
        except Exception as e:
            return {'error': str(e)}
            
    def _git_command_fallback(self, operation: str, **kwargs) -> Dict:
        """Fallback usando comandos git directos"""
        repo_path = kwargs.get('repo_path', '.')
        
        try:
            if operation == 'status':
                result = subprocess.run(
                    ['git', 'status', '--porcelain'], 
                    cwd=repo_path, 
                    capture_output=True, 
                    text=True
                )
            elif operation == 'diff':
                result = subprocess.run(
                    ['git', 'diff'], 
                    cwd=repo_path, 
                    capture_output=True, 
                    text=True
                )
            elif operation == 'log':
                limit = kwargs.get('limit', 10)
                result = subprocess.run(
                    ['git', 'log', f'--oneline', f'-n', str(limit)], 
                    cwd=repo_path, 
                    capture_output=True, 
                    text=True
                )
            else:
                return {'error': f'Operación no soportada: {operation}'}
                
            if result.returncode == 0:
                return {'success': True, 'output': result.stdout}
            else:
                return {'success': False, 'error': result.stderr}
                
        except Exception as e:
            return {'error': str(e)}
            
    def use_sequential_thinking(self, task: str, context: str = "") -> Dict:
        """Usa MCP de pensamiento secuencial para razonamiento"""
        if 'sequentialthinking' not in self.manager.get_available_mcps():
            # Fallback a archivo de pensamiento local
            return self._thinking_fallback(task, context)
            
        mcp = self.manager.mcps['sequentialthinking']
        
        # Preparar entrada
        thinking_input = f"Task: {task}\nContext: {context}"
        
        # Escribir a archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write(thinking_input)
            tmp_path = tmp.name
            
        try:
            cmd = mcp.command + ['think', tmp_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return {'success': True, 'output': result.stdout}
            else:
                return {'success': False, 'error': result.stderr}
                
        except Exception as e:
            return {'error': str(e)}
        finally:
            Path(tmp_path).unlink(missing_ok=True)
            
    def _thinking_fallback(self, task: str, context: str = "") -> Dict:
        """Fallback para pensamiento secuencial"""
        thinking_dir = Path.home() / '.batman' / 'thinking'
        thinking_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        thought_file = thinking_dir / f"thought_{timestamp}.md"
        
        # Crear estructura de pensamiento
        thought_content = f"""# Pensamiento Secuencial - Batman

**Timestamp**: {datetime.now().isoformat()}
**Tarea**: {task}

## Contexto
{context}

## Análisis
1. Descomponer la tarea en pasos
2. Identificar dependencias
3. Evaluar riesgos
4. Planificar ejecución

## Plan de Acción
- [ ] Paso 1: Analizar requisitos
- [ ] Paso 2: Preparar entorno
- [ ] Paso 3: Ejecutar tarea
- [ ] Paso 4: Verificar resultados

## Reflexiones
- La tarea requiere análisis cuidadoso
- Se debe proceder con precaución
- Documentar todos los pasos

---
*Generado por Batman Thinking Fallback*
"""
        
        thought_file.write_text(thought_content)
        
        return {
            'success': True, 
            'output': thought_content,
            'file': str(thought_file)
        }


# Funciones de utilidad
def test_mcp_availability():
    """Prueba la disponibilidad de todos los MCPs"""
    manager = MCPManager()
    
    print("🦇 Batman MCP Manager - Test de Disponibilidad\n")
    
    for mcp_name, mcp_config in manager.mcps.items():
        available = manager.check_mcp_availability(mcp_name)
        status = "✅ Disponible" if available else "❌ No disponible"
        print(f"{mcp_name}: {status}")
        
        if available:
            print(f"  Capacidades: {', '.join(mcp_config.capabilities)}")
            
    print(f"\nMCPs activos: {', '.join(manager.get_available_mcps())}")


def example_mcp_usage():
    """Ejemplo de uso de MCPs"""
    manager = MCPManager()
    interface = BatmanMCPInterface(manager)
    
    print("🦇 Batman MCP Interface - Ejemplos de Uso\n")
    
    # Ejemplo 1: Búsqueda en filesystem
    print("1. Buscando archivos Python:")
    result = interface.use_filesystem_mcp('search', pattern='*.py', path='.')
    if result.get('success'):
        print(f"  Encontrados: {result['output'][:200]}...")
    else:
        print(f"  Error: {result.get('error')}")
        
    # Ejemplo 2: Memoria persistente
    print("\n2. Usando memoria persistente:")
    interface.use_memory_mcp('store', key='last_run', value=datetime.now().isoformat())
    result = interface.use_memory_mcp('retrieve', key='last_run')
    if result.get('success'):
        print(f"  Última ejecución: {result['output']}")
        
    # Ejemplo 3: Estado de Git
    print("\n3. Estado del repositorio:")
    result = interface.use_git_mcp('status')
    if result.get('success'):
        print(f"  {result['output'][:200]}...")
        
    # Ejemplo 4: Pensamiento secuencial
    print("\n4. Razonamiento sobre tarea:")
    result = interface.use_sequential_thinking(
        "Optimizar el rendimiento del sistema",
        "El sistema está usando 80% de CPU"
    )
    if result.get('success'):
        print(f"  {result['output'][:300]}...")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_mcp_availability()
    elif len(sys.argv) > 1 and sys.argv[1] == "examples":
        example_mcp_usage()
    else:
        print("Uso: python batman_mcp_manager.py [test|examples]")