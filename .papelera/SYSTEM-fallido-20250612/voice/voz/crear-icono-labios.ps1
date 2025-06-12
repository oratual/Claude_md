# Script PowerShell para crear icono de labios rojos y acceso directo

# Crear imagen SVG de labios rojos
$svgContent = @'
<svg width="256" height="256" viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="lipGradient" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#FF1744;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#D50000;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#B71C1C;stop-opacity:1" />
    </linearGradient>
    <radialGradient id="glossGradient">
      <stop offset="0%" style="stop-color:#FFFFFF;stop-opacity:0.6" />
      <stop offset="100%" style="stop-color:#FFFFFF;stop-opacity:0" />
    </radialGradient>
  </defs>
  
  <!-- Sombra -->
  <ellipse cx="128" cy="138" rx="85" ry="65" fill="#000000" opacity="0.2"/>
  
  <!-- Labio inferior -->
  <path d="M 50 130 Q 128 180 206 130 Q 180 160 128 165 Q 76 160 50 130" 
        fill="url(#lipGradient)" stroke="#8B0000" stroke-width="2"/>
  
  <!-- Labio superior -->
  <path d="M 50 130 Q 70 100 90 105 Q 108 95 128 100 Q 148 95 166 105 Q 186 100 206 130 Q 180 125 166 120 Q 148 125 128 120 Q 108 125 90 120 Q 76 125 50 130" 
        fill="url(#lipGradient)" stroke="#8B0000" stroke-width="2"/>
  
  <!-- Línea central -->
  <line x1="50" y1="130" x2="206" y2="130" stroke="#8B0000" stroke-width="1.5" opacity="0.5"/>
  
  <!-- Brillo -->
  <ellipse cx="110" cy="115" rx="25" ry="15" fill="url(#glossGradient)" opacity="0.7"/>
  <ellipse cx="146" cy="115" rx="25" ry="15" fill="url(#glossGradient)" opacity="0.7"/>
</svg>
'@

# Guardar SVG
$svgPath = "$env:USERPROFILE\Desktop\lips-icon.svg"
$svgContent | Out-File -Encoding UTF8 $svgPath

# Convertir SVG a ICO usando ImageMagick si está disponible
$icoPath = "$env:USERPROFILE\Desktop\lips-icon.ico"

# Intentar con ImageMagick desde WSL
$convertCommand = "wsl convert -background transparent -define icon:auto-resize=256,128,64,48,32,16 '$svgPath' '$icoPath' 2>/dev/null"
Invoke-Expression $convertCommand

# Si no funciona, crear ICO básico con .NET
if (-not (Test-Path $icoPath)) {
    Add-Type -AssemblyName System.Drawing
    
    # Crear bitmap desde SVG (simplificado)
    $bitmap = New-Object System.Drawing.Bitmap(256, 256)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.Clear([System.Drawing.Color]::Transparent)
    
    # Dibujar labios simplificados
    $brush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 213, 0, 0))
    $pen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(139, 0, 0), 2)
    
    # Labio superior
    $upperPoints = @(
        [System.Drawing.Point]::new(50, 130),
        [System.Drawing.Point]::new(90, 105),
        [System.Drawing.Point]::new(128, 100),
        [System.Drawing.Point]::new(166, 105),
        [System.Drawing.Point]::new(206, 130)
    )
    
    # Labio inferior
    $lowerPoints = @(
        [System.Drawing.Point]::new(50, 130),
        [System.Drawing.Point]::new(128, 165),
        [System.Drawing.Point]::new(206, 130)
    )
    
    $graphics.FillPolygon($brush, $upperPoints)
    $graphics.FillPolygon($brush, $lowerPoints)
    $graphics.DrawPolygon($pen, $upperPoints)
    $graphics.DrawPolygon($pen, $lowerPoints)
    
    # Guardar como ICO
    $memoryStream = New-Object System.IO.MemoryStream
    $bitmap.Save($memoryStream, [System.Drawing.Imaging.ImageFormat]::Icon)
    [System.IO.File]::WriteAllBytes($icoPath, $memoryStream.ToArray())
    
    $graphics.Dispose()
    $bitmap.Dispose()
    $memoryStream.Dispose()
}

# Crear acceso directo con icono
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Voz Claude.lnk")
$Shortcut.TargetPath = "$env:USERPROFILE\Desktop\configurar-voz-windows.bat"
$Shortcut.IconLocation = $icoPath
$Shortcut.Description = "Configuración de Voz para Claude - Voces femeninas y más"
$Shortcut.Save()

Write-Host "✅ Icono de labios rojos creado" -ForegroundColor Green
Write-Host "✅ Acceso directo 'Voz Claude' creado en el escritorio" -ForegroundColor Green