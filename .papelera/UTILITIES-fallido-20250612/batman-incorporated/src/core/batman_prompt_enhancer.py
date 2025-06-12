"""
Sistema para mejorar los prompts que Batman da a los agentes Claude.
Asegura que los agentes usen todas las capacidades disponibles.
"""

from typing import Dict, List, Optional
from pathlib import Path


class BatmanPromptEnhancer:
    """Mejora los prompts para que Claude use Batman completamente."""
    
    def __init__(self, task_description: str, context_path: Optional[str] = None,
                 module_name: Optional[str] = None, mode: str = "safe"):
        self.task_description = task_description
        self.context_path = context_path or str(Path.cwd())
        self.module_name = module_name
        self.mode = mode
        
    def enhance_task_prompt(self) -> str:
        """
        Mejora la descripción de la tarea con información específica
        para que los agentes aprovechen todas las capacidades.
        """
        enhanced = f"{self.task_description}\n\n"
        
        # Agregar contexto del proyecto
        enhanced += f"📁 CONTEXTO DEL PROYECTO:\n"
        enhanced += f"- Ruta: {self.context_path}\n"
        
        # Detectar tipo de proyecto
        project_indicators = self._detect_project_type()
        if project_indicators:
            enhanced += f"- Tipo detectado: {', '.join(project_indicators)}\n"
            
        # Agregar capacidades del módulo si existe
        if self.module_name:
            enhanced += f"\n🔧 MÓDULO ACTIVO: {self.module_name}\n"
            enhanced += self._get_module_capabilities()
            
        # Agregar instrucciones específicas del modo
        enhanced += f"\n🎯 MODO DE EJECUCIÓN: {self.mode}\n"
        enhanced += self._get_mode_instructions()
        
        # Agregar recordatorios importantes
        enhanced += "\n⚠️ RECORDATORIOS IMPORTANTES:\n"
        enhanced += "- Usa las herramientas del módulo, NO subprocess directo\n"
        enhanced += "- Verifica que los archivos existen antes de modificarlos\n"
        enhanced += "- Commitea cambios incrementalmente\n"
        enhanced += "- Documenta decisiones importantes\n"
        
        return enhanced
    
    def enhance_agent_prompt(self, agent_name: str, base_prompt: str) -> str:
        """
        Mejora el prompt específico de cada agente con instrucciones
        detalladas según su rol.
        """
        enhanced = base_prompt + "\n\n"
        
        # Instrucciones específicas por agente
        agent_instructions = {
            'alfred': """
🎩 INSTRUCCIONES ESPECÍFICAS PARA ALFRED:
- Eres el arquitecto senior, diseña primero antes de implementar
- Usa patrones de diseño apropiados (SOLID, DRY, KISS)
- Si el módulo software está activo, usa sus herramientas para:
  * Compilación: compiler.compile()
  * Deployment: deployer.deploy_to_iis()
  * Windows: windows.run_powershell()
- Documenta decisiones arquitectónicas en comentarios
- Considera escalabilidad y mantenibilidad
""",
            'robin': """
🐦 INSTRUCCIONES ESPECÍFICAS PARA ROBIN:
- Eres el experto en DevOps e infraestructura
- Automatiza todo lo que puedas
- Si el módulo software está activo:
  * Crea pipelines CI/CD híbridos
  * Usa deployer.create_scheduled_task()
  * Configura scripts de build multiplataforma
- Asegura que los entornos sean reproducibles
- Implementa health checks y monitoring
""",
            'oracle': """
🔮 INSTRUCCIONES ESPECÍFICAS PARA ORACLE:
- Eres el guardián de la calidad y seguridad
- Escribe tests para TODO el código nuevo
- Si el módulo software está activo:
  * Usa tester.run_tests(platforms=['linux', 'windows'])
  * Implementa tests de seguridad
  * Verifica en ambas plataformas
- Busca vulnerabilidades y edge cases
- Mantén cobertura de tests > 80%
""",
            'batgirl': """
🦇 INSTRUCCIONES ESPECÍFICAS PARA BATGIRL:
- Eres la experta en frontend y UX
- Prioriza la experiencia del usuario
- Si el módulo software está activo:
  * Usa compiler.compile() para Electron/Tauri
  * Implementa builds para múltiples plataformas
  * Optimiza para Windows y Linux
- Asegura accesibilidad (WCAG 2.1)
- Implementa diseño responsive
""",
            'lucius': """
🔬 INSTRUCCIONES ESPECÍFICAS PARA LUCIUS:
- Eres el investigador y documentador
- Analiza el código existente antes de proponer cambios
- Si el módulo software está activo:
  * Usa office.create_excel_report() para métricas
  * Genera documentación en Word con office tools
  * Automatiza reportes
- Mantén documentación actualizada
- Sugiere optimizaciones basadas en datos
"""
        }
        
        if agent_name in agent_instructions:
            enhanced += agent_instructions[agent_name]
            
        # Agregar ejemplos de código si hay módulo
        if self.module_name == "software":
            enhanced += self._get_software_module_examples(agent_name)
            
        return enhanced
    
    def _detect_project_type(self) -> List[str]:
        """Detecta indicadores del tipo de proyecto."""
        indicators = []
        project_path = Path(self.context_path)
        
        # Archivos indicadores
        file_indicators = {
            'package.json': 'Node.js',
            'Cargo.toml': 'Rust',
            '*.csproj': '.NET',
            'requirements.txt': 'Python',
            'go.mod': 'Go',
            'pom.xml': 'Java/Maven',
            'build.gradle': 'Java/Gradle',
            'CMakeLists.txt': 'C++/CMake',
            'Makefile': 'Make',
            'docker-compose.yml': 'Docker',
            '.github/workflows': 'GitHub Actions',
            'src-tauri': 'Tauri',
            'electron': 'Electron'
        }
        
        for pattern, project_type in file_indicators.items():
            if '*' in pattern:
                if list(project_path.glob(pattern)):
                    indicators.append(project_type)
            else:
                if (project_path / pattern).exists():
                    indicators.append(project_type)
                    
        return indicators
    
    def _get_module_capabilities(self) -> str:
        """Retorna las capacidades del módulo activo."""
        if self.module_name == "software":
            return """
Capacidades disponibles:
- Windows Interop: Ejecución de comandos Windows, PowerShell, CMD
- Compilación: Multi-plataforma (dotnet, cargo, npm, tauri, electron)
- Testing: Ejecución en Linux y Windows simultáneamente
- Deployment: IIS, servicios Windows, tareas programadas
- Office: Automatización de Excel, Word, PowerPoint
- Herramientas: Conversión de rutas, clipboard, shortcuts

IMPORTANTE: Usa las herramientas del módulo, NO subprocess directo.
Ejemplo: windows.run_powershell() en lugar de subprocess.run(['powershell'])
"""
        return ""
    
    def _get_mode_instructions(self) -> str:
        """Retorna instrucciones específicas del modo."""
        mode_instructions = {
            'safe': """
- Trabajarás en un git worktree aislado
- Puedes experimentar sin afectar main
- Los cambios se mergearán al final
- Ideal para desarrollo normal
""",
            'fast': """
- Trabajarás directamente en la rama actual
- Ten cuidado con los cambios
- Commitea frecuentemente
- Ideal para hotfixes rápidos
""",
            'infinity': """
- Múltiples agentes trabajarán en paralelo
- Coordina a través de archivos compartidos
- Puede tomar varias horas
- Ideal para tareas complejas
""",
            'redundant': """
- Múltiples agentes verificarán tu trabajo
- Implementa con máxima calidad
- Otro agente revisará tu código
- Ideal para código crítico
"""
        }
        return mode_instructions.get(self.mode, "")
    
    def _get_software_module_examples(self, agent_name: str) -> str:
        """Retorna ejemplos específicos del módulo software por agente."""
        examples = {
            'alfred': """

EJEMPLOS DE CÓDIGO PARA ALFRED:
```python
# Compilar proyecto .NET
compiler = self.module_tools.get_tool('compiler')
result = compiler.compile(
    project_path='/path/to/project',
    target_platform='windows',
    project_type='dotnet'
)

# Deploy a IIS
deployer = self.module_tools.get_tool('deployer')
result = deployer.deploy_to_iis(
    app_path='/path/to/app',
    site_name='MiAPI',
    port=5000
)
```
""",
            'robin': """

EJEMPLOS DE CÓDIGO PARA ROBIN:
```python
# Crear tarea programada
deployer = self.module_tools.get_tool('deployer')
result = deployer.create_scheduled_task(
    name='NightlyBuild',
    command='C:\\\\scripts\\\\build.bat',
    schedule='Daily',
    time='03:00'
)

# Pipeline CI/CD híbrido
windows = self.module_tools.get_tool('windows')
# Compilar en Windows
win_result = windows.compile_project('npm', project_path)
# Tests en Linux
linux_result = subprocess.run(['npm', 'test'], capture_output=True)
```
""",
            'oracle': """

EJEMPLOS DE CÓDIGO PARA ORACLE:
```python
# Tests multiplataforma
tester = self.module_tools.get_tool('tester')
results = tester.run_tests(
    project_path='/path/to/project',
    platforms=['linux', 'windows'],
    test_filter='security'
)

# Análisis de cobertura
coverage_linux = tester.run_coverage(project_path, 'linux')
coverage_windows = tester.run_coverage(project_path, 'windows')
```
""",
            'batgirl': """

EJEMPLOS DE CÓDIGO PARA BATGIRL:
```python
# Build Electron para Windows
compiler = self.module_tools.get_tool('compiler')
result = compiler.compile(
    project_path='/path/to/electron-app',
    target_platform='windows',
    project_type='electron'
)

# Build Tauri multiplataforma
deployer = self.module_tools.get_tool('deployer')
result = deployer.deploy_electron_app(
    app_path='/path/to/app',
    platforms=['win32', 'linux']
)
```
""",
            'lucius': """

EJEMPLOS DE CÓDIGO PARA LUCIUS:
```python
# Generar reporte Excel
office = self.module_tools.get_tool('office')
data = analyze_codebase()  # Tu análisis
result = office.create_excel_report(
    data=data,
    output_path='analysis.xlsx',
    sheet_name='Métricas',
    auto_format=True
)

# Documentación en Word
content = {
    'title': 'Análisis de Arquitectura',
    'paragraphs': findings
}
result = office.generate_word_document(
    content=content,
    output_path='architecture.docx'
)
```
"""
        }
        return examples.get(agent_name, "")