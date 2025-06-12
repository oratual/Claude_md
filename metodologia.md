# Metodología para Compilar DiskDominator en Windows

## 📅 Fecha: 2025-01-11
## 🎯 Objetivo: Compilar aplicación Tauri (Next.js + Rust) para Windows

## ✅ Lo que Funciona

### 1. **Sincronización WSL → Windows**
```bash
c2w  # Sincroniza /home/lauta/glados/DiskDominator → K:\_Glados\DiskDominator
```

### 2. **Ejecución de Comandos Windows desde WSL**
```bash
# PowerShell
powershell.exe -c "comando"

# CMD
cmd.exe /c "comando"

# Aplicaciones HTA (interfaces gráficas)
mshta.exe "archivo.hta"
```

### 3. **Build de Next.js**
- ✅ `npm install` funciona correctamente
- ✅ `npm run build` compila sin errores
- ✅ Todos los errores TypeScript fueron resueltos

## ❌ Problemas Encontrados

### 1. **Error Principal: dlltool.exe not found**
- **Causa**: Rust está usando toolchain GNU (x86_64-pc-windows-gnu) en lugar de MSVC
- **Síntoma**: `error: Error calling dlltool 'dlltool.exe': program not found`
- **Contexto**: Ocurre al compilar dependencias de Rust que usan C (como getrandom)

### 2. **Configuración de Rust**
- Rust está instalado pero sin rustup
- No se puede cambiar fácilmente entre toolchains
- El toolchain actual es GNU pero faltan las herramientas de MinGW

### 3. **Módulos Faltantes**
- El proyecto espera módulos Rust que no existen:
  - auth-module
  - i18n-module
  - ai-module
  - logger-module
  - storage-module
  - update-module

## 🛠️ Soluciones Aplicadas

### 1. **Simplificar Cargo.toml**
Crear un Cargo.toml mínimo sin dependencias de módulos locales:
```toml
[package]
name = "disk-dominator"
version = "0.1.0"
edition = "2021"

[build-dependencies]
tauri-build = { version = "1", features = [] }

[dependencies]
tauri = { version = "1", features = ["fs-all", "path-all", "os-all", "shell-open"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

[features]
default = ["custom-protocol"]
custom-protocol = ["tauri/custom-protocol"]
```

### 2. **Scripts Creados**
- `BUILD-WINDOWS.ps1` - Script PowerShell directo
- `BUILD-DISKDOMINATOR.hta` - Interfaz gráfica (tuvo problemas con rutas)
- `FIX-DLLTOOL.bat` - Para instalar MinGW

## 📝 Proceso Paso a Paso

### Opción A: Con MinGW (Toolchain GNU)
1. Instalar MinGW para obtener dlltool.exe:
   ```batch
   choco install mingw -y
   ```
2. Ejecutar build:
   ```batch
   cd K:\_Glados\DiskDominator
   npm run tauri:build
   ```

### Opción B: Con MSVC (Recomendado)
1. Desinstalar Rust actual
2. Instalar Rust desde https://rustup.rs/
3. Durante instalación, seleccionar:
   - Default host: x86_64-pc-windows-msvc
   - Toolchain: stable-msvc
4. Verificar:
   ```batch
   rustup default stable-msvc
   rustup target list --installed
   ```
5. Ejecutar build

### Opción C: Cross-compilation desde Linux
```bash
# En WSL/Linux
rustup target add x86_64-pc-windows-gnu
npm run tauri build -- --target x86_64-pc-windows-gnu
```

## 🔍 Diagnóstico

### Verificar Entorno
```powershell
# Node.js
node --version  # ✅ v22.16.0

# Rust
rustc --version  # ✅ rustc 1.87.0
rustup show     # ❌ rustup no disponible

# Visual Studio
Test-Path "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"  # ✅ True
```

### Estado Actual
- ✅ Node.js y npm funcionando
- ✅ Next.js compila correctamente
- ✅ Visual Studio Build Tools instalado
- ⚠️ Rust instalado pero con toolchain GNU
- ❌ Falta dlltool.exe (parte de MinGW)
- ❌ No se puede cambiar toolchain sin rustup

## 🚀 Recomendación Final

**Para compilación más rápida la próxima vez:**

1. **Instalar Rust correctamente** con rustup y toolchain MSVC
2. **Usar el script BUILD-WINDOWS.ps1** directamente:
   ```powershell
   cd K:\_Glados\DiskDominator
   .\BUILD-WINDOWS.ps1
   ```

3. **Si persiste el error de dlltool**, instalar MinGW:
   ```powershell
   choco install mingw -y
   # Reiniciar terminal
   .\BUILD-WINDOWS.ps1
   ```

## 📌 Notas Importantes

- Los archivos HTA funcionan pero tienen problemas con rutas WSL
- PowerShell es más confiable que archivos batch para operaciones complejas
- El proyecto está diseñado para arquitectura modular pero los módulos no existen aún
- La sincronización con `c2w` funciona perfectamente
- Se puede ejecutar todo desde WSL usando `powershell.exe`