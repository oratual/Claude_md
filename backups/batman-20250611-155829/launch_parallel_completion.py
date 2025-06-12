#!/usr/bin/env python3
"""
Script para lanzar completación paralela del proyecto Batman Incorporated.
Asigna tareas a agentes específicos para evitar conflictos.
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

# Definir asignación de tareas sin conflictos
TASK_ASSIGNMENTS = {
    "alfred": {
        "agent": "Alfred - Senior Architect",
        "tasks": [
            {
                "id": "16",
                "title": "Arreglar imports faltantes",
                "description": "Arreglar todos los imports faltantes (Any, Dict, etc) en archivos Python",
                "files": [
                    "src/integrations/github_integration.py",
                    "src/integrations/mcp_integration.py",
                    "src/core/arsenal.py",
                    "src/execution/coordinator.py"
                ],
                "priority": "HIGH"
            }
        ]
    },
    "oracle": {
        "agent": "Oracle - QA Specialist", 
        "tasks": [
            {
                "id": "17",
                "title": "Completar tests unitarios",
                "description": "Crear y completar todos los tests unitarios que faltan",
                "files": [
                    "tests/test_arsenal.py",
                    "tests/test_mcp_integration.py",
                    "tests/test_agents.py",
                    "tests/test_config.py"
                ],
                "priority": "HIGH"
            }
        ]
    },
    "robin": {
        "agent": "Robin - DevOps Engineer",
        "tasks": [
            {
                "id": "18",
                "title": "Scripts de instalación",
                "description": "Crear scripts completos de instalación y deployment",
                "files": [
                    "install.sh",
                    "deploy.sh",
                    "scripts/setup_production.sh",
                    "scripts/health_check.sh"
                ],
                "priority": "MEDIUM"
            },
            {
                "id": "20", 
                "title": "GitHub Actions CI/CD",
                "description": "Configurar pipeline completo de CI/CD con GitHub Actions",
                "files": [
                    ".github/workflows/ci.yml",
                    ".github/workflows/deploy.yml",
                    ".github/workflows/tests.yml"
                ],
                "priority": "MEDIUM"
            }
        ]
    },
    "lucius": {
        "agent": "Lucius - Research & Documentation",
        "tasks": [
            {
                "id": "19",
                "title": "Documentar APIs",
                "description": "Crear documentación completa de APIs y ejemplos de uso",
                "files": [
                    "docs/API.md",
                    "docs/EXAMPLES.md",
                    "docs/ARCHITECTURE.md",
                    "examples/"
                ],
                "priority": "MEDIUM"
            }
        ]
    }
}

def create_agent_instructions(agent_name: str, agent_info: dict) -> str:
    """Crea instrucciones específicas para cada agente."""
    
    tasks_detail = []
    for task in agent_info["tasks"]:
        files_list = "\n".join(f"  - {f}" for f in task["files"])
        tasks_detail.append(f"""
### Tarea {task['id']}: {task['title']}
**Prioridad**: {task['priority']}
**Descripción**: {task['description']}
**Archivos asignados**:
{files_list}

**Importante**: Solo modifica los archivos listados arriba para evitar conflictos.
""")
    
    return f"""# Misión para {agent_info['agent']}

## 🎯 Objetivo
Completar las siguientes tareas del proyecto Batman Incorporated sin interferir con otros agentes.

## 📋 Tareas Asignadas
{"".join(tasks_detail)}

## 🔒 Coordinación
- **NO modifiques** archivos fuera de tu lista asignada
- Usa `#memoria` para compartir descubrimientos importantes
- Si necesitas información de otros archivos, úsalos solo como lectura
- Marca cada tarea como completada cuando termines

## 🛠️ Herramientas Recomendadas
- Usa `rg` o `fd` para búsquedas rápidas
- Usa `sd` para reemplazos masivos de texto
- Prefiere `MultiEdit` para cambios múltiples en un archivo

## 📝 Al terminar cada tarea
1. Verifica que el código funcione
2. Actualiza el estado con TodoWrite
3. Comparte insights importantes con #memoria

¡Adelante {agent_name}! 🦇
"""

def prepare_infinity_mode():
    """Prepara el modo Infinity con las asignaciones."""
    
    # Crear directorio de misiones
    missions_dir = Path.home() / ".batman" / "missions" / datetime.now().strftime("%Y%m%d_%H%M%S")
    missions_dir.mkdir(parents=True, exist_ok=True)
    
    # Crear archivo de contexto compartido
    shared_context = {
        "session": "Project Completion",
        "timestamp": datetime.now().isoformat(),
        "agents": list(TASK_ASSIGNMENTS.keys()),
        "total_tasks": sum(len(info["tasks"]) for info in TASK_ASSIGNMENTS.values()),
        "coordination": {
            "mode": "file-based-locking",
            "conflicts": "prevented by task assignment"
        }
    }
    
    context_file = missions_dir / "shared_context.json"
    context_file.write_text(json.dumps(shared_context, indent=2))
    
    print("🦇 BATMAN INCORPORATED - Parallel Project Completion")
    print("=" * 60)
    print(f"\n📁 Misión creada en: {missions_dir}")
    print(f"\n🤖 Agentes asignados:")
    
    instructions_files = {}
    
    for agent_name, agent_info in TASK_ASSIGNMENTS.items():
        # Crear archivo de instrucciones
        instructions = create_agent_instructions(agent_name, agent_info)
        inst_file = missions_dir / f"{agent_name}_mission.md"
        inst_file.write_text(instructions)
        instructions_files[agent_name] = inst_file
        
        print(f"\n  • {agent_info['agent']}:")
        for task in agent_info["tasks"]:
            print(f"    - {task['title']} ({len(task['files'])} archivos)")
    
    print("\n" + "=" * 60)
    print("\n🚀 INSTRUCCIONES DE LANZAMIENTO:\n")
    
    terminal_num = 1
    for agent_name, inst_file in instructions_files.items():
        print(f"Terminal {terminal_num} - {agent_name.upper()}:")
        print(f"  cd ~/glados/batman-incorporated")
        print(f"  claude --model opus --print --dangerously-skip-permissions")
        print(f"  # Luego pega: cat {inst_file}")
        print()
        terminal_num += 1
    
    print("💡 TIPS:")
    print("  - Abre 4 terminales o usa tmux/screen")
    print("  - Lanza todos los agentes al mismo tiempo")
    print("  - Monitorea progreso con: batman --status")
    print("  - Los agentes no se pisarán gracias a la asignación de archivos")
    print("\n🦇 ¡Que comience la operación paralela!")
    
    # Guardar resumen
    summary = {
        "missions_dir": str(missions_dir),
        "agents": {
            agent: {
                "instruction_file": str(inst_file),
                "tasks_count": len(TASK_ASSIGNMENTS[agent]["tasks"]),
                "files_count": sum(len(t["files"]) for t in TASK_ASSIGNMENTS[agent]["tasks"])
            }
            for agent, inst_file in instructions_files.items()
        }
    }
    
    summary_file = missions_dir / "launch_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2))
    
    return missions_dir

if __name__ == "__main__":
    prepare_infinity_mode()