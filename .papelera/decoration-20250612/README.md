# 🍊 NaranjaUserChat - Claude Code Orange Mode

Cambia el color de las intervenciones del usuario en Claude Code de gris oscuro a **naranja intenso** de manera eficiente.

## 🎯 Dos Versiones Disponibles

### 🚀 RECOMENDADO: Versión Wezterm (Nativa)
**Cero impacto en rendimiento**, usa capacidades nativas de Wezterm.

```bash
# Instalación automática
~/glados/scripts/decoration/install-wezterm-orange.sh

# Uso: Ctrl+Shift+O en Wezterm para toggle
```

### 🔧 Versión Universal (Wrapper)
Compatible con cualquier terminal, usa interceptor inteligente.

```bash
# Crear alias
echo 'alias claude="$HOME/glados/scripts/decoration/NaranjaUserChat"' >> ~/.bashrc
source ~/.bashrc

# Activar
claude --naranja-on
```

## ⌨️ Alias Recomendados

```bash
# Agregar a ~/.bashrc
alias orange="~/glados/scripts/decoration/toggle-orange.sh"
alias claude-orange="~/glados/scripts/decoration/NaranjaUserChat"

# Uso rápido
orange          # Toggle on/off
orange status   # Ver estado
orange on/off   # Control directo
```

## 🎨 Características

- **Naranja intenso** `#ff8c00` para intervenciones del usuario
- **Toggle instantáneo** (Ctrl+Shift+O en Wezterm)
- **Mínimo impacto** en rendimiento
- **Activación/desactivación** global persistente
- **Compatible** con todos los argumentos de Claude Code

## 🔧 Instalación Rápida (Wezterm)

```bash
# 1. Instalar
~/glados/scripts/decoration/install-wezterm-orange.sh

# 2. Reiniciar Wezterm

# 3. En Claude Code presionar: Ctrl+Shift+O
```

## 💡 Ventajas de la Versión Wezterm

1. **Cero overhead** - Usa semantic zones nativas
2. **Toggle instantáneo** - Sin reiniciar Claude
3. **No modifica** el comportamiento de Claude Code
4. **Notificaciones visuales** - Toast cuando activas/desactivas
5. **Más eficiente** - Procesamiento en el terminal, no en scripts externos

## 🐛 Troubleshooting

**¿No funciona el coloreo?**
```bash
# Verificar estado
orange status

# Verificar Wezterm config
cat ~/.config/wezterm/wezterm.lua | grep claude_orange
```

**¿Wezterm no responde a Ctrl+Shift+O?**
```bash
# Verificar que el módulo está cargado
ls ~/.config/wezterm/wezterm-claude-orange.lua
```

## 🎯 Patrones Detectados

El sistema colorea líneas que empiecen con:
- `Human:`
- `User:` 
- `> `
- Comandos cortos (1-20 caracteres)

## 🔄 Migrar de Wrapper a Wezterm

```bash
# Desactivar wrapper
claude --naranja-off

# Instalar versión Wezterm
~/glados/scripts/decoration/install-wezterm-orange.sh

# Quitar alias si ya no lo necesitas
# (Comentar línea en ~/.bashrc)
```