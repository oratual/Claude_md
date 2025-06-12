# Script completo para configurar accesos directos de Voz Claude en AppsWSL
# Genera icono y crea todos los accesos directos

param(
    [string]$AppsWSLPath = "$env:USERPROFILE\Desktop\AppsWSL"
)

# Cambiar al directorio del script
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "`n💋 Configurador de Accesos Directos - Voz Claude" -ForegroundColor Magenta
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Magenta

# 1. Verificar/crear carpeta AppsWSL
if (-not (Test-Path $AppsWSLPath)) {
    Write-Host "`n📁 Creando carpeta AppsWSL..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $AppsWSLPath -Force | Out-Null
}

# 2. Generar icono si no existe
$iconPath = "$scriptPath\voz-claude-lips.ico"
if (-not (Test-Path $iconPath)) {
    Write-Host "`n🎨 Generando icono de labios rojos..." -ForegroundColor Cyan
    
    # Crear SVG
    $svgContent = @'
<svg width="256" height="256" viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="lipGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#FF1744;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#E91E63;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#880E4F;stop-opacity:1" />
    </linearGradient>
    <radialGradient id="gloss">
      <stop offset="0%" style="stop-color:#FFFFFF;stop-opacity:0.6" />
      <stop offset="100%" style="stop-color:#FFFFFF;stop-opacity:0" />
    </radialGradient>
  </defs>
  <circle cx="128" cy="128" r="120" fill="#FFF0F5" opacity="0.2"/>
  <path d="M 60 135 Q 128 180 196 135 Q 180 165 128 170 Q 76 165 60 135 Z" fill="url(#lipGrad)" stroke="#B71C1C" stroke-width="2"/>
  <path d="M 60 135 C 65 105, 85 100, 100 110 Q 114 95, 128 98 Q 142 95, 156 110 C 171 100, 191 105, 196 135 Q 178 130, 165 125 Q 146 130, 128 125 Q 110 130, 91 125 Q 78 130, 60 135 Z" fill="url(#lipGrad)" stroke="#B71C1C" stroke-width="2"/>
  <ellipse cx="105" cy="115" rx="20" ry="12" fill="url(#gloss)" opacity="0.8"/>
  <ellipse cx="151" cy="115" rx="20" ry="12" fill="url(#gloss)" opacity="0.8"/>
</svg>
'@
    
    $svgPath = "$env:TEMP\lips-temp.svg"
    $svgContent | Out-File -Encoding UTF8 $svgPath
    
    # Intentar convertir con ImageMagick
    try {
        & wsl convert -background transparent -resize 256x256 "$svgPath" -define icon:auto-resize=256,128,64,48,32,16 "$iconPath" 2>$null
        if (Test-Path $iconPath) {
            Write-Host "✅ Icono creado con ImageMagick" -ForegroundColor Green
        }
    } catch {}
    
    # Si no funciona, crear icono básico con .NET
    if (-not (Test-Path $iconPath)) {
        Add-Type -AssemblyName System.Drawing
        
        $bitmap = New-Object System.Drawing.Bitmap(64, 64)
        $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
        $graphics.Clear([System.Drawing.Color]::Transparent)
        
        # Dibujar labios simples
        $brush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(220, 20, 60))
        $pen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(139, 0, 0), 2)
        
        # Forma de labios
        $upperPoints = @(
            [System.Drawing.Point]::new(10, 32),
            [System.Drawing.Point]::new(20, 25),
            [System.Drawing.Point]::new(32, 22),
            [System.Drawing.Point]::new(44, 25),
            [System.Drawing.Point]::new(54, 32)
        )
        $lowerPoints = @(
            [System.Drawing.Point]::new(10, 32),
            [System.Drawing.Point]::new(32, 42),
            [System.Drawing.Point]::new(54, 32)
        )
        
        $graphics.FillPolygon($brush, $upperPoints)
        $graphics.FillPolygon($brush, $lowerPoints)
        $graphics.DrawPolygon($pen, $upperPoints)
        $graphics.DrawPolygon($pen, $lowerPoints)
        
        # Guardar como ICO
        $icon = [System.Drawing.Icon]::FromHandle($bitmap.GetHicon())
        $fileStream = [System.IO.File]::Create($iconPath)
        $icon.Save($fileStream)
        $fileStream.Close()
        
        $graphics.Dispose()
        $bitmap.Dispose()
        
        Write-Host "✅ Icono creado con .NET" -ForegroundColor Green
    }
    
    # Limpiar temporal
    if (Test-Path $svgPath) { Remove-Item $svgPath -Force }
}

# 3. Crear función helper para shortcuts
function New-VozShortcut {
    param(
        [string]$Name,
        [string]$Target,
        [string]$Arguments = "",
        [string]$Description,
        [string]$Hotkey = "",
        [string]$Icon = $iconPath
    )
    
    $WshShell = New-Object -ComObject WScript.Shell
    $ShortcutPath = "$AppsWSLPath\$Name.lnk"
    
    if (Test-Path $ShortcutPath) { Remove-Item $ShortcutPath -Force }
    
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    
    if ($Target -like "*.bat") {
        $Shortcut.TargetPath = "cmd.exe"
        $Shortcut.Arguments = "/c `"$Target`""
    } elseif ($Target -like "*.ps1") {
        $Shortcut.TargetPath = "powershell.exe"
        $Shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$Target`""
    } else {
        $Shortcut.TargetPath = $Target
        if ($Arguments) { $Shortcut.Arguments = $Arguments }
    }
    
    $Shortcut.WorkingDirectory = Split-Path $Target -ErrorAction SilentlyContinue
    $Shortcut.IconLocation = "$Icon,0"
    $Shortcut.Description = $Description
    if ($Hotkey) { $Shortcut.Hotkey = $Hotkey }
    
    $Shortcut.Save()
    Write-Host "✅ $Name" -ForegroundColor Green
}

# 4. Crear accesos directos
Write-Host "`n📌 Creando accesos directos..." -ForegroundColor Cyan

# Verificar archivos existentes
$scripts = @{
    "VozClaude-Fixed.bat" = "💋 Voz Claude (Moderno)"
    "VozClaude-Optimized.ps1" = "🚀 Voz Claude (PowerShell)"
    "VozClaude-Minimal.bat" = "⚡ Voz Claude (Minimal)"
    "voz-claude-simple.bat" = "📱 Voz Claude (Simple)"
}

foreach ($script in $scripts.GetEnumerator()) {
    if (Test-Path "$scriptPath\$($script.Key)") {
        $desc = switch ($script.Key) {
            "VozClaude-Fixed.bat" { "Interfaz moderna con detección mejorada" }
            "VozClaude-Optimized.ps1" { "PowerShell optimizado con navegación fluida" }
            "VozClaude-Minimal.bat" { "Versión minimalista mejorada" }
            "voz-claude-simple.bat" { "Versión simple y funcional" }
        }
        
        $hotkey = switch ($script.Key) {
            "VozClaude-Fixed.bat" { "CTRL+SHIFT+V" }
            "VozClaude-Optimized.ps1" { "CTRL+SHIFT+F" }
            default { "" }
        }
        
        New-VozShortcut -Name $script.Value `
                       -Target "$scriptPath\$($script.Key)" `
                       -Description $desc `
                       -Hotkey $hotkey
    }
}

# Accesos directos WSL
New-VozShortcut -Name "🐧 Configurar Voz (Linux)" `
               -Target "wsl.exe" `
               -Arguments "-d Ubuntu-24.04 -- bash -c 'cd /home/lauta/glados/scripts/voz && ./configurar-voz.sh'" `
               -Description "Configuración completa desde terminal Linux"

New-VozShortcut -Name "🔊 Probar Voz Actual" `
               -Target "wsl.exe" `
               -Arguments "-d Ubuntu-24.04 -- bash -c 'cd /home/lauta/glados/scripts/voz && ./notificar-claude.sh \"Hola, soy tu asistente Claude\"'" `
               -Description "Prueba rápida de la voz configurada" `
               -Hotkey "CTRL+SHIFT+T"

# 5. Crear README
Write-Host "`n📄 Creando README..." -ForegroundColor Cyan

@'
💋 VOZ CLAUDE - ACCESOS DIRECTOS
================================

APLICACIONES DISPONIBLES:

1. Voz Claude (Moderno) - Ctrl+Shift+V
   Interfaz moderna con detección mejorada

2. Voz Claude (PowerShell) - Ctrl+Shift+F  
   PowerShell optimizado con navegación fluida

3. Voz Claude (Minimal/Simple)
   Versiones ligeras y funcionales

4. Configurar Voz (Linux)
   Configuración completa desde terminal

5. Probar Voz Actual - Ctrl+Shift+T
   Prueba rápida de la voz configurada

MOTORES DISPONIBLES:
- gtts: Google Text-to-Speech (requiere internet)
- pico2wave: Voz femenina natural (offline)
- festival: Voz masculina clara (offline)
- espeak: Voz robótica (offline)
- none: Modo silencioso

CONFIGURACIÓN:
~/.config/claude-voz/config

TIPS:
- Los atajos de teclado funcionan desde cualquier lugar
- Puedes cambiar el motor de voz en cualquier momento
- La configuración se guarda automáticamente
'@ | Out-File -Encoding UTF8 "$AppsWSLPath\VozClaude-README.txt"

# 6. Resumen final
Write-Host "`n✨ ¡Proceso completado!" -ForegroundColor Green
Write-Host "`n📁 Ubicación: $AppsWSLPath" -ForegroundColor Cyan
Write-Host "`n⌨️  Atajos configurados:" -ForegroundColor Yellow
Write-Host "   Ctrl+Shift+V - Voz Claude (Moderno)" -ForegroundColor Gray
Write-Host "   Ctrl+Shift+F - Voz Claude (PowerShell)" -ForegroundColor Gray
Write-Host "   Ctrl+Shift+T - Probar Voz" -ForegroundColor Gray

Write-Host "`n¿Abrir carpeta AppsWSL? (S/N): " -NoNewline -ForegroundColor Yellow
$response = Read-Host
if ($response -match '^[Ss]') {
    Start-Process explorer.exe $AppsWSLPath
}