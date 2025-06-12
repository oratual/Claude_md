"""
Clase base para todos los módulos temáticos de Batman Incorporated.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pathlib import Path
import yaml


class BaseModule(ABC):
    """
    Clase base para todos los módulos de Batman.
    
    Un módulo representa un conjunto de herramientas y capacidades
    específicas para un dominio particular (software, libros, música, etc.)
    """
    
    def __init__(self, module_path: str):
        self.path = Path(module_path)
        self.manifest = self._load_manifest()
        self.tools = {}
        self.templates = {}
        self._initialized = False
        
    def _load_manifest(self) -> Dict:
        """Carga el manifest.yaml del módulo"""
        manifest_path = self.path / "manifest.yaml"
        if not manifest_path.exists():
            raise FileNotFoundError(f"No manifest.yaml found in {self.path}")
            
        with open(manifest_path, 'r') as f:
            return yaml.safe_load(f)
    
    @property
    def name(self) -> str:
        """Nombre del módulo"""
        return self.manifest['name']
    
    @property
    def version(self) -> str:
        """Versión del módulo"""
        return self.manifest['version']
    
    @property
    def description(self) -> str:
        """Descripción del módulo"""
        return self.manifest['description']
    
    @property
    def capabilities(self) -> List[str]:
        """Lista de capacidades que provee el módulo"""
        return self.manifest.get('capabilities', [])
    
    @property
    def required_tools(self) -> Dict[str, List[str]]:
        """Herramientas externas requeridas por categoría"""
        return self.manifest.get('required_tools', {})
    
    @property
    def is_initialized(self) -> bool:
        """Indica si el módulo está inicializado"""
        return self._initialized
    
    def check_requirements(self) -> Dict[str, bool]:
        """
        Verifica que las herramientas requeridas estén disponibles.
        
        Returns:
            Dict con herramienta -> disponible
        """
        import shutil
        requirements_status = {}
        
        for category, tools in self.required_tools.items():
            for tool in tools:
                # Casos especiales para ejecutables Windows
                if tool.endswith('.exe'):
                    # En WSL2, los .exe de Windows están disponibles
                    requirements_status[tool] = shutil.which(tool) is not None
                else:
                    requirements_status[tool] = shutil.which(tool) is not None
                    
        return requirements_status
    
    def get_missing_requirements(self) -> List[str]:
        """Retorna lista de herramientas faltantes"""
        status = self.check_requirements()
        return [tool for tool, available in status.items() if not available]
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Inicializa el módulo y sus herramientas.
        Debe ser implementado por cada módulo específico.
        
        Returns:
            True si la inicialización fue exitosa
        """
        pass
    
    @abstractmethod
    def get_tool(self, tool_name: str) -> Any:
        """
        Obtiene una herramienta específica del módulo.
        
        Args:
            tool_name: Nombre de la herramienta
            
        Returns:
            Instancia de la herramienta o None si no existe
        """
        pass
    
    @abstractmethod
    def get_agent_enhancements(self) -> Dict[str, Dict]:
        """
        Retorna mejoras específicas para cada agente de Batman.
        
        Returns:
            Dict con estructura:
            {
                'agent_name': {
                    'extra_prompt': str,  # Texto adicional para el prompt
                    'tools': List[str],   # Herramientas disponibles
                    'templates': List[str] # Templates disponibles
                }
            }
        """
        pass
    
    def get_template(self, template_name: str) -> Optional[str]:
        """
        Obtiene un template específico.
        
        Args:
            template_name: Nombre del template
            
        Returns:
            Contenido del template o None si no existe
        """
        return self.templates.get(template_name)
    
    def list_tools(self) -> List[str]:
        """Lista todas las herramientas disponibles en el módulo"""
        return list(self.tools.keys())
    
    def list_templates(self) -> List[str]:
        """Lista todos los templates disponibles en el módulo"""
        return list(self.templates.keys())
    
    def get_capabilities_for_task(self, task_description: str) -> List[str]:
        """
        Determina qué capacidades del módulo son relevantes para una tarea.
        
        Args:
            task_description: Descripción de la tarea
            
        Returns:
            Lista de capacidades relevantes
        """
        relevant = []
        task_lower = task_description.lower()
        
        # Mapeo simple de keywords a capacidades
        capability_keywords = {
            'windows_interop': ['windows', 'powershell', 'cmd', 'exe'],
            'cross_compilation': ['compilar', 'build', 'compile'],
            'hybrid_development': ['híbrido', 'hybrid', 'cross-platform'],
            'automated_testing': ['test', 'prueba', 'testing'],
            'ci_cd_pipeline': ['ci', 'cd', 'pipeline', 'deploy'],
            'office_automation': ['excel', 'word', 'office', 'powerpoint'],
            'deployment': ['deploy', 'desplegar', 'publicar']
        }
        
        for capability in self.capabilities:
            if capability in capability_keywords:
                if any(keyword in task_lower for keyword in capability_keywords[capability]):
                    relevant.append(capability)
                    
        return relevant
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.name}' v{self.version}>"