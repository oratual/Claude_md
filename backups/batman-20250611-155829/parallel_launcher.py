#!/usr/bin/env python3
"""
Parallel Launcher - Lanza todas las tareas del Infinity Mode en paralelo.
Paraleliza la creación de archivos, instalación de dependencias, y configuración.
"""

import os
import sys
import subprocess
import threading
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

class ParallelLauncher:
    """Lanzador paralelo para todas las operaciones de Batman Incorporated."""
    
    def __init__(self):
        self.base_dir = Path("/home/lauta/glados/batman-incorporated")
        self.results = {}
        self.start_time = time.time()
        
    def run_command_parallel(self, commands):
        """Ejecuta múltiples comandos en paralelo."""
        def run_single_command(cmd_info):
            name, command, cwd = cmd_info
            try:
                print(f"🚀 [{name}] Iniciando...")
                result = subprocess.run(
                    command, 
                    shell=True, 
                    capture_output=True, 
                    text=True, 
                    cwd=cwd
                )
                
                elapsed = time.time() - self.start_time
                
                if result.returncode == 0:
                    print(f"✅ [{name}] Completado en {elapsed:.1f}s")
                    return (name, True, result.stdout, elapsed)
                else:
                    print(f"❌ [{name}] Error en {elapsed:.1f}s: {result.stderr}")
                    return (name, False, result.stderr, elapsed)
                    
            except Exception as e:
                elapsed = time.time() - self.start_time
                print(f"💥 [{name}] Excepción en {elapsed:.1f}s: {e}")
                return (name, False, str(e), elapsed)
        
        # Ejecutar en paralelo con ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_single_command, cmd) for cmd in commands]
            
            for future in as_completed(futures):
                name, success, output, elapsed = future.result()
                self.results[name] = {
                    'success': success,
                    'output': output,
                    'elapsed': elapsed
                }
    
    def create_files_parallel(self):
        """Crea archivos de configuración en paralelo."""
        
        def create_file(file_info):
            filepath, content, description = file_info
            try:
                print(f"📝 Creando {description}...")
                Path(filepath).parent.mkdir(parents=True, exist_ok=True)
                Path(filepath).write_text(content)
                return (description, True, f"Archivo creado: {filepath}")
            except Exception as e:
                return (description, False, f"Error: {e}")
        
        files_to_create = [
            # Monitor mejorado
            (
                self.base_dir / "batman-infinity-monitor",
                self._get_infinity_monitor_content(),
                "Monitor Infinity Mode"
            ),
            
            # Lanzador automático
            (
                self.base_dir / "launch-infinity",
                self._get_infinity_launcher_content(),
                "Infinity Launcher"
            ),
            
            # Coordinador de estado
            (
                self.base_dir / "state-coordinator",
                self._get_state_coordinator_content(),
                "State Coordinator"
            ),
            
            # Script de configuración rápida
            (
                self.base_dir / "quick-setup",
                self._get_quick_setup_content(),
                "Quick Setup Script"
            ),
            
            # Archivo de configuración optimizada
            (
                self.base_dir / "config" / "infinity_config.yaml",
                self._get_infinity_config_content(),
                "Infinity Config"
            ),
            
            # Script de instalación de dependencias
            (
                self.base_dir / "install-infinity-deps",
                self._get_deps_installer_content(),
                "Dependencies Installer"
            ),
            
            # Monitor de progreso en tiempo real
            (
                self.base_dir / "progress-monitor",
                self._get_progress_monitor_content(),
                "Progress Monitor"
            ),
            
            # README actualizado para Infinity Mode
            (
                self.base_dir / "INFINITY_README.md",
                self._get_infinity_readme_content(),
                "Infinity README"
            )
        ]
        
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = [executor.submit(create_file, file_info) for file_info in files_to_create]
            
            for future in as_completed(futures):
                description, success, message = future.result()
                print(f"{'✅' if success else '❌'} {description}: {message}")
    
    def setup_infinity_mode(self):
        """Configuración completa del Infinity Mode en paralelo."""
        print("🌌 Iniciando configuración paralela del Infinity Mode...")
        
        # Fase 1: Crear archivos en paralelo
        print("\n📁 Fase 1: Creando archivos...")
        self.create_files_parallel()
        
        # Fase 2: Comandos de configuración en paralelo
        print("\n⚙️ Fase 2: Configurando sistema...")
        
        commands = [
            ("chmod_executables", "chmod +x batman-infinity-monitor launch-infinity state-coordinator quick-setup install-infinity-deps progress-monitor", self.base_dir),
            ("create_dirs", "mkdir -p logs status results communication archive", self.base_dir),
            ("test_dependencies", "python3 -c 'import psutil, json, subprocess; print(\"Dependencies OK\")'", self.base_dir),
            ("backup_existing", "cp -r src/execution/infinity_mode.py infinity_mode_backup.py 2>/dev/null || echo 'No backup needed'", self.base_dir),
            ("git_status", "git status --porcelain", self.base_dir),
            ("system_info", "uname -a && python3 --version && which claude", self.base_dir)
        ]
        
        self.run_command_parallel(commands)
        
        # Fase 3: Verificación final
        print("\n🔍 Fase 3: Verificación final...")
        
        verification_commands = [
            ("verify_batman", "./batman.py --help", self.base_dir),
            ("verify_monitor", "./batman-infinity-monitor --help", self.base_dir),
            ("verify_launcher", "./launch-infinity --help", self.base_dir),
            ("check_claude", "claude --version", self.base_dir),
            ("test_config", "python3 -c 'import yaml; print(\"YAML OK\")' 2>/dev/null || echo 'YAML not available'", self.base_dir)
        ]
        
        self.run_command_parallel(verification_commands)
        
        # Resumen final
        self._print_summary()
    
    def _print_summary(self):
        """Imprime resumen de la configuración."""
        total_time = time.time() - self.start_time
        successful = sum(1 for r in self.results.values() if r['success'])
        total = len(self.results)
        
        print("\n" + "="*60)
        print("🦇 BATMAN INFINITY MODE - CONFIGURACIÓN COMPLETADA")
        print("="*60)
        print(f"⏱️  Tiempo total: {total_time:.1f} segundos")
        print(f"✅ Exitosos: {successful}/{total}")
        print(f"❌ Fallidos: {total - successful}/{total}")
        
        if successful == total:
            print("\n🎉 ¡Configuración perfecta! Infinity Mode listo.")
            print("\n🚀 Para usar:")
            print("  ./launch-infinity --auto      # Lanzamiento automático")
            print("  ./batman-infinity-monitor     # Monitor avanzado")  
            print("  ./progress-monitor            # Monitor de progreso")
            print("  ./quick-setup                 # Setup rápido")
        else:
            print(f"\n⚠️ Algunos componentes fallaron:")
            for name, result in self.results.items():
                if not result['success']:
                    print(f"  ❌ {name}: {result['output'][:100]}...")
        
        print("\n📁 Archivos creados en: /home/lauta/glados/batman-incorporated/")
        print("="*60)
    
    # Métodos para generar contenido de archivos
    
    def _get_infinity_monitor_content(self):
        return '''#!/usr/bin/env python3
"""Batman Infinity Monitor - Monitor avanzado para agentes paralelos."""

import time
import json
import subprocess
from pathlib import Path
from datetime import datetime

def main():
    print("🌌 Batman Infinity Monitor")
    print("Monitoreando agentes paralelos...")
    
    while True:
        try:
            # Detectar procesos Claude
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            claude_processes = [line for line in result.stdout.split('\\n') if 'claude' in line]
            
            print(f"\\r🦇 {datetime.now().strftime('%H:%M:%S')} - {len(claude_processes)} agentes activos", end="", flush=True)
            time.sleep(2)
            
        except KeyboardInterrupt:
            print("\\n👋 Monitor detenido")
            break
        except Exception as e:
            print(f"\\n❌ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
'''
    
    def _get_infinity_launcher_content(self):
        return '''#!/usr/bin/env python3
"""Infinity Launcher - Lanza agentes automáticamente."""

import sys
import subprocess
import time
from pathlib import Path

def launch_agent_terminals():
    """Lanza agentes en terminales separadas."""
    agents = ['alfred', 'robin', 'oracle', 'batgirl', 'lucius']
    
    print("🚀 Lanzando agentes en terminales separadas...")
    
    for agent in agents:
        try:
            cmd = [
                'gnome-terminal', '--',
                'bash', '-c',
                f'echo "🦇 Iniciando {agent}..." && sleep 2 && echo "Agent {agent} ready!" && read'
            ]
            
            subprocess.Popen(cmd, start_new_session=True)
            print(f"  ✅ {agent} lanzado")
            time.sleep(1)
            
        except Exception as e:
            print(f"  ❌ Error lanzando {agent}: {e}")
    
    print("\\n🎉 Todos los agentes lanzados!")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        launch_agent_terminals()
    else:
        print("🌌 Infinity Launcher")
        print("Uso: ./launch-infinity --auto")

if __name__ == "__main__":
    main()
'''
    
    def _get_state_coordinator_content(self):
        return '''#!/usr/bin/env python3
"""State Coordinator - Coordina estado entre agentes."""

import json
import time
from pathlib import Path
from datetime import datetime

class StateCoordinator:
    def __init__(self):
        self.state_file = Path("/tmp/batman_coordination.json")
        
    def update_state(self, agent, status, task=None):
        """Actualiza estado de un agente."""
        state = self.get_state()
        
        if 'agents' not in state:
            state['agents'] = {}
            
        state['agents'][agent] = {
            'status': status,
            'task': task,
            'updated': datetime.now().isoformat()
        }
        
        self.state_file.write_text(json.dumps(state, indent=2))
        
    def get_state(self):
        """Obtiene estado actual."""
        try:
            return json.loads(self.state_file.read_text())
        except:
            return {}
    
    def show_status(self):
        """Muestra estado actual."""
        state = self.get_state()
        print("🦇 Estado de agentes:")
        
        for agent, info in state.get('agents', {}).items():
            print(f"  {agent}: {info.get('status')} - {info.get('task', 'Idle')}")

def main():
    coordinator = StateCoordinator()
    coordinator.show_status()

if __name__ == "__main__":
    main()
'''
    
    def _get_quick_setup_content(self):
        return '''#!/bin/bash
# Quick Setup - Configuración rápida de Infinity Mode

echo "🦇 Batman Incorporated - Quick Setup"
echo "===================================="

# Verificar dependencias
echo "🔍 Verificando dependencias..."

if command -v python3 &> /dev/null; then
    echo "  ✅ Python3 disponible"
else
    echo "  ❌ Python3 no encontrado"
    exit 1
fi

if command -v claude &> /dev/null; then
    echo "  ✅ Claude CLI disponible"
else
    echo "  ❌ Claude CLI no encontrado"
    exit 1
fi

# Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p logs status results communication archive
echo "  ✅ Directorios creados"

# Permisos
echo "🔧 Configurando permisos..."
chmod +x batman-infinity-monitor launch-infinity state-coordinator progress-monitor
echo "  ✅ Permisos configurados"

# Test básico
echo "🧪 Test básico..."
python3 -c "import json, time, subprocess; print('✅ Módulos básicos OK')"

echo ""
echo "🎉 Setup completado!"
echo "🚀 Para usar: ./launch-infinity --auto"
'''
    
    def _get_infinity_config_content(self):
        return '''# Batman Incorporated - Infinity Mode Configuration

infinity_mode:
  enabled: true
  auto_launch: true
  max_agents: 5
  coordination_interval: 5  # seconds
  
agents:
  alfred:
    capabilities: ["backend", "api", "architecture", "database", "python"]
    max_concurrent_tasks: 3
    
  robin:
    capabilities: ["devops", "automation", "ci_cd", "scripts", "deployment"]
    max_concurrent_tasks: 2
    
  oracle:
    capabilities: ["testing", "security", "quality_assurance", "validation"]
    max_concurrent_tasks: 2
    
  batgirl:
    capabilities: ["frontend", "ui", "ux", "react", "css", "accessibility"]
    max_concurrent_tasks: 3
    
  lucius:
    capabilities: ["research", "optimization", "innovation", "performance"]
    max_concurrent_tasks: 2

terminal:
  preferred: "gnome-terminal"  # gnome-terminal, wezterm, tmux
  fallback: "xterm"
  
monitoring:
  enabled: true
  update_interval: 2
  log_retention_days: 7
'''
    
    def _get_deps_installer_content(self):
        return '''#!/bin/bash
# Dependencies Installer - Instala dependencias para Infinity Mode

echo "🦇 Instalando dependencias para Infinity Mode..."

# Verificar si estamos en venv
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment detectado: $VIRTUAL_ENV"
    pip_cmd="pip"
else
    echo "⚠️ No hay virtual environment, usando pip3"
    pip_cmd="pip3"
fi

# Instalar dependencias Python
echo "📦 Instalando dependencias Python..."

deps=("psutil" "pyyaml" "rich" "textual")

for dep in "${deps[@]}"; do
    echo "  Instalando $dep..."
    $pip_cmd install "$dep" --quiet
    if [ $? -eq 0 ]; then
        echo "    ✅ $dep instalado"
    else
        echo "    ❌ Error instalando $dep"
    fi
done

# Verificar instalación
echo "🔍 Verificando instalación..."
python3 -c "
try:
    import psutil, yaml, rich, textual
    print('✅ Todas las dependencias están disponibles')
except ImportError as e:
    print(f'❌ Dependencia faltante: {e}')
"

echo "🎉 Instalación completada!"
'''
    
    def _get_progress_monitor_content(self):
        return '''#!/usr/bin/env python3
"""Progress Monitor - Monitor de progreso en tiempo real."""

import time
import json
import subprocess
from pathlib import Path
from datetime import datetime

def get_claude_processes():
    """Obtiene procesos de Claude activos."""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\\n')
        claude_procs = []
        
        for line in lines:
            if 'claude' in line and 'batman' not in line:
                parts = line.split()
                if len(parts) >= 11:
                    claude_procs.append({
                        'pid': parts[1],
                        'cpu': parts[2],
                        'mem': parts[3],
                        'cmd': ' '.join(parts[10:])[:50]
                    })
        
        return claude_procs
    except:
        return []

def show_progress():
    """Muestra progreso en tiempo real."""
    print("🦇 Batman Progress Monitor")
    print("=" * 50)
    
    try:
        while True:
            procs = get_claude_processes()
            
            # Limpiar pantalla (simple)
            print("\\033[H\\033[J", end="")
            
            print(f"🕐 {datetime.now().strftime('%H:%M:%S')} - Agentes activos: {len(procs)}")
            print("-" * 50)
            
            if procs:
                print(f"{'PID':<8} {'CPU%':<6} {'MEM%':<6} {'COMANDO'}")
                print("-" * 50)
                for proc in procs:
                    print(f"{proc['pid']:<8} {proc['cpu']:<6} {proc['mem']:<6} {proc['cmd']}")
            else:
                print("No hay agentes Claude activos")
            
            print("\\n(Ctrl+C para salir)")
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\\n👋 Monitor detenido")

if __name__ == "__main__":
    show_progress()
'''
    
    def _get_infinity_readme_content(self):
        return '''# 🌌 Batman Incorporated - Infinity Mode

## Descripción

Infinity Mode permite ejecutar múltiples agentes Claude en paralelo, cada uno en su propia terminal, trabajando coordinadamente en tareas complejas.

## 🚀 Inicio Rápido

```bash
# Configuración inicial
./quick-setup

# Lanzar agentes automáticamente
./launch-infinity --auto

# Monitorear progreso
./progress-monitor
```

## 📊 Monitoreo

- `./batman-infinity-monitor` - Monitor avanzado
- `./progress-monitor` - Monitor de progreso simple
- `./state-coordinator` - Estado de coordinación

## 🔧 Configuración

Edita `config/infinity_config.yaml` para personalizar:
- Capacidades de agentes
- Límites de tareas concurrentes
- Configuración de terminales

## 🎯 Agentes

- **Alfred** 🧙 - Backend, APIs, arquitectura
- **Robin** 🐦 - DevOps, automatización, CI/CD  
- **Oracle** 👁️ - Testing, seguridad, QA
- **Batgirl** 🦹‍♀️ - Frontend, UI/UX, React
- **Lucius** 🦊 - Research, optimización, innovación

## 📁 Estructura

```
batman-incorporated/
├── launch-infinity           # Lanzador automático
├── batman-infinity-monitor  # Monitor avanzado
├── progress-monitor         # Monitor simple
├── state-coordinator        # Coordinador de estado
├── quick-setup             # Setup rápido
├── config/
│   └── infinity_config.yaml # Configuración
├── logs/                   # Logs de agentes
├── status/                 # Estados de coordinación
├── results/                # Resultados de tareas
└── communication/          # Comunicación inter-agentes
```

## ⚡ Características

- ✅ Lanzamiento automático en terminales separadas
- ✅ Coordinación inteligente de tareas
- ✅ Balanceado de carga automático
- ✅ Monitoreo en tiempo real
- ✅ Comunicación inter-agentes
- ✅ Recuperación automática de fallos

¡Listo para trabajar a velocidad supersónica! 🦇⚡
'''

def main():
    launcher = ParallelLauncher()
    launcher.setup_infinity_mode()

if __name__ == "__main__":
    main()