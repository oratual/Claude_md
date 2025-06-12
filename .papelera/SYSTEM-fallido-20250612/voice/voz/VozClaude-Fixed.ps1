# PowerShell Menu Moderno para Voz Claude - Version Corregida
# Compatible con Windows PowerShell 5.1+

# Configuracion inicial
$Host.UI.RawUI.WindowTitle = "Voz Claude - Configuracion"
$WSL_DISTRO = "Ubuntu-24.04"
$SCRIPT_DIR = "/home/lauta/glados/scripts/voz"

# Colores
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

# Limpiar pantalla con estilo
function Clear-HostStyled {
    Clear-Host
    $Host.UI.RawUI.BackgroundColor = $colors.Background
    $Host.UI.RawUI.ForegroundColor = $colors.Text
}

# Mostrar header
function Show-Header {
    Clear-HostStyled
    Write-Host ""
    Write-Host "  ===========================================================  " -ForegroundColor $colors.MenuBg
    Write-Host "  ||                                                       ||  " -ForegroundColor $colors.MenuBg
    Write-Host "  ||      VOZ CLAUDE - Tu asistente con personalidad      ||  " -ForegroundColor $colors.Accent
    Write-Host "  ||                                                       ||  " -ForegroundColor $colors.MenuBg
    Write-Host "  ===========================================================  " -ForegroundColor $colors.MenuBg
    Write-Host ""
}

# Obtener estado actual
function Get-VoiceStatus {
    $engine = & wsl -d $WSL_DISTRO -- bash -c "source ~/.config/claude-voz/config 2>/dev/null && echo `$CLAUDE_VOICE_ENGINE || echo 'gtts'"
    $enabled = & wsl -d $WSL_DISTRO -- bash -c "source ~/.config/claude-voz/config 2>/dev/null && [ `"`$CLAUDE_VOICE_ENABLED`" = `"1`" ] && echo 'true' || echo 'false'"
    $instance = & wsl -d $WSL_DISTRO -- bash -c "source ~/.config/claude-voz/config 2>/dev/null && echo `$CLAUDE_INSTANCE_NAME"
    
    return @{
        Engine = $engine.Trim()
        Enabled = $enabled.Trim() -eq 'true'
        Instance = if ($instance.Trim()) { $instance.Trim() } else { "Sin configurar" }
    }
}

# Mostrar estado
function Show-Status {
    $status = Get-VoiceStatus
    
    Write-Host "  Estado Actual:" -ForegroundColor $colors.Accent
    Write-Host "  -------------" -ForegroundColor DarkGray
    
    Write-Host "  Motor: " -NoNewline -ForegroundColor $colors.Text
    Write-Host $status.Engine -ForegroundColor $colors.Success
    
    if ($status.Enabled) {
        Write-Host "  Voz: " -NoNewline -ForegroundColor $colors.Text
        Write-Host "Activada" -ForegroundColor $colors.Success
    } else {
        Write-Host "  Voz: " -NoNewline -ForegroundColor $colors.Text
        Write-Host "Desactivada" -ForegroundColor $colors.Warning
    }
    
    Write-Host "  Instancia: " -NoNewline -ForegroundColor $colors.Text
    Write-Host $status.Instance -ForegroundColor $colors.Accent
    
    Write-Host ""
}

# Mostrar motores disponibles
function Show-Engines {
    Write-Host "  Motores Disponibles:" -ForegroundColor $colors.Accent
    Write-Host "  -------------------" -ForegroundColor DarkGray
    
    # pico2wave
    Write-Host "  [OK] " -NoNewline -ForegroundColor $colors.Success
    Write-Host "pico2wave - Voz femenina natural" -ForegroundColor $colors.Text
    
    # gtts
    $gttsInstalled = & wsl -d $WSL_DISTRO -- python3 -c "import gtts" 2>$null
    if ($?) {
        Write-Host "  [OK] " -NoNewline -ForegroundColor $colors.Success
    } else {
        Write-Host "  [--] " -NoNewline -ForegroundColor $colors.Error
    }
    Write-Host "gtts - Google, voz femenina perfecta" -ForegroundColor $colors.Text
    
    # festival
    $festivalInstalled = & wsl -d $WSL_DISTRO -- command -v festival 2>$null
    if ($?) {
        Write-Host "  [OK] " -NoNewline -ForegroundColor $colors.Success
    } else {
        Write-Host "  [--] " -NoNewline -ForegroundColor $colors.Error
    }
    Write-Host "festival - Voz masculina clara" -ForegroundColor $colors.Text
    
    # espeak
    $espeakInstalled = & wsl -d $WSL_DISTRO -- command -v espeak 2>$null
    if ($?) {
        Write-Host "  [OK] " -NoNewline -ForegroundColor $colors.Success
    } else {
        Write-Host "  [--] " -NoNewline -ForegroundColor $colors.Error
    }
    Write-Host "espeak - Robotica pero eficiente" -ForegroundColor $colors.Text
    
    # none
    Write-Host "  [OK] " -NoNewline -ForegroundColor $colors.Success
    Write-Host "none - Modo silencioso" -ForegroundColor $colors.Text
    
    Write-Host ""
}

# Menu con navegacion por cursor
function Show-Menu {
    param (
        [string]$Title,
        [array]$Options
    )
    
    $selectedIndex = 0
    $key = $null
    
    do {
        Show-Header
        Show-Status
        Show-Engines
        
        Write-Host "  $Title" -ForegroundColor $colors.Accent
        Write-Host "  -------------------------" -ForegroundColor DarkGray
        Write-Host ""
        
        for ($i = 0; $i -lt $Options.Count; $i++) {
            if ($i -eq $selectedIndex) {
                Write-Host "  > " -NoNewline -ForegroundColor $colors.Selected
                Write-Host $Options[$i] -ForegroundColor $colors.Selected
            } else {
                Write-Host "    $($Options[$i])" -ForegroundColor $colors.Text
            }
        }
        
        Write-Host ""
        Write-Host "  Usa las flechas para navegar, Enter para seleccionar, ESC para salir" -ForegroundColor DarkGray
        
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
        }
    } while ($true)
}

# Cambiar motor
function Change-Engine {
    Show-Header
    $engines = @(
        "pico2wave - Voz femenina con personalidad",
        "gtts - La reina de las voces (Google)",
        "festival - El caballero espanol",
        "espeak - Minimalista futurista",
        "none - El silencio es oro",
        "Volver al menu"
    )
    
    $selection = Show-Menu -Title "Elige tu voz favorita:" -Options $engines
    
    if ($selection -ge 0 -and $selection -lt 5) {
        $engineNames = @('pico2wave', 'gtts', 'festival', 'espeak', 'none')
        $newEngine = $engineNames[$selection]
        
        $cmd = "mkdir -p ~/.config/claude-voz; echo 'CLAUDE_VOICE_ENGINE=`"$newEngine`"' > ~/.config/claude-voz/config; echo 'CLAUDE_VOICE_ENABLED=1' >> ~/.config/claude-voz/config"
        & wsl -d $WSL_DISTRO -- bash -c $cmd
        
        Write-Host ""
        Write-Host "  Perfecto! Ahora uso la voz " -NoNewline -ForegroundColor $colors.Success
        Write-Host $newEngine -ForegroundColor $colors.Accent
        Start-Sleep -Seconds 2
    }
}

# Probar voz
function Test-Voice {
    Show-Header
    $messages = @(
        "'Hola carino, soy Claude'",
        "'Ultra think ha completado su magia'",
        "'Tu asistente favorita esta lista'",
        "Escribir mi propio mensaje",
        "Volver"
    )
    
    $selection = Show-Menu -Title "Que quieres que diga?" -Options $messages
    
    if ($selection -ge 0 -and $selection -lt 3) {
        $testMessages = @(
            "Hola carino, soy Claude",
            "Ultra think ha completado su magia",
            "Tu asistente favorita esta lista"
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
        Write-Host "  Reproduciendo..." -ForegroundColor $colors.Accent
        & wsl -d $WSL_DISTRO -- bash -c "cd $SCRIPT_DIR && ./notificar-claude.sh '$message'"
        Write-Host "  Listo!" -ForegroundColor $colors.Success
        Start-Sleep -Seconds 2
    }
}

# Configurar instancia
function Set-Instance {
    Show-Header
    Write-Host "  Dale personalidad a tu terminal" -ForegroundColor $colors.Accent
    Write-Host "  ------------------------------" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  Sugerencias creativas:" -ForegroundColor $colors.Text
    Write-Host "  - ultrathink - Para analisis profundos" -ForegroundColor DarkGray
    Write-Host "  - dreamweaver - Para proyectos creativos" -ForegroundColor DarkGray
    Write-Host "  - speedster - Para tareas rapidas" -ForegroundColor DarkGray
    Write-Host "  - nightowl - Para sesiones nocturnas" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  Nombre actual: " -NoNewline -ForegroundColor $colors.Text
    $current = (Get-VoiceStatus).Instance
    Write-Host $current -ForegroundColor $colors.Accent
    Write-Host ""
    Write-Host "  Nuevo nombre (Enter para mantener): " -NoNewline -ForegroundColor $colors.Selected
    $newName = Read-Host
    
    if ($newName) {
        $cmd = "sed -i '/CLAUDE_INSTANCE_NAME/d' ~/.config/claude-voz/config 2>/dev/null; echo 'CLAUDE_INSTANCE_NAME=`"$newName`"' >> ~/.config/claude-voz/config"
        & wsl -d $WSL_DISTRO -- bash -c $cmd
        Write-Host ""
        Write-Host "  Genial! Ahora eres '$newName'" -ForegroundColor $colors.Success
    }
    Start-Sleep -Seconds 2
}

# Funcion principal
function Main {
    do {
        $options = @(
            "Cambiar voz",
            "Probar voz actual",
            "Personalizar nombre",
            "Activar/Desactivar voz",
            "Instalar voces nuevas",
            "Configuracion avanzada (Linux)",
            "Salir"
        )
        
        $selection = Show-Menu -Title "Que quieres hacer hoy?" -Options $options
        
        switch ($selection) {
            0 { Change-Engine }
            1 { Test-Voice }
            2 { Set-Instance }
            3 { 
                $status = Get-VoiceStatus
                $newState = if ($status.Enabled) { '0' } else { '1' }
                $cmd = "sed -i 's/CLAUDE_VOICE_ENABLED=.*/CLAUDE_VOICE_ENABLED=$newState/' ~/.config/claude-voz/config"
                & wsl -d $WSL_DISTRO -- bash -c $cmd
                Write-Host ""
                if ($newState -eq '1') {
                    Write-Host "  Voz activada! Escucharas mi dulce voz" -ForegroundColor $colors.Success
                } else {
                    Write-Host "  Modo silencioso activado" -ForegroundColor $colors.Warning
                }
                Start-Sleep -Seconds 2
            }
            4 {
                Write-Host ""
                Write-Host "  Abriendo instalador de voces..." -ForegroundColor $colors.Accent
                & wsl -d $WSL_DISTRO -- bash -c "cd $SCRIPT_DIR && ./configurar-voz.sh"
            }
            5 {
                Write-Host ""
                Write-Host "  Abriendo configuracion Linux..." -ForegroundColor $colors.Accent
                & wsl -d $WSL_DISTRO -- bash -c "cd $SCRIPT_DIR && ./configurar-voz.sh"
            }
            6 { 
                Write-Host ""
                Write-Host "  Hasta la proxima!" -ForegroundColor $colors.Selected
                Start-Sleep -Seconds 1
                exit 
            }
            -1 { exit }
        }
    } while ($true)
}

# Iniciar
Main