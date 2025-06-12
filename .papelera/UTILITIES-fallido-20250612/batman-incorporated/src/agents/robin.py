"""
Robin - DevOps & Junior Developer Agent
El compañero entusiasta, experto en automatización e infraestructura.
"""

from typing import List
from .base import BaseAgent


class RobinAgent(BaseAgent):
    """
    Robin - El asistente DevOps y desarrollador junior.
    Experto en automatización, CI/CD, y tareas de infraestructura.
    """
    
    def __init__(self, logger=None):
        super().__init__(
            name="robin",
            role="DevOps & Junior Developer",
            logger=logger
        )
    
    def get_system_prompt(self) -> str:
        """Prompt que define la personalidad de Robin."""
        return """Eres Robin, el compañero joven y entusiasta de Batman.

Tu personalidad:
- Energético y optimista
- Siempre dispuesto a ayudar
- Aprendes rápido y haces muchas preguntas
- Te encanta automatizar tareas repetitivas
- Eres práctico y orientado a resultados

Tus especialidades técnicas:
- DevOps y automatización
- Docker y Kubernetes
- CI/CD (GitHub Actions, Jenkins)
- Scripts en Bash y Python
- Configuración de servidores
- Monitoreo y logging
- Herramientas de línea de comandos
- Desarrollo de features simples

Tu forma de trabajar:
- Buscas automatizar todo lo posible
- Escribes scripts claros y bien comentados
- Te aseguras de que todo esté bien documentado
- Pruebas todo en ambiente local primero
- Siempre piensas en la experiencia del desarrollador

Cuando respondas, hazlo como Robin: con entusiasmo juvenil pero competencia técnica."""
    
    def get_specialties(self) -> List[str]:
        """Especialidades técnicas de Robin."""
        return [
            "devops",
            "docker",
            "kubernetes",
            "ci-cd",
            "automation",
            "bash",
            "scripting",
            "infrastructure",
            "monitoring",
            "deployment",
            "configuration"
        ]
    
    def should_handle_task(self, task_description: str) -> bool:
        """
        Determina si Robin debería manejar esta tarea.
        
        Args:
            task_description: Descripción de la tarea
            
        Returns:
            True si la tarea es apropiada para Robin
        """
        robin_keywords = [
            "docker", "ci/cd", "deploy", "automation", "script", "bash",
            "infrastructure", "pipeline", "build", "test", "devops",
            "setup", "install", "configure", "environment", "monitoring"
        ]
        
        description_lower = task_description.lower()
        return any(keyword in description_lower for keyword in robin_keywords)