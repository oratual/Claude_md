#!/usr/bin/env python3
"""
Batman Incorporated - Sistema Unificado de Automatización
Un Batman para gobernarlos a todos.
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
import yaml
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.batman import BatmanIncorporated
from core.config import Config
from features.chapter_logger import ChapterLogger


def main():
    """Entry point principal de Batman Incorporated."""
    parser = argparse.ArgumentParser(
        description="Batman Incorporated - Sistema Unificado de Automatización",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  batman "crear API REST para blog"
  batman --mode=seguro "refactorizar sistema de pagos"
  batman --mode=redundante "implementar autenticación"
  batman --auto                      # Modo automático 24/7
  batman --status                    # Ver estado actual
  batman --off                       # Detener elegantemente
        """
    )
    
    # Argumentos principales
    parser.add_argument('task', nargs='?', help='Descripción de la tarea a realizar')
    
    # Modos de ejecución
    parser.add_argument('--mode', choices=['seguro', 'rapido', 'redundante', 'infinity'],
                        default='auto', help='Modo de ejecución')
    
    # Infinity Mode específico
    parser.add_argument('--infinity', action='store_true',
                        help='Activar Infinity Mode (agentes paralelos reales)')
    parser.add_argument('--real-agents', action='store_true',
                        help='Usar agentes Claude reales en lugar de simulados')
    
    # Control del sistema
    parser.add_argument('--auto', action='store_true',
                        help='Activar modo automático 24/7')
    parser.add_argument('--off', action='store_true',
                        help='Detener el sistema elegantemente')
    parser.add_argument('--status', action='store_true',
                        help='Mostrar estado actual del sistema')
    parser.add_argument('--install-tools', action='store_true',
                        help='Instalar herramientas del Arsenal sin sudo')
    
    # Opciones avanzadas
    parser.add_argument('--max-agents', type=int, default=5,
                        help='Número máximo de agentes paralelos')
    parser.add_argument('--no-ci', action='store_true',
                        help='Desactivar GitHub Actions')
    parser.add_argument('--local-only', action='store_true',
                        help='Solo ejecución local, sin push a GitHub')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Mostrar información detallada')
    parser.add_argument('--config', type=str,
                        help='Archivo de configuración alternativo')
    
    args = parser.parse_args()
    
    # Validar argumentos
    if not any([args.task, args.auto, args.off, args.status, args.install_tools, args.infinity]):
        parser.print_help()
        sys.exit(1)
    
    # Manejar Infinity Mode
    if args.infinity or args.mode == 'infinity':
        print("🌌 Activando Infinity Mode...")
        from pathlib import Path
        import subprocess
        
        # Verificar si el launcher está disponible
        launcher_path = Path(__file__).parent / "launch-infinity"
        if launcher_path.exists():
            print("🚀 Lanzando agentes paralelos...")
            subprocess.run([str(launcher_path), "--auto"])
        else:
            print("❌ Launcher no encontrado. Ejecuta primero: python3 parallel_launcher.py")
        return
    
    try:
        # Cargar configuración
        from pathlib import Path as PathlibPath
        config_path = args.config or PathlibPath.home() / ".glados" / "batman-incorporated" / "config.yaml"
        config = Config(config_path)
        
        # Aplicar opciones de línea de comandos
        if args.no_ci:
            config.set('github.actions.enabled', False)
        if args.local_only:
            config.set('github.push.enabled', False)
        if args.max_agents:
            config.set('execution.max_agents', args.max_agents)
        if args.real_agents:
            config.set('execution.use_real_agents', True)
        
        # Inicializar Batman
        batman = BatmanIncorporated(config, verbose=args.verbose)
        
        # Ejecutar comando
        if args.install_tools:
            # Modo especial: instalar herramientas
            from src.tools import ToolInstaller
            installer = ToolInstaller()
            installer.install_all()
            sys.exit(0)
        elif args.status:
            batman.show_status()
        elif args.off:
            batman.stop()
        elif args.auto:
            batman.start_auto_mode()
        elif args.task:
            batman.execute_task(args.task, mode=args.mode)
        
    except KeyboardInterrupt:
        print("\n\n🦇 Batman Incorporated detenido por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()