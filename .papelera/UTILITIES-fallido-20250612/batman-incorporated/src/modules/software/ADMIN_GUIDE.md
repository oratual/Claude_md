# 🔐 Guía de Permisos Administrativos - CUÁNDO SÍ y CUÁNDO NO

## ❌ NO NECESITAS ADMIN PARA:

### Compilación y Desarrollo
- ✅ `npm install` / `npm run build`
- ✅ `dotnet build` / `dotnet run`
- ✅ `cargo build` / `cargo run`
- ✅ `msbuild proyecto.csproj`
- ✅ `gradle build`
- ✅ `maven compile`
- ✅ Compilar Tauri, Electron, o cualquier app
- ✅ Ejecutar tests
- ✅ Generar documentación

### Operaciones de Archivo
- ✅ Crear/modificar archivos en tu directorio home
- ✅ Crear directorios en tu espacio de usuario
- ✅ Leer/escribir en `/home/usuario/*`
- ✅ Acceder a `/mnt/c/Users/TuUsuario/*`

### Ejecución de Programas
- ✅ Ejecutar aplicaciones normales
- ✅ Abrir IDEs (VS Code, Visual Studio, etc.)
- ✅ Ejecutar scripts Python, Node.js, etc.
- ✅ Usar Git, npm, cargo, dotnet CLI

## ✅ SÍ NECESITAS ADMIN PARA:

### Servicios Windows
```python
# Instalar servicio - SÍ necesita admin
deployer.deploy_windows_service(exe_path, service_name)  # as_admin=True interno

# Detener/iniciar servicios del sistema
windows.run_powershell('Stop-Service W3SVC', as_admin=True)
```

### IIS (Internet Information Services)
```python
# Configurar sitios IIS - SÍ necesita admin
deployer.deploy_to_iis(app_path, site_name)  # as_admin=True interno

# Crear application pools
windows.run_powershell('New-WebAppPool -Name "MiPool"', as_admin=True)
```

### Registro de Windows
```python
# Modificar HKEY_LOCAL_MACHINE - SÍ necesita admin
windows.run_powershell(
    'New-ItemProperty -Path "HKLM:\\SOFTWARE\\MiApp" -Name "Config" -Value "123"',
    as_admin=True
)

# Leer HKEY_CURRENT_USER - NO necesita admin
windows.run_powershell('Get-ItemProperty HKCU:\\SOFTWARE\\MiApp')
```

### Instalación Global
```python
# Instalar software para todos los usuarios - SÍ necesita admin
windows.run_powershell('choco install nodejs', as_admin=True)

# Instalar en espacio de usuario - NO necesita admin
windows.run_cmd('npm install -g typescript')  # Va a AppData\Roaming\npm
```

### Firewall y Red
```python
# Abrir puertos en firewall - SÍ necesita admin
windows.run_powershell(
    'New-NetFirewallRule -DisplayName "MiApp" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow',
    as_admin=True
)
```

## 🚨 ERRORES COMUNES

### Error: "Could not find a part of the path"
**Causa**: Intentando escribir en C:\Program Files sin admin
**Solución**: NO compiles ahí. Usa tu directorio home.

### Error: "Access to the path is denied"
**Posibles causas**:
1. Archivo en uso por otro proceso
2. Intentando escribir en directorio del sistema
3. Permisos NTFS incorrectos

**NO es porque necesites admin para compilar**

### Error: "This operation requires elevation"
**Significa**: Realmente necesitas admin
**Verifica**: ¿Estás instalando un servicio o modificando el sistema?

## 📋 Checklist Rápido

¿Necesito admin?

- [ ] ¿Estoy compilando código? → **NO**
- [ ] ¿Estoy instalando un servicio Windows? → **SÍ**
- [ ] ¿Estoy configurando IIS? → **SÍ**
- [ ] ¿Estoy modificando HKLM en el registro? → **SÍ**
- [ ] ¿Estoy ejecutando npm/dotnet/cargo build? → **NO**
- [ ] ¿Estoy creando archivos en mi home? → **NO**
- [ ] ¿Estoy abriendo puertos en el firewall? → **SÍ**

## 💡 Regla de Oro

> Si estás compilando o desarrollando, NO necesitas admin.
> Si estás instalando servicios o modificando el sistema, SÍ necesitas admin.

## 🔧 Alternativas Sin Admin

### En lugar de instalar un servicio:
```python
# Opción 1: Ejecutar como aplicación de consola
windows.run_cmd('node server.js')

# Opción 2: Usar PM2 (no requiere admin)
windows.run_cmd('pm2 start app.js')

# Opción 3: Tarea programada en espacio de usuario
windows.run_powershell('''
$action = New-ScheduledTaskAction -Execute "node" -Argument "C:\\app\\server.js"
$trigger = New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -TaskName "MiApp" -Action $action -Trigger $trigger
''')  # Sin as_admin=True, se crea para el usuario actual
```

### En lugar de IIS:
```python
# Usar servidor web integrado (desarrollo)
windows.run_cmd('npm run dev -- --port 3000')

# Usar http-server simple
windows.run_cmd('npx http-server -p 8080')
```

## ⚠️ IMPORTANTE PARA BATMAN

Cuando un agente sugiera usar `as_admin=True` para compilación:

1. **DETENTE** - La compilación NO necesita admin
2. **REVISA** - ¿Qué error exacto estás viendo?
3. **CORRIGE** - Probablemente es un problema de rutas o permisos de archivo

Ejemplo correcto:
```python
# Compilar DiskDominator - NO necesita admin
compiler = module.get_tool('compiler')
result = compiler.compile(
    project_path='/home/lauta/glados/DiskDominator',
    target_platform='windows',
    project_type='tauri'
)

# Si falla, NO agregues as_admin=True
# En su lugar, verifica:
# - ¿Existe el proyecto?
# - ¿Están instaladas las dependencias?
# - ¿Hay espacio en disco?
# - ¿El archivo está bloqueado?
```