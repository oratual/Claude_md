-- wezterm-claude-orange.lua
-- Configuración para colorear intervenciones de usuario en Claude Code (Wezterm)

local wezterm = require 'wezterm'

-- Configuración del módulo
local module = {}

-- Colores
local ORANGE = '#ff8c00'  -- Naranja intenso más visible que el gris
local BRIGHT_ORANGE = '#ff6500'  -- Variante más intensa

-- Patrones para detectar intervenciones del usuario
local USER_PATTERNS = {
    '^Human:.*',           -- Líneas que empiecen con "Human:"
    '^User:.*',            -- Líneas que empiecen con "User:"
    '^> .*',               -- Líneas que empiecen con "> "
    '^[a-zA-Z0-9_-]{1,20}$', -- Comandos cortos
}

-- Función para aplicar las reglas de coloreo
function module.get_semantic_zones(pane)
    local zones = {}
    local dims = pane:get_dimensions()
    
    -- Recorrer las líneas visibles
    for row = 0, dims.viewport_rows - 1 do
        local line = pane:get_logical_line(row)
        if line then
            local text = line:get_text()
            
            -- Verificar si la línea coincide con patrones de usuario
            for _, pattern in ipairs(USER_PATTERNS) do
                if string.match(text, pattern) then
                    table.insert(zones, {
                        start_y = row,
                        start_x = 0,
                        end_y = row,
                        end_x = string.len(text),
                        color = ORANGE,
                    })
                    break  -- Solo aplicar una regla por línea
                end
            end
        end
    end
    
    return zones
end

-- Función para activar/desactivar
function module.toggle_orange_mode(window, pane)
    local config = window:effective_config()
    
    if config.claude_orange_enabled then
        -- Desactivar
        window:set_config_overrides({
            claude_orange_enabled = false,
            semantic_zones = nil,
        })
        window:toast_notification('Claude Orange', 'Desactivado', nil, 3000)
    else
        -- Activar
        window:set_config_overrides({
            claude_orange_enabled = true,
            semantic_zones = module.get_semantic_zones,
        })
        window:toast_notification('Claude Orange', 'Activado - Naranja intenso', nil, 3000)
    end
end

-- Keybinding sugerido para el toggle
function module.get_keybindings()
    return {
        {
            key = 'o',
            mods = 'CTRL|SHIFT',
            action = wezterm.action_callback(function(window, pane)
                module.toggle_orange_mode(window, pane)
            end),
        },
    }
end

return module