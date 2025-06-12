#!/usr/bin/env python3
"""
Claude Code Runner - Sistema para ejecutar Claude Code automáticamente
Diseñado para trabajar toda la noche procesando tareas sin supervisión
"""

import os
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging
import yaml
import signal
import sys
from dataclasses import dataclass
from enum import Enum
import threading
import queue
import shutil
import tempfile


class ExecutionStrategy(Enum):
    """Estrategias de ejecución disponibles"""
    CLAUDE_CODE_CLI = "cli"          # Usar claude code CLI directamente
    TMUX_SESSION = "tmux"            # Crear sesión tmux con claude code
    EXPECT_SCRIPT = "expect"         # Usar expect para automatizar interacción
    MCP_SERVER = "mcp"               # Crear servidor MCP personalizado


@dataclass
class ClaudeTask:
    """Representa una tarea para Claude Code"""
    id: str
    prompt: str
    working_directory: str = "."
    context_files: List[str] = None
    expected_actions: List[str] = None  # read, write, edit, etc
    timeout: int = 300
    priority: int = 3
    metadata: Dict = None
    
    def __post_init__(self):
        if self.context_files is None:
            self.context_files = []
        if self.expected_actions is None:
            self.expected_actions = []
        if self.metadata is None:
            self.metadata = {}


class ClaudeCodeExecutor:
    """Ejecutor base para Claude Code"""
    
    def __init__(self, strategy: ExecutionStrategy = ExecutionStrategy.TMUX_SESSION):
        self.strategy = strategy
        self.logger = logging.getLogger(__name__)
        self.current_session = None
        
    def execute_task(self, task: ClaudeTask) -> Dict:
        """Ejecuta una tarea usando la estrategia configurada"""
        self.logger.info(f"Ejecutando tarea {task.id} con estrategia {self.strategy.value}")
        
        if self.strategy == ExecutionStrategy.TMUX_SESSION:
            return self._execute_tmux(task)
        elif self.strategy == ExecutionStrategy.EXPECT_SCRIPT:
            return self._execute_expect(task)
        elif self.strategy == ExecutionStrategy.CLAUDE_CODE_CLI:
            return self._execute_cli(task)
        elif self.strategy == ExecutionStrategy.MCP_SERVER:
            return self._execute_mcp(task)
        else:
            raise ValueError(f"Estrategia no soportada: {self.strategy}")
            
    def _execute_tmux(self, task: ClaudeTask) -> Dict:
        """Ejecuta usando sesión tmux"""
        session_name = f"batman-claude-{task.id[:8]}"
        result = {
            'task_id': task.id,
            'strategy': 'tmux',
            'started_at': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        try:
            # Crear sesión tmux
            cmd = f"tmux new-session -d -s {session_name} -c {task.working_directory}"
            subprocess.run(cmd, shell=True, check=True)
            
            # Preparar prompt con contexto
            full_prompt = self._prepare_prompt(task)
            
            # Escribir prompt a archivo temporal
            prompt_file = Path(f"/tmp/batman_prompt_{task.id}.txt")
            prompt_file.write_text(full_prompt)
            
            # Enviar comando a tmux para ejecutar claude
            # Usando echo para simular entrada interactiva
            tmux_cmd = f"""tmux send-keys -t {session_name} "claude code '{full_prompt}'" Enter"""
            subprocess.run(tmux_cmd, shell=True)
            
            # Esperar y capturar output
            time.sleep(5)  # Dar tiempo para que inicie
            
            # Monitorear progreso
            output = self._monitor_tmux_session(session_name, task.timeout)
            
            result['output'] = output
            result['status'] = 'completed'
            
        except subprocess.CalledProcessError as e:
            result['status'] = 'failed'
            result['error'] = str(e)
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
        finally:
            # Limpiar sesión tmux
            subprocess.run(f"tmux kill-session -t {session_name}", shell=True, stderr=subprocess.DEVNULL)
            result['completed_at'] = datetime.now().isoformat()
            
        return result
        
    def _execute_expect(self, task: ClaudeTask) -> Dict:
        """Ejecuta usando expect script para automatizar interacción"""
        result = {
            'task_id': task.id,
            'strategy': 'expect',
            'started_at': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        # Crear expect script
        expect_script = self._create_expect_script(task)
        script_path = Path(f"/tmp/batman_expect_{task.id}.exp")
        script_path.write_text(expect_script)
        script_path.chmod(0o755)
        
        try:
            # Ejecutar expect script
            process = subprocess.Popen(
                ['expect', str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=task.working_directory,
                text=True
            )
            
            stdout, stderr = process.communicate(timeout=task.timeout)
            
            result['output'] = stdout
            result['error'] = stderr if stderr else None
            result['status'] = 'completed' if process.returncode == 0 else 'failed'
            
        except subprocess.TimeoutExpired:
            process.kill()
            result['status'] = 'timeout'
            result['error'] = f"Timeout después de {task.timeout} segundos"
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
        finally:
            # Limpiar
            script_path.unlink(missing_ok=True)
            result['completed_at'] = datetime.now().isoformat()
            
        return result
        
    def _execute_cli(self, task: ClaudeTask) -> Dict:
        """Ejecuta usando Claude Code CLI directamente (si existe)"""
        result = {
            'task_id': task.id,
            'strategy': 'cli',
            'started_at': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        # Verificar si claude está disponible
        if not shutil.which('claude'):
            result['status'] = 'failed'
            result['error'] = 'Claude CLI no encontrado'
            return result
            
        try:
            # Preparar comando
            full_prompt = self._prepare_prompt(task)
            
            # Ejecutar claude con prompt
            process = subprocess.Popen(
                ['claude', 'code', full_prompt],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=task.working_directory,
                text=True
            )
            
            stdout, stderr = process.communicate(timeout=task.timeout)
            
            result['output'] = stdout
            result['error'] = stderr if stderr else None
            result['status'] = 'completed' if process.returncode == 0 else 'failed'
            
        except subprocess.TimeoutExpired:
            process.kill()
            result['status'] = 'timeout'
            result['error'] = f"Timeout después de {task.timeout} segundos"
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
        finally:
            result['completed_at'] = datetime.now().isoformat()
            
        return result
        
    def _execute_mcp(self, task: ClaudeTask) -> Dict:
        """Ejecuta usando servidor MCP personalizado"""
        # Esta estrategia requiere implementar un servidor MCP
        # que pueda recibir tareas y ejecutarlas con Claude
        result = {
            'task_id': task.id,
            'strategy': 'mcp',
            'started_at': datetime.now().isoformat(),
            'status': 'not_implemented',
            'error': 'MCP strategy requiere implementación adicional'
        }
        
        return result
        
    def _prepare_prompt(self, task: ClaudeTask) -> str:
        """Prepara el prompt completo con contexto"""
        prompt_parts = [task.prompt]
        
        # Agregar contexto de archivos si es necesario
        if task.context_files:
            prompt_parts.append("\nContexto de archivos:")
            for file_path in task.context_files:
                if Path(file_path).exists():
                    prompt_parts.append(f"\n--- {file_path} ---")
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                            # Limitar tamaño del contexto
                            if len(content) > 1000:
                                content = content[:1000] + "\n... (truncado)"
                            prompt_parts.append(content)
                    except Exception as e:
                        prompt_parts.append(f"Error leyendo archivo: {e}")
                        
        # Agregar instrucciones especiales
        if task.expected_actions:
            prompt_parts.append(f"\nAcciones esperadas: {', '.join(task.expected_actions)}")
            
        return "\n".join(prompt_parts)
        
    def _monitor_tmux_session(self, session_name: str, timeout: int) -> str:
        """Monitorea una sesión tmux y captura output"""
        start_time = time.time()
        output_parts = []
        
        while time.time() - start_time < timeout:
            # Capturar contenido del pane
            try:
                cmd = f"tmux capture-pane -t {session_name} -p"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    current_output = result.stdout
                    
                    # Detectar si terminó (buscar patrones de finalización)
                    if any(pattern in current_output for pattern in ['Task completed', 'Goodbye!', '>']):
                        output_parts.append(current_output)
                        break
                        
                    output_parts.append(current_output)
                    
            except Exception as e:
                self.logger.error(f"Error monitoreando tmux: {e}")
                
            time.sleep(2)
            
        return "\n".join(output_parts)
        
    def _create_expect_script(self, task: ClaudeTask) -> str:
        """Crea un script expect para automatizar Claude"""
        prompt = self._prepare_prompt(task).replace('"', '\\"').replace('\n', '\\n')
        
        script = f"""#!/usr/bin/expect -f
set timeout {task.timeout}

# Iniciar claude
spawn claude code

# Esperar prompt
expect {{
    ">" {{
        send "{prompt}\\r"
    }}
    timeout {{
        puts "Timeout esperando prompt"
        exit 1
    }}
}}

# Esperar que termine
expect {{
    "Task completed" {{
        puts "Tarea completada"
    }}
    "Goodbye!" {{
        puts "Claude terminó"
    }}
    timeout {{
        puts "Timeout esperando finalización"
    }}
}}

# Capturar output
expect eof
"""
        
        return script


class BatmanClaudeOrchestrator:
    """Orquestador principal para ejecutar Claude Code toda la noche"""
    
    def __init__(self, config_path: str = "~/.batman/claude_config.yaml"):
        self.config_path = Path(config_path).expanduser()
        self.config = self.load_config()
        self.logger = self.setup_logging()
        
        # Inicializar componentes
        self.executor = ClaudeCodeExecutor(
            ExecutionStrategy(self.config.get('execution_strategy', 'tmux'))
        )
        
        # Colas de tareas
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        
        # Control
        self.running = False
        self.workers = []
        
    def load_config(self) -> Dict:
        """Carga configuración"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        else:
            default_config = {
                'execution_strategy': 'tmux',
                'max_concurrent_tasks': 1,  # Claude puede ser pesado
                'task_check_interval': 60,
                'work_hours': {
                    'start': '22:00',
                    'end': '06:00'
                },
                'task_directories': ['~/.batman/tasks'],
                'log_level': 'INFO'
            }
            
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(default_config, f)
                
            return default_config
            
    def setup_logging(self) -> logging.Logger:
        """Configura logging"""
        logger = logging.getLogger('batman_claude')
        logger.setLevel(self.config.get('log_level', 'INFO'))
        
        # Handler para archivo
        log_path = Path.home() / '.batman' / 'logs' / f"claude_{datetime.now():%Y%m%d}.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        handler = logging.FileHandler(log_path)
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        
        logger.addHandler(handler)
        return logger
        
    def load_tasks(self):
        """Carga tareas desde directorios configurados"""
        for task_dir in self.config.get('task_directories', []):
            task_path = Path(task_dir).expanduser()
            
            if not task_path.exists():
                continue
                
            # Buscar archivos de tareas
            for task_file in task_path.glob('*.yaml'):
                try:
                    with open(task_file) as f:
                        data = yaml.safe_load(f)
                        
                    for task_data in data.get('tasks', []):
                        # Convertir a ClaudeTask
                        task = ClaudeTask(
                            id=task_data.get('id', f"{task_file.stem}_{time.time()}"),
                            prompt=task_data['prompt'],
                            working_directory=task_data.get('working_directory', '.'),
                            context_files=task_data.get('context_files', []),
                            expected_actions=task_data.get('expected_actions', []),
                            timeout=task_data.get('timeout', 300),
                            priority=task_data.get('priority', 3),
                            metadata=task_data.get('metadata', {})
                        )
                        
                        self.task_queue.put((task.priority, task))
                        
                except Exception as e:
                    self.logger.error(f"Error cargando tareas de {task_file}: {e}")
                    
    def worker_thread(self, worker_id: int):
        """Thread worker para procesar tareas"""
        self.logger.info(f"Worker {worker_id} iniciado")
        
        while self.running:
            try:
                # Obtener tarea (con timeout para poder chequear running)
                priority, task = self.task_queue.get(timeout=1)
                
                self.logger.info(f"Worker {worker_id} procesando tarea {task.id}")
                
                # Ejecutar tarea
                result = self.executor.execute_task(task)
                
                # Guardar resultado
                self.result_queue.put(result)
                
                # Log resultado
                if result['status'] == 'completed':
                    self.logger.info(f"Tarea {task.id} completada exitosamente")
                else:
                    self.logger.error(f"Tarea {task.id} falló: {result.get('error')}")
                    
            except queue.Empty:
                # No hay tareas, continuar
                continue
            except Exception as e:
                self.logger.error(f"Error en worker {worker_id}: {e}")
                
    def generate_report(self) -> str:
        """Genera reporte de ejecución"""
        results = []
        
        # Vaciar cola de resultados
        while not self.result_queue.empty():
            try:
                results.append(self.result_queue.get_nowait())
            except queue.Empty:
                break
                
        # Generar reporte
        report = f"""# Batman Claude Report - {datetime.now():%Y-%m-%d %H:%M}

## Resumen
- Tareas ejecutadas: {len(results)}
- Exitosas: {sum(1 for r in results if r['status'] == 'completed')}
- Fallidas: {sum(1 for r in results if r['status'] == 'failed')}
- Timeouts: {sum(1 for r in results if r['status'] == 'timeout')}

## Detalle de Tareas
"""
        
        for result in results:
            status_icon = "✅" if result['status'] == 'completed' else "❌"
            report += f"\n### {status_icon} Tarea {result['task_id']}\n"
            report += f"- Estado: {result['status']}\n"
            report += f"- Estrategia: {result['strategy']}\n"
            report += f"- Inicio: {result['started_at']}\n"
            report += f"- Fin: {result.get('completed_at', 'N/A')}\n"
            
            if result.get('error'):
                report += f"- Error: {result['error']}\n"
                
            if result.get('output'):
                report += f"\n#### Output:\n```\n{result['output'][:500]}...\n```\n"
                
        return report
        
    def start(self):
        """Inicia el orquestador"""
        self.logger.info("🦇 Batman Claude Orchestrator iniciando...")
        self.running = True
        
        # Configurar signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Cargar tareas iniciales
        self.load_tasks()
        
        # Iniciar workers
        num_workers = self.config.get('max_concurrent_tasks', 1)
        for i in range(num_workers):
            worker = threading.Thread(target=self.worker_thread, args=(i,))
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
            
        # Loop principal
        try:
            while self.running:
                # Recargar tareas periódicamente
                time.sleep(self.config.get('task_check_interval', 60))
                self.load_tasks()
                
        except KeyboardInterrupt:
            self.logger.info("Interrupción recibida")
            
        # Esperar a que terminen los workers
        self.running = False
        for worker in self.workers:
            worker.join(timeout=10)
            
        # Generar reporte final
        report = self.generate_report()
        report_path = Path.home() / '.batman' / 'reports' / f"claude_report_{datetime.now():%Y%m%d_%H%M}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report)
        
        self.logger.info(f"Reporte guardado en: {report_path}")
        
    def _signal_handler(self, signum, frame):
        """Maneja señales del sistema"""
        self.logger.info(f"Señal {signum} recibida, deteniendo...")
        self.running = False


# Script de ejemplo de tareas
EXAMPLE_TASKS = """
# Ejemplo de archivo de tareas para Batman Claude
tasks:
  - id: analyze_project_structure
    prompt: |
      Analiza la estructura del proyecto Batman en el directorio actual.
      Lista todos los archivos Python y proporciona un resumen de lo que hace cada uno.
      Identifica áreas de mejora y sugiere refactorizaciones.
    working_directory: /home/lauta/glados/batman
    context_files:
      - batman.py
      - src/task_executor.py
    expected_actions:
      - read
      - analyze
    timeout: 180
    priority: 2
    
  - id: update_documentation
    prompt: |
      Actualiza el archivo README.md con la información más reciente del proyecto.
      Asegúrate de documentar todas las nuevas características y cambios.
    working_directory: /home/lauta/glados/batman
    context_files:
      - README.md
      - CLAUDE.md
    expected_actions:
      - read
      - edit
    timeout: 300
    priority: 3
    
  - id: security_audit
    prompt: |
      Realiza una auditoría de seguridad básica del sistema.
      Busca permisos incorrectos, puertos abiertos y configuraciones inseguras.
      Genera un informe con recomendaciones.
    working_directory: /home/lauta
    expected_actions:
      - analyze
      - write
    timeout: 600
    priority: 1
"""


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Batman Claude Code Runner')
    parser.add_argument('command', choices=['start', 'test', 'example'])
    parser.add_argument('--strategy', choices=['tmux', 'expect', 'cli', 'mcp'])
    
    args = parser.parse_args()
    
    if args.command == 'start':
        orchestrator = BatmanClaudeOrchestrator()
        if args.strategy:
            orchestrator.config['execution_strategy'] = args.strategy
        orchestrator.start()
        
    elif args.command == 'test':
        # Ejecutar una tarea de prueba
        executor = ClaudeCodeExecutor(
            ExecutionStrategy(args.strategy or 'tmux')
        )
        
        test_task = ClaudeTask(
            id='test_001',
            prompt='Lista los archivos en el directorio actual y describe qué hace cada uno.',
            working_directory='.',
            timeout=60
        )
        
        result = executor.execute_task(test_task)
        print(json.dumps(result, indent=2))
        
    elif args.command == 'example':
        # Crear archivo de ejemplo
        example_path = Path.home() / '.batman' / 'tasks' / 'example_tasks.yaml'
        example_path.parent.mkdir(parents=True, exist_ok=True)
        example_path.write_text(EXAMPLE_TASKS)
        print(f"Archivo de ejemplo creado en: {example_path}")


if __name__ == "__main__":
    main()