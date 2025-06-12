# WSL2-Windows Interoperability Guide

## 📋 Resumen Ejecutivo
WSL2 puede ejecutar aplicaciones Windows directamente sin necesidad de SSH, PowerShell Remoting o configuraciones complejas. La interoperabilidad está habilitada por defecto y permite ejecución bidireccional completa.

## ✅ Capacidades Confirmadas

### 1. Ejecución Directa de Ejecutables Windows
```bash
# Programas del sistema
notepad.exe
calc.exe
explorer.exe .
mspaint.exe

# Programas instalados (en PATH)
code.exe archivo.txt
chrome.exe https://google.com

# Con rutas completas
/mnt/c/Windows/System32/ipconfig.exe
/mnt/c/Program\ Files/Mozilla\ Firefox/firefox.exe
```

### 2. Command Prompt (CMD)
```bash
# Ejecutar comandos simples
cmd.exe /c "echo Hola Windows"
cmd.exe /c "dir C:\\"
cmd.exe /c "systeminfo"

# Ejecutar archivos .bat
cmd.exe /c "$(wslpath -w archivo.bat)"
cmd.exe /c "C:\\ruta\\archivo.bat"

# Comandos encadenados
cmd.exe /c "cd C:\\proyecto && npm install"
```

### 3. PowerShell
```bash
# Comandos simples
powershell.exe -c "Get-Date"
powershell.exe -c "Get-Process | Where-Object {$_.CPU -gt 10}"

# Scripts complejos
powershell.exe -c "
    Write-Host 'Iniciando proceso...' -ForegroundColor Green
    Get-ChildItem C:\\ | Select-Object -First 5
"

# Ejecutar scripts .ps1
powershell.exe -ExecutionPolicy Bypass -File "$(wslpath -w script.ps1)"

# Comandos como administrador (requiere UAC)
powershell.exe -c "Start-Process powershell -Verb RunAs"
```

### 4. Conversión de Rutas
```bash
# WSL a Windows
wslpath -w /home/lauta/archivo.txt
# Resultado: \\wsl.localhost\Ubuntu-24.04\home\lauta\archivo.txt

# Windows a WSL
wslpath -u "C:\\Users\\lauta\\Documents"
# Resultado: /mnt/c/Users/lauta/Documents

# Ruta actual en formato Windows
wslpath -w $(pwd)
```

### 5. Archivos Batch (.bat)
```bash
# Crear y ejecutar .bat desde WSL
cat > test.bat << 'EOF'
@echo off
echo Ejecutado desde WSL
pause
EOF

cmd.exe /c "$(wslpath -w test.bat)"

# Wrapper para facilitar ejecución
alias run-bat='cmd.exe /c "$(wslpath -w "$1")"'
```

### 6. Interacción con GUI Windows
```bash
# Abrir explorador en directorio actual
explorer.exe .

# Abrir archivo con programa predeterminado
wslview documento.pdf
wslview imagen.png
wsl-open pagina.html

# Abrir URL en navegador predeterminado
wslview https://github.com

# Portapapeles de Windows
echo "texto" | clip.exe
powershell.exe -c "Get-Clipboard"
```

### 7. Compilación y Ejecución de Proyectos
```bash
# Node.js/npm en Windows
cmd.exe /c "cd C:\\proyecto && npm install"
cmd.exe /c "cd C:\\proyecto && npm run build"

# Cargo/Rust
cmd.exe /c "cd C:\\proyecto && cargo build --release"
/mnt/c/proyecto/target/release/app.exe

# Tauri
powershell.exe -c "cd $(wslpath -w $(pwd)); npm run tauri dev"

# .NET
cmd.exe /c "dotnet build C:\\proyecto\\app.csproj"
```

### 8. Procesos y Servicios Windows
```bash
# Ver procesos
powershell.exe -c "Get-Process"
tasklist.exe

# Matar proceso
taskkill.exe /F /IM notepad.exe

# Servicios Windows
powershell.exe -c "Get-Service | Where-Object {$_.Status -eq 'Running'}"
sc.exe query

# Información del sistema
systeminfo.exe
powershell.exe -c "Get-ComputerInfo"
```

### 9. Registro de Windows
```bash
# Leer registro
reg.exe query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion"

# PowerShell para registro
powershell.exe -c "Get-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion"

# Exportar registro
reg.exe export "HKLM\SOFTWARE\MyApp" backup.reg
```

### 10. Automatización Avanzada
```bash
# Crear tarea programada
schtasks.exe /Create /TN "MiTarea" /TR "C:\\script.bat" /SC DAILY

# WMI queries
wmic.exe cpu get name,numberofcores,maxclockspeed

# Eventos de Windows
powershell.exe -c "Get-EventLog -LogName Application -Newest 10"
```

## ⚠️ Limitaciones Conocidas

### 1. Rutas UNC
- CMD.exe no puede usar rutas UNC como directorio de trabajo
- Siempre vuelve a C:\Windows o usa rutas locales
- Solución: Usar `wslpath -w` para convertir rutas

### 2. Permisos y UAC
- Operaciones que requieren elevación mostrarán prompt UAC
- No se puede bypassear UAC desde WSL
- Solución: Usuario debe aprobar manualmente

### 3. Variables de Entorno
- Las variables de WSL no se pasan automáticamente a Windows
- PATH de Windows está disponible en WSL si `appendWindowsPath=true`
- Solución: Pasar variables explícitamente

### 4. Encoding
- Posibles problemas con caracteres especiales entre sistemas
- UTF-8 en WSL vs. codepage en Windows
- Solución: Usar `-Encoding UTF8` en PowerShell

### 5. Procesos en Background
- Procesos Windows iniciados desde WSL pueden terminar si se cierra terminal
- No heredan el control de jobs de Linux
- Solución: Usar `start /b` o `nohup` equivalentes

## 🛠️ Funciones Helper Recomendadas

```bash
# Agregar a ~/.bashrc

# Ejecutar cualquier .exe con logs
winexe() {
    echo "[$(date)] Ejecutando: $@" >> ~/.winexe.log
    "$@" 2>&1 | tee -a ~/.winexe.log
}

# Compilar y ejecutar en Windows
winbuild() {
    local project_dir=$(wslpath -w $(pwd))
    powershell.exe -c "cd '$project_dir'; $*"
}

# Abrir en VS Code Windows
wincode() {
    code.exe $(wslpath -w "${1:-.}")
}

# Clipboard bidireccional
winclip() {
    if [ -t 0 ]; then
        powershell.exe -c "Get-Clipboard"
    else
        clip.exe
    fi
}
```

## 📊 Configuración Óptima

### /etc/wsl.conf
```ini
[interop]
enabled = true
appendWindowsPath = true

[network]
generateHosts = true
generateResolvConf = true
```

### Verificar Estado
```bash
# Comprobar interop
cat /etc/wsl.conf | grep -A2 "\[interop\]"

# Ver PATH de Windows
echo $PATH | tr ':' '\n' | grep -E "(mnt|Program)"

# Test rápido
cmd.exe /c "echo OK" && echo "✅ Interop funcionando"
```

## 🚀 Casos de Uso Avanzados

### 1. CI/CD Híbrido
```bash
# Compilar en Windows, testear en Linux
cmd.exe /c "msbuild project.sln"
./run-tests.sh

# Deploy desde WSL a IIS
powershell.exe -c "Import-Module WebAdministration; ..."
```

### 2. Desarrollo Full Stack
```bash
# Backend en WSL, frontend build en Windows
npm run dev --host 0.0.0.0 &
cmd.exe /c "cd frontend && npm run build-windows"
```

### 3. Automatización de Office
```bash
# Generar Excel desde WSL
powershell.exe -c "
    \$excel = New-Object -ComObject Excel.Application
    \$workbook = \$excel.Workbooks.Add()
    # ... manipular Excel ...
    \$workbook.SaveAs('C:\\report.xlsx')
    \$excel.Quit()
"
```

## 📝 Notas Finales

- La interoperabilidad WSL2-Windows es bidireccional y completa
- No requiere configuración adicional en instalaciones estándar
- Performance overhead es mínimo para la mayoría de operaciones
- Ideal para flujos de trabajo híbridos Linux/Windows

**Última actualización**: $(date +%Y-%m-%d)