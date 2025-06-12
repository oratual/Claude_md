#!/usr/bin/env python3
"""
THE MONITOR SYSTEM - Automated Worktree Parallelization
Combina la arquitectura de Claude Squad con automatización total
"""

import os
import subprocess
import json
import time
import shutil
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

class MonitorAutomatedWorktrees:
    """
    Sistema de paralelización usando Git worktrees automatizados.
    Cada agente trabaja en su propio directorio físico sin conflictos.
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).absolute()
        self.monitor_dir = self.project_root / ".monitor"
        self.worktrees_dir = self.monitor_dir / "worktrees"
        self.logs_dir = self.monitor_dir / "logs"
        self.config_file = self.monitor_dir / "config.json"
        
        # Crear directorios necesarios
        self.worktrees_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Estado del sistema
        self.active_agents = {}
        self.completed_tasks = []
        
    def setup_worktree(self, agent_id: str, task_description: str) -> Dict[str, str]:
        """
        Crea un worktree para un agente específico
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        branch_name = f"monitor/{agent_id}-{timestamp}"
        worktree_path = self.worktrees_dir / f"agent-{agent_id}"
        
        # Remover worktree anterior si existe
        if worktree_path.exists():
            self._cleanup_worktree(str(worktree_path))
        
        # Crear nueva branch desde main/master
        base_branch = self._get_main_branch()
        subprocess.run([
            "git", "branch", branch_name, base_branch
        ], check=True)
        
        # Crear worktree
        subprocess.run([
            "git", "worktree", "add", 
            str(worktree_path), branch_name
        ], check=True)
        
        # Guardar metadata
        metadata = {
            "agent_id": agent_id,
            "branch": branch_name,
            "worktree_path": str(worktree_path),
            "task": task_description,
            "created_at": timestamp,
            "status": "active"
        }
        
        self.active_agents[agent_id] = metadata
        self._save_state()
        
        return metadata
    
    def spawn_agent_task(self, agent_id: str, task: str, worktree_path: str) -> Dict[str, Any]:
        """
        Crea la configuración para que un agente Task trabaje en su worktree
        """
        return {
            "agent_id": agent_id,
            "prompt": f"""
You are Agent {agent_id} working on an isolated Git worktree.

CONTEXT:
- Working Directory: {worktree_path}
- You have your own Git branch
- No other agents can modify your files
- You can work freely without coordination

TASK: {task}

IMPORTANT INSTRUCTIONS:
1. Change to your worktree directory first
2. Complete the assigned task
3. Commit your changes with descriptive messages
4. Use 'git add -A && git commit -m "..."' when ready
5. OPTIONAL: Push to GitHub for backup: 'git push -u origin <branch>'

Your work is completely isolated. Focus on quality over speed.

NOTE: After merge, your local branch will be deleted but preserved on GitHub if pushed.
""",
            "working_directory": worktree_path
        }
    
    def execute_parallel_tasks(self, tasks: Dict[str, str], max_agents: int = 5):
        """
        Ejecuta múltiples tareas en paralelo usando worktrees
        
        Args:
            tasks: Dict mapping agent_id to task description
            max_agents: Maximum number of parallel agents
        """
        # Limitar número de agentes
        if len(tasks) > max_agents:
            print(f"Warning: Limiting to {max_agents} agents")
            tasks = dict(list(tasks.items())[:max_agents])
        
        # Setup phase: Crear worktrees
        print("🚀 Setting up worktrees...")
        worktree_configs = {}
        for agent_id, task in tasks.items():
            config = self.setup_worktree(agent_id, task)
            worktree_configs[agent_id] = config
            print(f"  ✓ Agent {agent_id}: {config['worktree_path']}")
        
        # Execute phase: Spawn agents
        print("\n🤖 Spawning parallel agents...")
        agent_tasks = []
        for agent_id, task in tasks.items():
            config = worktree_configs[agent_id]
            agent_task = self.spawn_agent_task(
                agent_id, 
                task, 
                config['worktree_path']
            )
            agent_tasks.append(agent_task)
            print(f"  ✓ Agent {agent_id} started: {task[:50]}...")
        
        # Monitor phase
        print("\n📊 Monitoring progress...")
        self._monitor_agents(agent_tasks)
        
        # Merge phase
        print("\n🔀 Merging results...")
        merge_result = self.automated_merge(worktree_configs)
        
        return merge_result
    
    def _monitor_agents(self, agent_tasks: List[Dict]):
        """
        Monitorea el progreso de los agentes (simplificado para el ejemplo)
        """
        # En la implementación real, aquí se usaría Task.wait_all()
        # Por ahora, simulamos monitoreo
        
        while True:
            all_complete = True
            status_lines = []
            
            for task in agent_tasks:
                agent_id = task['agent_id']
                worktree = self.active_agents[agent_id]['worktree_path']
                
                # Check git status
                result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=worktree,
                    capture_output=True,
                    text=True
                )
                
                # Check for commits
                commits = subprocess.run(
                    ["git", "log", "--oneline", "-n", "1", "--pretty=format:%h %s"],
                    cwd=worktree,
                    capture_output=True,
                    text=True
                )
                
                status = "working" if result.stdout else "idle"
                status_lines.append(f"  Agent {agent_id}: {status} | {commits.stdout[:50]}")
                
                # Simulación: considerar completo si hay commits
                if not commits.stdout:
                    all_complete = False
            
            # Display status
            print("\r" + "\n".join(status_lines), end="")
            
            if all_complete:
                break
            
            time.sleep(5)
    
    def automated_merge(self, worktree_configs: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Merge automatizado de todas las branches
        """
        results = {
            "successful_merges": [],
            "conflicts": [],
            "strategy_used": "sequential"
        }
        
        # Volver a la branch principal
        os.chdir(self.project_root)
        main_branch = self._get_main_branch()
        subprocess.run(["git", "checkout", main_branch], check=True)
        
        # Merge secuencial (más seguro)
        for agent_id, config in worktree_configs.items():
            branch = config['branch']
            task = config['task']
            
            try:
                # Intentar merge
                result = subprocess.run(
                    ["git", "merge", "--no-ff", branch, 
                     "-m", f"Monitor: Merge {agent_id} - {task[:50]}"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    results["successful_merges"].append({
                        "agent_id": agent_id,
                        "branch": branch,
                        "task": task
                    })
                    print(f"✓ Merged {agent_id} successfully")
                    
                    # Eliminar branch local (se preserva en GitHub si fue pusheada)
                    self._delete_merged_branch(branch)
                else:
                    # Manejar conflictos
                    self._handle_merge_conflict(agent_id, branch)
                    results["conflicts"].append({
                        "agent_id": agent_id,
                        "branch": branch,
                        "resolution": "auto-resolved"
                    })
                    
            except Exception as e:
                print(f"✗ Error merging {agent_id}: {e}")
                results["conflicts"].append({
                    "agent_id": agent_id,
                    "branch": branch,
                    "error": str(e)
                })
        
        # Cleanup worktrees
        self._cleanup_all_worktrees()
        
        return results
    
    def _delete_merged_branch(self, branch: str):
        """
        Elimina branch local después del merge.
        Si fue pusheada a GitHub, se preserva allí.
        """
        try:
            # Verificar si la branch fue pusheada
            remote_exists = subprocess.run(
                ["git", "ls-remote", "--heads", "origin", branch],
                capture_output=True,
                text=True
            )
            
            if remote_exists.stdout:
                print(f"  → Branch {branch} preserved on GitHub")
            
            # Eliminar branch local
            subprocess.run(
                ["git", "branch", "-d", branch],
                capture_output=True,
                check=True
            )
            print(f"  → Local branch {branch} deleted")
            
        except subprocess.CalledProcessError:
            # Si falla con -d (no completamente mergeada), intentar con -D
            try:
                subprocess.run(
                    ["git", "branch", "-D", branch],
                    capture_output=True,
                    check=True
                )
                print(f"  → Force deleted local branch {branch}")
            except:
                print(f"  → Could not delete branch {branch}")
    
    def _handle_merge_conflict(self, agent_id: str, branch: str):
        """
        Estrategia simple de resolución de conflictos
        """
        # Por ahora, abortar y dejar para revisión manual
        subprocess.run(["git", "merge", "--abort"], check=True)
        print(f"⚠️  Conflict in {agent_id} - branch {branch} preserved for manual review")
    
    def _cleanup_worktree(self, worktree_path: str):
        """
        Limpia un worktree específico
        """
        try:
            subprocess.run(["git", "worktree", "remove", worktree_path, "--force"], 
                         capture_output=True)
        except:
            # Si falla, intentar limpieza manual
            if Path(worktree_path).exists():
                shutil.rmtree(worktree_path)
    
    def _cleanup_all_worktrees(self):
        """
        Limpia todos los worktrees activos
        """
        for agent_id, config in self.active_agents.items():
            self._cleanup_worktree(config['worktree_path'])
        
        # Limpiar referencias
        subprocess.run(["git", "worktree", "prune"], check=True)
        
        self.active_agents.clear()
        self._save_state()
    
    def _get_main_branch(self) -> str:
        """
        Detecta la branch principal (main o master)
        """
        result = subprocess.run(
            ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Extraer nombre de branch
            return result.stdout.strip().split('/')[-1]
        
        # Fallback
        return "main" if self._branch_exists("main") else "master"
    
    def _branch_exists(self, branch: str) -> bool:
        """
        Verifica si una branch existe
        """
        result = subprocess.run(
            ["git", "rev-parse", "--verify", branch],
            capture_output=True
        )
        return result.returncode == 0
    
    def _save_state(self):
        """
        Guarda el estado actual del sistema
        """
        state = {
            "active_agents": self.active_agents,
            "completed_tasks": self.completed_tasks,
            "last_updated": datetime.now().isoformat()
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del sistema
        """
        return {
            "active_agents": len(self.active_agents),
            "agents": self.active_agents,
            "worktrees": self._get_worktree_list()
        }
    
    def _get_worktree_list(self) -> List[str]:
        """
        Lista los worktrees actuales
        """
        result = subprocess.run(
            ["git", "worktree", "list"],
            capture_output=True,
            text=True
        )
        return result.stdout.strip().split('\n') if result.stdout else []


# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del Monitor
    monitor = MonitorAutomatedWorktrees()
    
    # Definir tareas paralelas
    tasks = {
        "auth": "Implement OAuth2 authentication with refresh tokens",
        "api": "Create REST API endpoints for user management", 
        "ui": "Build React components for user profile",
        "tests": "Write comprehensive unit tests for auth module",
        "docs": "Document the authentication flow and API"
    }
    
    # Ejecutar tareas en paralelo
    results = monitor.execute_parallel_tasks(tasks, max_agents=5)
    
    print("\n📋 Final Report:")
    print(f"  Successful merges: {len(results['successful_merges'])}")
    print(f"  Conflicts: {len(results['conflicts'])}")