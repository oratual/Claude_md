"""
Gestión de variables de entorno para múltiples instancias de Batman.
Permite ejecutar instancias paralelas sin conflictos.
"""

import os
from pathlib import Path


class BatmanEnvironment:
    """Gestiona rutas y archivos según variables de entorno para aislamiento."""
    
    @staticmethod
    def get_log_dir() -> str:
        """Obtiene directorio de logs respetando BATMAN_LOG_DIR."""
        return os.environ.get(
            'BATMAN_LOG_DIR',
            os.path.expanduser('~/.glados/batman-incorporated/logs')
        )
    
    @staticmethod
    def get_temp_dir() -> str:
        """Obtiene directorio temporal respetando BATMAN_TEMP_DIR."""
        return os.environ.get('BATMAN_TEMP_DIR', '/tmp')
    
    @staticmethod
    def get_status_file() -> str:
        """Obtiene archivo de estado respetando BATMAN_STATUS_FILE."""
        return os.environ.get(
            'BATMAN_STATUS_FILE',
            os.path.join(BatmanEnvironment.get_temp_dir(), 'batman_status.json')
        )
    
    @staticmethod
    def get_monitor_log() -> str:
        """Obtiene archivo de log del monitor respetando BATMAN_MONITOR_LOG."""
        return os.environ.get(
            'BATMAN_MONITOR_LOG',
            os.path.join(BatmanEnvironment.get_temp_dir(), 'batman_monitor.log')
        )
    
    @staticmethod
    def get_monitor_pid() -> str:
        """Obtiene archivo PID del monitor respetando BATMAN_MONITOR_PID."""
        return os.environ.get(
            'BATMAN_MONITOR_PID',
            os.path.join(BatmanEnvironment.get_temp_dir(), 'batman_monitor.pid')
        )
    
    @staticmethod
    def get_worktree_base() -> str:
        """Obtiene directorio base para worktrees respetando BATMAN_WORKTREE_BASE."""
        return os.environ.get(
            'BATMAN_WORKTREE_BASE',
            os.path.join(BatmanEnvironment.get_temp_dir(), 'batman-worktrees')
        )
    
    @staticmethod
    def get_real_work_log() -> str:
        """Obtiene archivo de log de trabajo real respetando BATMAN_REAL_WORK_LOG."""
        return os.environ.get(
            'BATMAN_REAL_WORK_LOG',
            os.path.join(BatmanEnvironment.get_temp_dir(), 'batman_real_work.log')
        )
    
    @staticmethod
    def get_instance_id() -> str:
        """Obtiene ID de instancia si está definido."""
        return os.environ.get('BATMAN_INSTANCE_ID', 'default')
    
    @staticmethod
    def get_project_name() -> str:
        """Obtiene nombre del proyecto si está definido."""
        return os.environ.get('BATMAN_PROJECT', 'default')
    
    @staticmethod
    def is_isolated() -> bool:
        """Verifica si estamos ejecutando en modo aislado."""
        return bool(os.environ.get('BATMAN_ISOLATED')) or \
               bool(os.environ.get('BATMAN_INSTANCE_ID')) or \
               bool(os.environ.get('BATMAN_PROJECT'))
    
    @staticmethod
    def get_environment_info() -> dict:
        """Obtiene información del entorno actual."""
        return {
            'instance_id': BatmanEnvironment.get_instance_id(),
            'project': BatmanEnvironment.get_project_name(),
            'isolated': BatmanEnvironment.is_isolated(),
            'log_dir': BatmanEnvironment.get_log_dir(),
            'temp_dir': BatmanEnvironment.get_temp_dir(),
            'worktree_base': BatmanEnvironment.get_worktree_base()
        }
    
    @staticmethod
    def setup_directories():
        """Crea directorios necesarios si no existen."""
        dirs = [
            BatmanEnvironment.get_log_dir(),
            BatmanEnvironment.get_temp_dir(),
            BatmanEnvironment.get_worktree_base(),
            os.path.dirname(BatmanEnvironment.get_status_file()),
            os.path.dirname(BatmanEnvironment.get_monitor_log()),
            os.path.dirname(BatmanEnvironment.get_monitor_pid())
        ]
        
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)