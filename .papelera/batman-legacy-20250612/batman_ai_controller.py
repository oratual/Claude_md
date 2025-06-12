#!/usr/bin/env python3
"""
Batman AI Controller - Sistema desde cero para ejecutar Claude Code toda la noche
Diseñado específicamente para trabajar con Claude API directamente
"""

import os
import json
import time
import asyncio
import aiohttp
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import yaml
from concurrent.futures import ThreadPoolExecutor
import signal
import sys

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"

class TaskPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    EXPERIMENTAL = 5

@dataclass
class Task:
    """Representa una tarea para ejecutar"""
    id: str
    title: str
    description: str
    command: Optional[str] = None
    prompt: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    dependencies: List[str] = None
    retry_count: int = 3
    timeout: int = 300
    context_needed: List[str] = None
    expected_output_type: str = "text"  # text, code, file, analysis
    validation_rules: Dict = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.context_needed is None:
            self.context_needed = []
        if self.validation_rules is None:
            self.validation_rules = {}
        if self.metadata is None:
            self.metadata = {}

@dataclass
class TaskResult:
    """Resultado de ejecutar una tarea"""
    task_id: str
    status: TaskStatus
    started_at: datetime
    completed_at: Optional[datetime]
    output: Optional[str]
    error: Optional[str]
    artifacts: List[Dict]  # Archivos creados, código generado, etc
    metrics: Dict  # Tiempo, tokens usados, etc
    
    def __post_init__(self):
        if self.artifacts is None:
            self.artifacts = []
        if self.metrics is None:
            self.metrics = {}


class ClaudeAPIClient:
    """Cliente para interactuar con Claude API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1"
        self.headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def send_message(self, messages: List[Dict], system: str = None, 
                          max_tokens: int = 4096) -> Dict:
        """Envía mensaje a Claude y obtiene respuesta"""
        payload = {
            "model": "claude-3-opus-20240229",
            "messages": messages,
            "max_tokens": max_tokens
        }
        
        if system:
            payload["system"] = system
            
        async with self.session.post(
            f"{self.base_url}/messages",
            json=payload,
            headers=self.headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error = await response.text()
                raise Exception(f"Claude API error: {response.status} - {error}")
                
    async def execute_task_prompt(self, task: Task, context: str = "") -> str:
        """Ejecuta un prompt de tarea con Claude"""
        system_prompt = """You are Batman, an AI assistant working autonomously at night.
You execute tasks without human supervision. Be decisive, thorough, and safe.
Always provide clear summaries of what you did and any issues encountered.
Format code blocks with appropriate language tags."""
        
        messages = [{
            "role": "user",
            "content": f"""Task: {task.title}

Description: {task.description}

{f'Context: {context}' if context else ''}

{f'Additional Instructions: {task.prompt}' if task.prompt else ''}

Execute this task and provide a detailed summary of actions taken."""
        }]
        
        response = await self.send_message(messages, system=system_prompt)
        return response['content'][0]['text']


class TaskDatabase:
    """Base de datos SQLite para persistencia de tareas"""
    
    def __init__(self, db_path: str = "~/.batman/tasks.db"):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
        
    def init_db(self):
        """Inicializa esquema de base de datos"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority INTEGER,
                    status TEXT,
                    created_at TIMESTAMP,
                    scheduled_for TIMESTAMP,
                    data JSON
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT,
                    status TEXT,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    output TEXT,
                    error TEXT,
                    artifacts JSON,
                    metrics JSON,
                    FOREIGN KEY (task_id) REFERENCES tasks(id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_dependencies (
                    task_id TEXT,
                    depends_on TEXT,
                    PRIMARY KEY (task_id, depends_on),
                    FOREIGN KEY (task_id) REFERENCES tasks(id),
                    FOREIGN KEY (depends_on) REFERENCES tasks(id)
                )
            """)
            
    def add_task(self, task: Task) -> None:
        """Agrega una nueva tarea"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO tasks 
                (id, title, description, priority, status, created_at, data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                task.id,
                task.title,
                task.description,
                task.priority.value,
                TaskStatus.PENDING.value,
                datetime.now(),
                json.dumps(asdict(task))
            ))
            
            # Agregar dependencias
            for dep in task.dependencies:
                conn.execute("""
                    INSERT OR IGNORE INTO task_dependencies (task_id, depends_on)
                    VALUES (?, ?)
                """, (task.id, dep))
                
    def get_pending_tasks(self) -> List[Task]:
        """Obtiene tareas pendientes ordenadas por prioridad"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT data FROM tasks 
                WHERE status = ? 
                ORDER BY priority ASC
            """, (TaskStatus.PENDING.value,))
            
            tasks = []
            for row in cursor:
                data = json.loads(row['data'])
                data['priority'] = TaskPriority(data['priority'])
                tasks.append(Task(**data))
                
            return tasks
            
    def save_result(self, result: TaskResult) -> None:
        """Guarda resultado de tarea"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO task_results 
                (task_id, status, started_at, completed_at, output, error, artifacts, metrics)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.task_id,
                result.status.value,
                result.started_at,
                result.completed_at,
                result.output,
                result.error,
                json.dumps(result.artifacts),
                json.dumps(result.metrics)
            ))
            
            # Actualizar estado de la tarea
            conn.execute("""
                UPDATE tasks SET status = ? WHERE id = ?
            """, (result.status.value, result.task_id))


class BatmanAIController:
    """Controlador principal del sistema Batman AI"""
    
    def __init__(self, config_path: str = "~/.batman/config.yaml"):
        self.config_path = Path(config_path).expanduser()
        self.config = self.load_config()
        self.db = TaskDatabase()
        self.logger = self.setup_logging()
        self.running = False
        self.current_tasks = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Obtener API key de variable de entorno o config
        self.api_key = os.getenv('CLAUDE_API_KEY') or self.config.get('claude_api_key')
        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY no configurada")
            
    def load_config(self) -> Dict:
        """Carga configuración desde archivo YAML"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        else:
            # Configuración por defecto
            default_config = {
                'work_hours': {
                    'start': '22:00',
                    'end': '06:00'
                },
                'max_concurrent_tasks': 3,
                'task_check_interval': 60,
                'report_email': None,
                'log_level': 'INFO'
            }
            
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(default_config, f)
                
            return default_config
            
    def setup_logging(self) -> logging.Logger:
        """Configura sistema de logging"""
        logger = logging.getLogger('batman_ai')
        logger.setLevel(self.config.get('log_level', 'INFO'))
        
        # Handler para archivo
        log_path = Path.home() / '.batman' / 'logs' / f"batman_{datetime.now():%Y%m%d}.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
        
    async def execute_command_task(self, task: Task) -> TaskResult:
        """Ejecuta una tarea de comando del sistema"""
        result = TaskResult(
            task_id=task.id,
            status=TaskStatus.IN_PROGRESS,
            started_at=datetime.now(),
            completed_at=None,
            output=None,
            error=None,
            artifacts=[],
            metrics={}
        )
        
        try:
            # Ejecutar comando con timeout
            process = await asyncio.create_subprocess_shell(
                task.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=task.timeout
                )
                
                result.output = stdout.decode() if stdout else ""
                result.error = stderr.decode() if stderr else ""
                
                if process.returncode == 0:
                    result.status = TaskStatus.COMPLETED
                else:
                    result.status = TaskStatus.FAILED
                    
            except asyncio.TimeoutError:
                process.kill()
                result.status = TaskStatus.FAILED
                result.error = f"Timeout after {task.timeout} seconds"
                
        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error = str(e)
            
        result.completed_at = datetime.now()
        result.metrics['duration'] = (result.completed_at - result.started_at).total_seconds()
        
        return result
        
    async def execute_ai_task(self, task: Task) -> TaskResult:
        """Ejecuta una tarea usando Claude API"""
        result = TaskResult(
            task_id=task.id,
            status=TaskStatus.IN_PROGRESS,
            started_at=datetime.now(),
            completed_at=None,
            output=None,
            error=None,
            artifacts=[],
            metrics={}
        )
        
        try:
            # Recopilar contexto si es necesario
            context = ""
            if task.context_needed:
                context_parts = []
                for context_item in task.context_needed:
                    if context_item.startswith('file:'):
                        file_path = context_item[5:]
                        if Path(file_path).exists():
                            with open(file_path) as f:
                                context_parts.append(f"Content of {file_path}:\n{f.read()}")
                    elif context_item.startswith('cmd:'):
                        cmd = context_item[4:]
                        try:
                            output = subprocess.check_output(cmd, shell=True, text=True)
                            context_parts.append(f"Output of '{cmd}':\n{output}")
                        except:
                            pass
                            
                context = "\n\n".join(context_parts)
                
            # Ejecutar con Claude
            async with ClaudeAPIClient(self.api_key) as client:
                response = await client.execute_task_prompt(task, context)
                result.output = response
                
                # Extraer artefactos (código, archivos, etc)
                artifacts = self.extract_artifacts(response)
                result.artifacts = artifacts
                
                result.status = TaskStatus.COMPLETED
                
        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error = str(e)
            self.logger.error(f"Error en tarea AI {task.id}: {e}")
            
        result.completed_at = datetime.now()
        result.metrics['duration'] = (result.completed_at - result.started_at).total_seconds()
        
        return result
        
    def extract_artifacts(self, response: str) -> List[Dict]:
        """Extrae artefactos (código, archivos) de la respuesta"""
        artifacts = []
        
        # Buscar bloques de código
        import re
        code_pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(code_pattern, response, re.DOTALL)
        
        for i, (lang, code) in enumerate(matches):
            artifacts.append({
                'type': 'code',
                'language': lang or 'text',
                'content': code.strip(),
                'index': i
            })
            
        # Buscar referencias a archivos creados/modificados
        file_pattern = r'(?:created|modified|wrote|saved)\s+(?:file\s+)?[`\'"]([^`\'"]+)[`\'"]'
        file_matches = re.findall(file_pattern, response, re.IGNORECASE)
        
        for file_path in file_matches:
            artifacts.append({
                'type': 'file_reference',
                'path': file_path
            })
            
        return artifacts
        
    async def execute_task(self, task: Task) -> TaskResult:
        """Ejecuta una tarea según su tipo"""
        self.logger.info(f"Ejecutando tarea: {task.title}")
        
        if task.command:
            # Es una tarea de comando
            return await self.execute_command_task(task)
        else:
            # Es una tarea de AI
            return await self.execute_ai_task(task)
            
    async def check_dependencies(self, task: Task) -> bool:
        """Verifica si las dependencias de una tarea están completas"""
        if not task.dependencies:
            return True
            
        with sqlite3.connect(self.db.db_path) as conn:
            placeholders = ','.join('?' * len(task.dependencies))
            cursor = conn.execute(f"""
                SELECT id, status FROM tasks 
                WHERE id IN ({placeholders})
            """, task.dependencies)
            
            for row in cursor:
                if row[1] != TaskStatus.COMPLETED.value:
                    return False
                    
        return True
        
    async def run_task_loop(self):
        """Loop principal de ejecución de tareas"""
        while self.running:
            try:
                # Obtener tareas pendientes
                pending_tasks = self.db.get_pending_tasks()
                
                # Filtrar por dependencias
                ready_tasks = []
                for task in pending_tasks:
                    if await self.check_dependencies(task):
                        ready_tasks.append(task)
                        
                # Ejecutar tareas hasta el límite de concurrencia
                current_count = len(self.current_tasks)
                max_concurrent = self.config.get('max_concurrent_tasks', 3)
                
                for task in ready_tasks[:max_concurrent - current_count]:
                    if task.id not in self.current_tasks:
                        # Ejecutar tarea en background
                        task_future = asyncio.create_task(self.execute_task(task))
                        self.current_tasks[task.id] = task_future
                        
                        # Callback para cuando termine
                        task_future.add_done_callback(
                            lambda f, tid=task.id: self.task_completed(tid, f)
                        )
                        
                # Esperar antes de siguiente check
                await asyncio.sleep(self.config.get('task_check_interval', 60))
                
            except Exception as e:
                self.logger.error(f"Error en loop de tareas: {e}")
                await asyncio.sleep(60)
                
    def task_completed(self, task_id: str, future: asyncio.Future):
        """Callback cuando una tarea se completa"""
        try:
            result = future.result()
            self.db.save_result(result)
            self.logger.info(f"Tarea completada: {task_id} - Status: {result.status.value}")
        except Exception as e:
            self.logger.error(f"Error procesando resultado de tarea {task_id}: {e}")
        finally:
            self.current_tasks.pop(task_id, None)
            
    def generate_morning_report(self) -> str:
        """Genera reporte matutino de actividades"""
        report_date = datetime.now().date()
        
        with sqlite3.connect(self.db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Obtener resultados de la noche
            cursor = conn.execute("""
                SELECT tr.*, t.title, t.priority
                FROM task_results tr
                JOIN tasks t ON tr.task_id = t.id
                WHERE DATE(tr.started_at) = ?
                ORDER BY tr.started_at
            """, (report_date,))
            
            results = []
            for row in cursor:
                results.append(dict(row))
                
        # Generar reporte
        report = f"""# Batman AI Morning Report - {report_date}

## Summary
- Total tasks executed: {len(results)}
- Successful: {sum(1 for r in results if r['status'] == 'completed')}
- Failed: {sum(1 for r in results if r['status'] == 'failed')}

## Task Details
"""
        
        for result in results:
            status_icon = "✅" if result['status'] == 'completed' else "❌"
            report += f"\n### {status_icon} {result['title']}\n"
            report += f"- Started: {result['started_at']}\n"
            report += f"- Completed: {result['completed_at']}\n"
            report += f"- Duration: {result.get('metrics', {}).get('duration', 'N/A')}s\n"
            
            if result['error']:
                report += f"- Error: {result['error']}\n"
                
            if result['artifacts']:
                artifacts = json.loads(result['artifacts'])
                report += f"- Artifacts: {len(artifacts)} items\n"
                
        return report
        
    async def start(self):
        """Inicia el controlador Batman AI"""
        self.logger.info("🦇 Batman AI Controller iniciando...")
        self.running = True
        
        # Configurar manejo de señales
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Iniciar loop de tareas
        await self.run_task_loop()
        
    def signal_handler(self, signum, frame):
        """Maneja señales de sistema para shutdown graceful"""
        self.logger.info("Señal recibida, deteniendo...")
        self.running = False
        
    def load_tasks_from_file(self, file_path: str):
        """Carga tareas desde archivo YAML"""
        with open(file_path) as f:
            tasks_data = yaml.safe_load(f)
            
        for task_data in tasks_data.get('tasks', []):
            # Convertir a objeto Task
            task_data['priority'] = TaskPriority[task_data.get('priority', 'MEDIUM').upper()]
            task = Task(**task_data)
            
            # Agregar a base de datos
            self.db.add_task(task)
            
        self.logger.info(f"Cargadas {len(tasks_data.get('tasks', []))} tareas desde {file_path}")


# CLI para interactuar con Batman AI
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Batman AI Controller')
    parser.add_argument('command', choices=['start', 'add-tasks', 'status', 'report'])
    parser.add_argument('--task-file', help='Archivo YAML con tareas')
    parser.add_argument('--daemon', action='store_true', help='Ejecutar como daemon')
    
    args = parser.parse_args()
    
    controller = BatmanAIController()
    
    if args.command == 'start':
        # Iniciar controlador
        asyncio.run(controller.start())
        
    elif args.command == 'add-tasks':
        if not args.task_file:
            print("Error: --task-file requerido")
            sys.exit(1)
        controller.load_tasks_from_file(args.task_file)
        
    elif args.command == 'status':
        # Mostrar estado actual
        pending = controller.db.get_pending_tasks()
        print(f"Tareas pendientes: {len(pending)}")
        for task in pending[:5]:
            print(f"  - {task.title} (Priority: {task.priority.name})")
            
    elif args.command == 'report':
        # Generar reporte
        report = controller.generate_morning_report()
        print(report)


if __name__ == "__main__":
    main()