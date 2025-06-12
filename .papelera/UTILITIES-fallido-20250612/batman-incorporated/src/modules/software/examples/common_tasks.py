"""
Ejemplos prácticos de tareas comunes Windows para Batman.
USAR ESTOS EJEMPLOS, NO INVENTAR COMANDOS.
"""

from pathlib import Path
from typing import Dict, List


class WindowsTaskExamples:
    """Ejemplos listos para usar - NO INVENTAR, COPIAR Y ADAPTAR"""
    
    def __init__(self, software_module):
        self.module = software_module
        self.windows = software_module.get_tool('windows')
        self.compiler = software_module.get_tool('compiler')
        self.deployer = software_module.get_tool('deployer')
        self.office = software_module.get_tool('office')
        
    # ============= EJEMPLOS DE COMPILACIÓN =============
    
    def compile_dotnet_project(self, project_path: str) -> Dict:
        """Compilar proyecto .NET Framework/Core"""
        print("🔨 Compilando proyecto .NET...")
        
        # SIEMPRE verificar que existe
        if not Path(project_path).exists():
            return {'success': False, 'error': 'Project path not found'}
            
        # Usar compiler, NO comandos directos
        result = self.compiler.compile(
            project_path=project_path,
            target_platform='windows',
            project_type='dotnet'
        )
        
        if result['success']:
            print("✅ Compilación exitosa")
            # Buscar ejecutables generados
            output_dir = Path(project_path) / 'bin' / 'Release'
            if output_dir.exists():
                exes = list(output_dir.glob('**/*.exe'))
                dlls = list(output_dir.glob('**/*.dll'))
                print(f"📦 Generados: {len(exes)} EXE, {len(dlls)} DLL")
        else:
            print(f"❌ Error: {result.get('stderr', 'Unknown error')}")
            
        return result
    
    def build_tauri_app(self, project_path: str) -> Dict:
        """Compilar app Tauri para Windows"""
        print("🦀 Compilando Tauri app...")
        
        # Verificar estructura Tauri
        tauri_conf = Path(project_path) / 'src-tauri' / 'tauri.conf.json'
        if not tauri_conf.exists():
            return {'success': False, 'error': 'Not a Tauri project'}
            
        result = self.compiler.compile(
            project_path=project_path,
            target_platform='windows',
            project_type='tauri'
        )
        
        if result['success']:
            # Tauri genera instaladores en bundle/
            bundle_path = Path(project_path) / 'src-tauri' / 'target' / 'release' / 'bundle'
            msi_files = list(bundle_path.glob('**/*.msi'))
            exe_files = list(bundle_path.glob('**/*.exe'))
            
            print(f"📦 Instaladores creados:")
            for installer in msi_files + exe_files:
                size_mb = installer.stat().st_size / 1024 / 1024
                print(f"  - {installer.name} ({size_mb:.1f} MB)")
                
        return result
    
    def build_electron_app(self, project_path: str) -> Dict:
        """Compilar app Electron con instalador"""
        print("⚡ Compilando Electron app...")
        
        # Primero instalar dependencias si es necesario
        package_json = Path(project_path) / 'package.json'
        if not package_json.exists():
            return {'success': False, 'error': 'No package.json found'}
            
        # Instalar dependencias
        print("📦 Instalando dependencias...")
        npm_install = self.windows.run_cmd(
            'npm install',
            cwd=project_path
        )
        
        if not npm_install['success']:
            return npm_install
            
        # Compilar para Windows
        result = self.deployer.deploy_electron_app(
            app_path=project_path,
            platforms=['win32']
        )
        
        return result
    
    # ============= EJEMPLOS DE DEPLOYMENT =============
    
    def deploy_web_app_to_iis(self, app_path: str, domain: str = None) -> Dict:
        """Deploy completo de web app a IIS"""
        print("🌐 Desplegando a IIS...")
        
        site_name = Path(app_path).name
        port = 80 if not domain else 443
        
        # Deploy básico
        result = self.deployer.deploy_to_iis(
            app_path=app_path,
            site_name=site_name,
            port=port
        )
        
        if result['success'] and domain:
            # Configurar SSL si hay dominio
            print(f"🔐 Configurando SSL para {domain}...")
            ssl_script = f"""
            Import-Module WebAdministration
            
            # Crear binding HTTPS
            New-WebBinding -Name "{site_name}" -Protocol https -Port 443 -HostHeader "{domain}"
            
            # Aplicar certificado (asume que existe)
            $cert = Get-ChildItem -Path Cert:\\LocalMachine\\My | Where-Object {{$_.Subject -match "{domain}"}}
            if ($cert) {{
                $binding = Get-WebBinding -Name "{site_name}" -Protocol https
                $binding.AddSslCertificate($cert.Thumbprint, "my")
            }}
            """
            
            self.windows.run_powershell(ssl_script, as_admin=True)
            
        return result
    
    def create_windows_service_from_exe(self, exe_path: str, 
                                      service_name: str,
                                      auto_restart: bool = True) -> Dict:
        """Crear servicio Windows con auto-restart"""
        print(f"🔧 Creando servicio Windows: {service_name}")
        
        # Verificar que el exe existe
        if not Path(exe_path).exists():
            # Si es ruta Linux, convertir
            win_path = self.windows.wslpath(exe_path)
            # Verificar de nuevo con comando Windows
            check = self.windows.run_cmd(f'if exist "{win_path}" echo EXISTS')
            if 'EXISTS' not in check['stdout']:
                return {'success': False, 'error': 'EXE not found'}
        
        # Crear servicio
        result = self.deployer.deploy_windows_service(
            exe_path=exe_path,
            service_name=service_name,
            display_name=f"{service_name} Service",
            description=f"Servicio gestionado por Batman Incorporated",
            start_type="Automatic"
        )
        
        if result['success'] and auto_restart:
            # Configurar recuperación automática
            recovery_script = f"""
            sc.exe failure "{service_name}" reset= 86400 actions= restart/60000/restart/60000/restart/60000
            sc.exe failureflag "{service_name}" 1
            """
            self.windows.run_cmd(recovery_script)
            print("♻️ Auto-restart configurado")
            
        return result
    
    # ============= EJEMPLOS DE AUTOMATIZACIÓN OFFICE =============
    
    def create_project_report_excel(self, project_stats: Dict, 
                                  output_path: str) -> Dict:
        """Crear reporte Excel profesional del proyecto"""
        print("📊 Generando reporte Excel...")
        
        # Preparar datos en formato tabular
        data = []
        
        # Métricas del código
        if 'code_stats' in project_stats:
            for lang, stats in project_stats['code_stats'].items():
                data.append({
                    'Categoría': 'Código',
                    'Tipo': lang,
                    'Archivos': stats.get('files', 0),
                    'Líneas': stats.get('lines', 0),
                    'Tamaño (KB)': stats.get('size_kb', 0)
                })
                
        # Métricas de tests
        if 'test_results' in project_stats:
            for platform, results in project_stats['test_results'].items():
                data.append({
                    'Categoría': 'Tests',
                    'Tipo': platform,
                    'Archivos': results.get('total', 0),
                    'Líneas': results.get('passed', 0),
                    'Tamaño (KB)': 0
                })
                
        # Crear Excel con formato
        result = self.office.create_excel_report(
            data=data,
            output_path=output_path,
            sheet_name='Análisis de Proyecto',
            auto_format=True
        )
        
        if result['success']:
            print(f"✅ Reporte guardado en: {output_path}")
            # Abrir automáticamente
            self.windows.open_in_windows(output_path)
            
        return result
    
    def generate_documentation_word(self, project_info: Dict,
                                  output_path: str) -> Dict:
        """Generar documentación en Word"""
        print("📝 Generando documentación Word...")
        
        content = {
            'title': project_info.get('name', 'Documentación del Proyecto'),
            'paragraphs': []
        }
        
        # Descripción
        content['paragraphs'].append(f"Descripción: {project_info.get('description', 'N/A')}")
        content['paragraphs'].append("")  # Línea en blanco
        
        # Requisitos
        content['paragraphs'].append("REQUISITOS DEL SISTEMA:")
        for req in project_info.get('requirements', []):
            content['paragraphs'].append(f"• {req}")
        content['paragraphs'].append("")
        
        # Instalación
        content['paragraphs'].append("INSTRUCCIONES DE INSTALACIÓN:")
        for step in project_info.get('install_steps', []):
            content['paragraphs'].append(f"{step}")
        
        result = self.office.generate_word_document(
            content=content,
            output_path=output_path
        )
        
        return result
    
    # ============= EJEMPLOS DE TAREAS PROGRAMADAS =============
    
    def setup_backup_task(self, source_path: str, 
                        backup_path: str,
                        time: str = "02:00") -> Dict:
        """Configurar backup automático diario"""
        print("💾 Configurando backup automático...")
        
        # Crear script de backup
        backup_script = f"""@echo off
echo Iniciando backup - %date% %time%
robocopy "{self.windows.wslpath(source_path)}" "{self.windows.wslpath(backup_path)}" /E /MIR /R:3 /W:10
echo Backup completado - %date% %time%
"""
        
        # Guardar script
        script_path = Path.home() / '.batman' / 'backup_script.bat'
        script_path.parent.mkdir(exist_ok=True)
        script_path.write_text(backup_script)
        
        # Crear tarea programada
        result = self.deployer.create_scheduled_task(
            name='BatmanBackup',
            command=str(script_path),
            schedule='Daily',
            time=time
        )
        
        return result
    
    # ============= EJEMPLOS DE TESTING =============
    
    def run_full_test_suite(self, project_path: str) -> Dict:
        """Ejecutar suite completa de tests en ambas plataformas"""
        print("🧪 Ejecutando tests completos...")
        
        tester = self.module.get_tool('tester')
        
        # Tests en ambas plataformas
        results = tester.run_tests(
            project_path=project_path,
            platforms=['linux', 'windows']
        )
        
        # Generar reporte de cobertura si los tests pasaron
        if results['overall_success']:
            print("📊 Generando reporte de cobertura...")
            
            coverage_linux = tester.run_coverage(project_path, 'linux')
            coverage_windows = tester.run_coverage(project_path, 'windows')
            
            # Crear reporte Excel con resultados
            test_data = []
            for platform, result in results['platforms'].items():
                if 'stats' in result:
                    test_data.append({
                        'Plataforma': platform,
                        'Total': result['stats']['total'],
                        'Pasados': result['stats']['passed'],
                        'Fallidos': result['stats']['failed'],
                        'Porcentaje': f"{(result['stats']['passed'] / result['stats']['total'] * 100):.1f}%"
                    })
                    
            self.office.create_excel_report(
                data=test_data,
                output_path=str(Path(project_path) / 'test_report.xlsx'),
                sheet_name='Resultados de Tests'
            )
            
        return results
    
    # ============= UTILIDADES COMUNES =============
    
    def check_and_install_dependencies(self, project_path: str) -> bool:
        """Verificar e instalar dependencias del proyecto"""
        path = Path(project_path)
        
        # Node.js
        if (path / 'package.json').exists():
            print("📦 Instalando dependencias Node.js...")
            result = self.windows.run_cmd('npm install', cwd=project_path)
            if not result['success']:
                print(f"❌ Error: {result['stderr']}")
                return False
                
        # .NET
        if any(path.glob('*.csproj')):
            print("📦 Restaurando paquetes NuGet...")
            result = self.windows.run_cmd('dotnet restore', cwd=project_path)
            if not result['success']:
                return False
                
        # Python
        if (path / 'requirements.txt').exists():
            print("📦 Instalando dependencias Python...")
            result = self.windows.run_cmd('pip install -r requirements.txt', cwd=project_path)
            if not result['success']:
                return False
                
        return True
    
    def open_project_in_ide(self, project_path: str, ide: str = 'code') -> bool:
        """Abrir proyecto en IDE"""
        ides = {
            'code': 'code.exe',
            'vscode': 'code.exe',
            'visualstudio': 'devenv.exe',
            'rider': 'rider64.exe',
            'idea': 'idea64.exe'
        }
        
        exe = ides.get(ide.lower())
        if not exe:
            print(f"❌ IDE no reconocido: {ide}")
            return False
            
        # Verificar si está disponible
        if not self.windows.available_tools.get(exe):
            print(f"❌ {exe} no encontrado en PATH")
            return False
            
        print(f"🚀 Abriendo proyecto en {ide}...")
        result = self.windows.run_windows_exe(exe, [project_path])
        
        return result['success']


# ============= FUNCIÓN HELPER PARA BATMAN =============

def get_example_for_task(task_description: str, software_module) -> str:
    """
    Retorna el código ejemplo apropiado para la tarea.
    USAR ESTO EN LUGAR DE INVENTAR COMANDOS.
    """
    examples = WindowsTaskExamples(software_module)
    
    task_lower = task_description.lower()
    
    # Mapeo de palabras clave a ejemplos
    if any(word in task_lower for word in ['compilar', 'build', 'compile']):
        if 'dotnet' in task_lower or '.net' in task_lower:
            return "examples.compile_dotnet_project(project_path)"
        elif 'tauri' in task_lower:
            return "examples.build_tauri_app(project_path)"
        elif 'electron' in task_lower:
            return "examples.build_electron_app(project_path)"
            
    elif any(word in task_lower for word in ['deploy', 'desplegar', 'iis']):
        if 'iis' in task_lower or 'web' in task_lower:
            return "examples.deploy_web_app_to_iis(app_path, domain)"
        elif 'service' in task_lower or 'servicio' in task_lower:
            return "examples.create_windows_service_from_exe(exe_path, service_name)"
            
    elif any(word in task_lower for word in ['test', 'prueba', 'testing']):
        return "examples.run_full_test_suite(project_path)"
        
    elif any(word in task_lower for word in ['excel', 'reporte', 'report']):
        return "examples.create_project_report_excel(stats, output_path)"
        
    elif any(word in task_lower for word in ['word', 'documento', 'documentation']):
        return "examples.generate_documentation_word(info, output_path)"
        
    elif any(word in task_lower for word in ['backup', 'respaldo']):
        return "examples.setup_backup_task(source, backup_path)"
        
    elif any(word in task_lower for word in ['open', 'abrir', 'ide']):
        return "examples.open_project_in_ide(project_path, 'vscode')"
        
    # Default
    return "examples.check_and_install_dependencies(project_path)"