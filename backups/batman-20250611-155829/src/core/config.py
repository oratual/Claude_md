"""
Sistema de configuración para Batman Incorporated.
Maneja configuración por defecto y personalizada.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
import copy


class Config:
    """Gestor de configuración para Batman Incorporated."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Inicializa la configuración.
        
        Args:
            config_path: Ruta al archivo de configuración personalizado
        """
        # Cargar configuración por defecto
        self.default_config_path = Path(__file__).parent.parent.parent / "config" / "default_config.yaml"
        self.config = self._load_default_config()
        
        # Cargar configuración del usuario si existe
        if config_path and config_path.exists():
            self._merge_user_config(config_path)
        else:
            # Intentar cargar desde ubicación estándar
            user_config = Path.home() / ".glados" / "batman-incorporated" / "config.yaml"
            if user_config.exists():
                self._merge_user_config(user_config)
        
        # Expandir variables
        self._expand_variables()
        
        # Crear directorios necesarios
        self._create_directories()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Carga la configuración por defecto."""
        with open(self.default_config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _merge_user_config(self, config_path: Path):
        """
        Mezcla la configuración del usuario con la por defecto.
        
        Args:
            config_path: Ruta al archivo de configuración del usuario
        """
        with open(config_path, 'r') as f:
            user_config = yaml.safe_load(f)
        
        if user_config:
            self._deep_merge(self.config, user_config)
    
    def _deep_merge(self, base: Dict, update: Dict):
        """
        Mezcla recursivamente dos diccionarios.
        
        Args:
            base: Diccionario base
            update: Diccionario con actualizaciones
        """
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _expand_variables(self):
        """Expande variables en la configuración (ej: ${paths.base})."""
        def expand_value(value: Any, context: Dict) -> Any:
            if isinstance(value, str):
                # Expandir ~ a home
                if value.startswith('~'):
                    value = os.path.expanduser(value)
                
                # Expandir variables ${...}
                while '${' in value:
                    start = value.find('${')
                    end = value.find('}', start)
                    if end == -1:
                        break
                    
                    var_path = value[start+2:end]
                    var_value = self._get_nested_value(var_path, context)
                    
                    if var_value is not None:
                        value = value[:start] + str(var_value) + value[end+1:]
                    else:
                        break
                
                return value
            elif isinstance(value, dict):
                return {k: expand_value(v, context) for k, v in value.items()}
            elif isinstance(value, list):
                return [expand_value(v, context) for v in value]
            else:
                return value
        
        self.config = expand_value(self.config, self.config)
    
    def _get_nested_value(self, path: str, data: Dict) -> Any:
        """
        Obtiene un valor anidado usando notación de puntos.
        
        Args:
            path: Ruta tipo "paths.base"
            data: Diccionario de datos
        
        Returns:
            Valor encontrado o None
        """
        keys = path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    def _create_directories(self):
        """Crea los directorios necesarios si no existen."""
        paths_to_create = [
            self.get('paths.base'),
            self.get('paths.logs'),
            self.get('paths.tasks'),
            self.get('paths.reports'),
            self.get('paths.cache'),
            self.get('paths.worktrees')
        ]
        
        for path_str in paths_to_create:
            if path_str:
                path = Path(path_str)
                path.mkdir(parents=True, exist_ok=True)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración.
        
        Args:
            key: Clave en notación de puntos (ej: "agents.alfred.enabled")
            default: Valor por defecto si no se encuentra
        
        Returns:
            Valor de configuración o default
        """
        value = self._get_nested_value(key, self.config)
        return value if value is not None else default
    
    def set(self, key: str, value: Any):
        """
        Establece un valor de configuración.
        
        Args:
            key: Clave en notación de puntos
            value: Valor a establecer
        """
        keys = key.split('.')
        current = self.config
        
        for i, k in enumerate(keys[:-1]):
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """
        Obtiene la configuración de un agente específico.
        
        Args:
            agent_name: Nombre del agente (alfred, robin, etc.)
        
        Returns:
            Configuración del agente
        """
        return self.get(f'agents.{agent_name}', {})
    
    def is_agent_enabled(self, agent_name: str) -> bool:
        """
        Verifica si un agente está habilitado.
        
        Args:
            agent_name: Nombre del agente
        
        Returns:
            True si está habilitado
        """
        return self.get(f'agents.{agent_name}.enabled', False)
    
    def get_execution_mode(self) -> str:
        """Obtiene el modo de ejecución actual."""
        return self.get('execution.default_mode', 'auto')
    
    def save(self, path: Optional[Path] = None):
        """
        Guarda la configuración actual.
        
        Args:
            path: Ruta donde guardar (por defecto la ubicación estándar)
        """
        if path is None:
            path = Path.home() / ".glados" / "batman-incorporated" / "config.yaml"
        
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Retorna la configuración como diccionario."""
        return copy.deepcopy(self.config)