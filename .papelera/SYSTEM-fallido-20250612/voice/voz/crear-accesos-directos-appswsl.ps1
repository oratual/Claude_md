# Script para crear accesos directos de Voz Claude en AppsWSL
# Crea múltiples accesos directos con iconos personalizados

param(
    [string]$AppsWSLPath = "$env:USERPROFILE\Desktop\AppsWSL"
)

# Verificar que existe la carpeta AppsWSL
if (-not (Test-Path $AppsWSLPath)) {
    Write-Host "❌ No existe la carpeta AppsWSL en el escritorio" -ForegroundColor Red
    Write-Host "Creando carpeta..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $AppsWSLPath -Force | Out-Null
}

# Función para crear icono de labios si no existe
function Ensure-LipsIcon {
    $iconPath = "$AppsWSLPath\voz-claude-lips.ico"
    
    if (Test-Path $iconPath) {
        return $iconPath
    }
    
    Write-Host "🎨 Creando icono de labios rojos..." -ForegroundColor Cyan
    
    # Intentar ejecutar el script generador si existe
    $generatorScript = "$PSScriptRoot\crear-icono-labios-mejorado.ps1"
    if (Test-Path $generatorScript) {
        & $generatorScript -TargetScript "dummy" -ShortcutName "temp" | Out-Null
        
        # Mover el icono generado
        $desktopIco = "$env:USERPROFILE\Desktop\voz-claude-lips.ico"
        if (Test-Path $desktopIco) {
            Move-Item $desktopIco $iconPath -Force
            return $iconPath
        }
    }
    
    # Si no, crear un icono básico
    Add-Type -AssemblyName System.Drawing
    
    $bitmap = New-Object System.Drawing.Bitmap(64, 64)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.Clear([System.Drawing.Color]::Transparent)
    
    # Dibujar labios simples
    $brush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(220, 20, 60))
    $pen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(139, 0, 0), 2)
    
    # Forma básica de labios
    $points = @(
        [System.Drawing.Point]::new(10, 32),
        [System.Drawing.Point]::new(32, 20),
        [System.Drawing.Point]::new(54, 32),
        [System.Drawing.Point]::new(32, 44),
        [System.Drawing.Point]::new(10, 32)
    )
    
    $graphics.FillPolygon($brush, $points)
    $graphics.DrawPolygon($pen, $points)
    
    # Guardar como ICO
    $icon = [System.Drawing.Icon]::FromHandle($bitmap.GetHicon())
    $fileStream = [System.IO.File]::Create($iconPath)
    $icon.Save($fileStream)
    $fileStream.Close()
    
    $graphics.Dispose()
    $bitmap.Dispose()
    
    return $iconPath
}

# Función para crear acceso directo
function Create-Shortcut {
    param(
        [string]$Name,
        [string]$Target,
        [string]$Arguments = "",
        [string]$Icon,
        [string]$Description,
        [string]$Hotkey = ""
    )
    
    $WshShell = New-Object -ComObject WScript.Shell
    $ShortcutPath = "$AppsWSLPath\$Name.lnk"
    
    # Eliminar si existe
    if (Test-Path $ShortcutPath) {
        Remove-Item $ShortcutPath -Force
    }
    
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    
    if ($Target -like "*.bat") {
        $Shortcut.TargetPath = "cmd.exe"
        $Shortcut.Arguments = "/c `"$Target`""
    } elseif ($Target -like "*.ps1") {
        $Shortcut.TargetPath = "powershell.exe"
        $Shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$Target`""
    } else {
        $Shortcut.TargetPath = $Target
        if ($Arguments) {
            $Shortcut.Arguments = $Arguments
        }
    }
    
    $Shortcut.WorkingDirectory = Split-Path $Target
    $Shortcut.IconLocation = "$Icon,0"
    $Shortcut.Description = $Description
    
    if ($Hotkey) {
        $Shortcut.Hotkey = $Hotkey
    }
    
    $Shortcut.Save()
    
    Write-Host "✅ Creado: $Name" -ForegroundColor Green
}

# Script principal
Write-Host "`n💋 Creador de Accesos Directos - Voz Claude" -ForegroundColor Magenta
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Magenta
Write-Host "📍 Destino: $AppsWSLPath`n" -ForegroundColor Cyan

# Obtener icono
$lipsIcon = Ensure-LipsIcon

# Definir rutas base
$scriptDir = "$PSScriptRoot"
$wslScriptDir = "/home/lauta/glados/scripts/voz"

# Lista de accesos directos a crear
$shortcuts = @(
    @{
        Name = "💋 Voz Claude (Moderno)"
        Target = "$scriptDir\VozClaude-Fixed.bat"
        Description = "Configuración moderna de voz con detección mejorada"
        Hotkey = "CTRL+SHIFT+V"
    },
    @{
        Name = "🚀 Voz Claude (Rápido)"
        Target = "$scriptDir\VozClaude-Optimized.ps1"
        Description = "Versión PowerShell optimizada con navegación fluida"
        Hotkey = "CTRL+SHIFT+F"
    },
    @{
        Name = "⚡ Voz Claude (Simple)"
        Target = "$scriptDir\voz-claude-simple.bat"
        Description = "Versión minimalista y funcional"
        Hotkey = ""
    },
    @{
        Name = "🐧 Configurar Voz (Linux)"
        Target = "wsl.exe"
        Arguments = "-d Ubuntu-24.04 -- bash -c `"cd $wslScriptDir && ./configurar-voz.sh`""
        Description = "Configuración completa desde terminal Linux"
        Hotkey = ""
    },
    @{
        Name = "🔊 Probar Voz Actual"
        Target = "wsl.exe"
        Arguments = "-d Ubuntu-24.04 -- bash -c `"cd $wslScriptDir && ./notificar-claude.sh 'Hola, soy tu asistente Claude'`""
        Description = "Prueba rápida de la voz configurada"
        Hotkey = "CTRL+SHIFT+T"
    }
)

# Crear cada acceso directo
foreach ($shortcut in $shortcuts) {
    # Verificar que el target existe (excepto para wsl.exe)
    if ($shortcut.Target -ne "wsl.exe" -and -not (Test-Path $shortcut.Target)) {
        Write-Host "⚠️  Omitiendo '$($shortcut.Name)' - No existe: $($shortcut.Target)" -ForegroundColor Yellow
        continue
    }
    
    Create-Shortcut `
        -Name $shortcut.Name `
        -Target $shortcut.Target `
        -Arguments $shortcut.Arguments `
        -Icon $lipsIcon `
        -Description $shortcut.Description `
        -Hotkey $shortcut.Hotkey
}

# Crear también un README
$readmeContent = @'
# 💋 Voz Claude - Accesos Directos

## Aplicaciones disponibles:

### 💋 Voz Claude (Moderno)
- **Descripción**: Interfaz moderna con detección mejorada de estado
- **Atajo**: Ctrl+Shift+V
- **Tecnología**: Batch script optimizado

### 🚀 Voz Claude (Rápido)
- **Descripción**: Versión PowerShell con navegación ultra fluida
- **Atajo**: Ctrl+Shift+F
- **Tecnología**: PowerShell con caché de estado

### ⚡ Voz Claude (Simple)
- **Descripción**: Versión minimalista sin florituras
- **Tecnología**: Batch script básico

### 🐧 Configurar Voz (Linux)
- **Descripción**: Abre el configurador completo en terminal
- **Características**: Instalación de motores, configuración avanzada

### 🔊 Probar Voz Actual
- **Descripción**: Prueba rápida de la voz configurada
- **Atajo**: Ctrl+Shift+T

## Motores de voz disponibles:
- 🌟 **gtts**: Google Text-to-Speech (requiere internet)
- 💃 **pico2wave**: Voz femenina natural (offline)
- 🎭 **festival**: Voz masculina clara (offline)
- 🤖 **espeak**: Voz robótica minimalista (offline)
- 🔇 **none**: Modo silencioso

## Configuración guardada en:
~/.config/claude-voz/config
'@

$readmeContent | Out-File -Encoding UTF8 -FilePath "$AppsWSLPath\VozClaude-README.txt"
Write-Host "📄 Creado: VozClaude-README.txt" -ForegroundColor Green

Write-Host "`n✨ ¡Proceso completado!" -ForegroundColor Green
Write-Host "📁 Accesos directos creados en: $AppsWSLPath" -ForegroundColor Cyan
Write-Host "`nAtalhos de teclado configurados:" -ForegroundColor Yellow
Write-Host "  Ctrl+Shift+V - Voz Claude (Moderno)" -ForegroundColor Gray
Write-Host "  Ctrl+Shift+F - Voz Claude (Rápido)" -ForegroundColor Gray
Write-Host "  Ctrl+Shift+T - Probar Voz" -ForegroundColor Gray

# Abrir la carpeta
Write-Host "`n¿Deseas abrir la carpeta AppsWSL? (S/N): " -NoNewline -ForegroundColor Yellow
$response = Read-Host
if ($response -match '^[Ss]') {
    Start-Process explorer.exe $AppsWSLPath
}