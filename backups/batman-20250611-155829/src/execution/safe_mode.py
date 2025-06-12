"""
Safe Mode - Ejecución con Git worktrees.
Cada agente trabaja en su propio worktree para evitar conflictos.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import tempfile
import shutil

from .base import ExecutionMode
from core.task import Task


class SafeMode(ExecutionMode):
    """
    Modo Seguro: Usa Git worktrees para aislar el trabajo de cada agente.
    Permite trabajo paralelo sin conflictos y merge controlado al final.
    """
    
    def __init__(self, config: Dict[str, Any], logger=None):
        super().__init__("Safe Mode", config, logger)
        self.worktrees: Dict[str, Path] = {}
        self.branches: Dict[str, str] = {}
        self.worktree_base = Path(self.config.get('worktree_base', '/tmp/batman-worktrees'))
        
    def prepare(self, tasks: List[Task]) -> bool:
        """Prepara worktrees para las tareas."""
        self._log("🛡️ Preparando modo SEGURO con Git worktrees")
        
        # Verificar que estamos en un repo git
        success, _, _ = self._run_command("git rev-parse --git-dir")
        if not success:
            self._log("❌ No estamos en un repositorio Git")
            return False
        
        # Crear directorio base para worktrees
        self.worktree_base.mkdir(parents=True, exist_ok=True)
        
        # Obtener branch actual
        success, current_branch, _ = self._run_command("git branch --show-current")
        if not success:
            self._log("❌ No se pudo obtener el branch actual")
            return False
        
        self.main_branch = current_branch.strip()
        
        # Crear un worktree para cada agente único
        agents = set(task.assigned_to for task in tasks if task.assigned_to)
        
        for agent in agents:
            if not self._create_worktree_for_agent(agent):
                self._log(f"❌ Error creando worktree para {agent}")
                return False
        
        self._log(f"✅ Creados {len(self.worktrees)} worktrees")
        return True
    
    def _create_worktree_for_agent(self, agent_name: str) -> bool:
        """Crea un worktree para un agente específico."""
        # Generar nombres únicos
        timestamp = Path(tempfile.mktemp()).name[-8:]
        branch_name = f"batman/{agent_name}-{timestamp}"
        worktree_path = self.worktree_base / f"{agent_name}-{timestamp}"
        
        # Crear branch y worktree
        self._log(f"  📁 Creando worktree para {agent_name}")
        
        # Crear nuevo branch basado en el actual
        success, _, error = self._run_command(
            f"git worktree add -b {branch_name} {worktree_path} HEAD"
        )
        
        if not success:
            self._log(f"    ❌ Error: {error}")
            return False
        
        self.worktrees[agent_name] = worktree_path
        self.branches[agent_name] = branch_name
        
        self._log(f"    ✅ Worktree creado en {worktree_path}")
        return True
    
    def execute(self, task: Task, agent: Any) -> bool:
        """Ejecuta una tarea en el worktree del agente."""
        agent_name = task.assigned_to or "batman"
        
        if agent_name not in self.worktrees:
            self._log(f"❌ No hay worktree para {agent_name}")
            return False
        
        # Cambiar el directorio de trabajo del agente
        original_dir = agent.working_dir
        agent.working_dir = self.worktrees[agent_name]
        
        self._log(f"🔧 Ejecutando en worktree: {agent.working_dir}")
        
        try:
            # Ejecutar la tarea
            success = agent.execute_task(task)
            
            if success:
                # Commit cambios en el worktree
                self._commit_changes(agent_name, task)
            
            return success
            
        finally:
            # Restaurar directorio original
            agent.working_dir = original_dir
    
    def _commit_changes(self, agent_name: str, task: Task):
        """Commit cambios en el worktree del agente."""
        worktree = self.worktrees[agent_name]
        
        # Add todos los cambios
        self._run_command("git add -A", cwd=worktree)
        
        # Verificar si hay cambios
        success, status, _ = self._run_command("git status --porcelain", cwd=worktree)
        
        if success and status.strip():
            # Hacer commit
            commit_msg = f"{agent_name}: {task.title}\n\nTask ID: {task.id}"
            self._run_command(f'git commit -m "{commit_msg}"', cwd=worktree)
            self._log(f"  💾 Commit realizado para {agent_name}")
    
    def cleanup(self) -> bool:
        """Limpia worktrees y hace merge de cambios."""
        self._log("🧹 Limpiando y haciendo merge de cambios")
        
        # Volver al branch principal
        self._run_command(f"git checkout {self.main_branch}")
        
        # Merge cada branch
        for agent_name, branch_name in self.branches.items():
            self._log(f"  🔀 Merging {branch_name}")
            
            # Intentar merge automático
            success, _, error = self._run_command(f"git merge --no-ff {branch_name}")
            
            if not success:
                self._log(f"    ⚠️ Conflicto en merge, requiere resolución manual")
                self._log(f"    Branch: {branch_name}")
                # No hacer cleanup del worktree si hay conflicto
                continue
            
            self._log(f"    ✅ Merge exitoso")
        
        # Limpiar worktrees exitosos
        for agent_name, worktree_path in self.worktrees.items():
            if worktree_path.exists():
                self._log(f"  🗑️ Eliminando worktree {agent_name}")
                
                # Eliminar worktree
                self._run_command(f"git worktree remove --force {worktree_path}")
                
                # Eliminar branch si se mergeó exitosamente
                branch = self.branches[agent_name]
                self._run_command(f"git branch -d {branch}")
        
        return True
    
    def can_parallelize(self) -> bool:
        """Safe mode soporta paralelización completa."""
        return True
    
    def max_parallel_tasks(self) -> int:
        """Limitado por recursos del sistema."""
        return self.config.get('max_parallel', 5)