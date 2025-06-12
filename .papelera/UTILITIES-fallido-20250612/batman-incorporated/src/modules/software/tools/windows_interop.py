"""
Herramienta completa de interoperabilidad WSL2-Windows.
Basada en el documento wsl2Win.md con mejoras adicionales.
"""

import subprocess
import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple
from functools import lru_cache
import shlex
import time


class WindowsInterop:
    """
    Herramienta completa de interoperabilidad WSL2-Windows.
    Provee acceso transparente a funcionalidades Windows desde WSL2.
    """
    
    def __init__(self):
        self.wsl_distro = self._detect_wsl_distro()
        self.windows_version = self._get_windows_version()
        self.available_tools = self._detect_windows_tools()
        self.encoding = 'utf-8'  # Default encoding para Windows
        
    def _detect_wsl_distro(self) -> str:
        """Detecta la distribución WSL actual"""
        try:
            result = subprocess.run(
                ['wslpath', '-w', '/'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                # Extraer nombre de distro de la ruta
                path = result.stdout.strip()
                if 'wsl.localhost' in path:
                    parts = path.split('\\')
                    for i, part in enumerate(parts):
                        if part == 'wsl.localhost' and i + 1 < len(parts):
                            return parts[i + 1]
                elif 'wsl$' in path:
                    parts = path.split('\\')
                    for i, part in enumerate(parts):
                        if part == 'wsl$' and i + 1 < len(parts):
                            return parts[i + 1]
            return "Unknown"
        except:
            return "Unknown"
    
    def _get_windows_version(self) -> Dict[str, str]:
        """Obtiene información de la versión de Windows"""
        try:
            result = self.run_powershell(
                "Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, BuildNumber | ConvertTo-Json",
                output_json=True
            )
            if result['success'] and isinstance(result.get('data'), dict):
                return result['data']
        except:
            pass
        return {"Caption": "Unknown", "Version": "Unknown", "BuildNumber": "Unknown"}
    
    def _detect_windows_tools(self) -> Dict[str, bool]:
        """Detecta herramientas Windows disponibles"""
        tools = {
            'powershell.exe': False,
            'pwsh.exe': False,  # PowerShell Core
            'cmd.exe': False,
            'wslpath': False,
            'clip.exe': False,
            'wslview': False,
            'wsl-open': False,
            'explorer.exe': False,
            'notepad.exe': False,
            'code.exe': False,  # VS Code
            'msbuild.exe': False,
            'dotnet.exe': False,
            'npm.cmd': False,
            'cargo.exe': False
        }
        
        for tool in tools:
            try:
                result = subprocess.run(
                    ['which', tool],
                    capture_output=True,
                    text=True
                )
                tools[tool] = result.returncode == 0
            except:
                tools[tool] = False
                
        return tools
    
    @lru_cache(maxsize=1000)
    def wslpath(self, path: str, to_windows: bool = True) -> str:
        """
        Convierte rutas entre WSL y Windows con caché.
        
        Args:
            path: Ruta a convertir
            to_windows: True para WSL->Windows, False para Windows->WSL
            
        Returns:
            Ruta convertida
        """
        if not path:
            return ""
            
        flag = "-w" if to_windows else "-u"
        
        try:
            result = subprocess.run(
                ["wslpath", flag, path],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except subprocess.TimeoutExpired:
            print(f"Timeout converting path: {path}")
        except Exception as e:
            print(f"Error converting path: {e}")
            
        return path
    
    def run_windows_exe(self, exe: str, args: List[str] = None, 
                       cwd: Optional[str] = None,
                       timeout: Optional[int] = None) -> Dict:
        """
        Ejecuta un ejecutable Windows con argumentos.
        
        Args:
            exe: Nombre del ejecutable o ruta completa
            args: Lista de argumentos
            cwd: Directorio de trabajo (se convertirá a ruta Windows)
            timeout: Timeout en segundos
            
        Returns:
            Dict con success, stdout, stderr, returncode
        """
        cmd = [exe]
        if args:
            cmd.extend(args)
            
        # Convertir directorio de trabajo si es necesario
        if cwd:
            cwd = self.wslpath(cwd, to_windows=True)
            
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=timeout,
                encoding=self.encoding
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '',
                'stderr': f'Timeout after {timeout} seconds',
                'returncode': -1
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'returncode': -1
            }
    
    def run_cmd(self, command: str, cwd: Optional[str] = None) -> Dict:
        """
        Ejecuta comando en Command Prompt.
        
        Args:
            command: Comando a ejecutar
            cwd: Directorio de trabajo
            
        Returns:
            Dict con resultado
        """
        # Escapar comillas en el comando
        command = command.replace('"', '\\"')
        
        args = ['/c', command]
        
        # Si hay directorio de trabajo, agregar cd
        if cwd:
            win_cwd = self.wslpath(cwd, to_windows=True)
            args = ['/c', f'cd /d "{win_cwd}" && {command}']
            
        return self.run_windows_exe('cmd.exe', args)
    
    def run_powershell(self, script: str, 
                      as_admin: bool = False,
                      output_json: bool = False,
                      execution_policy: str = "Bypass",
                      timeout: int = 30) -> Dict:
        """
        Ejecuta PowerShell con opciones avanzadas.
        
        Args:
            script: Script o comando PowerShell
            as_admin: Solicitar elevación de privilegios
            output_json: Convertir salida a JSON
            execution_policy: Política de ejecución
            timeout: Timeout en segundos
            
        Returns:
            Dict con success, stdout, stderr, y opcionalmente 'data' si output_json=True
        """
        # Detectar PowerShell disponible
        ps_exe = 'pwsh.exe' if self.available_tools.get('pwsh.exe') else 'powershell.exe'
        
        if output_json:
            script = f"({script}) | ConvertTo-Json -Depth 10"
            
        # Construir comando
        cmd = [ps_exe, '-NoProfile', '-NonInteractive']
        
        if execution_policy:
            cmd.extend(['-ExecutionPolicy', execution_policy])
            
        if as_admin:
            # Crear script que solicita elevación
            elevated_script = f"""
            $ErrorActionPreference = 'Stop'
            try {{
                Start-Process {ps_exe} -Verb RunAs -Wait -ArgumentList @(
                    '-NoProfile',
                    '-NonInteractive',
                    '-ExecutionPolicy', '{execution_policy}',
                    '-Command', '{script.replace("'", "''")}'
                )
                "ADMIN_SUCCESS"
            }} catch {{
                Write-Error $_.Exception.Message
            }}
            """
            script = elevated_script
            
        cmd.extend(['-Command', script])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding=self.encoding
            )
            
            response = {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
            
            # Si se pidió JSON, intentar parsearlo
            if output_json and result.returncode == 0 and result.stdout.strip():
                try:
                    data = json.loads(result.stdout)
                    response['data'] = data
                except json.JSONDecodeError:
                    # No es JSON válido, dejar stdout como está
                    pass
                    
            # Verificar si fue elevación exitosa
            if as_admin and "ADMIN_SUCCESS" in result.stdout:
                response['elevated'] = True
                
            return response
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '',
                'stderr': f'PowerShell timeout after {timeout} seconds',
                'returncode': -1
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'returncode': -1
            }
    
    def run_batch(self, batch_file: str, args: List[str] = None) -> Dict:
        """
        Ejecuta archivo batch (.bat).
        
        Args:
            batch_file: Ruta al archivo .bat
            args: Argumentos adicionales
            
        Returns:
            Dict con resultado
        """
        win_path = self.wslpath(batch_file, to_windows=True)
        
        cmd = f'"{win_path}"'
        if args:
            cmd += ' ' + ' '.join(f'"{arg}"' for arg in args)
            
        return self.run_cmd(cmd)
    
    def compile_project(self, project_type: str, 
                       project_path: str,
                       config: Dict = None,
                       output_path: Optional[str] = None) -> Dict:
        """
        Compilación inteligente según tipo de proyecto.
        
        IMPORTANTE: La compilación NUNCA requiere permisos de administrador.
        Si encuentras errores de acceso, revisa:
        - Archivos en uso (cierra IDEs)
        - Antivirus bloqueando
        - Permisos de carpeta
        
        Args:
            project_type: Tipo de proyecto (dotnet, msbuild, cargo, npm, tauri, etc.)
            project_path: Ruta al proyecto
            config: Configuración adicional
            output_path: Ruta de salida personalizada
            
        Returns:
            Dict con resultado de compilación
        """
        win_path = self.wslpath(project_path, to_windows=True)
        config = config or {}
        
        # Comandos de compilación por tipo
        compilers = {
            'dotnet': {
                'check': 'dotnet.exe',
                'cmd': f'dotnet build "{win_path}" -c Release',
                'with_output': f'dotnet build "{win_path}" -c Release -o "{{output}}"'
            },
            'msbuild': {
                'check': 'msbuild.exe',
                'cmd': f'msbuild "{win_path}" /p:Configuration=Release',
                'with_output': f'msbuild "{win_path}" /p:Configuration=Release /p:OutputPath="{{output}}"'
            },
            'cargo': {
                'check': 'cargo.exe',
                'cmd': f'cd "{win_path}" && cargo build --release',
                'with_output': f'cd "{win_path}" && cargo build --release --target-dir "{{output}}"'
            },
            'npm': {
                'check': 'npm.cmd',
                'cmd': f'cd "{win_path}" && npm install && npm run build',
                'with_output': None  # NPM generalmente tiene su propia config de output
            },
            'tauri': {
                'check': 'npm.cmd',
                'cmd': f'cd "{win_path}" && npm run tauri build',
                'with_output': None
            },
            'gradle': {
                'check': 'gradle.bat',
                'cmd': f'cd "{win_path}" && gradle build',
                'with_output': f'cd "{win_path}" && gradle build -PoutputDir="{{output}}"'
            }
        }
        
        if project_type not in compilers:
            return {
                'success': False,
                'stdout': '',
                'stderr': f'Unknown project type: {project_type}',
                'returncode': -1
            }
            
        compiler_info = compilers[project_type]
        
        # Verificar que la herramienta esté disponible
        if not self.available_tools.get(compiler_info['check'], True):
            return {
                'success': False,
                'stdout': '',
                'stderr': f'{compiler_info["check"]} not found',
                'returncode': -1
            }
        
        # Construir comando
        if output_path and compiler_info.get('with_output'):
            win_output = self.wslpath(output_path, to_windows=True)
            command = compiler_info['with_output'].format(output=win_output)
        else:
            command = compiler_info['cmd']
            
        # Agregar flags adicionales de config
        if config.get('flags'):
            command += ' ' + ' '.join(config['flags'])
            
        # Ejecutar compilación
        result = self.run_cmd(command)
        
        # Post-procesamiento según tipo
        if result['success'] and project_type == 'tauri':
            # Buscar la ruta del instalador generado
            bundle_path = Path(project_path) / 'src-tauri' / 'target' / 'release' / 'bundle'
            if bundle_path.exists():
                result['installer_path'] = str(bundle_path)
                
        return result
    
    def create_windows_shortcut(self, target: str, 
                              shortcut_name: str,
                              description: str = "",
                              icon_path: Optional[str] = None,
                              working_dir: Optional[str] = None) -> bool:
        """
        Crea un acceso directo de Windows.
        
        Args:
            target: Ruta al ejecutable objetivo
            shortcut_name: Nombre del acceso directo (incluir .lnk)
            description: Descripción del acceso directo
            icon_path: Ruta al icono
            working_dir: Directorio de trabajo
            
        Returns:
            True si se creó exitosamente
        """
        # Convertir rutas
        win_target = self.wslpath(target, to_windows=True)
        win_shortcut = self.wslpath(shortcut_name, to_windows=True)
        
        script = f"""
        $WScriptShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WScriptShell.CreateShortcut("{win_shortcut}")
        $Shortcut.TargetPath = "{win_target}"
        """
        
        if description:
            script += f'$Shortcut.Description = "{description}"\n'
            
        if icon_path:
            win_icon = self.wslpath(icon_path, to_windows=True)
            script += f'$Shortcut.IconLocation = "{win_icon}"\n'
            
        if working_dir:
            win_working = self.wslpath(working_dir, to_windows=True)
            script += f'$Shortcut.WorkingDirectory = "{win_working}"\n'
            
        script += "$Shortcut.Save()"
        
        result = self.run_powershell(script)
        return result['success']
    
    def clipboard_sync(self, text: str = None, 
                      paste: bool = False,
                      file_path: Optional[str] = None) -> Optional[str]:
        """
        Sincronización bidireccional del portapapeles.
        
        Args:
            text: Texto a copiar al portapapeles
            paste: Si True, obtiene el contenido del portapapeles
            file_path: Archivo a copiar al portapapeles
            
        Returns:
            Contenido del portapapeles si paste=True
        """
        if paste:
            # Obtener del portapapeles
            result = self.run_powershell("Get-Clipboard")
            if result['success']:
                return result['stdout'].rstrip('\n\r')
            return None
            
        elif file_path:
            # Copiar archivo al portapapeles
            with open(file_path, 'r') as f:
                content = f.read()
            return self.clipboard_sync(text=content)
            
        elif text is not None:
            # Copiar texto al portapapeles
            # Usar clip.exe que es más confiable
            try:
                process = subprocess.Popen(
                    ['clip.exe'],
                    stdin=subprocess.PIPE,
                    text=True,
                    encoding=self.encoding
                )
                process.communicate(input=text)
                return text if process.returncode == 0 else None
            except Exception as e:
                print(f"Error copying to clipboard: {e}")
                return None
                
        return None
    
    def open_in_windows(self, file_path: str, 
                       app: Optional[str] = None) -> bool:
        """
        Abre archivo con aplicación Windows.
        
        Args:
            file_path: Ruta al archivo
            app: Aplicación específica (opcional)
            
        Returns:
            True si se abrió exitosamente
        """
        win_path = self.wslpath(file_path, to_windows=True)
        
        # Usar wslview si está disponible
        if self.available_tools.get('wslview'):
            result = subprocess.run(['wslview', file_path])
            return result.returncode == 0
            
        # Alternativa con explorer.exe
        if app:
            # Abrir con aplicación específica
            result = self.run_cmd(f'start "" "{app}" "{win_path}"')
        else:
            # Abrir con aplicación predeterminada
            result = self.run_cmd(f'start "" "{win_path}"')
            
        return result['success']
    
    def get_windows_env(self, var_name: Optional[str] = None) -> Union[str, Dict[str, str]]:
        """
        Obtiene variables de entorno de Windows.
        
        Args:
            var_name: Nombre de variable específica o None para todas
            
        Returns:
            Valor de la variable o dict con todas
        """
        if var_name:
            result = self.run_cmd(f'echo %{var_name}%')
            if result['success']:
                return result['stdout'].strip()
            return ""
        else:
            # Obtener todas las variables
            result = self.run_powershell(
                "Get-ChildItem Env: | Select-Object Name, Value | ConvertTo-Json",
                output_json=True
            )
            if result['success'] and 'data' in result:
                # Convertir a dict simple
                env_dict = {}
                for item in result['data']:
                    if isinstance(item, dict):
                        env_dict[item.get('Name', '')] = item.get('Value', '')
                return env_dict
            return {}
    
    def create_windows_executable(self, 
                                script_path: str,
                                exe_name: str,
                                icon_path: Optional[str] = None,
                                admin_required: bool = False) -> Optional[str]:
        """
        Crea ejecutable Windows desde script PowerShell.
        
        Args:
            script_path: Ruta al script .ps1
            exe_name: Nombre del ejecutable (sin .exe)
            icon_path: Ruta al icono .ico
            admin_required: Si requiere permisos de administrador
            
        Returns:
            Ruta al ejecutable creado o None si falla
        """
        win_script = self.wslpath(script_path, to_windows=True)
        output_dir = str(Path(script_path).parent)
        output_path = f"{output_dir}/{exe_name}.exe"
        win_output = self.wslpath(output_path, to_windows=True)
        
        # Script para instalar y usar PS2EXE
        ps_script = f"""
        # Verificar si PS2EXE está instalado
        if (!(Get-Module -ListAvailable -Name ps2exe)) {{
            Write-Host "Instalando PS2EXE..."
            Install-Module -Name ps2exe -Force -Scope CurrentUser -AllowClobber
        }}
        
        Import-Module ps2exe
        
        # Convertir a EXE
        $params = @{{
            InputFile = "{win_script}"
            OutputFile = "{win_output}"
            NoConsole = $true
            RequireAdmin = ${str(admin_required).lower()}
        }}
        
        """
        
        if icon_path:
            win_icon = self.wslpath(icon_path, to_windows=True)
            ps_script += f'$params.IconFile = "{win_icon}"\n'
            
        ps_script += """
        Invoke-PS2EXE @params
        
        if (Test-Path $params.OutputFile) {
            Write-Host "SUCCESS: $($params.OutputFile)"
        } else {
            Write-Error "Failed to create executable"
        }
        """
        
        result = self.run_powershell(ps_script, timeout=60)
        
        if result['success'] and os.path.exists(output_path):
            return output_path
            
        return None
    
    def get_system_info(self) -> Dict:
        """Obtiene información detallada del sistema Windows"""
        info = {
            'os': self.windows_version,
            'wsl': {
                'distro': self.wsl_distro,
                'version': 'WSL2'  # Asumimos WSL2 para interop completo
            },
            'tools': self.available_tools,
            'powershell': {
                'version': 'Unknown',
                'core': self.available_tools.get('pwsh.exe', False)
            }
        }
        
        # Obtener versión de PowerShell
        ps_version = self.run_powershell("$PSVersionTable.PSVersion.ToString()")
        if ps_version['success']:
            info['powershell']['version'] = ps_version['stdout'].strip()
            
        return info