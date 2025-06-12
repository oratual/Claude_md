# Windows Interoperability Test Results

**Test Environment**: WSL2 Ubuntu 24.04 on Windows 11
**Test Date**: Wednesday, June 11, 2025 23:20:59 CEST
**Test Directory**: `/home/lauta/glados/test-windows-interop/`

## Executive Summary

- ✅ **Batch files (.bat)**: Execute successfully via `cmd.exe` with `wslpath -w` conversion
- ✅ **PowerShell scripts (.ps1)**: Execute successfully with `powershell.exe -File`
- ⚠️ **VBScript (.vbs)**: `cscript.exe` times out, `wscript.exe` runs in background
- ✅ **Windows Script Files (.wsf)**: Execute successfully with `cscript.exe`
- ⚠️ **HTA Applications (.hta)**: Launch with `wslview` but no console output
- ⚠️ **CMD files (.cmd)**: Execute with limitations (wmic not available, path issues)
- ✅ **Pipes**: Bidirectional pipes work between WSL and Windows commands
- ⚠️ **UNC Path Warning**: All executions show "CMD.EXE started with UNC path" warning

## Detailed Test Results

### 1. Batch Files (.bat)

#### test1.bat - Basic Batch File
**Timestamp**: 23:21:24
**Command**: `cmd.exe /c "$(wslpath -w test1.bat)"`
**Result**: ✅ SUCCESS
**Output**:
```
=== Test 1: Archivo BAT Básico ===
Fecha: 11/06/2025
Hora: 23:21:24,18
Usuario: lauta
Directorio: C:\Windows
[Lists Windows directory contents]
Test completado!
```
**Notes**: 
- UNC path warning appears but script executes
- Working directory defaults to C:\Windows
- All batch commands execute correctly

#### test2.bat - Batch with Logic
**Timestamp**: 23:21:30
**Command**: `cmd.exe /c "$(wslpath -w test2.bat)"`
**Result**: ✅ SUCCESS
**Output**:
```
=== Test 2: BAT con Lógica ===
Iteración: 1
Iteración: 2
Iteración: 3
[OK] Directorio Windows encontrado
Test finalizado con 3 iteraciones
```
**Notes**: FOR loops and IF conditions work correctly

### 2. PowerShell Scripts (.ps1)

#### script1.ps1 - Basic PowerShell
**Timestamp**: 23:21:38
**Command**: `powershell.exe -File "$(wslpath -w script1.ps1)"`
**Result**: ✅ SUCCESS
**Output**:
```
=== Test PowerShell 1 ===
Fecha: 06/11/2025 23:21:38
Usuario: lauta
Computadora: CEREBRO
Sistema: Microsoft Windows 11 Pro
Versión: 10.0.26100
[Top 5 processes by CPU listed]
```
**Notes**: Full access to Windows system information

#### script2.ps1 - PowerShell with Parameters
**Timestamp**: 23:21:45
**Command**: `powershell.exe -ExecutionPolicy Bypass -File "$(wslpath -w script2.ps1)" TestParam`
**Result**: ✅ SUCCESS
**Output**:
```
=== System Information ===
OS: Microsoft Windows 11 Pro 10.0.26100
Architecture: 64 bits
[Network information displayed]
=== Message ===
TestParam
Created file: C:\Users\lauta\AppData\Local\Temp\test_from_ps.txt
```
**Notes**: Parameters pass correctly, file creation works

### 3. VBScript Files (.vbs)

#### hello.vbs - Interactive VBScript
**Timestamp**: 23:22:00
**Command**: `cscript.exe //NoLogo "$(wslpath -w hello.vbs)"`
**Result**: ❌ TIMEOUT (2 minutes)
**Notes**: Script likely waiting for user interaction (MsgBox)

**Alternative Command**: `wscript.exe "$(wslpath -w hello.vbs)" &`
**Result**: ⚠️ BACKGROUND EXECUTION
**Notes**: Runs in background, likely displays GUI dialog

### 4. HTA Applications (.hta)

#### app.hta - HTML Application
**Timestamp**: 23:24:00
**Command**: `wslview app.hta`
**Result**: ⚠️ NO CONSOLE OUTPUT
**Notes**: Application launches in Windows but provides no console feedback

### 5. Windows Script Files (.wsf)

#### mixed.wsf - Mixed VBScript/JScript
**Timestamp**: 23:25:04
**Command**: `cscript.exe //NoLogo "$(wslpath -w mixed.wsf)"`
**Result**: ✅ SUCCESS
**Output**:
```
Parte VBScript del WSF
Sistema: Windows_NT
Parte JScript del WSF
Fecha JavaScript: Wed Jun 11 23:25:04 UTC+0200 2025
Archivo creado en: C:\Users\lauta\AppData\Local\Temp\wsl_test.txt
```
**Notes**: Both VBScript and JScript sections execute correctly

### 6. CMD Files (.cmd)

#### advanced.cmd - Advanced CMD Script
**Timestamp**: 23:25:20
**Command**: `cmd.exe /c "$(wslpath -w advanced.cmd)"`
**Result**: ⚠️ PARTIAL SUCCESS
**Output**:
```
=== Test CMD Avanzado ===
"wmic" no se reconoce como un comando interno o externo
Timestamp: [garbled due to parsing error]
Version Windows: 10.0
[PowerShell execution successful]
[OK] Conectividad Internet 
CMD avanzado completado!
```
**Issues**:
- WMIC not available in current environment
- Date/time parsing failed
- File creation failed due to invalid filename

### 7. Windows Applications

#### notepad.exe
**Command**: `notepad.exe &`
**Result**: ❌ TIMEOUT
**Notes**: GUI application blocks console

#### calc.exe
**Command**: `calc.exe &`
**Result**: ✅ LAUNCHES
**Notes**: Calculator opens in Windows

#### explorer.exe
**Command**: `explorer.exe .`
**Result**: ❌ ERROR
**Notes**: Cannot open UNC paths directly

### 8. Pipes and Redirection

#### WSL to Windows Pipe
**Command**: `echo "Test from WSL" | cmd.exe /c "findstr Test"`
**Result**: ✅ SUCCESS
**Output**: `Test from WSL`

#### Windows to WSL Pipe
**Command**: `cmd.exe /c "echo Test from Windows" | grep Windows`
**Result**: ✅ SUCCESS
**Output**: `Test from Windows`

### 9. File Creation from Windows

#### creator.bat
**Command**: `cmd.exe /c "$(wslpath -w creator.bat)"`
**Result**: ❌ ACCESS DENIED
**Notes**: Cannot create files in C:\Windows (default directory)

## Key Findings

### Working Methods
1. **Best Practice**: Use `wslpath -w` to convert paths before passing to Windows executables
2. **Batch/CMD**: `cmd.exe /c "$(wslpath -w script.bat)"`
3. **PowerShell**: `powershell.exe -File "$(wslpath -w script.ps1)"`
4. **WSF/VBS Console**: `cscript.exe //NoLogo "$(wslpath -w script.wsf)"`
5. **GUI Applications**: Use `wslview` for .hta and other GUI files

### Common Issues
1. **UNC Path Warning**: Always appears but doesn't prevent execution
2. **Working Directory**: Defaults to C:\Windows (may cause permission issues)
3. **GUI Applications**: Block console or timeout when run synchronously
4. **WMIC**: Not available in some Windows environments
5. **File Creation**: Limited by Windows permissions in default directory

### Recommendations
1. Use absolute Windows paths via `wslpath -w`
2. Run GUI applications with `&` or use `wslview`
3. For file operations, specify full paths to writable directories
4. Use `-ExecutionPolicy Bypass` for unsigned PowerShell scripts
5. Prefer `cscript.exe` over `wscript.exe` for console output

## Test Files Created
- test1.bat - Basic batch commands
- test2.bat - Batch with logic (FOR, IF)
- script1.ps1 - PowerShell system info
- script2.ps1 - PowerShell with parameters
- hello.vbs - VBScript with GUI
- system.vbs - VBScript system access
- app.hta - HTML Application
- mixed.wsf - Multi-language script
- advanced.cmd - Complex CMD script
- creator.bat - File creation test

All test files remain in `/home/lauta/glados/test-windows-interop/` for future reference.