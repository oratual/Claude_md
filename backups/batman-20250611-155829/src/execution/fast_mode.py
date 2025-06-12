"""
Fast Mode - Ejecución directa sin branches.
Rápido pero sin protección contra conflictos.
"""

from typing import List, Dict, Any
from pathlib import Path

from .base import ExecutionMode
from core.task import Task


class FastMode(ExecutionMode):
    """
    Modo Rápido: Ejecuta directamente en el directorio actual.
    Sin branches, sin worktrees, máxima velocidad.
    Ideal para tareas simples sin conflictos.
    """
    
    def __init__(self, config: Dict[str, Any], logger=None):
        super().__init__("Fast Mode", config, logger)
        self.completed_tasks = []
        
    def prepare(self, tasks: List[Task]) -> bool:
        """Preparación mínima para modo rápido."""
        self._log("⚡ Preparando modo RÁPIDO (sin branches)")
        
        # Verificar que no haya cambios sin commitear
        success, status, _ = self._run_command("git status --porcelain")
        
        if success and status.strip():
            self._log("⚠️ Hay cambios sin commitear en el repositorio")
            self._log("   Considera hacer commit antes de continuar")
        
        # Guardar estado actual
        self._run_command("git stash create")
        
        return True
    
    def execute(self, task: Task, agent: Any) -> bool:
        """Ejecuta directamente en el directorio actual."""
        self._log(f"⚡ Ejecutando directamente: {task.title}")
        
        # Ejecutar tarea
        success = agent.execute_task(task)
        
        if success:
            self.completed_tasks.append(task)
            
            # Auto-commit si está configurado
            if self.config.get('auto_commit', False):
                self._auto_commit(task, agent.name)
        
        return success
    
    def _auto_commit(self, task: Task, agent_name: str):
        """Hace commit automático de cambios."""
        # Add cambios
        self._run_command("git add -A")
        
        # Verificar si hay cambios
        success, status, _ = self._run_command("git status --porcelain")
        
        if success and status.strip():
            # Commit
            commit_msg = f"{agent_name}: {task.title} (fast mode)"
            self._run_command(f'git commit -m "{commit_msg}"')
            self._log(f"  💾 Auto-commit realizado")
    
    def cleanup(self) -> bool:
        """Limpieza mínima para modo rápido."""
        self._log("✅ Modo rápido completado")
        
        # Resumen de tareas
        self._log(f"  📊 Tareas completadas: {len(self.completed_tasks)}")
        
        # Si no hay auto-commit, recordar al usuario
        if not self.config.get('auto_commit', False):
            success, status, _ = self._run_command("git status --porcelain")
            if success and status.strip():
                self._log("  ⚠️ Hay cambios sin commitear")
                self._log("     Ejecuta: git add . && git commit")
        
        return True
    
    def can_parallelize(self) -> bool:
        """
        Fast mode NO soporta paralelización segura.
        Las tareas se ejecutan secuencialmente.
        """
        return False