"""
Infinity Mode - Coordinación de múltiples instancias reales de Claude Code.

En lugar de simular agentes, coordina instancias reales trabajando en paralelo,
compartiendo contexto via MCP Memory, TodoRead/TodoWrite y archivos compartidos.
"""

import json
import time
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from .base import ExecutionMode
from core.task import Task, TaskBatch


class InfinityMode(ExecutionMode):
    """
    Modo Infinity: Múltiples instancias reales de Claude Code trabajando juntas.
    
    Revoluciona la paralelización usando:
    - MCP Memory para conocimiento compartido
    - TodoRead/TodoWrite para coordinación de tareas
    - Archivos compartidos para estado en tiempo real
    - Sesiones JSONL para análisis posterior
    """
    
    def __init__(self, config: Dict[str, Any], logger=None):
        super().__init__("Infinity Mode", config, logger)
        self.shared_dir = Path.home() / '.batman' / 'infinity'
        self.shared_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = str(uuid.uuid4())
        self.instances = {}
        
    def prepare(self, tasks: List[Task]) -> bool:
        """Prepara el entorno para múltiples instancias."""
        self._log("🌌 Preparando Infinity Mode - Instancias reales en paralelo")
        
        # Crear estructura de directorios compartidos
        (self.shared_dir / 'context').mkdir(exist_ok=True)
        (self.shared_dir / 'status').mkdir(exist_ok=True)
        (self.shared_dir / 'results').mkdir(exist_ok=True)
        
        # Archivo de contexto principal
        self.context_file = self.shared_dir / 'context' / f'session_{self.session_id}.json'
        self.status_file = self.shared_dir / 'status' / f'session_{self.session_id}.json'
        
        # Inicializar contexto compartido
        initial_context = {
            'session_id': self.session_id,
            'started_at': datetime.now().isoformat(),
            'total_tasks': len(tasks),
            'mode': 'infinity',
            'shared_memory_hint': 'Usa #memoria para compartir descubrimientos importantes',
            'coordination': {
                'context_file': str(self.context_file),
                'status_file': str(self.status_file),
                'results_dir': str(self.shared_dir / 'results')
            }
        }
        
        self._write_json(self.context_file, initial_context)
        self._log(f"📁 Contexto compartido: {self.context_file}")
        
        # Agrupar tareas por agente
        self.agent_tasks = self._group_tasks_by_agent(tasks)
        
        return True
    
    def execute(self, batch: TaskBatch) -> Dict[str, Any]:
        """Coordina la ejecución en múltiples instancias."""
        self._log("🚀 Iniciando ejecución con instancias reales")
        
        # Generar instrucciones para cada agente
        instructions = self._generate_instance_instructions()
        
        # Opción 1: Lanzamiento automático (experimental)
        if self.config.get('auto_launch', False):
            self._auto_launch_instances(instructions)
        else:
            # Opción 2: Mostrar instrucciones manuales
            self._display_launch_instructions(instructions)
        
        # Monitorear progreso
        results = self._monitor_execution()
        
        return results
    
    def _generate_instance_instructions(self) -> Dict[str, Dict]:
        """Genera instrucciones específicas para cada instancia."""
        instructions = {}
        
        for agent_name, tasks in self.agent_tasks.items():
            instance_id = str(uuid.uuid4())[:8]
            
            # Crear archivo de instrucciones para el agente
            agent_file = self.shared_dir / 'context' / f'agent_{agent_name}_{instance_id}.md'
            
            agent_instructions = f"""# Instrucciones para {agent_name}

## Tu rol
Eres {agent_name}, parte del equipo Batman Incorporated.
{self._get_agent_personality(agent_name)}

## Sesión
- ID: {self.session_id}
- Instance ID: {instance_id}
- Modo: Infinity (trabajo paralelo con otros agentes)

## Tareas asignadas
{self._format_tasks(tasks)}

## Coordinación
1. **Contexto compartido**: Lee `{self.context_file}` para contexto general
2. **Estado**: Actualiza `{self.status_file}` con tu progreso
3. **Resultados**: Guarda en `{self.shared_dir / 'results' / agent_name}`
4. **Memoria**: Usa `#memoria [descubrimiento]` para compartir hallazgos importantes
5. **Tareas**: Usa TodoWrite para actualizar estado de tareas

## Comunicación con otros agentes
- Alfred está trabajando en: {self._get_agent_focus('alfred')}
- Robin está trabajando en: {self._get_agent_focus('robin')}
- Oracle está trabajando en: {self._get_agent_focus('oracle')}
- Batgirl está trabajando en: {self._get_agent_focus('batgirl')}
- Lucius está trabajando en: {self._get_agent_focus('lucius')}

## Workflow
1. Lee el contexto compartido
2. Revisa tus tareas asignadas
3. Antes de empezar, actualiza tu estado: "Trabajando en [tarea]"
4. Usa #memoria para compartir descubrimientos clave
5. Guarda resultados en tu directorio
6. Actualiza estado cuando termines

## Comando para empezar
```bash
# En tu terminal, después de abrir Claude Code:
cat {agent_file}
```

¡Buena suerte, {agent_name}! 🦇
"""
            
            agent_file.write_text(agent_instructions)
            
            instructions[agent_name] = {
                'instance_id': instance_id,
                'instruction_file': str(agent_file),
                'tasks_count': len(tasks),
                'launch_command': f'claude  # Luego: cat {agent_file}'
            }
            
            self.instances[agent_name] = {
                'id': instance_id,
                'status': 'pending',
                'started': None,
                'tasks': tasks
            }
        
        # Actualizar archivo de estado
        self._update_status()
        
        return instructions
    
    def _auto_launch_instances(self, instructions: Dict[str, Dict]):
        """Lanza instancias automáticamente usando terminales separadas."""
        import subprocess
        import threading
        
        self._log("🤖 Lanzando instancias automáticamente...")
        
        def launch_agent_terminal(agent_name: str, inst: Dict):
            """Lanza un agente en una terminal separada."""
            try:
                instruction_file = inst['instruction_file']
                instance_id = inst['instance_id']
                
                # Comando para nueva terminal con Claude
                if self._has_wezterm():
                    # Usar wezterm si está disponible (mejor para WSL)
                    cmd = [
                        'wezterm', 'cli', 'spawn',
                        '--new-window',
                        '--cwd', str(self.shared_dir),
                        'bash', '-c',
                        f'echo "🦇 Iniciando {agent_name}..." && sleep 2 && claude --print --dangerously-skip-permissions "$(cat {instruction_file})"'
                    ]
                elif self._has_tmux():
                    # Usar tmux como alternativa
                    cmd = [
                        'tmux', 'new-window',
                        '-n', f'batman-{agent_name}',
                        '-c', str(self.shared_dir),
                        f'bash -c "echo \\"🦇 Iniciando {agent_name}...\\" && sleep 2 && claude --print --dangerously-skip-permissions \\"$(cat {instruction_file})\\""'
                    ]
                else:
                    # Fallback: xterm o gnome-terminal
                    cmd = [
                        'gnome-terminal', '--',
                        'bash', '-c',
                        f'cd {self.shared_dir} && echo "🦇 Iniciando {agent_name}..." && sleep 2 && claude --print --dangerously-skip-permissions "$(cat {instruction_file})" && echo "Presiona Enter para cerrar..." && read'
                    ]
                
                # Log del lanzamiento
                log_file = self.shared_dir / 'logs' / f'{agent_name}_{instance_id}_launch.log'
                log_file.parent.mkdir(exist_ok=True)
                
                self._log(f"  🚀 Lanzando {agent_name} en nueva terminal...")
                
                # Ejecutar el lanzamiento
                with open(log_file, 'w') as log:
                    process = subprocess.Popen(
                        cmd,
                        stdout=log,
                        stderr=subprocess.STDOUT,
                        start_new_session=True
                    )
                    
                    # Actualizar información de la instancia
                    self.instances[agent_name].update({
                        'launcher_process': process,
                        'log_file': log_file,
                        'started_at': datetime.now().isoformat(),
                        'status': 'launched'
                    })
                    
                self._log(f"  ✅ {agent_name} lanzado en terminal separada")
                
            except Exception as e:
                self._log(f"  ❌ Error lanzando {agent_name}: {e}")
                self.instances[agent_name]['status'] = 'error'
                self.instances[agent_name]['error'] = str(e)
        
        # Lanzar todos los agentes
        threads = []
        for agent_name, inst in instructions.items():
            thread = threading.Thread(
                target=launch_agent_terminal,
                args=(agent_name, inst)
            )
            thread.start()
            threads.append(thread)
            time.sleep(3)  # Pausa entre lanzamientos para evitar conflicts
        
        # Esperar a que todos se lancen
        for thread in threads:
            thread.join(timeout=15)
        
        launched_count = sum(1 for inst in self.instances.values() if inst.get('status') == 'launched')
        self._log(f"\n✅ {launched_count}/{len(self.instances)} instancias lanzadas en terminales separadas")
        
        if launched_count < len(self.instances):
            self._log("⚠️ Algunas instancias no se pudieron lanzar automáticamente")
            self._log("💡 Usa las instrucciones manuales como respaldo")
    
    def _has_wezterm(self) -> bool:
        """Verifica si wezterm está disponible."""
        try:
            subprocess.run(['wezterm', '--version'], capture_output=True, check=True)
            return True
        except:
            return False
    
    def _has_tmux(self) -> bool:
        """Verifica si tmux está disponible y corriendo."""
        try:
            result = subprocess.run(['tmux', 'list-sessions'], capture_output=True)
            return result.returncode == 0
        except:
            return False
    
    def _display_launch_instructions(self, instructions: Dict[str, Dict]) -> None:
        """Muestra instrucciones claras para lanzar las instancias."""
        print("\n" + "="*60)
        print("🌌 INFINITY MODE - Instrucciones de lanzamiento")
        print("="*60)
        
        print("\n📋 Abre una terminal nueva para cada agente:\n")
        
        for i, (agent, info) in enumerate(instructions.items(), 1):
            print(f"Terminal {i} - {agent}:")
            print(f"  1. Abre nueva terminal")
            print(f"  2. Ejecuta: {info['launch_command']}")
            print(f"  3. El agente verá sus {info['tasks_count']} tareas")
            print()
        
        print("💡 Tips:")
        print("  - Usa tmux o terminales separadas")
        print("  - Los agentes compartirán contexto via MCP Memory")
        print("  - Monitorea progreso con: watch -n 2 batman --status")
        print("\n" + "="*60)
        
        # Guardar resumen
        summary_file = self.shared_dir / f'launch_summary_{self.session_id}.txt'
        summary_file.write_text(f"""Infinity Mode Session: {self.session_id}

Agentes activos:
{chr(10).join(f'- {agent}: {info["tasks_count"]} tareas' for agent, info in instructions.items())}

Archivos de contexto:
- Principal: {self.context_file}
- Estado: {self.status_file}
- Resultados: {self.shared_dir / 'results'}

Iniciado: {datetime.now()}
""")
    
    def _monitor_execution(self) -> Dict[str, Any]:
        """Monitorea el progreso de las instancias."""
        self._log("👁️ Monitoreando ejecución...")
        
        start_time = time.time()
        monitoring = True
        check_interval = 5  # segundos
        
        while monitoring:
            # Leer estado actualizado
            status = self._read_json(self.status_file)
            
            # Verificar progreso
            all_complete = True
            for agent, info in self.instances.items():
                agent_status = status.get('agents', {}).get(agent, {})
                
                # Si es lanzamiento automático, verificar proceso
                if 'process' in info:
                    process = info['process']
                    if process.poll() is None:
                        info['status'] = 'working'
                        all_complete = False
                    else:
                        info['status'] = 'completed'
                        if process.returncode != 0:
                            self._log(f"⚠️ {agent} terminó con código {process.returncode}")
                else:
                    # Modo manual - verificar por archivos de estado
                    if agent_status.get('status') == 'completed':
                        info['status'] = 'completed'
                    elif agent_status.get('status') == 'working':
                        info['status'] = 'working'
                        all_complete = False
                    else:
                        info['status'] = 'waiting'
                        all_complete = False
            
            # Mostrar progreso
            self._show_progress()
            
            if all_complete:
                monitoring = False
            else:
                time.sleep(check_interval)
            
            # Timeout después de 1 hora
            if time.time() - start_time > 3600:
                self._log("⏰ Timeout alcanzado (1 hora)")
                monitoring = False
        
        # Recopilar resultados
        return self._collect_results()
    
    def _collect_results(self) -> Dict[str, Any]:
        """Recopila los resultados de todas las instancias."""
        results = {
            'session_id': self.session_id,
            'mode': 'infinity',
            'agents': {}
        }
        
        results_dir = self.shared_dir / 'results'
        
        for agent in self.instances:
            agent_results_dir = results_dir / agent
            if agent_results_dir.exists():
                agent_results = []
                
                # Leer todos los archivos de resultados del agente
                for result_file in agent_results_dir.glob('*.json'):
                    try:
                        result_data = self._read_json(result_file)
                        agent_results.append(result_data)
                    except:
                        pass
                
                results['agents'][agent] = {
                    'tasks_completed': len(agent_results),
                    'results': agent_results
                }
        
        return results
    
    def _group_tasks_by_agent(self, tasks: List[Task]) -> Dict[str, List[Task]]:
        """Agrupa tareas por agente asignado."""
        grouped = {}
        
        for task in tasks:
            agent = task.assigned_to or 'alfred'  # Default a Alfred
            if agent not in grouped:
                grouped[agent] = []
            grouped[agent].append(task)
        
        return grouped
    
    def _get_agent_personality(self, agent: str) -> str:
        """Retorna la descripción de personalidad del agente."""
        personalities = {
            'alfred': "El mayordomo perfecto, experto en arquitectura y código limpio.",
            'robin': "Joven entusiasta, especialista en DevOps y automatización.",
            'oracle': "Genio de la seguridad, obsesionada con testing y calidad.",
            'batgirl': "Artista del frontend, crea interfaces hermosas y accesibles.",
            'lucius': "Inventor e innovador, siempre buscando nuevas tecnologías."
        }
        return personalities.get(agent, "Agente especializado del equipo.")
    
    def _get_agent_focus(self, agent: str) -> str:
        """Obtiene en qué está trabajando cada agente."""
        if agent in self.agent_tasks:
            tasks = self.agent_tasks[agent]
            if tasks:
                return tasks[0].description[:50] + "..."
        return "Sin tareas asignadas"
    
    def _format_tasks(self, tasks: List[Task]) -> str:
        """Formatea las tareas para mostrar."""
        if not tasks:
            return "No hay tareas asignadas"
        
        formatted = []
        for i, task in enumerate(tasks, 1):
            formatted.append(f"{i}. {task.description}")
            if task.context:
                formatted.append(f"   Contexto: {task.context}")
        
        return "\n".join(formatted)
    
    def _show_progress(self) -> None:
        """Muestra el progreso actual."""
        print("\r", end="")
        statuses = []
        for agent, info in self.instances.items():
            emoji = "✅" if info['status'] == 'completed' else "🔄" if info['status'] == 'working' else "⏳"
            statuses.append(f"{agent}:{emoji}")
        
        print(f"Progreso: {' | '.join(statuses)}", end="", flush=True)
    
    def _update_status(self) -> None:
        """Actualiza el archivo de estado."""
        status = {
            'session_id': self.session_id,
            'updated_at': datetime.now().isoformat(),
            'agents': {}
        }
        
        for agent, info in self.instances.items():
            status['agents'][agent] = {
                'id': info['id'],
                'status': info['status'],
                'tasks_count': len(info['tasks']),
                'started': info['started']
            }
        
        self._write_json(self.status_file, status)
    
    def _write_json(self, path: Path, data: Dict) -> None:
        """Escribe datos JSON a archivo."""
        path.write_text(json.dumps(data, indent=2))
    
    def _read_json(self, path: Path) -> Dict:
        """Lee datos JSON de archivo."""
        try:
            return json.loads(path.read_text())
        except:
            return {}
    
    def cleanup(self) -> None:
        """Limpieza post-ejecución."""
        self._log("🧹 Limpiando archivos temporales de Infinity Mode")
        
        # Archivar la sesión
        archive_dir = self.shared_dir / 'archive' / self.session_id
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Mover archivos de contexto al archivo
        for file in [self.context_file, self.status_file]:
            if file.exists():
                file.rename(archive_dir / file.name)
        
        self._log(f"📦 Sesión archivada en: {archive_dir}")