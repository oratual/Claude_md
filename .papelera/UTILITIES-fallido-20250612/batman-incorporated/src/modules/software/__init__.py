"""
Módulo Software Development para Batman Incorporated.
Provee herramientas completas para desarrollo de software con integración WSL2-Windows.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

sys.path.append(str(Path(__file__).parent.parent))
from base_module import BaseModule
from .tools.windows_interop import WindowsInterop
from .tools.compilation import CrossCompiler
from .tools.testing import HybridTester
from .tools.deployment import MultiPlatformDeployer
from .tools.office_automation import OfficeAutomation
from .examples.common_tasks import WindowsTaskExamples, get_example_for_task


class SoftwareModule(BaseModule):
    """
    Módulo completo para desarrollo de software con capacidades híbridas Linux/Windows.
    """
    
    def initialize(self) -> bool:
        """Inicializa todas las herramientas del módulo"""
        try:
            # Verificar requisitos críticos
            missing = self.get_missing_requirements()
            critical_missing = [
                tool for tool in missing 
                if tool in ['powershell.exe', 'cmd.exe', 'wslpath']
            ]
            
            if critical_missing:
                print(f"Critical tools missing: {critical_missing}")
                print("This module requires WSL2 with Windows interop enabled")
                return False
            
            # Inicializar herramientas core
            self.tools['windows'] = WindowsInterop()
            self.tools['compiler'] = CrossCompiler(self.tools['windows'])
            self.tools['tester'] = HybridTester(self.tools['windows'])
            self.tools['deployer'] = MultiPlatformDeployer(self.tools['windows'])
            self.tools['office'] = OfficeAutomation(self.tools['windows'])
            
            # Cargar templates
            self._load_templates()
            
            self._initialized = True
            return True
            
        except Exception as e:
            print(f"Error initializing software module: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_tool(self, tool_name: str) -> Any:
        """Obtiene una herramienta específica"""
        return self.tools.get(tool_name)
    
    def get_agent_enhancements(self) -> Dict[str, Dict]:
        """Mejoras específicas para cada agente"""
        # Cargar ejemplos para referencia
        self._examples = WindowsTaskExamples(self)
        
        enhancements = {
            'alfred': {
                'extra_prompt': """You have access to Windows interop tools for:
- IIS deployment and Windows service management
- .NET/C# development and MSBuild
- Registry access and Windows configuration
- PowerShell advanced scripting

IMPORTANT: Use the module's tools, NOT raw subprocess commands:
- windows = module.get_tool('windows')
- compiler = module.get_tool('compiler')
- deployer = module.get_tool('deployer')

See WINDOWS_GUIDE.md for exact usage. Use examples from common_tasks.py.
NEVER use subprocess.run() or os.system() for Windows commands.""",
                'tools': ['windows', 'compiler', 'deployer'],
                'templates': ['dotnet_api', 'windows_service', 'iis_config']
            },
            
            'robin': {
                'extra_prompt': """You can execute hybrid CI/CD pipelines:
- GitHub Actions with Windows runners
- Azure DevOps pipelines
- Cross-platform build scripts
- Windows scheduled tasks

IMPORTANT: Always use module tools:
- windows.run_powershell() for PowerShell
- windows.run_cmd() for CMD
- deployer.create_scheduled_task() for automation
Check examples in common_tasks.py before implementing.""",
                'tools': ['windows', 'deployer'],
                'templates': ['github_actions_hybrid', 'azure_pipeline', 'scheduled_task']
            },
            
            'batgirl': {
                'extra_prompt': """You can build desktop apps for Windows:
- Electron apps with Windows installers
- Tauri apps with native Windows features
- PWAs with Windows integration
- Browser automation for testing

IMPORTANT: Use compiler.compile() with correct project_type:
- 'electron' for Electron apps
- 'tauri' for Tauri apps
- 'npm' for general Node.js
See examples.build_electron_app() and examples.build_tauri_app().""",
                'tools': ['windows', 'compiler', 'tester'],
                'templates': ['electron_builder', 'tauri_config', 'pwa_manifest']
            },
            
            'oracle': {
                'extra_prompt': """You can perform security and testing on both platforms:
- Windows Defender scans
- Cross-platform test execution
- Performance profiling on Windows/Linux
- Security vulnerability checks

IMPORTANT: Use tester.run_tests() with platforms=['linux', 'windows']
Never run test commands directly. See examples.run_full_test_suite()
for proper cross-platform testing.""",
                'tools': ['windows', 'tester'],
                'templates': ['security_scan', 'cross_platform_tests', 'performance_test']
            },
            
            'lucius': {
                'extra_prompt': """You can automate Microsoft Office applications:
- Excel automation for data analysis
- Word document generation
- PowerPoint presentation creation
- Outlook email automation

IMPORTANT: Always use office tools:
- office.create_excel_report() for Excel
- office.generate_word_document() for Word
- office.create_powerpoint_presentation() for PowerPoint
See examples.create_project_report_excel() for reference.""",
                'tools': ['windows', 'office'],
                'templates': ['excel_report', 'word_template', 'powerpoint_slides']
            }
        }
        
        return enhancements
    
    def _load_templates(self):
        """Carga templates del módulo"""
        templates_path = self.path / "templates"
        
        if not templates_path.exists():
            templates_path.mkdir(parents=True, exist_ok=True)
            self._create_default_templates(templates_path)
            
        # Cargar todos los archivos de templates
        for template_file in templates_path.glob("**/*"):
            if template_file.is_file() and template_file.suffix in ['.yaml', '.yml', '.json', '.xml', '.ps1', '.bat']:
                relative_name = str(template_file.relative_to(templates_path))
                name_without_ext = relative_name.rsplit('.', 1)[0]
                self.templates[name_without_ext] = template_file.read_text()
    
    def _create_default_templates(self, templates_path: Path):
        """Crea templates por defecto si no existen"""
        
        # Template: GitHub Actions Hybrid
        github_actions = templates_path / "github_actions_hybrid.yaml"
        github_actions.write_text("""name: Hybrid CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  linux-build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Build on Linux
      run: |
        make build
        make test
        
  windows-build:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v3
    - name: Build on Windows
      run: |
        msbuild /p:Configuration=Release
        .\\test.exe
        
  cross-platform-test:
    needs: [linux-build, windows-build]
    runs-on: ubuntu-latest
    steps:
    - name: Integration Tests
      run: |
        echo "Running cross-platform integration tests"
""")
        
        # Template: Tauri Config
        tauri_config = templates_path / "tauri_config.json"
        tauri_config.write_text("""{
  "tauri": {
    "bundle": {
      "identifier": "com.batman.app",
      "windows": {
        "certificateThumbprint": null,
        "digestAlgorithm": "sha256",
        "timestampUrl": ""
      }
    },
    "windows": [
      {
        "title": "Batman App",
        "width": 1200,
        "height": 800
      }
    ]
  }
}""")
        
        # Template: Excel Automation
        excel_template = templates_path / "excel_report.ps1"
        excel_template.write_text("""# Excel Report Generation Template
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$workbook = $excel.Workbooks.Add()
$worksheet = $workbook.Worksheets.Item(1)

# Add headers
$worksheet.Cells.Item(1,1) = "Date"
$worksheet.Cells.Item(1,2) = "Metric"
$worksheet.Cells.Item(1,3) = "Value"

# Style headers
$headerRange = $worksheet.Range("A1:C1")
$headerRange.Font.Bold = $true
$headerRange.Interior.ColorIndex = 15

# Add data (customize this section)
# $worksheet.Cells.Item(2,1) = Get-Date
# $worksheet.Cells.Item(2,2) = "Performance"
# $worksheet.Cells.Item(2,3) = 95.5

# Auto-fit columns
$worksheet.UsedRange.EntireColumn.AutoFit()

# Save and close
$workbook.SaveAs("$PWD\\report.xlsx")
$excel.Quit()

[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
""")
        
        # Template: .NET API
        dotnet_api = templates_path / "dotnet_api.csproj"
        dotnet_api.write_text("""<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.AspNetCore.OpenApi" Version="8.0.0" />
    <PackageReference Include="Swashbuckle.AspNetCore" Version="6.5.0" />
  </ItemGroup>
</Project>""")
    
    def suggest_tools_for_task(self, task_description: str) -> Dict[str, Any]:
        """
        Sugiere las mejores herramientas para una tarea específica.
        
        Args:
            task_description: Descripción de la tarea
            
        Returns:
            Dict con herramientas sugeridas y razón
        """
        suggestions = {
            'tools': [],
            'templates': [],
            'reason': []
        }
        
        task_lower = task_description.lower()
        
        # Análisis de la tarea
        if any(word in task_lower for word in ['compilar', 'build', 'compile']):
            suggestions['tools'].append('compiler')
            suggestions['reason'].append('Compilación detectada')
            
        if any(word in task_lower for word in ['windows', 'powershell', 'exe']):
            suggestions['tools'].append('windows')
            suggestions['reason'].append('Operaciones Windows requeridas')
            
        if any(word in task_lower for word in ['excel', 'word', 'office']):
            suggestions['tools'].append('office')
            suggestions['templates'].append('excel_report')
            suggestions['reason'].append('Automatización Office detectada')
            
        if any(word in task_lower for word in ['test', 'prueba', 'testing']):
            suggestions['tools'].append('tester')
            suggestions['templates'].append('cross_platform_tests')
            suggestions['reason'].append('Testing requerido')
            
        if any(word in task_lower for word in ['deploy', 'desplegar', 'publicar']):
            suggestions['tools'].append('deployer')
            suggestions['reason'].append('Deployment detectado')
            
        # Si no hay sugerencias específicas, recomendar windows para interop general
        if not suggestions['tools']:
            suggestions['tools'].append('windows')
            suggestions['reason'].append('Herramienta de interoperabilidad general')
            
        return suggestions
    
    def get_example_code(self, task_description: str) -> str:
        """
        Obtiene código ejemplo para una tarea específica.
        Los agentes deben usar esto en lugar de inventar comandos.
        """
        return get_example_for_task(task_description, self)