"""
Task Analyzer - Analiza descripciones de tareas y genera planes de ejecución.
Utiliza Claude para análisis inteligente de requisitos.
"""

import subprocess
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from core.task import Task, TaskType, TaskPriority
from features.chapter_logger import ChapterLogger


class TaskAnalyzer:
    """
    Analiza descripciones de tareas y genera planes de ejecución detallados.
    Usa Claude para entender requisitos y crear subtareas apropiadas.
    """
    
    def __init__(self, logger: Optional[ChapterLogger] = None):
        """
        Inicializa el analizador de tareas.
        
        Args:
            logger: Logger para registrar actividades
        """
        self.logger = logger
        self.analysis_cache = {}
        
    def analyze_task(self, description: str) -> List[Task]:
        """
        Analiza una descripción de tarea y genera un plan detallado.
        
        Args:
            description: Descripción en lenguaje natural de la tarea
            
        Returns:
            Lista de tareas organizadas y priorizadas
        """
        self._log("🔍 Analizando requisitos del usuario...")
        
        # Verificar cache
        if description in self.analysis_cache:
            self._log("📋 Usando plan cacheado")
            return self.analysis_cache[description]
        
        # Crear prompt para análisis
        analysis_prompt = self._build_analysis_prompt(description)
        
        # Ejecutar análisis con Claude
        success, analysis_result, error = self._execute_claude_analysis(analysis_prompt)
        
        if not success:
            self._log(f"❌ Error en análisis: {error}")
            # Fallback a análisis básico
            return self._basic_analysis(description)
        
        # Parsear resultado y crear tareas
        tasks = self._parse_analysis_result(analysis_result, description)
        
        # Cachear resultado
        self.analysis_cache[description] = tasks
        
        return tasks
    
    def _build_analysis_prompt(self, description: str) -> str:
        """Construye el prompt para análisis de tareas."""
        return f"""Analiza la siguiente solicitud y descompónla en tareas específicas para el equipo Batman Incorporated.

**Solicitud del usuario**: {description}

Necesito que:
1. Identifiques el objetivo principal
2. Descompongas en subtareas específicas y atómicas
3. Asignes cada tarea al agente más apropiado:
   - Alfred: Backend, APIs, arquitectura, bases de datos
   - Batgirl: Frontend, UI/UX, componentes visuales
   - Robin: DevOps, automatización, scripts, CI/CD
   - Oracle: Testing, QA, seguridad, validación
   - Lucius: Investigación, optimización, nuevas tecnologías

Responde en formato JSON con la siguiente estructura:
{{
  "main_goal": "descripción del objetivo principal",
  "estimated_complexity": "low|medium|high",
  "tasks": [
    {{
      "title": "título corto de la tarea",
      "description": "descripción detallada",
      "type": "development|testing|infrastructure|documentation|research",
      "priority": 1-5,
      "assigned_to": "alfred|batgirl|robin|oracle|lucius",
      "estimated_hours": 0.5-8,
      "dependencies": [],
      "tags": ["tag1", "tag2"]
    }}
  ],
  "execution_mode": "seguro|rapido|redundante",
  "notes": "observaciones adicionales"
}}

Asegúrate de:
- Crear tareas específicas y ejecutables
- Establecer dependencias lógicas entre tareas
- Asignar prioridades basadas en importancia y orden de ejecución
- Estimar tiempos realistas
- Elegir el modo de ejecución apropiado según la complejidad"""
    
    def _execute_claude_analysis(self, prompt: str) -> Tuple[bool, str, str]:
        """Ejecuta el análisis usando Claude CLI."""
        self._log("🤖 Consultando con Claude para análisis inteligente...")
        
        try:
            # Preparar comando
            cmd = [
                'claude',
                '--print',
                '--dangerously-skip-permissions',
                '--max-turns', '1',  # Solo necesitamos una respuesta
                prompt
            ]
            
            # Ejecutar
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30  # 30 segundos para análisis
            )
            
            if result.returncode == 0:
                # Extraer JSON de la respuesta
                json_match = re.search(r'\{[\s\S]*\}', result.stdout)
                if json_match:
                    return True, json_match.group(0), ""
                else:
                    return False, "", "No se encontró JSON válido en la respuesta"
            else:
                return False, "", result.stderr
                
        except subprocess.TimeoutExpired:
            return False, "", "Timeout en análisis"
        except Exception as e:
            return False, "", f"Error: {str(e)}"
    
    def _parse_analysis_result(self, analysis_json: str, original_description: str) -> List[Task]:
        """Parsea el resultado del análisis y crea objetos Task."""
        tasks = []
        
        try:
            analysis = json.loads(analysis_json)
            
            self._log(f"📊 Análisis completado: {analysis.get('main_goal', 'N/A')}")
            self._log(f"📈 Complejidad estimada: {analysis.get('estimated_complexity', 'N/A')}")
            
            # Crear tarea principal
            main_task = Task(
                title=analysis.get('main_goal', original_description)[:100],
                description=original_description,
                type=TaskType.DEVELOPMENT,
                priority=TaskPriority.HIGH,
                estimated_hours=sum(t.get('estimated_hours', 1) for t in analysis.get('tasks', []))
            )
            tasks.append(main_task)
            
            # Crear subtareas
            task_map = {0: main_task.id}  # Mapeo de índices a IDs
            
            for idx, task_data in enumerate(analysis.get('tasks', []), 1):
                # Determinar tipo
                type_str = task_data.get('type', 'development')
                task_type = {
                    'development': TaskType.DEVELOPMENT,
                    'testing': TaskType.TESTING,
                    'infrastructure': TaskType.INFRASTRUCTURE,
                    'documentation': TaskType.DOCUMENTATION,
                    'research': TaskType.RESEARCH
                }.get(type_str, TaskType.DEVELOPMENT)
                
                # Determinar prioridad
                priority_val = task_data.get('priority', 3)
                if priority_val <= 2:
                    priority = TaskPriority.LOW
                elif priority_val <= 3:
                    priority = TaskPriority.MEDIUM
                elif priority_val <= 4:
                    priority = TaskPriority.HIGH
                else:
                    priority = TaskPriority.CRITICAL
                
                # Resolver dependencias
                dependencies = []
                for dep in task_data.get('dependencies', []):
                    if isinstance(dep, int) and dep in task_map:
                        dependencies.append(task_map[dep])
                    else:
                        dependencies.append(main_task.id)
                
                # Crear tarea
                task = Task(
                    title=task_data.get('title', f'Subtarea {idx}'),
                    description=task_data.get('description', ''),
                    type=task_type,
                    priority=priority,
                    assigned_to=task_data.get('assigned_to'),
                    depends_on=dependencies,
                    estimated_hours=task_data.get('estimated_hours', 1.0),
                    tags=task_data.get('tags', [])
                )
                
                tasks.append(task)
                task_map[idx] = task.id
            
            self._log(f"✅ Plan generado: {len(tasks)} tareas")
            
        except json.JSONDecodeError as e:
            self._log(f"⚠️ Error parseando JSON: {e}")
            # Fallback a análisis básico
            return self._basic_analysis(original_description)
        except Exception as e:
            self._log(f"⚠️ Error procesando análisis: {e}")
            return self._basic_analysis(original_description)
        
        return tasks
    
    def _basic_analysis(self, description: str) -> List[Task]:
        """
        Análisis básico cuando falla el análisis con Claude.
        Crea un conjunto estándar de tareas basado en patrones comunes.
        """
        self._log("📋 Usando análisis básico (fallback)")
        
        tasks = []
        
        # Tarea principal
        main_task = Task(
            title=f"Implementar: {description[:80]}",
            description=description,
            type=TaskType.DEVELOPMENT,
            priority=TaskPriority.HIGH,
            estimated_hours=4.0
        )
        tasks.append(main_task)
        
        # Detectar tipo de proyecto
        desc_lower = description.lower()
        
        # Patrones comunes
        if any(word in desc_lower for word in ['api', 'backend', 'servidor', 'server']):
            # Proyecto backend
            subtasks = [
                ("Diseñar estructura de API", TaskType.DEVELOPMENT, "alfred", 1.0),
                ("Implementar endpoints", TaskType.DEVELOPMENT, "alfred", 2.0),
                ("Configurar base de datos", TaskType.INFRASTRUCTURE, "robin", 1.0),
                ("Escribir tests de API", TaskType.TESTING, "oracle", 1.5),
                ("Documentar endpoints", TaskType.DOCUMENTATION, "lucius", 0.5)
            ]
        elif any(word in desc_lower for word in ['frontend', 'ui', 'interfaz', 'web']):
            # Proyecto frontend
            subtasks = [
                ("Diseñar interfaz de usuario", TaskType.DEVELOPMENT, "batgirl", 1.0),
                ("Implementar componentes", TaskType.DEVELOPMENT, "batgirl", 2.0),
                ("Configurar build pipeline", TaskType.INFRASTRUCTURE, "robin", 0.5),
                ("Escribir tests de UI", TaskType.TESTING, "oracle", 1.0),
                ("Optimizar rendimiento", TaskType.RESEARCH, "lucius", 1.0)
            ]
        elif any(word in desc_lower for word in ['full', 'completa', 'aplicación', 'app']):
            # Aplicación completa
            subtasks = [
                ("Diseñar arquitectura", TaskType.DEVELOPMENT, "alfred", 1.0),
                ("Implementar backend", TaskType.DEVELOPMENT, "alfred", 2.0),
                ("Crear interfaz de usuario", TaskType.DEVELOPMENT, "batgirl", 2.0),
                ("Configurar infraestructura", TaskType.INFRASTRUCTURE, "robin", 1.0),
                ("Implementar tests", TaskType.TESTING, "oracle", 1.5),
                ("Investigar optimizaciones", TaskType.RESEARCH, "lucius", 0.5)
            ]
        else:
            # Genérico
            subtasks = [
                ("Analizar requisitos", TaskType.RESEARCH, "lucius", 0.5),
                ("Implementar funcionalidad", TaskType.DEVELOPMENT, "alfred", 2.0),
                ("Crear interfaz", TaskType.DEVELOPMENT, "batgirl", 1.0),
                ("Configurar entorno", TaskType.INFRASTRUCTURE, "robin", 0.5),
                ("Validar implementación", TaskType.TESTING, "oracle", 1.0)
            ]
        
        # Crear subtareas
        for title, task_type, agent, hours in subtasks:
            task = Task(
                title=title,
                type=task_type,
                priority=TaskPriority.MEDIUM,
                assigned_to=agent,
                depends_on=[main_task.id],
                estimated_hours=hours
            )
            tasks.append(task)
        
        return tasks
    
    def _log(self, message: str):
        """Helper para logging."""
        if self.logger:
            self.logger.log(f"[ANALYZER] {message}")
        else:
            print(f"[ANALYZER] {message}")