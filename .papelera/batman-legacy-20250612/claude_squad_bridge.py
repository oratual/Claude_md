#!/usr/bin/env python3
"""
Claude Squad Bridge - Integración con Claude Squad para Batman
Permite controlar sesiones de Claude Squad programáticamente
"""

import subprocess
import json
import time
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime

class ClaudeSquadBridge:
    def __init__(self, squad_dir: str = None):
        """Inicializa el bridge con Claude Squad"""
        self.squad_dir = Path(squad_dir or Path.home() / ".claude-squad")
        self.state_file = self.squad_dir / "state.json"
        self.logger = logging.getLogger(__name__)
        
    def get_active_sessions(self) -> List[Dict]:
        """Obtiene lista de sesiones activas de Claude Squad"""
        if not self.state_file.exists():
            return []
            
        with open(self.state_file, 'r') as f:
            state = json.load(f)
            
        active = []
        for instance in state.get('instances', []):
            if instance.get('state') == 'running':
                active.append({
                    'id': instance.get('id'),
                    'title': instance.get('title'),
                    'branch': instance.get('branch'),
                    'path': instance.get('path'),
                    'program': instance.get('program', 'aider'),
                    'started': instance.get('startedAt')
                })
        return active
        
    def send_to_tmux_pane(self, session_name: str, command: str) -> bool:
        """Envía comando a un pane de tmux específico"""
        try:
            # Primero verificar que la sesión existe
            check_cmd = ['tmux', 'has-session', '-t', session_name]
            result = subprocess.run(check_cmd, capture_output=True)
            if result.returncode != 0:
                self.logger.error(f"Sesión tmux '{session_name}' no encontrada")
                return False
                
            # Enviar comando
            send_cmd = ['tmux', 'send-keys', '-t', f'{session_name}:0.0', command, 'Enter']
            result = subprocess.run(send_cmd, capture_output=True)
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Error enviando comando a tmux: {e}")
            return False
            
    def capture_tmux_output(self, session_name: str, lines: int = 100) -> str:
        """Captura el output reciente de un pane de tmux"""
        try:
            cmd = ['tmux', 'capture-pane', '-t', f'{session_name}:0.0', '-p', '-S', f'-{lines}']
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout
            return ""
        except Exception as e:
            self.logger.error(f"Error capturando output de tmux: {e}")
            return ""
            
    def wait_for_prompt(self, session_name: str, timeout: int = 60) -> bool:
        """Espera hasta que aparezca un prompt indicando que está listo"""
        start_time = time.time()
        last_output = ""
        
        # Patrones que indican que está listo para recibir comandos
        ready_patterns = [
            r'^\s*>',  # Prompt de Aider
            r'Human:',  # Prompt de Claude
            r'Assistant:',  # Respuesta completa
            r'^\s*$',  # Línea vacía después de output
            r'Commands:',  # Menú de comandos
        ]
        
        while time.time() - start_time < timeout:
            output = self.capture_tmux_output(session_name, 20)
            
            # Verificar si hay nuevo output
            if output != last_output:
                last_output = output
                
                # Buscar patrones de prompt
                lines = output.strip().split('\n')
                if lines:
                    last_lines = '\n'.join(lines[-5:])  # Últimas 5 líneas
                    for pattern in ready_patterns:
                        if re.search(pattern, last_lines, re.MULTILINE):
                            time.sleep(0.5)  # Pequeña pausa para asegurar
                            return True
                            
            time.sleep(1)
            
        return False
        
    def send_task_to_session(self, session_id: str, task: str) -> Tuple[bool, str]:
        """Envía una tarea a una sesión específica y captura el resultado"""
        session_name = f"claude-squad-{session_id}"
        
        # Verificar que la sesión está activa
        sessions = self.get_active_sessions()
        if not any(s['id'] == session_id for s in sessions):
            return False, "Sesión no encontrada o no activa"
            
        # Esperar a que esté listo
        if not self.wait_for_prompt(session_name):
            return False, "Timeout esperando prompt"
            
        # Capturar output inicial
        initial_output = self.capture_tmux_output(session_name)
        
        # Enviar tarea
        if not self.send_to_tmux_pane(session_name, task):
            return False, "Error enviando comando"
            
        # Esperar respuesta completa
        time.sleep(5)  # Dar tiempo inicial para procesar
        if not self.wait_for_prompt(session_name, timeout=300):  # 5 min timeout
            return False, "Timeout esperando respuesta"
            
        # Capturar respuesta
        final_output = self.capture_tmux_output(session_name, 200)
        
        # Extraer solo la respuesta nueva
        response = self._extract_response(initial_output, final_output)
        
        return True, response
        
    def _extract_response(self, before: str, after: str) -> str:
        """Extrae la respuesta nueva comparando outputs"""
        # Encontrar dónde divergen los outputs
        before_lines = before.strip().split('\n')
        after_lines = after.strip().split('\n')
        
        # Encontrar primera línea diferente
        start_idx = 0
        for i, (b, a) in enumerate(zip(before_lines, after_lines)):
            if b != a:
                start_idx = i
                break
        else:
            start_idx = len(before_lines)
            
        # Extraer líneas nuevas
        new_lines = after_lines[start_idx:]
        
        return '\n'.join(new_lines)
        
    def create_new_session(self, title: str, path: str, branch: str = None) -> Optional[str]:
        """Crea una nueva sesión de Claude Squad programáticamente"""
        # Por ahora requiere interacción manual
        # TODO: Implementar creación automática
        self.logger.warning("Creación automática de sesiones no implementada aún")
        return None
        
    def extract_code_blocks(self, response: str) -> List[Dict[str, str]]:
        """Extrae bloques de código de la respuesta"""
        code_blocks = []
        
        # Patrón para bloques de código con lenguaje
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, response, re.DOTALL)
        
        for lang, code in matches:
            code_blocks.append({
                'language': lang or 'text',
                'code': code.strip()
            })
            
        return code_blocks
        
    def save_session_state(self, session_id: str, state: Dict) -> None:
        """Guarda estado adicional de la sesión para Batman"""
        batman_state_dir = Path.home() / ".batman" / "claude-squad-states"
        batman_state_dir.mkdir(parents=True, exist_ok=True)
        
        state_file = batman_state_dir / f"{session_id}.json"
        with open(state_file, 'w') as f:
            json.dump({
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'state': state
            }, f, indent=2)


class BatmanClaudeSquadIntegration:
    """Integración completa de Batman con Claude Squad"""
    
    def __init__(self):
        self.bridge = ClaudeSquadBridge()
        self.logger = logging.getLogger(__name__)
        self.task_history = []
        
    def process_task_file(self, task_file: Path) -> List[Dict]:
        """Procesa archivo de tareas para Claude Squad"""
        tasks = []
        
        with open(task_file, 'r') as f:
            content = f.read()
            
        # Parsear tareas (formato simplificado por ahora)
        task_blocks = content.split('\n\n')
        
        for block in task_blocks:
            if block.strip():
                lines = block.strip().split('\n')
                task = {
                    'title': lines[0].replace('TASK:', '').strip(),
                    'description': '\n'.join(lines[1:]),
                    'session_preference': None,  # Puede especificar sesión específica
                    'priority': 'medium'
                }
                
                # Buscar metadatos
                for line in lines:
                    if line.startswith('PRIORITY:'):
                        task['priority'] = line.split(':')[1].strip()
                    elif line.startswith('SESSION:'):
                        task['session_preference'] = line.split(':')[1].strip()
                        
                tasks.append(task)
                
        return tasks
        
    def execute_task(self, task: Dict, session: Dict) -> Dict:
        """Ejecuta una tarea en una sesión específica"""
        result = {
            'task': task['title'],
            'session': session['id'],
            'started': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        # Formatear prompt para Claude/Aider
        prompt = f"""
Task: {task['title']}

{task['description']}

Please complete this task and provide a summary of what was done.
"""
        
        # Enviar tarea
        success, response = self.bridge.send_task_to_session(session['id'], prompt)
        
        result['completed'] = datetime.now().isoformat()
        result['success'] = success
        result['response'] = response
        result['status'] = 'completed' if success else 'failed'
        
        # Extraer código si hay
        if success:
            code_blocks = self.bridge.extract_code_blocks(response)
            result['code_blocks'] = code_blocks
            
        # Guardar estado
        self.bridge.save_session_state(session['id'], result)
        
        return result
        
    def distribute_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """Distribuye tareas entre sesiones activas"""
        sessions = self.bridge.get_active_sessions()
        
        if not sessions:
            self.logger.error("No hay sesiones activas de Claude Squad")
            return []
            
        results = []
        
        # Distribuir round-robin por ahora
        for i, task in enumerate(tasks):
            session = sessions[i % len(sessions)]
            
            # Si la tarea tiene preferencia de sesión, intentar usarla
            if task.get('session_preference'):
                preferred = next((s for s in sessions if s['id'] == task['session_preference']), None)
                if preferred:
                    session = preferred
                    
            self.logger.info(f"Asignando tarea '{task['title']}' a sesión {session['id']}")
            
            result = self.execute_task(task, session)
            results.append(result)
            
            # Pausa entre tareas para no sobrecargar
            time.sleep(5)
            
        return results
        
    def generate_report(self, results: List[Dict]) -> str:
        """Genera reporte de ejecución"""
        report = f"""
# Batman Claude Squad Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Resumen
- Total tareas: {len(results)}
- Completadas: {sum(1 for r in results if r['status'] == 'completed')}
- Fallidas: {sum(1 for r in results if r['status'] == 'failed')}

## Detalle de Tareas
"""
        
        for result in results:
            status_icon = "✅" if result['status'] == 'completed' else "❌"
            report += f"\n### {status_icon} {result['task']}\n"
            report += f"- Sesión: {result['session']}\n"
            report += f"- Duración: {result['started']} - {result['completed']}\n"
            
            if result.get('code_blocks'):
                report += f"- Bloques de código generados: {len(result['code_blocks'])}\n"
                
            if not result['success']:
                report += f"- Error: {result['response']}\n"
                
        return report


if __name__ == "__main__":
    # Test básico
    logging.basicConfig(level=logging.INFO)
    
    print("🦇 Batman Claude Squad Bridge - Test")
    
    bridge = ClaudeSquadBridge()
    sessions = bridge.get_active_sessions()
    
    print(f"\nSesiones activas: {len(sessions)}")
    for session in sessions:
        print(f"  - {session['id']}: {session['title']} ({session['program']})")
        
    if sessions:
        print("\nProbando captura de output...")
        output = bridge.capture_tmux_output(f"claude-squad-{sessions[0]['id']}", 10)
        print(f"Últimas líneas:\n{output}")