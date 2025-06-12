#!/usr/bin/env python3
"""
Batman Hybrid System - Combina lo mejor de ambos mundos
Puede usar Claude Squad cuando está disponible o trabajar independientemente
"""

import os
import json
import time
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Union
import logging
from abc import ABC, abstractmethod
import yaml
import threading
from queue import Queue, Empty
import schedule
from dataclasses import dataclass
from enum import Enum

# Importar componentes de otros sistemas
try:
    from claude_squad_bridge import ClaudeSquadBridge, BatmanClaudeSquadIntegration
    CLAUDE_SQUAD_AVAILABLE = True
except ImportError:
    CLAUDE_SQUAD_AVAILABLE = False

try:
    from batman_ai_controller import (
        ClaudeAPIClient, Task, TaskResult, TaskStatus, 
        TaskPriority, TaskDatabase
    )
    AI_CONTROLLER_AVAILABLE = True
except ImportError:
    AI_CONTROLLER_AVAILABLE = False


class ExecutionMode(Enum):
    """Modos de ejecución disponibles"""
    CLAUDE_SQUAD = "claude_squad"      # Usar Claude Squad existente
    DIRECT_API = "direct_api"          # Usar Claude API directamente
    HYBRID = "hybrid"                  # Combinar ambos según disponibilidad
    LOCAL_ONLY = "local_only"          # Solo comandos locales, sin AI


class TaskExecutor(ABC):
    """Interfaz abstracta para ejecutores de tareas"""
    
    @abstractmethod
    async def execute(self, task: Task) -> TaskResult:
        """Ejecuta una tarea y retorna resultado"""
        pass
        
    @abstractmethod
    def is_available(self) -> bool:
        """Verifica si el ejecutor está disponible"""
        pass
        
    @abstractmethod
    def get_capacity(self) -> int:
        """Retorna cuántas tareas puede manejar simultáneamente"""
        pass


class ClaudeSquadExecutor(TaskExecutor):
    """Ejecutor que usa Claude Squad"""
    
    def __init__(self):
        if not CLAUDE_SQUAD_AVAILABLE:
            raise ImportError("Claude Squad bridge no disponible")
        self.bridge = ClaudeSquadBridge()
        self.integration = BatmanClaudeSquadIntegration()
        
    async def execute(self, task: Task) -> TaskResult:
        """Ejecuta tarea usando Claude Squad"""
        sessions = self.bridge.get_active_sessions()
        
        if not sessions:
            return TaskResult(
                task_id=task.id,
                status=TaskStatus.FAILED,
                started_at=datetime.now(),
                completed_at=datetime.now(),
                error="No hay sesiones activas de Claude Squad",
                output=None,
                artifacts=[],
                metrics={}
            )
            
        # Convertir tarea a formato Claude Squad
        cs_task = {
            'title': task.title,
            'description': task.description,
            'priority': task.priority.name
        }
        
        # Ejecutar en la primera sesión disponible
        result_dict = self.integration.execute_task(cs_task, sessions[0])
        
        # Convertir resultado
        return TaskResult(
            task_id=task.id,
            status=TaskStatus.COMPLETED if result_dict['success'] else TaskStatus.FAILED,
            started_at=datetime.fromisoformat(result_dict['started']),
            completed_at=datetime.fromisoformat(result_dict['completed']),
            output=result_dict.get('response'),
            error=result_dict.get('response') if not result_dict['success'] else None,
            artifacts=result_dict.get('code_blocks', []),
            metrics={'session_id': sessions[0]['id']}
        )
        
    def is_available(self) -> bool:
        """Verifica si hay sesiones de Claude Squad activas"""
        try:
            sessions = self.bridge.get_active_sessions()
            return len(sessions) > 0
        except:
            return False
            
    def get_capacity(self) -> int:
        """Retorna número de sesiones activas"""
        try:
            return len(self.bridge.get_active_sessions())
        except:
            return 0


class DirectAPIExecutor(TaskExecutor):
    """Ejecutor que usa Claude API directamente"""
    
    def __init__(self, api_key: str):
        if not AI_CONTROLLER_AVAILABLE:
            raise ImportError("Batman AI Controller no disponible")
        self.api_key = api_key
        self.concurrent_limit = 3
        self.current_tasks = 0
        self.lock = threading.Lock()
        
    async def execute(self, task: Task) -> TaskResult:
        """Ejecuta tarea usando Claude API"""
        with self.lock:
            self.current_tasks += 1
            
        try:
            async with ClaudeAPIClient(self.api_key) as client:
                # Recopilar contexto
                context = await self._gather_context(task)
                
                # Ejecutar
                response = await client.execute_task_prompt(task, context)
                
                return TaskResult(
                    task_id=task.id,
                    status=TaskStatus.COMPLETED,
                    started_at=datetime.now(),
                    completed_at=datetime.now(),
                    output=response,
                    error=None,
                    artifacts=self._extract_artifacts(response),
                    metrics={'api_calls': 1}
                )
        except Exception as e:
            return TaskResult(
                task_id=task.id,
                status=TaskStatus.FAILED,
                started_at=datetime.now(),
                completed_at=datetime.now(),
                output=None,
                error=str(e),
                artifacts=[],
                metrics={}
            )
        finally:
            with self.lock:
                self.current_tasks -= 1
                
    async def _gather_context(self, task: Task) -> str:
        """Recopila contexto necesario para la tarea"""
        context_parts = []
        
        for context_item in task.context_needed or []:
            if context_item.startswith('file:'):
                file_path = context_item[5:]
                try:
                    with open(file_path) as f:
                        context_parts.append(f"Content of {file_path}:\n{f.read()}")
                except:
                    pass
            elif context_item.startswith('cmd:'):
                cmd = context_item[4:]
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    context_parts.append(f"Output of '{cmd}':\n{result.stdout}")
                except:
                    pass
                    
        return "\n\n".join(context_parts)
        
    def _extract_artifacts(self, response: str) -> List[Dict]:
        """Extrae artefactos del response"""
        import re
        artifacts = []
        
        # Buscar bloques de código
        code_pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(code_pattern, response, re.DOTALL)
        
        for i, (lang, code) in enumerate(matches):
            artifacts.append({
                'type': 'code',
                'language': lang or 'text',
                'content': code.strip()
            })
            
        return artifacts
        
    def is_available(self) -> bool:
        """Siempre disponible si hay API key"""
        return bool(self.api_key)
        
    def get_capacity(self) -> int:
        """Retorna capacidad disponible"""
        with self.lock:
            return self.concurrent_limit - self.current_tasks


class LocalExecutor(TaskExecutor):
    """Ejecutor para comandos locales sin AI"""
    
    def __init__(self):
        self.concurrent_limit = 5
        self.current_tasks = 0
        self.lock = threading.Lock()
        
    async def execute(self, task: Task) -> TaskResult:
        """Ejecuta comando local"""
        if not task.command:
            return TaskResult(
                task_id=task.id,
                status=TaskStatus.FAILED,
                started_at=datetime.now(),
                completed_at=datetime.now(),
                error="Esta tarea requiere AI pero no está disponible",
                output=None,
                artifacts=[],
                metrics={}
            )
            
        with self.lock:
            self.current_tasks += 1
            
        try:
            # Ejecutar comando
            process = await asyncio.create_subprocess_shell(
                task.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=task.timeout
            )
            
            return TaskResult(
                task_id=task.id,
                status=TaskStatus.COMPLETED if process.returncode == 0 else TaskStatus.FAILED,
                started_at=datetime.now(),
                completed_at=datetime.now(),
                output=stdout.decode() if stdout else "",
                error=stderr.decode() if stderr else None,
                artifacts=[],
                metrics={'return_code': process.returncode}
            )
        except asyncio.TimeoutError:
            return TaskResult(
                task_id=task.id,
                status=TaskStatus.FAILED,
                started_at=datetime.now(),
                completed_at=datetime.now(),
                error=f"Timeout después de {task.timeout} segundos",
                output=None,
                artifacts=[],
                metrics={}
            )
        except Exception as e:
            return TaskResult(
                task_id=task.id,
                status=TaskStatus.FAILED,
                started_at=datetime.now(),
                completed_at=datetime.now(),
                error=str(e),
                output=None,
                artifacts=[],
                metrics={}
            )
        finally:
            with self.lock:
                self.current_tasks -= 1
                
    def is_available(self) -> bool:
        """Siempre disponible"""
        return True
        
    def get_capacity(self) -> int:
        """Retorna capacidad disponible"""
        with self.lock:
            return self.concurrent_limit - self.current_tasks


class BatmanHybridSystem:
    """Sistema híbrido que combina todos los ejecutores"""
    
    def __init__(self, config_path: str = "~/.batman/hybrid_config.yaml"):
        self.config_path = Path(config_path).expanduser()
        self.config = self.load_config()
        self.logger = self.setup_logging()
        self.db = TaskDatabase() if AI_CONTROLLER_AVAILABLE else None
        
        # Inicializar ejecutores según disponibilidad
        self.executors = self.initialize_executors()
        self.mode = ExecutionMode(self.config.get('execution_mode', 'hybrid'))
        
        # Cola de tareas y workers
        self.task_queue = Queue()
        self.result_queue = Queue()
        self.workers = []
        self.running = False
        
    def load_config(self) -> Dict:
        """Carga configuración"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        else:
            default_config = {
                'execution_mode': 'hybrid',
                'work_schedule': {
                    'start': '22:00',
                    'end': '06:00'
                },
                'claude_api_key': os.getenv('CLAUDE_API_KEY'),
                'max_workers': 4,
                'task_check_interval': 60,
                'priorities': {
                    'use_claude_squad_for': ['code_generation', 'refactoring'],
                    'use_api_for': ['analysis', 'documentation'],
                    'use_local_for': ['backups', 'cleanup']
                }
            }
            
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(default_config, f)
                
            return default_config
            
    def setup_logging(self) -> logging.Logger:
        """Configura logging"""
        logger = logging.getLogger('batman_hybrid')
        logger.setLevel(logging.INFO)
        
        # Handler para archivo
        log_path = Path.home() / '.batman' / 'logs' / f"hybrid_{datetime.now():%Y%m%d}.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        
        logger.addHandler(file_handler)
        return logger
        
    def initialize_executors(self) -> Dict[str, TaskExecutor]:
        """Inicializa ejecutores disponibles"""
        executors = {}
        
        # Intentar inicializar Claude Squad
        if CLAUDE_SQUAD_AVAILABLE:
            try:
                executors['claude_squad'] = ClaudeSquadExecutor()
                self.logger.info("Claude Squad executor inicializado")
            except Exception as e:
                self.logger.warning(f"No se pudo inicializar Claude Squad: {e}")
                
        # Intentar inicializar API directa
        api_key = self.config.get('claude_api_key')
        if AI_CONTROLLER_AVAILABLE and api_key:
            try:
                executors['direct_api'] = DirectAPIExecutor(api_key)
                self.logger.info("Direct API executor inicializado")
            except Exception as e:
                self.logger.warning(f"No se pudo inicializar Direct API: {e}")
                
        # Siempre disponible
        executors['local'] = LocalExecutor()
        self.logger.info("Local executor inicializado")
        
        return executors
        
    def select_executor(self, task: Task) -> Optional[TaskExecutor]:
        """Selecciona el mejor ejecutor para una tarea"""
        if self.mode == ExecutionMode.LOCAL_ONLY:
            return self.executors.get('local')
            
        # Si la tarea es solo comando local
        if task.command and not task.prompt:
            return self.executors.get('local')
            
        # Verificar preferencias por tipo de tarea
        task_type = task.metadata.get('type', 'general')
        priorities = self.config.get('priorities', {})
        
        # Claude Squad para ciertas tareas
        if task_type in priorities.get('use_claude_squad_for', []):
            cs_executor = self.executors.get('claude_squad')
            if cs_executor and cs_executor.is_available():
                return cs_executor
                
        # API directa para otras
        if task_type in priorities.get('use_api_for', []):
            api_executor = self.executors.get('direct_api')
            if api_executor and api_executor.is_available():
                return api_executor
                
        # Modo híbrido: usar lo que esté disponible
        if self.mode == ExecutionMode.HYBRID:
            # Prioridad: Claude Squad > API > Local
            for executor_name in ['claude_squad', 'direct_api', 'local']:
                executor = self.executors.get(executor_name)
                if executor and executor.is_available() and executor.get_capacity() > 0:
                    return executor
                    
        return None
        
    async def worker(self, worker_id: int):
        """Worker que procesa tareas de la cola"""
        self.logger.info(f"Worker {worker_id} iniciado")
        
        while self.running:
            try:
                # Obtener tarea de la cola (timeout de 1 segundo)
                task = self.task_queue.get(timeout=1)
                
                # Seleccionar ejecutor
                executor = self.select_executor(task)
                
                if not executor:
                    self.logger.error(f"No hay ejecutor disponible para tarea {task.id}")
                    result = TaskResult(
                        task_id=task.id,
                        status=TaskStatus.FAILED,
                        started_at=datetime.now(),
                        completed_at=datetime.now(),
                        error="No hay ejecutor disponible",
                        output=None,
                        artifacts=[],
                        metrics={}
                    )
                else:
                    self.logger.info(f"Worker {worker_id} ejecutando tarea {task.id} con {executor.__class__.__name__}")
                    result = await executor.execute(task)
                    
                # Guardar resultado
                self.result_queue.put(result)
                
                if self.db:
                    self.db.save_result(result)
                    
            except Empty:
                # No hay tareas, esperar
                await asyncio.sleep(1)
            except Exception as e:
                self.logger.error(f"Error en worker {worker_id}: {e}")
                
    async def task_loader(self):
        """Carga tareas periódicamente"""
        while self.running:
            try:
                if self.db:
                    # Cargar desde base de datos
                    pending_tasks = self.db.get_pending_tasks()
                    
                    for task in pending_tasks:
                        # Verificar dependencias
                        if await self.check_dependencies(task):
                            self.task_queue.put(task)
                            
                # También cargar desde archivos YAML
                task_files = Path.home() / '.batman' / 'tasks'
                if task_files.exists():
                    for yaml_file in task_files.glob('*.yaml'):
                        self.load_tasks_from_file(yaml_file)
                        
                # Esperar antes de siguiente carga
                await asyncio.sleep(self.config.get('task_check_interval', 60))
                
            except Exception as e:
                self.logger.error(f"Error cargando tareas: {e}")
                await asyncio.sleep(60)
                
    async def check_dependencies(self, task: Task) -> bool:
        """Verifica dependencias de una tarea"""
        # Implementación simplificada
        return True
        
    def load_tasks_from_file(self, file_path: Path):
        """Carga tareas desde archivo YAML"""
        try:
            with open(file_path) as f:
                data = yaml.safe_load(f)
                
            for task_data in data.get('tasks', []):
                # Convertir a Task
                task_data['id'] = task_data.get('id', f"{file_path.stem}_{datetime.now().timestamp()}")
                task_data['priority'] = TaskPriority[task_data.get('priority', 'MEDIUM').upper()]
                
                task = Task(**task_data)
                
                # Agregar a cola si no existe
                self.task_queue.put(task)
                
        except Exception as e:
            self.logger.error(f"Error cargando tareas de {file_path}: {e}")
            
    async def start(self):
        """Inicia el sistema híbrido"""
        self.logger.info("🦇 Batman Hybrid System iniciando...")
        self.running = True
        
        # Crear workers
        num_workers = self.config.get('max_workers', 4)
        for i in range(num_workers):
            worker_task = asyncio.create_task(self.worker(i))
            self.workers.append(worker_task)
            
        # Iniciar cargador de tareas
        loader_task = asyncio.create_task(self.task_loader())
        
        # Esperar a que terminen (o se interrumpan)
        await asyncio.gather(loader_task, *self.workers, return_exceptions=True)
        
    def stop(self):
        """Detiene el sistema"""
        self.logger.info("Deteniendo Batman Hybrid System...")
        self.running = False
        
    def status_report(self) -> Dict:
        """Genera reporte de estado actual"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'mode': self.mode.value,
            'executors': {},
            'queue_size': self.task_queue.qsize(),
            'workers': len(self.workers)
        }
        
        for name, executor in self.executors.items():
            status['executors'][name] = {
                'available': executor.is_available(),
                'capacity': executor.get_capacity()
            }
            
        return status


# Script principal para CLI
async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Batman Hybrid System')
    parser.add_argument('command', choices=['start', 'status', 'test'])
    parser.add_argument('--mode', choices=['hybrid', 'claude_squad', 'direct_api', 'local_only'])
    
    args = parser.parse_args()
    
    system = BatmanHybridSystem()
    
    if args.mode:
        system.mode = ExecutionMode(args.mode)
        
    if args.command == 'start':
        await system.start()
        
    elif args.command == 'status':
        status = system.status_report()
        print(json.dumps(status, indent=2))
        
    elif args.command == 'test':
        # Modo test: ejecutar una tarea simple
        test_task = Task(
            id='test_001',
            title='Test task',
            description='Verificar que el sistema funciona',
            command='echo "Batman Hybrid System funcionando!"',
            priority=TaskPriority.HIGH
        )
        
        executor = system.select_executor(test_task)
        if executor:
            print(f"Ejecutando con: {executor.__class__.__name__}")
            result = await executor.execute(test_task)
            print(f"Resultado: {result.status.value}")
            print(f"Output: {result.output}")
        else:
            print("No hay ejecutor disponible")


if __name__ == "__main__":
    asyncio.run(main())