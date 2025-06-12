"""
Lucius Fox - Research & Innovation Agent
El genio inventor, experto en nuevas tecnologías y optimización.
"""

from typing import List
from .base import BaseAgent


class LuciusAgent(BaseAgent):
    """
    Lucius Fox - El investigador e innovador.
    Experto en nuevas tecnologías, optimización y soluciones creativas.
    """
    
    def __init__(self, logger=None):
        super().__init__(
            name="lucius",
            role="Research & Innovation",
            logger=logger
        )
    
    def get_system_prompt(self) -> str:
        """Prompt que define la personalidad de Lucius."""
        return """Eres Lucius Fox, el genio tecnológico e innovador de Wayne Enterprises.

Tu personalidad:
- Brillante y visionario
- Siempre buscas la solución más elegante
- Te encanta experimentar con nuevas tecnologías
- Eres pragmático a pesar de tu creatividad
- Explicas conceptos complejos de forma simple

Tus especialidades técnicas:
- Investigación de nuevas tecnologías
- Optimización de algoritmos
- Machine Learning y AI
- Arquitecturas innovadoras
- Proof of concepts
- Performance optimization
- Documentación técnica avanzada
- Análisis de viabilidad técnica
- Integración de tecnologías emergentes

Tu forma de trabajar:
- Investigas exhaustivamente antes de proponer
- Creas prototipos para validar ideas
- Documentas tus hallazgos meticulosamente
- Consideras pros y contras de cada tecnología
- Piensas en el futuro y la escalabilidad
- Balanceas innovación con practicidad

Cuando respondas, hazlo como Lucius: con sabiduría técnica profunda pero comunicación clara y accesible."""
    
    def get_specialties(self) -> List[str]:
        """Especialidades técnicas de Lucius."""
        return [
            "research",
            "innovation",
            "optimization",
            "prototyping",
            "ai-ml",
            "performance",
            "documentation",
            "architecture",
            "emerging-tech",
            "proof-of-concept"
        ]
    
    def should_handle_task(self, task_description: str) -> bool:
        """
        Determina si Lucius debería manejar esta tarea.
        
        Args:
            task_description: Descripción de la tarea
            
        Returns:
            True si la tarea es apropiada para Lucius
        """
        lucius_keywords = [
            "research", "innovation", "optimization", "prototype", "ai",
            "ml", "machine learning", "algorithm", "performance",
            "documentation", "analysis", "emerging", "experiment",
            "poc", "proof of concept", "architecture", "design"
        ]
        
        description_lower = task_description.lower()
        return any(keyword in description_lower for keyword in lucius_keywords)