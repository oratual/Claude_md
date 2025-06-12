"""
Alfred - Senior Developer Agent
El mayordomo confiable de Batman, experto en desarrollo backend y arquitectura.
"""

from typing import List
from .base import BaseAgent


class AlfredAgent(BaseAgent):
    """
    Alfred Pennyworth - El desarrollador senior del equipo.
    Experto en arquitectura, APIs, y código limpio.
    """
    
    def __init__(self, logger=None):
        super().__init__(
            name="alfred",
            role="Senior Developer",
            logger=logger
        )
    
    def get_system_prompt(self) -> str:
        """Prompt que define la personalidad de Alfred."""
        return """Eres Alfred Pennyworth, el mayordomo y consejero técnico de Batman.

Tu personalidad:
- Extremadamente profesional y cortés
- Meticuloso con los detalles
- Siempre piensas en la arquitectura a largo plazo
- Prefieres soluciones elegantes sobre hacks rápidos
- Hablas con respeto pero con autoridad técnica

Tus especialidades técnicas:
- Arquitectura de software y patrones de diseño
- Desarrollo backend (Node.js, Python, Go)
- APIs REST y GraphQL
- Bases de datos (SQL y NoSQL)
- Microservicios y arquitectura distribuida
- Seguridad y mejores prácticas
- Code review y refactoring

Tu forma de trabajar:
- Siempre empiezas entendiendo el contexto completo
- Escribes código limpio, bien documentado y testeable
- Prefieres usar patrones establecidos antes que reinventar
- Te aseguras de que el código sea mantenible
- Consideras rendimiento y escalabilidad desde el inicio

Cuando respondas, hazlo como Alfred: con clase, precisión y un toque de sofisticación británica."""
    
    def get_specialties(self) -> List[str]:
        """Especialidades técnicas de Alfred."""
        return [
            "backend",
            "api",
            "architecture",
            "database",
            "security",
            "refactoring",
            "code-review",
            "microservices",
            "design-patterns",
            "performance"
        ]
    
    def should_handle_task(self, task_description: str) -> bool:
        """
        Determina si Alfred debería manejar esta tarea.
        
        Args:
            task_description: Descripción de la tarea
            
        Returns:
            True si la tarea es apropiada para Alfred
        """
        alfred_keywords = [
            "backend", "api", "database", "arquitectura", "architecture",
            "endpoint", "servidor", "server", "modelo", "model",
            "schema", "migration", "security", "auth", "refactor",
            "pattern", "service", "controller", "repository"
        ]
        
        description_lower = task_description.lower()
        return any(keyword in description_lower for keyword in alfred_keywords)