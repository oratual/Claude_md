"""
Sistema de módulos temáticos para Batman Incorporated.
Permite cargar dinámicamente herramientas especializadas según el tipo de tarea.
"""

from .base_module import BaseModule
from .module_loader import ModuleLoader

__all__ = ['BaseModule', 'ModuleLoader']