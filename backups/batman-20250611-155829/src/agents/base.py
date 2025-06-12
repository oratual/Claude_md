"""
BaseAgent - Clase base para todos los agentes de Batman Incorporated.
Cada agente es una instancia especializada de Claude con su propio prompt y estilo.
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from abc import ABC, abstractmethod
from datetime import datetime

from core.task import Task, TaskStatus
from features.chapter_logger import ChapterLogger


class BaseAgent(ABC):
    """Clase base para todos los agentes del sistema."""
    
    def __init__(self, name: str, role: str, logger: Optional[ChapterLogger] = None):
        """
        Inicializa un agente base.
        
        Args:
            name: Nombre del agente (alfred, robin, etc.)
            role: Rol/descripción del agente
            logger: Logger para registrar actividades
        """
        self.name = name
        self.role = role
        self.logger = logger
        self.working_dir = Path.cwd()
        
        # Estadísticas del agente
        self.stats = {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'total_time': 0,
            'files_created': [],
            'files_modified': []
        }
        
        # Herramientas disponibles del Arsenal
        self.available_tools = {}
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Retorna el prompt del sistema que define la personalidad del agente.
        Debe ser implementado por cada agente específico.
        """
        pass
    
    @abstractmethod
    def get_specialties(self) -> List[str]:
        """
        Retorna la lista de especialidades del agente.
        Usado para asignar tareas apropiadas.
        """
        pass
    
    def execute_task(self, task: Task, context_files: List[str] = None) -> bool:
        """
        Ejecuta una tarea usando Claude CLI.
        
        Args:
            task: Tarea a ejecutar
            context_files: Lista de archivos para incluir como contexto
            
        Returns:
            True si la tarea se completó exitosamente
        """
        start_time = datetime.now()
        self._log(f"Iniciando tarea: {task.title}")
        
        try:
            # Marcar tarea como en progreso
            task.start()
            
            # Construir el prompt completo
            prompt = self._build_prompt(task, context_files)
            
            # Ejecutar con Claude CLI
            success, output, error = self._execute_claude(prompt, task)
            
            if success:
                task.complete(output)
                self.stats['tasks_completed'] += 1
                self._log(f"✅ Tarea completada: {task.title}")
            else:
                task.fail(error)
                self.stats['tasks_failed'] += 1
                self._log(f"❌ Tarea fallida: {task.title}")
            
            # Actualizar tiempo total
            elapsed = (datetime.now() - start_time).total_seconds()
            self.stats['total_time'] += elapsed
            
            return success
            
        except Exception as e:
            error_msg = f"Error ejecutando tarea: {str(e)}"
            self._log(f"💥 {error_msg}")
            task.fail(error_msg)
            self.stats['tasks_failed'] += 1
            return False
    
    def _build_prompt(self, task: Task, context_files: List[str] = None) -> str:
        """
        Construye el prompt completo para Claude.
        
        Args:
            task: Tarea a ejecutar
            context_files: Archivos a incluir como contexto
            
        Returns:
            Prompt completo formateado
        """
        prompt_parts = []
        
        # System prompt del agente
        prompt_parts.append(self.get_system_prompt())
        prompt_parts.append("")
        
        # Información de la tarea
        prompt_parts.append(f"## Tarea Actual")
        prompt_parts.append(f"**Título**: {task.title}")
        prompt_parts.append(f"**Descripción**: {task.description}")
        prompt_parts.append(f"**Tipo**: {task.type.value}")
        prompt_parts.append(f"**Prioridad**: {task.priority.value}")
        
        if task.tags:
            prompt_parts.append(f"**Tags**: {', '.join(task.tags)}")
        
        prompt_parts.append("")
        
        # Contexto de archivos si se proporciona
        if context_files:
            prompt_parts.append("## Contexto del Proyecto")
            for file_path in context_files:
                if Path(file_path).exists():
                    prompt_parts.append(f"\n### Archivo: {file_path}")
                    prompt_parts.append("```")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Limitar tamaño del archivo
                            if len(content) > 10000:
                                content = content[:10000] + "\n... (truncado)"
                            prompt_parts.append(content)
                    except Exception as e:
                        prompt_parts.append(f"Error leyendo archivo: {e}")
                    prompt_parts.append("```")
            prompt_parts.append("")
        
        # Arsenal de herramientas disponibles
        if self.available_tools:
            prompt_parts.append("## Arsenal de Herramientas")
            prompt_parts.append("Las siguientes herramientas optimizadas están disponibles:")
            for tool_type, tool_cmd in self.available_tools.items():
                prompt_parts.append(f"- **{tool_type}**: `{tool_cmd}`")
            prompt_parts.append("\nPrefiérelas sobre las herramientas estándar cuando sea posible.\n")
        
        # Instrucciones específicas
        prompt_parts.append("## Instrucciones")
        prompt_parts.append("1. Ejecuta la tarea descrita arriba")
        prompt_parts.append("2. Usa las herramientas disponibles (Edit, Write, Bash, etc.)")
        prompt_parts.append("3. Prefiere las herramientas del Arsenal cuando estén disponibles")
        prompt_parts.append("4. Sé eficiente y directo")
        prompt_parts.append("5. Reporta el progreso claramente")
        prompt_parts.append("6. Si encuentras problemas, intenta resolverlos")
        
        # MCPs disponibles
        prompt_parts.append("\n## MCPs Disponibles")
        prompt_parts.append("- **filesystem**: Operaciones de archivos optimizadas")
        prompt_parts.append("- **memory**: Compartir conocimiento entre agentes")
        prompt_parts.append("- **everything**: Búsqueda global de archivos")
        prompt_parts.append("- **sequentialthinking**: Razonamiento paso a paso")
        
        # Contexto MCP compartido si está disponible
        if hasattr(self, 'mcp_prompt_section') and self.mcp_prompt_section:
            prompt_parts.append(self.mcp_prompt_section)
        
        # Directorio de trabajo
        prompt_parts.append(f"\n**Directorio de trabajo**: {self.working_dir}")
        
        return "\n".join(prompt_parts)
    
    def _execute_claude(self, prompt: str, task: Task) -> Tuple[bool, str, str]:
        """
        Ejecuta Claude CLI con el prompt dado.
        
        Args:
            prompt: Prompt completo para Claude
            task: Tarea siendo ejecutada (para logging)
            
        Returns:
            Tupla (success, output, error)
        """
        self._log("🤖 Ejecutando con Claude CLI...")
        
        # Guardar prompt para debugging
        prompt_file = Path(f"/tmp/batman_prompt_{task.id}.txt")
        prompt_file.write_text(prompt, encoding='utf-8')
        
        try:
            # Ejecutar Claude CLI
            cmd = [
                'claude',
                '--print',  # Modo no interactivo
                '--dangerously-skip-permissions',  # Sin interrupciones
                '--max-turns', '10',  # Máximo 10 turnos
                prompt
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.working_dir),
                timeout=600  # 10 minutos máximo
            )
            
            # Guardar respuesta para debugging
            response_file = Path(f"/tmp/batman_response_{task.id}.txt")
            response_file.write_text(result.stdout, encoding='utf-8')
            
            if result.returncode == 0:
                return True, result.stdout, ""
            else:
                return False, result.stdout, result.stderr
                
        except subprocess.TimeoutExpired:
            error = "Timeout: La tarea tomó más de 10 minutos"
            self._log(f"⏱️ {error}")
            return False, "", error
            
        except Exception as e:
            error = f"Error ejecutando Claude: {str(e)}"
            self._log(f"💥 {error}")
            return False, "", error
    
    def _log(self, message: str):
        """Helper para logging."""
        if self.logger:
            self.logger.log(f"[{self.name.upper()}] {message}")
        else:
            print(f"[{self.name.upper()}] {message}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del agente."""
        return {
            'name': self.name,
            'role': self.role,
            'stats': self.stats,
            'specialties': self.get_specialties()
        }