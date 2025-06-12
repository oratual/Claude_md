# Script PowerShell para crear icono de labios rojos y acceso directo
# Versión mejorada con generación de ICO real

param(
    [string]$TargetScript = "$PSScriptRoot\VozClaude-Fixed.bat",
    [string]$ShortcutName = "💋 Voz Claude",
    [string]$IconSize = "256"
)

# Función para crear SVG de labios rojos más detallado
function Create-LipsSVG {
    param([string]$Path)
    
    $svgContent = @'
<svg width="256" height="256" viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Gradiente principal para los labios -->
    <linearGradient id="lipGradient" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#FF1744;stop-opacity:1" />
      <stop offset="30%" style="stop-color:#E91E63;stop-opacity:1" />
      <stop offset="60%" style="stop-color:#C2185B;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#880E4F;stop-opacity:1" />
    </linearGradient>
    
    <!-- Gradiente para el brillo -->
    <radialGradient id="glossGradient" cx="50%" cy="30%" r="50%">
      <stop offset="0%" style="stop-color:#FFFFFF;stop-opacity:0.7" />
      <stop offset="50%" style="stop-color:#FFCCDD;stop-opacity:0.3" />
      <stop offset="100%" style="stop-color:#FFFFFF;stop-opacity:0" />
    </radialGradient>
    
    <!-- Sombra suave -->
    <filter id="softShadow">
      <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
      <feOffset dx="0" dy="3" result="offsetblur"/>
      <feComponentTransfer>
        <feFuncA type="linear" slope="0.3"/>
      </feComponentTransfer>
      <feMerge> 
        <feMergeNode/>
        <feMergeNode in="SourceGraphic"/> 
      </feMerge>
    </filter>
  </defs>
  
  <!-- Fondo circular suave -->
  <circle cx="128" cy="128" r="120" fill="#FFF0F5" opacity="0.3"/>
  
  <!-- Labio inferior con forma más realista -->
  <path d="M 60 135 
           Q 90 175, 128 180
           Q 166 175, 196 135
           Q 180 165, 128 170
           Q 76 165, 60 135 Z" 
        fill="url(#lipGradient)" 
        stroke="#B71C1C" 
        stroke-width="1.5"
        filter="url(#softShadow)"/>
  
  <!-- Labio superior con curva cupido -->
  <path d="M 60 135 
           C 65 105, 85 100, 100 110
           Q 114 95, 128 98
           Q 142 95, 156 110
           C 171 100, 191 105, 196 135
           Q 178 130, 165 125
           Q 146 130, 128 125
           Q 110 130, 91 125
           Q 78 130, 60 135 Z" 
        fill="url(#lipGradient)" 
        stroke="#B71C1C" 
        stroke-width="1.5"
        filter="url(#softShadow)"/>
  
  <!-- Línea central sutil -->
  <line x1="65" y1="135" x2="191" y2="135" 
        stroke="#C2185B" 
        stroke-width="1" 
        opacity="0.4"/>
  
  <!-- Brillos principales -->
  <ellipse cx="105" cy="115" rx="20" ry="12" 
           fill="url(#glossGradient)" 
           opacity="0.8"
           transform="rotate(-10 105 115)"/>
  <ellipse cx="151" cy="115" rx="20" ry="12" 
           fill="url(#glossGradient)" 
           opacity="0.8"
           transform="rotate(10 151 115)"/>
  
  <!-- Brillo central pequeño -->
  <ellipse cx="128" cy="108" rx="8" ry="5" 
           fill="#FFFFFF" 
           opacity="0.5"/>
  
  <!-- Pequeños detalles de volumen -->
  <ellipse cx="128" cy="155" rx="15" ry="8" 
           fill="#B71C1C" 
           opacity="0.2"/>
</svg>
'@
    
    $svgContent | Out-File -Encoding UTF8 -FilePath $Path
    Write-Host "✅ SVG creado: $Path" -ForegroundColor Green
}

# Función para convertir SVG a ICO usando Windows Forms
function Convert-SVGtoICO {
    param(
        [string]$SvgPath,
        [string]$IcoPath,
        [int]$Size = 256
    )
    
    try {
        # Primero intentar con ImageMagick desde WSL
        $wslCommand = "convert -background transparent -resize ${Size}x${Size} '$SvgPath' -define icon:auto-resize=256,128,64,48,32,16 '$IcoPath'"
        $result = wsl bash -c $wslCommand 2>&1
        
        if (Test-Path $IcoPath) {
            Write-Host "✅ ICO creado con ImageMagick" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "⚠️ ImageMagick no disponible, usando método alternativo" -ForegroundColor Yellow
    }
    
    # Método alternativo: crear ICO con .NET
    Add-Type -AssemblyName System.Drawing
    Add-Type -AssemblyName System.Windows.Forms
    
    try {
        # Crear bitmap de 256x256
        $bitmap = New-Object System.Drawing.Bitmap($Size, $Size)
        $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
        $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
        $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
        
        # Fondo transparente
        $graphics.Clear([System.Drawing.Color]::Transparent)
        
        # Crear gradiente para los labios
        $rect = New-Object System.Drawing.Rectangle(0, 0, $Size, $Size)
        $brush = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
            $rect,
            [System.Drawing.Color]::FromArgb(255, 26, 26),
            [System.Drawing.Color]::FromArgb(139, 0, 0),
            [System.Drawing.Drawing2D.LinearGradientMode]::Vertical
        )
        
        # Dibujar forma de labios simplificada
        $pen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(139, 0, 0), 3)
        
        # Escalar coordenadas
        $scale = $Size / 256.0
        
        # Labio superior
        $upperPath = New-Object System.Drawing.Drawing2D.GraphicsPath
        $upperPath.AddBezier(
            [int](60 * $scale), [int](135 * $scale),
            [int](65 * $scale), [int](105 * $scale),
            [int](85 * $scale), [int](100 * $scale),
            [int](100 * $scale), [int](110 * $scale)
        )
        $upperPath.AddBezier(
            [int](100 * $scale), [int](110 * $scale),
            [int](114 * $scale), [int](95 * $scale),
            [int](142 * $scale), [int](95 * $scale),
            [int](156 * $scale), [int](110 * $scale)
        )
        $upperPath.AddBezier(
            [int](156 * $scale), [int](110 * $scale),
            [int](171 * $scale), [int](100 * $scale),
            [int](191 * $scale), [int](105 * $scale),
            [int](196 * $scale), [int](135 * $scale)
        )
        
        # Labio inferior
        $lowerPath = New-Object System.Drawing.Drawing2D.GraphicsPath
        $lowerPath.AddBezier(
            [int](60 * $scale), [int](135 * $scale),
            [int](90 * $scale), [int](175 * $scale),
            [int](166 * $scale), [int](175 * $scale),
            [int](196 * $scale), [int](135 * $scale)
        )
        
        # Dibujar los labios
        $graphics.FillPath($brush, $upperPath)
        $graphics.FillPath($brush, $lowerPath)
        $graphics.DrawPath($pen, $upperPath)
        $graphics.DrawPath($pen, $lowerPath)
        
        # Agregar brillo
        $glossBrush = New-Object System.Drawing.SolidBrush(
            [System.Drawing.Color]::FromArgb(100, 255, 255, 255)
        )
        $graphics.FillEllipse($glossBrush, 
            [int](85 * $scale), [int](103 * $scale), 
            [int](40 * $scale), [int](24 * $scale))
        $graphics.FillEllipse($glossBrush, 
            [int](131 * $scale), [int](103 * $scale), 
            [int](40 * $scale), [int](24 * $scale))
        
        # Guardar como ICO
        $icon = [System.Drawing.Icon]::FromHandle($bitmap.GetHicon())
        $fileStream = [System.IO.File]::Create($IcoPath)
        $icon.Save($fileStream)
        $fileStream.Close()
        
        # Limpiar recursos
        $graphics.Dispose()
        $bitmap.Dispose()
        $brush.Dispose()
        $pen.Dispose()
        $glossBrush.Dispose()
        $upperPath.Dispose()
        $lowerPath.Dispose()
        
        Write-Host "✅ ICO creado con .NET" -ForegroundColor Green
        return $true
        
    } catch {
        Write-Host "❌ Error al crear ICO: $_" -ForegroundColor Red
        return $false
    }
}

# Función para crear acceso directo mejorado
function Create-VoiceShortcut {
    param(
        [string]$IconPath,
        [string]$TargetPath,
        [string]$Name
    )
    
    $WshShell = New-Object -ComObject WScript.Shell
    $ShortcutPath = "$([Environment]::GetFolderPath('Desktop'))\$Name.lnk"
    
    # Eliminar acceso directo existente si existe
    if (Test-Path $ShortcutPath) {
        Remove-Item $ShortcutPath -Force
    }
    
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    
    # Si el target es un .bat, ejecutarlo a través de cmd
    if ($TargetPath -like "*.bat") {
        $Shortcut.TargetPath = "cmd.exe"
        $Shortcut.Arguments = "/c `"$TargetPath`""
        $Shortcut.WindowStyle = 1  # Normal window
    } else {
        $Shortcut.TargetPath = $TargetPath
    }
    
    $Shortcut.WorkingDirectory = Split-Path $TargetPath
    $Shortcut.IconLocation = "$IconPath,0"
    $Shortcut.Description = "Configuración de Voz para Claude - Sistema de notificación por voz con múltiples motores TTS"
    $Shortcut.Hotkey = "CTRL+SHIFT+V"  # Atajo de teclado opcional
    
    $Shortcut.Save()
    
    Write-Host "✅ Acceso directo creado: $ShortcutPath" -ForegroundColor Green
    Write-Host "   Atajo de teclado: Ctrl+Shift+V" -ForegroundColor Cyan
}

# Script principal
Write-Host "`n💋 Creador de Icono y Acceso Directo para Voz Claude" -ForegroundColor Magenta
Write-Host "═══════════════════════════════════════════════════`n" -ForegroundColor Magenta

# Rutas
$DesktopPath = [Environment]::GetFolderPath('Desktop')
$SvgPath = Join-Path $DesktopPath "voz-claude-lips.svg"
$IcoPath = Join-Path $DesktopPath "voz-claude-lips.ico"

# Verificar que existe el script target
if (-not (Test-Path $TargetScript)) {
    # Buscar alternativas
    $alternatives = @(
        "$PSScriptRoot\VozClaude-Minimal.bat",
        "$PSScriptRoot\voz-claude-simple.bat",
        "$PSScriptRoot\lanzar-voz-claude.bat"
    )
    
    foreach ($alt in $alternatives) {
        if (Test-Path $alt) {
            $TargetScript = $alt
            Write-Host "📍 Usando script alternativo: $(Split-Path -Leaf $alt)" -ForegroundColor Yellow
            break
        }
    }
}

if (-not (Test-Path $TargetScript)) {
    Write-Host "❌ No se encontró ningún script de Voz Claude" -ForegroundColor Red
    Write-Host "   Buscando en: $PSScriptRoot" -ForegroundColor Yellow
    exit 1
}

# Crear SVG
Write-Host "🎨 Creando SVG de labios rojos..." -ForegroundColor Cyan
Create-LipsSVG -Path $SvgPath

# Convertir a ICO
Write-Host "`n🔄 Convirtiendo SVG a ICO..." -ForegroundColor Cyan
$icoCreated = Convert-SVGtoICO -SvgPath $SvgPath -IcoPath $IcoPath -Size 256

if ($icoCreated) {
    # Crear acceso directo
    Write-Host "`n🔗 Creando acceso directo..." -ForegroundColor Cyan
    Create-VoiceShortcut -IconPath $IcoPath -TargetPath $TargetScript -Name $ShortcutName
    
    # Limpiar SVG temporal
    if (Test-Path $SvgPath) {
        Remove-Item $SvgPath -Force
        Write-Host "`n🧹 SVG temporal eliminado" -ForegroundColor Gray
    }
    
    Write-Host "`n✨ ¡Proceso completado con éxito!" -ForegroundColor Green
    Write-Host "   Icono: $IcoPath" -ForegroundColor Gray
    Write-Host "   Acceso directo: $DesktopPath\$ShortcutName.lnk" -ForegroundColor Gray
} else {
    Write-Host "`n❌ No se pudo crear el icono ICO" -ForegroundColor Red
}

# Opción para abrir el programa
Write-Host "`n¿Deseas ejecutar Voz Claude ahora? (S/N): " -NoNewline -ForegroundColor Yellow
$response = Read-Host
if ($response -match '^[Ss]') {
    Start-Process $TargetScript
}