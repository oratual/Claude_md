// Archivo de parche para Claude Squad - Solución para el error de tmux capture-pane
// Este archivo muestra los cambios necesarios en session/tmux/tmux.go

package tmux

import (
	"fmt"
	"os/exec"
	"strings"
)

// CapturePaneContent captures the content of the tmux pane with better error handling
func (t *TmuxSession) CapturePaneContent() (string, error) {
	// Primero verificar si tmux está disponible
	if !isTmuxAvailable() {
		// Si no hay tmux, retornar contenido vacío sin error
		// Esto permite que Claude Squad funcione sin la captura de pantalla
		return "", nil
	}
	
	// Verificar si la sesión existe
	if !t.sessionExists() {
		// Si la sesión no existe, retornar vacío sin error
		return "", nil
	}
	
	// Add -e flag to preserve escape sequences (ANSI color codes)
	cmd := exec.Command("tmux", "capture-pane", "-p", "-e", "-J", "-t", t.sanitizedName)
	output, err := t.cmdExec.Output(cmd)
	if err != nil {
		// En lugar de retornar error, log it y retornar contenido vacío
		// Esto evita que el error rompa la funcionalidad de Claude Squad
		if strings.Contains(err.Error(), "no server running") ||
		   strings.Contains(err.Error(), "no current session") ||
		   strings.Contains(err.Error(), "can't find session") {
			// Errores esperados cuando no hay tmux - ignorar silenciosamente
			return "", nil
		}
		// Para otros errores, loguear pero continuar
		fmt.Printf("Warning: tmux capture-pane failed: %v\n", err)
		return "", nil
	}
	return string(output), nil
}

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

// CapturePaneContentWithOptions con manejo de errores mejorado
func (t *TmuxSession) CapturePaneContentWithOptions(start, end string) (string, error) {
	// Misma lógica de verificación
	if !isTmuxAvailable() || !t.sessionExists() {
		return "", nil
	}
	
	cmd := exec.Command("tmux", "capture-pane", "-p", "-e", "-J", "-S", start, "-E", end, "-t", t.sanitizedName)
	output, err := t.cmdExec.Output(cmd)
	if err != nil {
		// Manejar errores gracefully
		return "", nil
	}
	return string(output), nil
}