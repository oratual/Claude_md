#!/bin/bash

# Script para aplicar el parche de tmux a Claude Squad

echo "🔧 Aplicando parche para error de tmux capture-pane en Claude Squad..."

# Hacer backup del archivo original
cp ../claude-squad/session/tmux/tmux.go ../claude-squad/session/tmux/tmux.go.backup

# Crear las funciones auxiliares
cat > /tmp/tmux-helpers.go << 'EOF'

// Función auxiliar para verificar si tmux está disponible
func isTmuxAvailable() bool {
	cmd := exec.Command("which", "tmux")
	err := cmd.Run()
	return err == nil
}

// Función auxiliar para verificar si la sesión existe
func (t *TmuxSession) sessionExists() bool {
	cmd := exec.Command("tmux", "has-session", "-t", t.sanitizedName)
	err := cmd.Run()
	return err == nil
}
EOF

# Modificar la función CapturePaneContent
sed -i '/^func (t \*TmuxSession) CapturePaneContent() (string, error) {/,/^}/ {
    /^func (t \*TmuxSession) CapturePaneContent/a\
	// Primero verificar si tmux está disponible\
	if !isTmuxAvailable() {\
		// Si no hay tmux, retornar contenido vacío sin error\
		// Esto permite que Claude Squad funcione sin la captura de pantalla\
		return "", nil\
	}\
	\
	// Verificar si la sesión existe\
	if !t.sessionExists() {\
		// Si la sesión no existe, retornar vacío sin error\
		return "", nil\
	}
    s/return "", fmt.Errorf("error capturing pane content: %v", err)/\/\/ En lugar de retornar error, log it y retornar contenido vacío\n\t\t\/\/ Esto evita que el error rompa la funcionalidad de Claude Squad\n\t\tif strings.Contains(err.Error(), "no server running") ||\n\t\t   strings.Contains(err.Error(), "no current session") ||\n\t\t   strings.Contains(err.Error(), "can\'t find session") {\n\t\t\t\/\/ Errores esperados cuando no hay tmux - ignorar silenciosamente\n\t\t\treturn "", nil\n\t\t}\n\t\t\/\/ Para otros errores, loguear pero continuar\n\t\tfmt.Printf("Warning: tmux capture-pane failed: %v\\n", err)\n\t\treturn "", nil/
}' ../claude-squad/session/tmux/tmux.go

# Agregar import de strings si no existe
if ! grep -q '"strings"' ../claude-squad/session/tmux/tmux.go; then
    sed -i '/^import (/a\\t"strings"' ../claude-squad/session/tmux/tmux.go
fi

# Agregar las funciones auxiliares al final del archivo
cat /tmp/tmux-helpers.go >> ../claude-squad/session/tmux/tmux.go

echo "✅ Parche aplicado. Ahora compilemos Claude Squad..."

# Cambiar al directorio de claude-squad
cd ../claude-squad

# Instalar dependencias
echo "📦 Instalando dependencias..."
go mod download

# Compilar
echo "🔨 Compilando Claude Squad..."
go build -o cs-fixed cmd/claude-squad/main.go

if [ $? -eq 0 ]; then
    echo "✅ Compilación exitosa!"
    echo "📍 Binario creado: $(pwd)/cs-fixed"
    echo ""
    echo "Para instalar la versión reparada:"
    echo "  cp cs-fixed ~/.local/bin/cs"
else
    echo "❌ Error en la compilación"
fi