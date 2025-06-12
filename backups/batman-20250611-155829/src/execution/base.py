"""
Base execution mode class for Batman Incorporated.
Define la interfaz común para todos los modos de ejecución.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path
import subprocess

from core.task import Task, TaskBatch
from features.chapter_logger import ChapterLogger


class ExecutionMode(ABC):
    """Clase base para todos los modos de ejecución."""
    
    def __init__(self, name: str, config: Dict[str, Any], logger: Optional[ChapterLogger] = None):
        """
        Inicializa un modo de ejecución.
        
        Args:
            name: Nombre del modo
            config: Configuración del modo
            logger: Logger para registrar actividades
        """
        self.name = name
        self.config = config
        self.logger = logger
        self.working_dir = Path.cwd()
        
    @abstractmethod
    def prepare(self, tasks: List[Task]) -> bool:
        """
        Prepara el entorno para ejecutar las tareas.
        
        Args:
            tasks: Lista de tareas a ejecutar
            
        Returns:
            True si la preparación fue exitosa
        """
        pass
    
    @abstractmethod
    def execute(self, task: Task, agent: Any) -> bool:
        """
        Ejecuta una tarea en este modo.
        
        Args:
            task: Tarea a ejecutar
            agent: Agente que ejecutará la tarea
            
        Returns:
            True si la ejecución fue exitosa
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """
        Limpia el entorno después de la ejecución.
        
        Returns:
            True si la limpieza fue exitosa
        """
        pass
    
    def can_parallelize(self) -> bool:
        """
        Indica si este modo soporta paralelización.
        
        Returns:
            True si soporta ejecución paralela
        """
        return False
    
    def max_parallel_tasks(self) -> int:
        """
        Número máximo de tareas paralelas soportadas.
        
        Returns:
            Número máximo de tareas paralelas
        """
        return 1
    
    def _log(self, message: str):
        """Helper para logging."""
        if self.logger:
            self.logger.log(f"[{self.name.upper()}] {message}")
        else:
            print(f"[{self.name.upper()}] {message}")
    
    def _run_command(self, command: str, cwd: Optional[Path] = None) -> tuple[bool, str, str]:
        """
        Ejecuta un comando del sistema.
        
        Args:
            command: Comando a ejecutar
            cwd: Directorio de trabajo (opcional)
            
        Returns:
            Tupla (success, stdout, stderr)
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(cwd or self.working_dir),
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos
            )
            
            return result.returncode == 0, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)