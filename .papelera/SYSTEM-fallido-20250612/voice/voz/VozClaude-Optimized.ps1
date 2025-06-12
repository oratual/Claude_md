# PowerShell Menu Optimizado para Voz Claude
# Requiere Windows PowerShell 5.1 o PowerShell Core 7+

# Configuración inicial
$Host.UI.RawUI.WindowTitle = "💋 Voz Claude - Configuración"
$WSL_DISTRO = "Ubuntu-24.04"
$SCRIPT_DIR = "/home/lauta/glados/scripts/voz"

# Colores personalizados
$colors = @{
    Background = 'Black'
    MenuBg = 'DarkMagenta'
    Selected = 'Magenta'
    Text = 'White'
    Accent = 'Cyan'
    Success = 'Green'
    Warning = 'Yellow'
    Error = 'Red'
}

# Cache global para el estado
$global:VoiceStatusCache = $null
$global:LastStatusCheck = [DateTime]::MinValue

# Función para limpiar pantalla con estilo
function Clear-HostStyled {
    Clear-Host
    $Host.UI.RawUI.BackgroundColor = $colors.Background
    $Host.UI.RawUI.ForegroundColor = $colors.Text
}

# Función para mostrar header
function Show-Header {
    Clear-HostStyled
    Write-Host ""
    Write-Host "  ╔════════════════════════════════════════════════════════════╗" -ForegroundColor $colors.MenuBg
    Write-Host "  ║                                                            ║" -ForegroundColor $colors.MenuBg
    Write-Host "  ║  💋  " -NoNewline -ForegroundColor $colors.MenuBg
    Write-Host "VOZ CLAUDE" -NoNewline -ForegroundColor $colors.Accent
    Write-Host " - Tu asistente con personalidad     ║" -ForegroundColor $colors.MenuBg
    Write-Host "  ║                                                            ║" -ForegroundColor $colors.MenuBg
    Write-Host "  ╚════════════════════════════════════════════════════════════╝" -ForegroundColor $colors.MenuBg
    Write-Host ""
}

# Función para obtener estado actual (con cache)
function Get-VoiceStatus {
    param (
        [switch]$ForceRefresh
    )
    
    # Usar cache si es reciente (menos de 5 segundos)
    $now = [DateTime]::Now
    if (-not $ForceRefresh -and $global:VoiceStatusCache -and ($now - $global:LastStatusCheck).TotalSeconds -lt 5) {
        return $global:VoiceStatusCache
    }
    
    # Actualizar cache
    $engine = & wsl -d $WSL_DISTRO -- bash -c "source ~/.config/claude-voz/config 2>/dev/null && echo `$CLAUDE_VOICE_ENGINE || echo 'gtts'"
    $enabled = & wsl -d $WSL_DISTRO -- bash -c "source ~/.config/claude-voz/config 2>/dev/null && [ `"`$CLAUDE_VOICE_ENABLED`" = `"1`" ] && echo 'true' || echo 'false'"
    $instance = & wsl -d $WSL_DISTRO -- bash -c "source ~/.config/claude-voz/config 2>/dev/null && echo `$CLAUDE_INSTANCE_NAME"
    
    $global:VoiceStatusCache = @{
        Engine = $engine.Trim()
        Enabled = $enabled.Trim() -eq 'true'
        Instance = if ($instance.Trim()) { $instance.Trim() } else { "Sin configurar" }
    }
    $global:LastStatusCheck = $now
    
    return $global:VoiceStatusCache
}

# Función para mostrar estado con estilo (versión ligera)
function Show-StatusLight {
    param (
        [PSCustomObject]$Status
    )
    
    # Motor actual con emoji
    $engineEmoji = switch ($Status.Engine) {
        'gtts' { '🌐' }
        'pico2wave' { '🔊' }
        'festival' { '🎭' }
        'espeak' { '🤖' }
        'mimic3' { '🧠' }
        'none' { '🔇' }
        default { '❓' }
    }
    
    # Línea de estado compacta
    Write-Host "  " -NoNewline
    Write-Host "$engineEmoji $($Status.Engine)" -NoNewline -ForegroundColor $colors.Success
    Write-Host " | " -NoNewline -ForegroundColor DarkGray
    
    if ($Status.Enabled) {
        Write-Host "🔊 ON" -NoNewline -ForegroundColor $colors.Success
    } else {
        Write-Host "🔇 OFF" -NoNewline -ForegroundColor $colors.Warning
    }
    
    Write-Host " | " -NoNewline -ForegroundColor DarkGray
    Write-Host "🏷️ $($Status.Instance)" -ForegroundColor $colors.Accent
    Write-Host ""
}

# Función de menú optimizada con navegación rápida
function Show-MenuOptimized {
    param (
        [string]$Title,
        [array]$Options
    )
    
    $selectedIndex = 0
    $key = $null
    $needsFullRedraw = $true
    $status = Get-VoiceStatus
    
    # Guardar posición del cursor para actualizaciones parciales
    $menuStartRow = 12  # Ajustar según tu diseño
    
    do {
        if ($needsFullRedraw) {
            Show-Header
            Show-StatusLight -Status $status
            
            Write-Host ""
            Write-Host "  $Title" -ForegroundColor $colors.Accent
            Write-Host "  ─────────────────────────" -ForegroundColor DarkGray
            Write-Host ""
            
            # Guardar posición antes del menú
            $Host.UI.RawUI.CursorPosition = New-Object System.Management.Automation.Host.Coordinates 0, $menuStartRow
        }
        
        # Solo redibujar las opciones del menú
        for ($i = 0; $i -lt $Options.Count; $i++) {
            $Host.UI.RawUI.CursorPosition = New-Object System.Management.Automation.Host.Coordinates 0, ($menuStartRow + $i)
            
            if ($i -eq $selectedIndex) {
                Write-Host "  ▶ " -NoNewline -ForegroundColor $colors.Selected
                Write-Host "$($Options[$i])                    " -ForegroundColor $colors.Selected
            } else {
                Write-Host "    $($Options[$i])                    " -ForegroundColor $colors.Text
            }
        }
        
        # Posicionar cursor para instrucciones
        $Host.UI.RawUI.CursorPosition = New-Object System.Management.Automation.Host.Coordinates 0, ($menuStartRow + $Options.Count + 1)
        Write-Host ""
        Write-Host "  Usa ↑↓ para navegar, Enter para seleccionar, ESC para salir" -ForegroundColor DarkGray
        
        $needsFullRedraw = $false
        $key = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        
        switch ($key.VirtualKeyCode) {
            38 { # Flecha arriba
                if ($selectedIndex -gt 0) { $selectedIndex-- }
                else { $selectedIndex = $Options.Count - 1 }
            }
            40 { # Flecha abajo
                if ($selectedIndex -lt $Options.Count - 1) { $selectedIndex++ }
                else { $selectedIndex = 0 }
            }
            13 { # Enter
                return $selectedIndex
            }
            27 { # ESC
                return -1
            }
            82 { # R - Refrescar estado
                if ($key.ControlKeyState -band [System.Management.Automation.Host.ControlKeyStates]::LeftCtrlPressed) {
                    $status = Get-VoiceStatus -ForceRefresh
                    $needsFullRedraw = $true
                }
            }
        }
    } while ($true)
}

# Función para cambiar motor (simplificada)
function Change-Engine {
    $engines = @(
        "💃 pico2wave - Voz femenina con personalidad",
        "🌟 gtts - La reina de las voces (Google)",
        "🎭 festival - El caballero español",
        "🤖 espeak - Minimalista futurista",
        "🔇 none - El silencio es oro",
        "🔙 Volver al menú"
    )
    
    $selection = Show-MenuOptimized -Title "Elige tu voz favorita:" -Options $engines
    
    if ($selection -ge 0 -and $selection -lt 5) {
        $engineNames = @('pico2wave', 'gtts', 'festival', 'espeak', 'none')
        $newEngine = $engineNames[$selection]
        
        & wsl -d $WSL_DISTRO -- bash -c "mkdir -p ~/.config/claude-voz && echo 'CLAUDE_VOICE_ENGINE=`"$newEngine`"' > ~/.config/claude-voz/config && echo 'CLAUDE_VOICE_ENABLED=1' >> ~/.config/claude-voz/config"
        
        # Forzar actualización del cache
        $null = Get-VoiceStatus -ForceRefresh
        
        Write-Host ""
        Write-Host "  ✨ ¡Perfecto! Ahora uso la voz " -NoNewline -ForegroundColor $colors.Success
        Write-Host $newEngine -ForegroundColor $colors.Accent
        Write-Host "  Presiona cualquier tecla para continuar..." -ForegroundColor DarkGray
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
}

# Función para probar voz (simplificada)
function Test-Voice {
    $messages = @(
        "💬 'Hola cariño, soy Claude'",
        "🚀 'Ultra think ha completado su magia'",
        "💋 'Tu asistente favorita está lista'",
        "✨ Escribir mi propio mensaje",
        "🔙 Volver"
    )
    
    $selection = Show-MenuOptimized -Title "¿Qué quieres que diga?" -Options $messages
    
    if ($selection -ge 0 -and $selection -lt 3) {
        $testMessages = @(
            "Hola cariño, soy Claude",
            "Ultra think ha completado su magia",
            "Tu asistente favorita está lista"
        )
        $message = $testMessages[$selection]
    } elseif ($selection -eq 3) {
        Write-Host ""
        Write-Host "  Escribe tu mensaje:" -ForegroundColor $colors.Accent
        Write-Host "  > " -NoNewline -ForegroundColor $colors.Selected
        $message = Read-Host
    } else {
        return
    }
    
    if ($message) {
        Write-Host ""
        Write-Host "  🔊 Reproduciendo..." -ForegroundColor $colors.Accent
        & wsl -d $WSL_DISTRO -- bash -c "cd $SCRIPT_DIR && ./notificar-claude.sh '$message'"
        Write-Host "  ✨ ¡Listo! Presiona cualquier tecla..." -ForegroundColor $colors.Success
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
}

# Función para configurar instancia
function Set-Instance {
    Show-Header
    Write-Host "  Dale personalidad a tu terminal" -ForegroundColor $colors.Accent
    Write-Host "  ──────────────────────────────" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  Sugerencias creativas:" -ForegroundColor $colors.Text
    Write-Host "  • ultrathink - Para análisis profundos" -ForegroundColor DarkGray
    Write-Host "  • dreamweaver - Para proyectos creativos" -ForegroundColor DarkGray
    Write-Host "  • speedster - Para tareas rápidas" -ForegroundColor DarkGray
    Write-Host "  • nightowl - Para sesiones nocturnas" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  Nombre actual: " -NoNewline -ForegroundColor $colors.Text
    $current = (Get-VoiceStatus).Instance
    Write-Host $current -ForegroundColor $colors.Accent
    Write-Host ""
    Write-Host "  Nuevo nombre (Enter para mantener): " -NoNewline -ForegroundColor $colors.Selected
    $newName = Read-Host
    
    if ($newName) {
        & wsl -d $WSL_DISTRO -- bash -c "sed -i '/CLAUDE_INSTANCE_NAME/d' ~/.config/claude-voz/config 2>/dev/null; echo 'CLAUDE_INSTANCE_NAME=`"$newName`"' >> ~/.config/claude-voz/config"
        
        # Forzar actualización del cache
        $null = Get-VoiceStatus -ForceRefresh
        
        Write-Host ""
        Write-Host "  ✨ ¡Genial! Ahora eres '$newName'" -ForegroundColor $colors.Success
        Write-Host "  Presiona cualquier tecla..." -ForegroundColor DarkGray
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
}

# Función principal
function Main {
    do {
        $options = @(
            "🎤 Cambiar voz",
            "🔊 Probar voz actual",
            "🏷️  Personalizar nombre",
            "💡 Activar/Desactivar voz",
            "📥 Instalar voces nuevas",
            "🎛️  Configuración avanzada (Linux)",
            "👋 Salir"
        )
        
        $selection = Show-MenuOptimized -Title "¿Qué quieres hacer hoy?" -Options $options
        
        switch ($selection) {
            0 { Change-Engine }
            1 { Test-Voice }
            2 { Set-Instance }
            3 { 
                $status = Get-VoiceStatus
                $newState = if ($status.Enabled) { '0' } else { '1' }
                & wsl -d $WSL_DISTRO -- bash -c "sed -i 's/CLAUDE_VOICE_ENABLED=.*/CLAUDE_VOICE_ENABLED=$newState/' ~/.config/claude-voz/config"
                
                # Forzar actualización del cache
                $null = Get-VoiceStatus -ForceRefresh
                
                Write-Host ""
                if ($newState -eq '1') {
                    Write-Host "  🔊 ¡Voz activada! Escucharás mi dulce voz" -ForegroundColor $colors.Success
                } else {
                    Write-Host "  🔇 Modo silencioso activado" -ForegroundColor $colors.Warning
                }
                Write-Host "  Presiona cualquier tecla..." -ForegroundColor DarkGray
                $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            }
            4 {
                Write-Host ""
                Write-Host "  🚀 Abriendo instalador de voces..." -ForegroundColor $colors.Accent
                & wsl -d $WSL_DISTRO -- bash -c "cd $SCRIPT_DIR && ./configurar-voz.sh"
            }
            5 {
                Write-Host ""
                Write-Host "  🐧 Abriendo configuración Linux..." -ForegroundColor $colors.Accent
                & wsl -d $WSL_DISTRO -- bash -c "cd $SCRIPT_DIR && ./configurar-voz.sh"
            }
            6 { 
                Write-Host ""
                Write-Host "  💋 ¡Hasta la próxima, cariño!" -ForegroundColor $colors.Selected
                Start-Sleep -Seconds 1
                exit 
            }
            -1 { exit }
        }
    } while ($true)
}

# Mensaje de inicio
Write-Host "  💋 Voz Claude - Versión Optimizada" -ForegroundColor $colors.Accent
Write-Host "  Tip: Usa Ctrl+R para refrescar el estado" -ForegroundColor DarkGray
Start-Sleep -Seconds 1

# Iniciar
Main