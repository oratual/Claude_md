"""
Herramienta de testing híbrido Linux/Windows.
"""

from typing import Dict, List, Optional
import json
from pathlib import Path

from .windows_interop import WindowsInterop


class HybridTester:
    """
    Sistema de testing que puede ejecutar pruebas
    tanto en Linux como Windows desde WSL2.
    """
    
    def __init__(self, windows_interop: WindowsInterop):
        self.windows = windows_interop
        
    def run_tests(self, project_path: str,
                 test_command: Optional[str] = None,
                 platforms: List[str] = None,
                 test_filter: Optional[str] = None) -> Dict:
        """
        Ejecuta tests en las plataformas especificadas.
        
        Args:
            project_path: Ruta al proyecto
            test_command: Comando de test personalizado
            platforms: Lista de plataformas ['linux', 'windows']
            test_filter: Filtro para ejecutar tests específicos
            
        Returns:
            Dict con resultados por plataforma
        """
        if platforms is None:
            platforms = ['linux']
            
        results = {
            'overall_success': True,
            'platforms': {}
        }
        
        # Detectar comando de test si no se proporciona
        if not test_command:
            test_command = self._detect_test_command(project_path)
            
        for platform in platforms:
            if platform == 'linux':
                result = self._run_linux_tests(
                    project_path, test_command, test_filter
                )
            elif platform == 'windows':
                result = self._run_windows_tests(
                    project_path, test_command, test_filter
                )
            else:
                result = {
                    'success': False,
                    'error': f'Unknown platform: {platform}'
                }
                
            results['platforms'][platform] = result
            if not result.get('success', False):
                results['overall_success'] = False
                
        return results
    
    def _detect_test_command(self, project_path: str) -> str:
        """Detecta comando de test basado en el proyecto"""
        path = Path(project_path)
        
        # Verificar diferentes archivos de configuración
        if (path / "package.json").exists():
            # Leer package.json para encontrar script de test
            try:
                with open(path / "package.json") as f:
                    pkg = json.load(f)
                    scripts = pkg.get('scripts', {})
                    if 'test' in scripts:
                        return 'npm test'
                    elif 'test:all' in scripts:
                        return 'npm run test:all'
            except:
                pass
                
        elif (path / "Cargo.toml").exists():
            return 'cargo test'
            
        elif any(path.glob("*.csproj")):
            return 'dotnet test'
            
        elif (path / "build.gradle").exists():
            return './gradlew test'
            
        elif (path / "pom.xml").exists():
            return 'mvn test'
            
        # Default
        return 'npm test'
    
    def _run_linux_tests(self, project_path: str,
                        test_command: str,
                        test_filter: Optional[str]) -> Dict:
        """Ejecuta tests en Linux"""
        import subprocess
        import os
        
        # Construir comando con filtro si existe
        cmd = test_command
        if test_filter:
            # Agregar filtro según el tipo de comando
            if 'npm' in cmd or 'jest' in cmd:
                cmd += f' -- --testNamePattern="{test_filter}"'
            elif 'cargo' in cmd:
                cmd += f' {test_filter}'
            elif 'dotnet' in cmd:
                cmd += f' --filter "{test_filter}"'
                
        try:
            # Cambiar al directorio del proyecto
            original_dir = os.getcwd()
            os.chdir(project_path)
            
            # Ejecutar tests
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )
            
            os.chdir(original_dir)
            
            # Analizar salida para extraer estadísticas
            stats = self._parse_test_output(result.stdout, test_command)
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'stats': stats,
                'command': cmd
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _run_windows_tests(self, project_path: str,
                          test_command: str,
                          test_filter: Optional[str]) -> Dict:
        """Ejecuta tests en Windows"""
        win_path = self.windows.wslpath(project_path)
        
        # Adaptar comando para Windows
        if test_filter:
            if 'npm' in test_command:
                test_command += f' -- --testNamePattern="{test_filter}"'
            elif 'dotnet' in test_command:
                test_command += f' --filter "{test_filter}"'
                
        # Ejecutar en Windows
        cmd = f'cd "{win_path}" && {test_command}'
        result = self.windows.run_cmd(cmd)
        
        # Analizar salida
        if result['success']:
            stats = self._parse_test_output(result['stdout'], test_command)
            result['stats'] = stats
            
        return result
    
    def _parse_test_output(self, output: str, test_command: str) -> Dict:
        """Analiza salida de tests para extraer estadísticas"""
        stats = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0
        }
        
        lines = output.split('\n')
        
        # Patrones según el framework de testing
        if 'jest' in test_command or 'npm' in test_command:
            # Jest pattern
            for line in lines:
                if 'Tests:' in line:
                    # Tests:       1 failed, 2 passed, 3 total
                    parts = line.split(',')
                    for part in parts:
                        if 'failed' in part:
                            stats['failed'] = int(part.split()[0])
                        elif 'passed' in part:
                            stats['passed'] = int(part.split()[0])
                        elif 'total' in part:
                            stats['total'] = int(part.split()[0])
                            
        elif 'dotnet' in test_command:
            # .NET pattern
            for line in lines:
                if 'Total tests:' in line:
                    stats['total'] = int(line.split(':')[1].strip())
                elif 'Passed:' in line:
                    stats['passed'] = int(line.split(':')[1].strip())
                elif 'Failed:' in line:
                    stats['failed'] = int(line.split(':')[1].strip())
                    
        elif 'cargo' in test_command:
            # Rust pattern
            for line in lines:
                if 'test result:' in line:
                    # test result: ok. 5 passed; 0 failed; 0 ignored
                    parts = line.split(';')
                    for part in parts:
                        if 'passed' in part:
                            stats['passed'] = int(part.split()[0])
                        elif 'failed' in part:
                            stats['failed'] = int(part.split()[0])
                            
        return stats
    
    def run_coverage(self, project_path: str,
                    platform: str = "linux") -> Dict:
        """
        Ejecuta análisis de cobertura de código.
        
        Args:
            project_path: Ruta al proyecto
            platform: Plataforma donde ejecutar
            
        Returns:
            Dict con resultados de cobertura
        """
        if platform == "linux":
            return self._run_linux_coverage(project_path)
        elif platform == "windows":
            return self._run_windows_coverage(project_path)
        else:
            return {
                'success': False,
                'error': f'Unknown platform: {platform}'
            }
    
    def _run_linux_coverage(self, project_path: str) -> Dict:
        """Ejecuta cobertura en Linux"""
        import subprocess
        import os
        
        # Detectar herramienta de cobertura
        path = Path(project_path)
        
        if (path / "package.json").exists():
            cmd = "npm run coverage"
        elif (path / "Cargo.toml").exists():
            cmd = "cargo tarpaulin"
        elif any(path.glob("*.csproj")):
            cmd = "dotnet test /p:CollectCoverage=true"
        else:
            return {
                'success': False,
                'error': 'No coverage tool detected'
            }
            
        try:
            original_dir = os.getcwd()
            os.chdir(project_path)
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )
            
            os.chdir(original_dir)
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'command': cmd
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _run_windows_coverage(self, project_path: str) -> Dict:
        """Ejecuta cobertura en Windows"""
        win_path = self.windows.wslpath(project_path)
        
        # Detectar comando según proyecto
        if Path(project_path, "package.json").exists():
            cmd = f'cd "{win_path}" && npm run coverage'
        else:
            cmd = f'cd "{win_path}" && dotnet test /p:CollectCoverage=true'
            
        return self.windows.run_cmd(cmd)