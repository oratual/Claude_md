"""
Oracle - QA & Security Lead Agent
La experta en información, testing y seguridad.
"""

from typing import List
from .base import BaseAgent


class OracleAgent(BaseAgent):
    """
    Oracle (Barbara Gordon) - La experta en QA y seguridad.
    Especialista en testing, análisis de vulnerabilidades y calidad.
    """
    
    def __init__(self, logger=None):
        super().__init__(
            name="oracle",
            role="QA & Security Lead",
            logger=logger
        )
    
    def get_system_prompt(self) -> str:
        """Prompt que define la personalidad de Oracle."""
        return """Eres Oracle (Barbara Gordon), la experta en información y seguridad del equipo.

Tu personalidad:
- Analítica y detallista
- No dejas pasar ningún error
- Siempre piensas en casos edge
- Te obsesiona la seguridad
- Eres metódica y sistemática

Tus especialidades técnicas:
- Testing (unit, integration, E2E)
- Seguridad y análisis de vulnerabilidades
- Performance testing y optimización
- Code quality y linting
- Debugging y troubleshooting
- Monitoreo y observabilidad
- Documentación técnica
- Análisis de datos y métricas

Tu forma de trabajar:
- Escribes tests exhaustivos que cubren todos los casos
- Siempre verificas inputs y validas datos
- Buscas vulnerabilidades potenciales
- Documentas todos los hallazgos
- Usas herramientas automatizadas cuando es posible
- Priorizas basándote en impacto y probabilidad

Cuando respondas, hazlo como Oracle: precisa, analítica y sin dejar ningún detalle sin revisar."""
    
    def get_specialties(self) -> List[str]:
        """Especialidades técnicas de Oracle."""
        return [
            "testing",
            "qa",
            "security",
            "performance",
            "debugging",
            "monitoring",
            "documentation",
            "code-quality",
            "vulnerability",
            "metrics"
        ]
    
    def should_handle_task(self, task_description: str) -> bool:
        """
        Determina si Oracle debería manejar esta tarea.
        
        Args:
            task_description: Descripción de la tarea
            
        Returns:
            True si la tarea es apropiada para Oracle
        """
        oracle_keywords = [
            "test", "testing", "qa", "security", "vulnerability", "debug",
            "performance", "monitor", "analyze", "quality", "bug",
            "error", "exception", "validation", "audit", "review"
        ]
        
        description_lower = task_description.lower()
        return any(keyword in description_lower for keyword in oracle_keywords)