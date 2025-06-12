"""
Herramienta de deployment multiplataforma.
"""

from typing import Dict, List, Optional
from pathlib import Path
import json

from .windows_interop import WindowsInterop


class MultiPlatformDeployer:
    """
    Sistema de deployment que puede desplegar aplicaciones
    a múltiples plataformas desde WSL2.
    """
    
    def __init__(self, windows_interop: WindowsInterop):
        self.windows = windows_interop
        
    def deploy_to_iis(self, app_path: str,
                     site_name: str,
                     app_pool: Optional[str] = None,
                     port: int = 80) -> Dict:
        """
        Despliega aplicación a IIS en Windows.
        
        Args:
            app_path: Ruta a la aplicación
            site_name: Nombre del sitio IIS
            app_pool: Application pool (se crea si no existe)
            port: Puerto del sitio
            
        Returns:
            Dict con resultado del deployment
        """
        win_path = self.windows.wslpath(app_path)
        
        if not app_pool:
            app_pool = site_name + "AppPool"
            
        # Script PowerShell para configurar IIS
        script = f"""
        Import-Module WebAdministration
        
        # Crear Application Pool si no existe
        if (!(Test-Path "IIS:\\AppPools\\{app_pool}")) {{
            New-WebAppPool -Name "{app_pool}"
            Set-ItemProperty -Path "IIS:\\AppPools\\{app_pool}" -Name processIdentity.identityType -Value ApplicationPoolIdentity
        }}
        
        # Crear sitio web si no existe
        if (!(Get-Website -Name "{site_name}" -ErrorAction SilentlyContinue)) {{
            New-Website -Name "{site_name}" -Port {port} -PhysicalPath "{win_path}" -ApplicationPool "{app_pool}"
        }} else {{
            # Actualizar sitio existente
            Set-ItemProperty "IIS:\\Sites\\{site_name}" -Name physicalPath -Value "{win_path}"
        }}
        
        # Iniciar sitio y app pool
        Start-WebAppPool -Name "{app_pool}"
        Start-Website -Name "{site_name}"
        
        Write-Host "Deployment successful to IIS"
        """
        
        # Ejecutar con permisos elevados
        result = self.windows.run_powershell(script, as_admin=True)
        
        if result['success']:
            result['url'] = f"http://localhost:{port}"
            result['site_name'] = site_name
            result['app_pool'] = app_pool
            
        return result
    
    def deploy_windows_service(self, exe_path: str,
                             service_name: str,
                             display_name: Optional[str] = None,
                             description: Optional[str] = None,
                             start_type: str = "Automatic") -> Dict:
        """
        Instala y ejecuta un servicio Windows.
        
        Args:
            exe_path: Ruta al ejecutable del servicio
            service_name: Nombre interno del servicio
            display_name: Nombre visible del servicio
            description: Descripción del servicio
            start_type: Tipo de inicio (Automatic, Manual, Disabled)
            
        Returns:
            Dict con resultado
        """
        win_exe = self.windows.wslpath(exe_path)
        
        if not display_name:
            display_name = service_name
            
        script = f"""
        # Detener servicio si existe
        if (Get-Service -Name "{service_name}" -ErrorAction SilentlyContinue) {{
            Stop-Service -Name "{service_name}" -Force
            & sc.exe delete "{service_name}"
            Start-Sleep -Seconds 2
        }}
        
        # Crear nuevo servicio
        New-Service -Name "{service_name}" `
                   -BinaryPathName "{win_exe}" `
                   -DisplayName "{display_name}" `
                   -StartupType {start_type}
        """
        
        if description:
            script += f"""
        Set-Service -Name "{service_name}" -Description "{description}"
        """
        
        script += f"""
        # Iniciar servicio
        Start-Service -Name "{service_name}"
        Get-Service -Name "{service_name}" | Select-Object Name, Status, StartType
        """
        
        return self.windows.run_powershell(script, as_admin=True)
    
    def create_scheduled_task(self, name: str,
                            command: str,
                            schedule: str = "Daily",
                            time: str = "09:00",
                            user: str = "SYSTEM") -> Dict:
        """
        Crea una tarea programada en Windows.
        
        Args:
            name: Nombre de la tarea
            command: Comando a ejecutar
            schedule: Frecuencia (Daily, Weekly, Monthly, Once)
            time: Hora de ejecución (HH:MM)
            user: Usuario que ejecuta la tarea
            
        Returns:
            Dict con resultado
        """
        # Si el comando es una ruta WSL, convertirla
        if command.startswith('/'):
            command = self.windows.wslpath(command)
            
        script = f"""
        # Eliminar tarea si existe
        Unregister-ScheduledTask -TaskName "{name}" -Confirm:$false -ErrorAction SilentlyContinue
        
        # Crear acción
        $action = New-ScheduledTaskAction -Execute "{command}"
        
        # Crear trigger según schedule
        """
        
        if schedule == "Daily":
            script += f'$trigger = New-ScheduledTaskTrigger -Daily -At "{time}"'
        elif schedule == "Weekly":
            script += f'$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At "{time}"'
        elif schedule == "Monthly":
            script += f'$trigger = New-ScheduledTaskTrigger -Monthly -DaysOfMonth 1 -At "{time}"'
        else:
            script += f'$trigger = New-ScheduledTaskTrigger -Once -At "{time}"'
            
        script += f"""
        
        # Configurar principal
        $principal = New-ScheduledTaskPrincipal -UserId "{user}" -LogonType ServiceAccount
        
        # Registrar tarea
        Register-ScheduledTask -TaskName "{name}" `
                              -Action $action `
                              -Trigger $trigger `
                              -Principal $principal `
                              -Description "Created by Batman Incorporated"
                              
        Get-ScheduledTask -TaskName "{name}" | Select-Object TaskName, State
        """
        
        return self.windows.run_powershell(script, as_admin=True)
    
    def deploy_to_docker(self, project_path: str,
                        image_name: str,
                        dockerfile: Optional[str] = None,
                        platform: str = "linux/amd64",
                        push: bool = False,
                        registry: Optional[str] = None) -> Dict:
        """
        Construye y despliega imagen Docker.
        
        Args:
            project_path: Ruta al proyecto
            image_name: Nombre de la imagen
            dockerfile: Ruta al Dockerfile (opcional)
            platform: Plataforma objetivo
            push: Si hacer push al registry
            registry: Registry URL (opcional)
            
        Returns:
            Dict con resultado
        """
        import subprocess
        
        # Construir comando docker build
        cmd = ["docker", "build", "-t", image_name]
        
        if dockerfile:
            cmd.extend(["-f", dockerfile])
            
        cmd.extend(["--platform", platform, project_path])
        
        # Ejecutar build
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        response = {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'image': image_name
        }
        
        # Push si se solicita
        if response['success'] and push:
            if registry:
                full_image = f"{registry}/{image_name}"
                # Tag para registry
                tag_result = subprocess.run(
                    ["docker", "tag", image_name, full_image],
                    capture_output=True,
                    text=True
                )
                if tag_result.returncode == 0:
                    image_name = full_image
                    
            # Push
            push_result = subprocess.run(
                ["docker", "push", image_name],
                capture_output=True,
                text=True
            )
            
            response['push_success'] = push_result.returncode == 0
            response['push_output'] = push_result.stdout
            
        return response
    
    def deploy_electron_app(self, app_path: str,
                          platforms: List[str] = None) -> Dict:
        """
        Empaqueta y distribuye aplicación Electron.
        
        Args:
            app_path: Ruta a la aplicación Electron
            platforms: Lista de plataformas ['win32', 'darwin', 'linux']
            
        Returns:
            Dict con archivos generados
        """
        if platforms is None:
            platforms = ['win32']
            
        results = {'platforms': {}}
        
        for platform in platforms:
            if platform == 'win32':
                # Compilar para Windows
                result = self.windows.run_cmd(
                    f'cd "{self.windows.wslpath(app_path)}" && npm run dist:win'
                )
                
                if result['success']:
                    # Buscar archivos generados
                    dist_path = Path(app_path) / "dist"
                    installers = list(dist_path.glob("*.exe")) + \
                               list(dist_path.glob("*.msi"))
                    
                    result['artifacts'] = [str(p) for p in installers]
                    
            else:
                # Compilar para otras plataformas en Linux
                import subprocess
                cmd = f"cd {app_path} && npm run dist:{platform}"
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True
                )
                result = {
                    'success': result.returncode == 0,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
                
            results['platforms'][platform] = result
            
        results['success'] = any(
            p.get('success', False) for p in results['platforms'].values()
        )
        
        return results
    
    def create_github_release(self, repo: str,
                            tag: str,
                            title: str,
                            body: str,
                            files: List[str] = None) -> Dict:
        """
        Crea release en GitHub con archivos.
        
        Args:
            repo: Repositorio (owner/name)
            tag: Tag de la release
            title: Título de la release
            body: Descripción
            files: Lista de archivos para subir
            
        Returns:
            Dict con resultado
        """
        import subprocess
        
        # Crear release
        cmd = [
            "gh", "release", "create", tag,
            "--repo", repo,
            "--title", title,
            "--notes", body
        ]
        
        # Agregar archivos si existen
        if files:
            for file in files:
                if Path(file).exists():
                    cmd.append(file)
                    
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'tag': tag,
            'url': f"https://github.com/{repo}/releases/tag/{tag}" if result.returncode == 0 else None
        }