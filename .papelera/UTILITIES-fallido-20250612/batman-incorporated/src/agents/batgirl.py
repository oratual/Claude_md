"""
Batgirl - Frontend Specialist Agent
La experta en UI/UX y desarrollo frontend.
"""

from typing import List
from .base import BaseAgent


class BatgirlAgent(BaseAgent):
    """
    Batgirl - La especialista en frontend.
    Experta en UI/UX, componentes modernos y accesibilidad.
    """
    
    def __init__(self, logger=None):
        super().__init__(
            name="batgirl",
            role="Frontend Specialist",
            logger=logger
        )
    
    def get_system_prompt(self) -> str:
        """Prompt que define la personalidad de Batgirl."""
        return """Eres Batgirl, la especialista en frontend y diseño del equipo.

Tu personalidad:
- Creativa y orientada al usuario
- Perfeccionista con los detalles visuales
- Apasionada por la accesibilidad
- Siempre al día con las últimas tendencias
- Equilibras estética con funcionalidad

Tus especialidades técnicas:
- React, Vue, Angular y frameworks modernos
- CSS avanzado y animaciones
- Diseño responsive y mobile-first
- Accesibilidad (WCAG compliance)
- Component libraries y design systems
- State management (Redux, Zustand, etc.)
- Performance optimization frontend
- Testing de componentes
- UX/UI best practices

Tu forma de trabajar:
- Piensas primero en la experiencia del usuario
- Creas componentes reutilizables y mantenibles
- Te aseguras de que todo sea accesible
- Optimizas para performance desde el inicio
- Documentas componentes con ejemplos visuales
- Usas herramientas modernas pero con criterio

Cuando respondas, hazlo como Batgirl: con pasión por el diseño pero fundamentada en buenas prácticas técnicas."""
    
    def get_specialties(self) -> List[str]:
        """Especialidades técnicas de Batgirl."""
        return [
            "frontend",
            "ui",
            "ux",
            "react",
            "vue",
            "css",
            "responsive",
            "accessibility",
            "components",
            "design-system"
        ]
    
    def should_handle_task(self, task_description: str) -> bool:
        """
        Determina si Batgirl debería manejar esta tarea.
        
        Args:
            task_description: Descripción de la tarea
            
        Returns:
            True si la tarea es apropiada para Batgirl
        """
        batgirl_keywords = [
            "frontend", "ui", "ux", "react", "vue", "angular", "css",
            "component", "interface", "design", "responsive", "mobile",
            "accessibility", "styling", "animation", "layout", "visual"
        ]
        
        description_lower = task_description.lower()
        return any(keyword in description_lower for keyword in batgirl_keywords)