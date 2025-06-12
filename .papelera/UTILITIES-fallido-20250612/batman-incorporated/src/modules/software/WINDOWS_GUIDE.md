# 🪟 Guía Definitiva de Windows para Batman

## ⚡ REGLAS DE ORO - NUNCA OLVIDAR

1. **SIEMPRE usa las herramientas del módulo software** - NO inventes comandos
2. **SIEMPRE convierte rutas con wslpath** antes de usarlas en Windows
3. **SIEMPRE usa comillas dobles** para rutas con espacios
4. **NUNCA uses sudo** en comandos Windows
5. **NUNCA asumas que un programa está en PATH** - verifica primero
6. **NO necesitas admin para compilar** - Solo para instalar servicios/IIS

## 📋 Cheatsheet Rápido

```python
# SIEMPRE usar estas herramientas, NO comandos inventados:
from modules.software import SoftwareModule

# Obtener herramienta Windows
windows = module.get_tool('windows')

# ✅ CORRECTO - Ejecutar programa Windows
result = windows.run_windows_exe('notepad.exe', ['archivo.txt'])

# ❌ INCORRECTO - NO hacer esto
subprocess.run(['notepad.exe', 'archivo.txt'])  # MAL!
```

## 🔧 Casos de Uso Comunes

### 1. Ejecutar Programas Windows

```python
# ✅ FORMA CORRECTA - Abrir archivo con programa predeterminado
windows.open_in_windows('/home/user/documento.pdf')

# ✅ FORMA CORRECTA - Ejecutar programa específico
windows.run_windows_exe('code.exe', ['proyecto.py'])

# ✅ FORMA CORRECTA - Programa con ruta completa
windows.run_windows_exe('C:\\Program Files\\App\\app.exe', ['--help'])

# ❌ NUNCA hacer esto
os.system('notepad.exe file.txt')  # MAL!
subprocess.call(['explorer.exe', '.'])  # MAL!
```

### 2. PowerShell - Usa SIEMPRE run_powershell()

```python
# ✅ CORRECTO - Comando simple
result = windows.run_powershell('Get-Date')

# ✅ CORRECTO - Script complejo
script = '''
$files = Get-ChildItem -Path C:\\temp -Filter *.log
foreach ($file in $files) {
    Write-Host "Processing $($file.Name)"
}
'''
result = windows.run_powershell(script)

# ✅ CORRECTO - Con permisos admin
result = windows.run_powershell('Stop-Service servicename', as_admin=True)

# ✅ CORRECTO - Obtener JSON
result = windows.run_powershell(
    'Get-Process | Select-Object Name, CPU',
    output_json=True
)
if result['success']:
    processes = result['data']  # Ya es un dict/list Python

# ❌ NUNCA hacer esto
subprocess.run(['powershell.exe', '-c', 'comando'])  # MAL!
os.system('powershell Get-Date')  # MAL!
```

### 3. Command Prompt (CMD)

```python
# ✅ CORRECTO - Comando simple
result = windows.run_cmd('dir C:\\')

# ✅ CORRECTO - Cambiar directorio y ejecutar
result = windows.run_cmd('npm install', cwd='/home/user/proyecto')

# ✅ CORRECTO - Comandos encadenados
result = windows.run_cmd('cd C:\\proyecto && npm run build')

# ❌ NUNCA hacer esto
subprocess.run(['cmd.exe', '/c', 'dir'])  # MAL!
```

### 4. Compilación de Proyectos - NO REQUIERE ADMIN

⚠️ **IMPORTANTE**: La compilación NUNCA requiere permisos de administrador. Si te piden ejecutar como admin para compilar, algo está mal configurado.

```python
# ✅ CORRECTO - Compilar SIN admin
compiler = module.get_tool('compiler')

# Auto-detecta tipo de proyecto
project_type = compiler.detect_project_type('/home/user/proyecto')

# Compila para Windows - NO necesita admin
result = compiler.compile(
    project_path='/home/user/proyecto',
    target_platform='windows',
    project_type=project_type  # o especificar: 'dotnet', 'cargo', etc.
)

# ❌ NUNCA hacer esto
os.system('msbuild proyecto.csproj')  # MAL!
subprocess.run(['dotnet', 'build'])  # MAL!
windows.run_powershell('dotnet build', as_admin=True)  # MAL! No necesita admin!

# 📌 CUANDO SÍ NECESITAS ADMIN:
# - Instalar/desinstalar servicios Windows
# - Configurar IIS
# - Modificar registro del sistema
# - Instalar software globalmente
# 
# CUANDO NO NECESITAS ADMIN:
# - Compilar cualquier proyecto (npm, dotnet, cargo, etc.)
# - Ejecutar tests
# - Crear archivos/directorios en tu espacio de usuario
# - Ejecutar aplicaciones normales
```

### 5. Conversión de Rutas - SIEMPRE NECESARIA

```python
# ✅ CORRECTO - Convertir ruta WSL a Windows
linux_path = '/home/user/archivo.txt'
win_path = windows.wslpath(linux_path, to_windows=True)
# Resultado: \\wsl.localhost\Ubuntu\home\user\archivo.txt

# ✅ CORRECTO - Convertir ruta Windows a WSL
win_path = 'C:\\Users\\User\\Documents'
linux_path = windows.wslpath(win_path, to_windows=False)
# Resultado: /mnt/c/Users/User/Documents

# ❌ NUNCA pasar rutas Linux directamente a Windows
windows.run_cmd(f'type /home/user/file.txt')  # MAL! Windows no entiende
```

### 6. Archivos Batch (.bat)

```python
# ✅ CORRECTO - Ejecutar .bat existente
result = windows.run_batch('/home/user/script.bat', args=['param1', 'param2'])

# ✅ CORRECTO - Crear y ejecutar .bat temporal
import tempfile

with tempfile.NamedTemporaryFile(suffix='.bat', delete=False, mode='w') as f:
    f.write('''@echo off
echo Hola desde batch
pause
''')
    temp_bat = f.name

result = windows.run_batch(temp_bat)
os.unlink(temp_bat)  # Limpiar

# ❌ NUNCA hacer esto
os.system('script.bat')  # MAL!
```

### 7. Testing Híbrido

```python
# ✅ CORRECTO - Usar el tester del módulo
tester = module.get_tool('tester')

# Ejecutar tests en ambas plataformas
results = tester.run_tests(
    project_path='/home/user/proyecto',
    platforms=['linux', 'windows'],
    test_filter='integration'  # opcional
)

# Verificar resultados
for platform, result in results['platforms'].items():
    if result['success']:
        print(f"{platform}: {result['stats']['passed']}/{result['stats']['total']} passed")
```

### 8. Deployment

```python
# ✅ CORRECTO - Deploy a IIS
deployer = module.get_tool('deployer')

result = deployer.deploy_to_iis(
    app_path='/home/user/webapp',
    site_name='MiSitio',
    port=8080
)

# ✅ CORRECTO - Crear servicio Windows
result = deployer.deploy_windows_service(
    exe_path='/home/user/servicio/app.exe',
    service_name='MiServicio',
    display_name='Mi Servicio App',
    description='Servicio de ejemplo'
)

# ✅ CORRECTO - Tarea programada
result = deployer.create_scheduled_task(
    name='BackupDiario',
    command='C:\\Scripts\\backup.bat',
    schedule='Daily',
    time='02:00'
)
```

### 9. Automatización Office

```python
# ✅ CORRECTO - Crear Excel
office = module.get_tool('office')

data = [
    {'Fecha': '2024-01-01', 'Ventas': 1000, 'Region': 'Norte'},
    {'Fecha': '2024-01-02', 'Ventas': 1500, 'Region': 'Sur'}
]

result = office.create_excel_report(
    data=data,
    output_path='/home/user/reporte.xlsx',
    sheet_name='Ventas',
    auto_format=True
)

# ✅ CORRECTO - Generar Word
content = {
    'title': 'Informe Mensual',
    'paragraphs': [
        'Este es el resumen del mes.',
        'Los resultados fueron positivos.'
    ]
}

result = office.generate_word_document(
    content=content,
    output_path='/home/user/informe.docx'
)
```

### 10. Clipboard (Portapapeles)

```python
# ✅ CORRECTO - Copiar al portapapeles
windows.clipboard_sync(text="Texto a copiar")

# ✅ CORRECTO - Pegar del portapapeles
contenido = windows.clipboard_sync(paste=True)

# ✅ CORRECTO - Copiar archivo al portapapeles
windows.clipboard_sync(file_path='/home/user/codigo.py')
```

## 🚫 ERRORES COMUNES Y SOLUCIONES

### Error: "El sistema no puede encontrar la ruta especificada"
```python
# ❌ PROBLEMA: Ruta Linux en comando Windows
windows.run_cmd('type /home/user/file.txt')

# ✅ SOLUCIÓN: Convertir ruta primero
win_path = windows.wslpath('/home/user/file.txt')
windows.run_cmd(f'type "{win_path}"')
```

### Error: "No se reconoce como comando interno o externo"
```python
# ❌ PROBLEMA: Programa no está en PATH
windows.run_windows_exe('codigo.exe')

# ✅ SOLUCIÓN: Usar ruta completa o verificar primero
if windows.available_tools.get('code.exe'):
    windows.run_windows_exe('code.exe', ['archivo.py'])
else:
    # Usar ruta completa
    windows.run_windows_exe('C:\\Program Files\\VS Code\\Code.exe', ['archivo.py'])
```

### Error: "Acceso denegado"
```python
# ❌ PROBLEMA: Necesita permisos de administrador
windows.run_powershell('Stop-Service MiServicio')

# ✅ SOLUCIÓN: Usar as_admin=True
windows.run_powershell('Stop-Service MiServicio', as_admin=True)
```

### Error: "La sintaxis del comando no es correcta"
```python
# ❌ PROBLEMA: Espacios en rutas sin comillas
windows.run_cmd('cd C:\\Program Files\\App')

# ✅ SOLUCIÓN: Siempre usar comillas
windows.run_cmd('cd "C:\\Program Files\\App"')
```

## 📚 Plantillas para Agentes

### Para Alfred (Backend/Servicios)
```python
# Deploy de API .NET a IIS
if task.involves('deploy', 'api', 'windows'):
    windows = self.module_tools.get_tool('windows')
    deployer = self.module_tools.get_tool('deployer')
    
    # Compilar proyecto
    result = windows.compile_project('dotnet', project_path)
    
    # Deploy a IIS
    if result['success']:
        deployer.deploy_to_iis(
            app_path=project_path,
            site_name='MyAPI',
            port=5000
        )
```

### Para Robin (DevOps)
```python
# CI/CD Pipeline híbrido
if task.involves('pipeline', 'ci/cd'):
    windows = self.module_tools.get_tool('windows')
    
    # Crear tarea programada para builds nocturnos
    windows.create_scheduled_task(
        name='NightlyBuild',
        command='C:\\CI\\build.bat',
        schedule='Daily',
        time='03:00'
    )
```

### Para Batgirl (Frontend)
```python
# Build de app Electron para Windows
if task.involves('electron', 'build'):
    compiler = self.module_tools.get_tool('compiler')
    
    result = compiler.compile(
        project_path=app_path,
        target_platform='windows',
        project_type='electron'
    )
```

### Para Oracle (Testing)
```python
# Tests multiplataforma
if task.involves('test', 'cross-platform'):
    tester = self.module_tools.get_tool('tester')
    
    results = tester.run_tests(
        project_path=project_path,
        platforms=['linux', 'windows']
    )
    
    # Generar reporte
    self.generate_test_report(results)
```

### Para Lucius (Research/Docs)
```python
# Generar documentación en Word
if task.involves('documentation', 'report'):
    office = self.module_tools.get_tool('office')
    
    # Analizar código y generar stats
    stats = self.analyze_codebase(project_path)
    
    # Crear reporte Excel
    office.create_excel_report(
        data=stats,
        output_path='code_analysis.xlsx'
    )
```

## 🎯 Resumen: Las 10 Reglas de Oro

1. **USA SIEMPRE** las herramientas del módulo, NO subprocess directo
2. **CONVIERTE SIEMPRE** las rutas con wslpath()
3. **USA COMILLAS DOBLES** para rutas con espacios
4. **VERIFICA** que los programas existen antes de ejecutarlos
5. **USA run_powershell()** para PowerShell, NO subprocess
6. **USA run_cmd()** para CMD, NO os.system()
7. **USA as_admin=True** cuando necesites permisos elevados
8. **USA output_json=True** para obtener datos estructurados
9. **MANEJA ERRORES** - verifica result['success']
10. **NO INVENTES** - si no está en esta guía, pregunta primero

## 💡 Debugging

Si algo no funciona:
1. Verifica que el módulo software esté cargado
2. Usa `windows.get_system_info()` para ver herramientas disponibles
3. Revisa result['stderr'] para mensajes de error
4. Convierte las rutas - es el error más común
5. Verifica permisos - usa as_admin si es necesario