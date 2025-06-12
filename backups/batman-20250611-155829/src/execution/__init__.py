"""
Modos de ejecución para Batman Incorporated.
"""

from .base import ExecutionMode
from .safe_mode import SafeMode
from .fast_mode import FastMode
from .redundant_mode import RedundantMode
from .infinity_mode import InfinityMode

__all__ = ['ExecutionMode', 'SafeMode', 'FastMode', 'RedundantMode', 'InfinityMode']