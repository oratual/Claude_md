"""
Cargador dinámico de módulos para Batman Incorporated.
"""

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Dict, Optional, List, Set
import yaml

from .base_module import BaseModule


class ModuleLoader:
    """
    Carga dinámica de módulos temáticos para Batman.
    
    Los módulos permiten extender las capacidades de Batman con
    herramientas especializadas según el tipo de tarea.
    """
    
    def __init__(self, modules_path: str = None):
        if modules_path is None:
            # Usar ruta relativa al archivo actual
            modules_path = Path(__file__).parent
        
        self.modules_path = Path(modules_path)
        self.loaded_modules: Dict[str, BaseModule] = {}
        self.available_modules: Set[str] = set()
        
        # Descubrir módulos disponibles al inicializar
        self._discover_modules()
        
    def _discover_modules(self):
        """Descubre todos los módulos disponibles"""
        self.available_modules.clear()
        
        for item in self.modules_path.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                manifest_path = item / "manifest.yaml"
                if manifest_path.exists():
                    self.available_modules.add(item.name)
                    
    def discover_modules(self) -> List[str]:
        """
        Retorna lista de módulos disponibles.
        
        Returns:
            Lista de nombres de módulos
        """
        return sorted(list(self.available_modules))
    
    def get_module_info(self, module_name: str) -> Optional[Dict]:
        """
        Obtiene información de un módulo sin cargarlo.
        
        Args:
            module_name: Nombre del módulo
            
        Returns:
            Dict con información del manifest o None
        """
        if module_name not in self.available_modules:
            return None
            
        manifest_path = self.modules_path / module_name / "manifest.yaml"
        
        try:
            with open(manifest_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error reading manifest for {module_name}: {e}")
            return None
    
    def load_module(self, module_name: str) -> Optional[BaseModule]:
        """
        Carga un módulo específico.
        
        Args:
            module_name: Nombre del módulo a cargar
            
        Returns:
            Instancia del módulo o None si hay error
        """
        # Si ya está cargado, retornarlo
        if module_name in self.loaded_modules:
            return self.loaded_modules[module_name]
            
        # Verificar que el módulo existe
        if module_name not in self.available_modules:
            print(f"Module '{module_name}' not found")
            return None
            
        module_path = self.modules_path / module_name
        
        try:
            # Importar el módulo dinámicamente
            module_init = module_path / "__init__.py"
            
            if module_init.exists():
                # Cargar como paquete Python
                spec = importlib.util.spec_from_file_location(
                    f"batman_modules.{module_name}",
                    module_init
                )
                
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[f"batman_modules.{module_name}"] = module
                    spec.loader.exec_module(module)
                    
                    # Buscar la clase del módulo
                    # Convención: SoftwareModule, BooksModule, etc.
                    class_name = f"{module_name.title().replace('_', '')}Module"
                    
                    if hasattr(module, class_name):
                        module_class = getattr(module, class_name)
                        instance = module_class(str(module_path))
                        
                        # Verificar requisitos antes de inicializar
                        missing = instance.get_missing_requirements()
                        if missing:
                            print(f"Warning: Module '{module_name}' missing requirements: {missing}")
                            
                        # Inicializar el módulo
                        if instance.initialize():
                            self.loaded_modules[module_name] = instance
                            print(f"Successfully loaded module: {module_name}")
                            return instance
                        else:
                            print(f"Failed to initialize module: {module_name}")
                    else:
                        print(f"Module class '{class_name}' not found in {module_name}")
            else:
                print(f"No __init__.py found in module: {module_name}")
                
        except Exception as e:
            print(f"Error loading module '{module_name}': {e}")
            import traceback
            traceback.print_exc()
            
        return None
    
    def unload_module(self, module_name: str) -> bool:
        """
        Descarga un módulo de memoria.
        
        Args:
            module_name: Nombre del módulo
            
        Returns:
            True si se descargó exitosamente
        """
        if module_name in self.loaded_modules:
            del self.loaded_modules[module_name]
            
            # Limpiar de sys.modules
            module_key = f"batman_modules.{module_name}"
            if module_key in sys.modules:
                del sys.modules[module_key]
                
            return True
        return False
    
    def get_module_for_task(self, task_description: str) -> Optional[BaseModule]:
        """
        Determina qué módulo usar basado en la descripción de la tarea.
        
        Args:
            task_description: Descripción de la tarea
            
        Returns:
            Módulo más apropiado o None
        """
        task_lower = task_description.lower()
        
        # Mapeo de keywords a módulos
        module_keywords = {
            'software': [
                'código', 'code', 'programa', 'software', 'app', 'aplicación',
                'compilar', 'build', 'deploy', 'test', 'api', 'backend', 'frontend',
                'bug', 'error', 'debug', 'git', 'github', 'windows', 'linux',
                'docker', 'kubernetes', 'ci/cd', 'pipeline'
            ],
            'books': [
                'libro', 'book', 'escribir', 'write', 'capítulo', 'chapter',
                'publicar', 'publish', 'epub', 'pdf', 'markdown', 'documento',
                'manual', 'guía', 'tutorial'
            ],
            'music': [
                'música', 'music', 'audio', 'sonido', 'sound', 'mezclar', 'mix',
                'masterizar', 'master', 'grabar', 'record', 'midi', 'mp3'
            ],
            'data': [
                'datos', 'data', 'análisis', 'analysis', 'estadística', 'statistics',
                'machine learning', 'ml', 'ai', 'visualización', 'gráfico', 'chart'
            ]
        }
        
        # Contar coincidencias para cada módulo
        scores = {}
        
        for module_name, keywords in module_keywords.items():
            if module_name in self.available_modules:
                score = sum(1 for keyword in keywords if keyword in task_lower)
                if score > 0:
                    scores[module_name] = score
        
        # Si no hay coincidencias, intentar con módulo 'software' por defecto
        if not scores and 'software' in self.available_modules:
            return self.load_module('software')
        
        # Cargar el módulo con mayor puntuación
        if scores:
            best_module = max(scores.items(), key=lambda x: x[1])[0]
            return self.load_module(best_module)
            
        return None
    
    def get_all_capabilities(self) -> Dict[str, List[str]]:
        """
        Obtiene todas las capacidades de todos los módulos cargados.
        
        Returns:
            Dict con módulo -> lista de capacidades
        """
        capabilities = {}
        
        for module_name, module in self.loaded_modules.items():
            capabilities[module_name] = module.capabilities
            
        return capabilities
    
    def reload_module(self, module_name: str) -> Optional[BaseModule]:
        """
        Recarga un módulo (útil durante desarrollo).
        
        Args:
            module_name: Nombre del módulo
            
        Returns:
            Instancia recargada o None
        """
        self.unload_module(module_name)
        return self.load_module(module_name)
    
    def get_loaded_modules(self) -> List[str]:
        """Retorna lista de módulos actualmente cargados"""
        return list(self.loaded_modules.keys())
    
    def get_module(self, module_name: str) -> Optional[BaseModule]:
        """
        Obtiene un módulo ya cargado.
        
        Args:
            module_name: Nombre del módulo
            
        Returns:
            Instancia del módulo o None
        """
        return self.loaded_modules.get(module_name)