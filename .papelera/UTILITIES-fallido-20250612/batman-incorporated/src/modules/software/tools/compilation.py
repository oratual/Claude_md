"""
Herramienta de compilación multiplataforma.
"""

from typing import Dict, List, Optional
from pathlib import Path
import json

from .windows_interop import WindowsInterop


class CrossCompiler:
    """
    Compilador multiplataforma que puede construir proyectos
    tanto en Linux como Windows desde WSL2.
    """
    
    def __init__(self, windows_interop: WindowsInterop):
        self.windows = windows_interop
        self.project_detectors = {
            'dotnet': self._detect_dotnet,
            'cargo': self._detect_cargo,
            'npm': self._detect_npm,
            'gradle': self._detect_gradle,
            'maven': self._detect_maven,
            'tauri': self._detect_tauri,
            'electron': self._detect_electron
        }
        
    def _detect_dotnet(self, project_path: Path) -> bool:
        """Detecta proyecto .NET"""
        return any(project_path.glob("*.csproj")) or \
               any(project_path.glob("*.sln")) or \
               any(project_path.glob("*.fsproj"))
    
    def _detect_cargo(self, project_path: Path) -> bool:
        """Detecta proyecto Rust/Cargo"""
        return (project_path / "Cargo.toml").exists()
    
    def _detect_npm(self, project_path: Path) -> bool:
        """Detecta proyecto Node.js/npm"""
        return (project_path / "package.json").exists()
    
    def _detect_gradle(self, project_path: Path) -> bool:
        """Detecta proyecto Gradle"""
        return (project_path / "build.gradle").exists() or \
               (project_path / "build.gradle.kts").exists()
    
    def _detect_maven(self, project_path: Path) -> bool:
        """Detecta proyecto Maven"""
        return (project_path / "pom.xml").exists()
    
    def _detect_tauri(self, project_path: Path) -> bool:
        """Detecta proyecto Tauri"""
        tauri_conf = project_path / "src-tauri" / "tauri.conf.json"
        return tauri_conf.exists()
    
    def _detect_electron(self, project_path: Path) -> bool:
        """Detecta proyecto Electron"""
        if (project_path / "package.json").exists():
            try:
                with open(project_path / "package.json") as f:
                    pkg = json.load(f)
                    return "electron" in pkg.get("devDependencies", {}) or \
                           "electron" in pkg.get("dependencies", {})
            except:
                pass
        return False
    
    def detect_project_type(self, project_path: str) -> Optional[str]:
        """
        Detecta automáticamente el tipo de proyecto.
        
        Args:
            project_path: Ruta al proyecto
            
        Returns:
            Tipo de proyecto o None
        """
        path = Path(project_path)
        
        for project_type, detector in self.project_detectors.items():
            if detector(path):
                return project_type
                
        return None
    
    def compile(self, project_path: str, 
               target_platform: str = "current",
               project_type: Optional[str] = None,
               config: Optional[Dict] = None) -> Dict:
        """
        Compila proyecto para la plataforma objetivo.
        
        Args:
            project_path: Ruta al proyecto
            target_platform: 'windows', 'linux', 'current', o 'both'
            project_type: Tipo de proyecto (auto-detectado si None)
            config: Configuración adicional
            
        Returns:
            Dict con resultados de compilación
        """
        # Auto-detectar tipo si no se especifica
        if not project_type:
            project_type = self.detect_project_type(project_path)
            if not project_type:
                return {
                    'success': False,
                    'error': 'Could not detect project type',
                    'platforms': {}
                }
        
        results = {'platforms': {}}
        
        # Compilar según plataforma objetivo
        if target_platform in ['linux', 'current', 'both']:
            results['platforms']['linux'] = self._compile_linux(
                project_path, project_type, config
            )
            
        if target_platform in ['windows', 'both']:
            results['platforms']['windows'] = self._compile_windows(
                project_path, project_type, config
            )
            
        # Determinar éxito general
        results['success'] = any(
            platform_result.get('success', False) 
            for platform_result in results['platforms'].values()
        )
        
        results['project_type'] = project_type
        return results
    
    def _compile_linux(self, project_path: str, 
                      project_type: str,
                      config: Optional[Dict]) -> Dict:
        """Compila para Linux nativo"""
        import subprocess
        
        commands = {
            'dotnet': ['dotnet', 'build', '-c', 'Release'],
            'cargo': ['cargo', 'build', '--release'],
            'npm': ['npm', 'run', 'build'],
            'gradle': ['./gradlew', 'build'],
            'maven': ['mvn', 'package'],
            'tauri': ['npm', 'run', 'tauri', 'build'],
            'electron': ['npm', 'run', 'build:linux']
        }
        
        if project_type not in commands:
            return {
                'success': False,
                'error': f'Unknown project type for Linux: {project_type}'
            }
            
        try:
            # Cambiar al directorio del proyecto
            import os
            original_dir = os.getcwd()
            os.chdir(project_path)
            
            # Ejecutar comando de compilación
            result = subprocess.run(
                commands[project_type],
                capture_output=True,
                text=True
            )
            
            os.chdir(original_dir)
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'command': ' '.join(commands[project_type])
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _compile_windows(self, project_path: str,
                        project_type: str,
                        config: Optional[Dict]) -> Dict:
        """Compila para Windows usando interop - NO REQUIERE ADMIN"""
        result = self.windows.compile_project(
            project_type,
            project_path,
            config
        )
        
        # Si falla con "acceso denegado", dar mensaje claro
        if not result['success'] and 'denied' in result.get('stderr', '').lower():
            result['admin_note'] = (
                "IMPORTANTE: La compilación NO requiere admin. "
                "El error puede ser porque:\n"
                "1. Un archivo está en uso (cierra el IDE/app)\n"
                "2. Antivirus bloqueando acceso\n"
                "3. Permisos NTFS incorrectos en la carpeta\n"
                "NO uses as_admin=True para compilar."
            )
            
        return result
    
    def build_installer(self, project_path: str,
                       project_type: str,
                       platform: str = "windows") -> Dict:
        """
        Construye instalador para la plataforma.
        
        Args:
            project_path: Ruta al proyecto
            project_type: Tipo de proyecto
            platform: Plataforma objetivo
            
        Returns:
            Dict con información del instalador
        """
        if platform == "windows":
            if project_type == "tauri":
                # Tauri ya genera instalador en el build
                result = self.windows.compile_project("tauri", project_path)
                if result['success']:
                    # Buscar instaladores generados
                    bundle_path = Path(project_path) / "src-tauri" / "target" / "release" / "bundle"
                    installers = list(bundle_path.glob("**/*.msi")) + \
                                list(bundle_path.glob("**/*.exe"))
                    
                    return {
                        'success': True,
                        'installers': [str(p) for p in installers]
                    }
                    
            elif project_type == "electron":
                # Usar electron-builder
                result = self.windows.run_cmd(
                    f'cd "{self.windows.wslpath(project_path)}" && npm run dist:win'
                )
                return result
                
        return {
            'success': False,
            'error': f'Installer build not supported for {project_type} on {platform}'
        }