#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Instala MinGW-w64 en Windows y configura el PATH del sistema
.DESCRIPTION
    Este script descarga e instala MinGW-w64, lo configura en C:\mingw64
    y agrega la ruta al PATH del sistema. Verifica la instalación de dlltool.exe
.NOTES
    Requiere permisos de administrador
    Autor: Batman Incorporated
    Fecha: $(Get-Date -Format "yyyy-MM-dd")
#>

param(
    [switch]$Force,
    [switch]$Silent
)

# Configuración
$ErrorActionPreference = "Stop"
$ProgressPreference = 'SilentlyContinue'

# Variables
$InstallPath = "C:\mingw64"
$TempPath = "$env:TEMP\mingw64-install"
$MinGWUrl = "https://github.com/niXman/mingw-builds-binaries/releases/download/13.2.0-rt_v11-rev1/x86_64-13.2.0-release-posix-seh-ucrt-rt_v11-rev1.7z"
$7ZipUrl = "https://www.7-zip.org/a/7zr.exe"

# Colores para output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$ForegroundColor = "White"
    )
    if (-not $Silent) {
        Write-Host $Message -ForegroundColor $ForegroundColor
    }
}

function Write-Info { Write-ColorOutput "ℹ️  $args" "Cyan" }
function Write-Success { Write-ColorOutput "✅ $args" "Green" }
function Write-Warning { Write-ColorOutput "⚠️  $args" "Yellow" }
function Write-Error { Write-ColorOutput "❌ $args" "Red" }

# Función para verificar si ya está instalado
function Test-MinGWInstalled {
    if (Test-Path "$InstallPath\bin\dlltool.exe") {
        return $true
    }
    
    # Verificar si dlltool está en PATH
    $dlltool = Get-Command dlltool.exe -ErrorAction SilentlyContinue
    if ($dlltool) {
        Write-Info "dlltool.exe encontrado en: $($dlltool.Source)"
        return $true
    }
    
    return $false
}

# Función para descargar archivos con reintentos
function Download-FileWithRetry {
    param(
        [string]$Url,
        [string]$OutFile,
        [int]$MaxRetries = 3
    )
    
    $retryCount = 0
    while ($retryCount -lt $MaxRetries) {
        try {
            Write-Info "Descargando desde: $Url"
            Write-Info "Destino: $OutFile"
            
            # Usar diferentes métodos según la disponibilidad
            if (Get-Command curl.exe -ErrorAction SilentlyContinue) {
                & curl.exe -L -o "$OutFile" "$Url" --progress-bar
            } else {
                Invoke-WebRequest -Uri $Url -OutFile $OutFile -UseBasicParsing
            }
            
            if (Test-Path $OutFile) {
                $fileSize = (Get-Item $OutFile).Length / 1MB
                Write-Success "Descarga completa: $([math]::Round($fileSize, 2)) MB"
                return $true
            }
        }
        catch {
            $retryCount++
            if ($retryCount -lt $MaxRetries) {
                Write-Warning "Error en descarga, reintentando ($retryCount/$MaxRetries)..."
                Start-Sleep -Seconds 5
            } else {
                throw "Error al descargar después de $MaxRetries intentos: $_"
            }
        }
    }
    return $false
}

# Función para agregar al PATH
function Add-ToSystemPath {
    param([string]$PathToAdd)
    
    try {
        $currentPath = [System.Environment]::GetEnvironmentVariable("Path", [System.EnvironmentVariableTarget]::Machine)
        
        if ($currentPath -notlike "*$PathToAdd*") {
            Write-Info "Agregando $PathToAdd al PATH del sistema..."
            
            # Limpiar PATH de entradas duplicadas
            $paths = $currentPath -split ';' | Where-Object { $_ -ne '' } | Select-Object -Unique
            $paths += $PathToAdd
            $newPath = $paths -join ';'
            
            [System.Environment]::SetEnvironmentVariable("Path", $newPath, [System.EnvironmentVariableTarget]::Machine)
            
            # Actualizar PATH de la sesión actual
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path", [System.EnvironmentVariableTarget]::Machine) + ";" + 
                        [System.Environment]::GetEnvironmentVariable("Path", [System.EnvironmentVariableTarget]::User)
            
            Write-Success "PATH actualizado correctamente"
            return $true
        } else {
            Write-Info "$PathToAdd ya está en el PATH"
            return $true
        }
    }
    catch {
        throw "Error al actualizar PATH: $_"
    }
}

# Función principal
function Install-MinGW64 {
    try {
        Write-Info "=== Instalador de MinGW-w64 ==="
        Write-Info "Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        Write-Info ""

        # Verificar permisos de administrador
        if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
            throw "Este script requiere permisos de administrador"
        }

        # Verificar si ya está instalado
        if ((Test-MinGWInstalled) -and -not $Force) {
            Write-Success "MinGW-w64 ya está instalado y dlltool.exe está disponible"
            Write-Info "Use -Force para reinstalar"
            return
        }

        # Crear directorio temporal
        Write-Info "Creando directorio temporal..."
        if (Test-Path $TempPath) {
            Remove-Item $TempPath -Recurse -Force
        }
        New-Item -ItemType Directory -Path $TempPath -Force | Out-Null

        # Descargar 7-Zip portable si no está disponible
        $7zipPath = "$TempPath\7zr.exe"
        if (-not (Get-Command 7z.exe -ErrorAction SilentlyContinue)) {
            Write-Info "Descargando 7-Zip portable..."
            if (-not (Download-FileWithRetry -Url $7ZipUrl -OutFile $7zipPath)) {
                throw "No se pudo descargar 7-Zip"
            }
        } else {
            $7zipPath = "7z.exe"
        }

        # Descargar MinGW-w64
        Write-Info "Descargando MinGW-w64 (esto puede tomar varios minutos)..."
        $mingwArchive = "$TempPath\mingw64.7z"
        if (-not (Download-FileWithRetry -Url $MinGWUrl -OutFile $mingwArchive)) {
            throw "No se pudo descargar MinGW-w64"
        }

        # Limpiar instalación anterior si existe
        if (Test-Path $InstallPath) {
            Write-Warning "Eliminando instalación anterior..."
            Remove-Item $InstallPath -Recurse -Force
        }

        # Extraer archivo
        Write-Info "Extrayendo MinGW-w64 (esto puede tomar varios minutos)..."
        $extractPath = "$TempPath\extracted"
        New-Item -ItemType Directory -Path $extractPath -Force | Out-Null
        
        $extractArgs = "x", "-y", "-o$extractPath", $mingwArchive
        $process = Start-Process -FilePath $7zipPath -ArgumentList $extractArgs -Wait -NoNewWindow -PassThru
        
        if ($process.ExitCode -ne 0) {
            throw "Error al extraer el archivo (código: $($process.ExitCode))"
        }

        # Mover a ubicación final
        Write-Info "Instalando en $InstallPath..."
        $mingwFolder = Get-ChildItem -Path $extractPath -Directory | Select-Object -First 1
        if (-not $mingwFolder) {
            throw "No se encontró la carpeta de MinGW en el archivo extraído"
        }
        
        Move-Item -Path $mingwFolder.FullName -Destination $InstallPath -Force

        # Verificar instalación
        if (-not (Test-Path "$InstallPath\bin\gcc.exe")) {
            throw "La instalación parece incompleta - no se encontró gcc.exe"
        }

        # Agregar al PATH
        Add-ToSystemPath -PathToAdd "$InstallPath\bin"

        # Verificar dlltool
        Write-Info "Verificando instalación de dlltool..."
        $dlltoolPath = "$InstallPath\bin\dlltool.exe"
        if (Test-Path $dlltoolPath) {
            $dlltoolInfo = Get-Item $dlltoolPath
            Write-Success "dlltool.exe instalado correctamente"
            Write-Info "  Ubicación: $dlltoolPath"
            Write-Info "  Tamaño: $([math]::Round($dlltoolInfo.Length / 1KB, 2)) KB"
            
            # Verificar versión
            try {
                $version = & $dlltoolPath --version 2>&1 | Select-Object -First 1
                Write-Info "  Versión: $version"
            } catch {
                Write-Warning "No se pudo obtener la versión de dlltool"
            }
        } else {
            throw "dlltool.exe no se encontró después de la instalación"
        }

        # Verificar otras herramientas
        Write-Info ""
        Write-Info "Herramientas instaladas:"
        $tools = @("gcc", "g++", "make", "gdb", "dlltool", "windres", "objdump")
        foreach ($tool in $tools) {
            if (Test-Path "$InstallPath\bin\$tool.exe") {
                Write-Success "  ✓ $tool"
            } else {
                Write-Warning "  ✗ $tool"
            }
        }

        # Limpiar archivos temporales
        Write-Info "Limpiando archivos temporales..."
        Remove-Item $TempPath -Recurse -Force -ErrorAction SilentlyContinue

        # Mensaje final
        Write-Success ""
        Write-Success "¡MinGW-w64 instalado exitosamente!"
        Write-Info ""
        Write-Info "Ubicación: $InstallPath"
        Write-Info "Herramientas disponibles en: $InstallPath\bin"
        Write-Warning ""
        Write-Warning "IMPORTANTE: Cierre y vuelva a abrir su terminal para que los cambios en PATH surtan efecto"
        Write-Info ""
        Write-Info "Para verificar la instalación, ejecute:"
        Write-Info "  dlltool --version"
        Write-Info "  gcc --version"
        
    }
    catch {
        Write-Error "Error durante la instalación: $_"
        
        # Limpiar en caso de error
        if (Test-Path $TempPath) {
            Write-Info "Limpiando archivos temporales..."
            Remove-Item $TempPath -Recurse -Force -ErrorAction SilentlyContinue
        }
        
        throw
    }
}

# Ejecutar instalación
try {
    Install-MinGW64
}
catch {
    Write-Error $_
    exit 1
}