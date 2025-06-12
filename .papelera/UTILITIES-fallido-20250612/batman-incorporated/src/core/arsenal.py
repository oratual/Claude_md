"""
Arsenal de herramientas avanzadas para Batman Incorporated.
Detecta y usa automáticamente las mejores herramientas disponibles.
"""

import shutil
import subprocess
from typing import List, Optional, Dict, Any
from pathlib import Path


class Arsenal:
    """
    Gestiona el arsenal de herramientas avanzadas.
    Prefiere herramientas modernas cuando están disponibles.
    """
    
    # Mapeo de herramientas preferidas
    TOOL_PREFERENCES = {
        'search': {
            'preferred': ['rg', 'ag', 'ack'],
            'fallback': 'grep'
        },
        'find': {
            'preferred': ['fd', 'fdfind'],
            'fallback': 'find'
        },
        'view': {
            'preferred': ['bat', 'batcat'],
            'fallback': 'cat'
        },
        'ls': {
            'preferred': ['exa', 'eza'],
            'fallback': 'ls'
        },
        'diff': {
            'preferred': ['delta', 'diff-so-fancy'],
            'fallback': 'diff'
        },
        'sed': {
            'preferred': ['sd'],
            'fallback': 'sed'
        },
        'ps': {
            'preferred': ['procs'],
            'fallback': 'ps'
        },
        'top': {
            'preferred': ['htop', 'btop'],
            'fallback': 'top'
        },
        'http': {
            'preferred': ['http', 'httpie', 'curl'],
            'fallback': 'wget'
        },
        'json': {
            'preferred': ['jq', 'jaq'],
            'fallback': None
        },
        'yaml': {
            'preferred': ['yq'],
            'fallback': None
        },
        'git': {
            'preferred': ['gh'],
            'fallback': 'git'
        }
    }
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.available_tools = self._detect_available_tools()
        
    def _detect_available_tools(self) -> Dict[str, str]:
        """Detecta qué herramientas están disponibles en el sistema."""
        available = {}
        
        for category, tools in self.TOOL_PREFERENCES.items():
            # Buscar herramienta preferida
            for tool in tools['preferred']:
                if shutil.which(tool):
                    available[category] = tool
                    break
            
            # Si no hay preferida, usar fallback
            if category not in available and tools['fallback']:
                if shutil.which(tools['fallback']):
                    available[category] = tools['fallback']
        
        return available
    
    def get_tool(self, category: str) -> Optional[str]:
        """Obtiene la mejor herramienta disponible para una categoría."""
        return self.available_tools.get(category)
    
    def search_text(self, pattern: str, path: str = ".", options: List[str] = None) -> subprocess.CompletedProcess:
        """Busca texto usando la mejor herramienta disponible."""
        tool = self.get_tool('search')
        
        if tool == 'rg':
            # ripgrep
            cmd = [tool, pattern, path]
            if options:
                cmd.extend(options)
            else:
                cmd.extend(['--color=never', '--no-heading'])
        elif tool == 'ag':
            # silver searcher
            cmd = [tool, pattern, path]
            if options:
                cmd.extend(options)
        else:
            # grep fallback
            cmd = ['grep', '-r', pattern, path]
            if options:
                cmd.extend(options)
        
        return subprocess.run(cmd, capture_output=True, text=True)
    
    def find_files(self, pattern: str, path: str = ".", options: List[str] = None) -> subprocess.CompletedProcess:
        """Busca archivos usando la mejor herramienta disponible."""
        tool = self.get_tool('find')
        
        if tool in ['fd', 'fdfind']:
            # fd
            cmd = [tool, pattern, path]
            if options:
                cmd.extend(options)
        else:
            # find fallback
            cmd = ['find', path, '-name', pattern]
            if options:
                cmd.extend(options)
        
        return subprocess.run(cmd, capture_output=True, text=True)
    
    def view_file(self, file_path: str, options: List[str] = None) -> subprocess.CompletedProcess:
        """Visualiza archivo con sintaxis highlighting si es posible."""
        tool = self.get_tool('view')
        
        if tool in ['bat', 'batcat']:
            cmd = [tool, file_path, '--style=plain']
            if options:
                cmd.extend(options)
        else:
            # cat fallback
            cmd = ['cat', file_path]
            if options:
                cmd.extend(options)
        
        return subprocess.run(cmd, capture_output=True, text=True)
    
    def list_directory(self, path: str = ".", options: List[str] = None) -> subprocess.CompletedProcess:
        """Lista directorio con información mejorada si es posible."""
        tool = self.get_tool('ls')
        
        if tool in ['exa', 'eza']:
            cmd = [tool, '-la', '--git', path]
            if options:
                cmd.extend(options)
        else:
            # ls fallback
            cmd = ['ls', '-la', path]
            if options:
                cmd.extend(options)
        
        return subprocess.run(cmd, capture_output=True, text=True)
    
    def replace_text(self, old: str, new: str, files: List[str], options: List[str] = None) -> bool:
        """Reemplaza texto usando la herramienta más segura."""
        tool = self.get_tool('sed')
        
        if tool == 'sd':
            # sd es más seguro y simple
            for file in files:
                cmd = [tool, old, new, file]
                if options:
                    cmd.extend(options)
                result = subprocess.run(cmd)
                if result.returncode != 0:
                    return False
            return True
        else:
            # sed fallback
            for file in files:
                cmd = ['sed', '-i', f's/{old}/{new}/g', file]
                if options:
                    cmd.extend(options)
                result = subprocess.run(cmd)
                if result.returncode != 0:
                    return False
            return True
    
    def process_json(self, input_data: str, query: str = ".") -> Optional[str]:
        """Procesa JSON con jq si está disponible."""
        tool = self.get_tool('json')
        
        if not tool:
            return None
        
        try:
            result = subprocess.run(
                [tool, query],
                input=input_data,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout
        except:
            pass
        
        return None
    
    def github_cli(self, args: List[str]) -> subprocess.CompletedProcess:
        """Ejecuta comandos de GitHub CLI si está disponible."""
        tool = self.get_tool('git')
        
        if tool == 'gh':
            cmd = [tool] + args
            return subprocess.run(cmd, capture_output=True, text=True)
        else:
            # Fallback a git
            return subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr="gh not available")
    
    def get_status_report(self) -> Dict[str, str]:
        """Genera reporte de herramientas disponibles."""
        report = {
            "available": {},
            "missing": []
        }
        
        for category, tool in self.available_tools.items():
            report["available"][category] = tool
        
        # Verificar herramientas faltantes
        for category, tools in self.TOOL_PREFERENCES.items():
            if category not in self.available_tools:
                report["missing"].extend(tools['preferred'])
        
        return report
    
    def get_best_tools_for_task(self, task) -> Dict[str, str]:
        """
        Determina las mejores herramientas para una tarea específica.
        
        Args:
            task: Objeto Task con información de la tarea
            
        Returns:
            Dict con tipo de herramienta -> comando
        """
        tools = {}
        
        # Analizar tipo de tarea y descripción
        task_lower = f"{task.title} {task.description}".lower()
        
        # Seleccionar herramientas según la tarea
        if any(word in task_lower for word in ['buscar', 'search', 'find', 'grep']):
            if tool := self.get_tool('search'):
                tools['search'] = tool
                
        if any(word in task_lower for word in ['archivo', 'file', 'encontrar']):
            if tool := self.get_tool('find'):
                tools['find'] = tool
                
        if any(word in task_lower for word in ['ver', 'view', 'mostrar', 'display']):
            if tool := self.get_tool('view'):
                tools['view'] = tool
                
        if any(word in task_lower for word in ['diff', 'diferencia', 'comparar']):
            if tool := self.get_tool('diff'):
                tools['diff'] = tool
                
        if any(word in task_lower for word in ['reemplazar', 'replace', 'cambiar']):
            if tool := self.get_tool('sed'):
                tools['sed'] = tool
                
        if any(word in task_lower for word in ['proceso', 'process', 'monitor']):
            if tool := self.get_tool('ps'):
                tools['ps'] = tool
                
        # Herramientas base siempre útiles
        if tool := self.get_tool('ls'):
            tools['ls'] = tool
            
        return tools
    
    def suggest_installations(self) -> List[str]:
        """Sugiere comandos para instalar herramientas faltantes."""
        suggestions = []
        missing = set()
        
        for category, tools in self.TOOL_PREFERENCES.items():
            if category not in self.available_tools:
                missing.update(tools['preferred'])
        
        if missing:
            # Herramientas que se pueden instalar con apt
            apt_tools = {'ripgrep', 'fd-find', 'bat', 'jq', 'htop'}
            apt_missing = missing.intersection(apt_tools)
            if apt_missing:
                suggestions.append(f"sudo apt install {' '.join(apt_missing)}")
            
            # Herramientas que necesitan otros métodos
            if 'gh' in missing:
                suggestions.append("# GitHub CLI: https://cli.github.com/")
            if 'sd' in missing:
                suggestions.append("cargo install sd")
            if 'procs' in missing:
                suggestions.append("cargo install procs")
            if 'exa' in missing or 'eza' in missing:
                suggestions.append("cargo install eza")
            if 'delta' in missing:
                suggestions.append("cargo install git-delta")
        
        return suggestions


# Singleton global para fácil acceso
_arsenal_instance = None

def get_arsenal(config: Optional[Dict] = None) -> Arsenal:
    """Obtiene la instancia global del Arsenal."""
    global _arsenal_instance
    if _arsenal_instance is None:
        _arsenal_instance = Arsenal(config)
    return _arsenal_instance