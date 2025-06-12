"""
Redundant Mode - Múltiples implementaciones para elegir la mejor.
Ideal para features críticas donde necesitamos la mejor solución.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import tempfile
import shutil

from .base import ExecutionMode
from core.task import Task


class RedundantMode(ExecutionMode):
    """
    Modo Redundante: Genera múltiples implementaciones de la misma tarea.
    Permite comparar y elegir la mejor solución.
    Ideal para features críticas como autenticación o pagos.
    """
    
    def __init__(self, config: Dict[str, Any], logger=None):
        super().__init__("Redundant Mode", config, logger)
        self.implementations: Dict[str, List[Path]] = {}
        self.results_dir = Path(self.config.get('results_dir', '/tmp/batman-redundant'))
        self.min_implementations = self.config.get('min_implementations', 2)
        self.max_implementations = self.config.get('max_implementations', 5)
        
    def prepare(self, tasks: List[Task]) -> bool:
        """Prepara directorios para múltiples implementaciones."""
        self._log("🎯 Preparando modo REDUNDANTE")
        
        # Crear directorio para resultados
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Preparar estructura para cada tarea
        for task in tasks:
            task_dir = self.results_dir / f"task_{task.id}"
            task_dir.mkdir(exist_ok=True)
            self.implementations[task.id] = []
            
        self._log(f"  📁 Directorio de resultados: {self.results_dir}")
        self._log(f"  🔢 Implementaciones por tarea: {self.min_implementations}-{self.max_implementations}")
        
        return True
    
    def execute(self, task: Task, agent: Any) -> bool:
        """Ejecuta múltiples versiones de la misma tarea."""
        self._log(f"🎯 Generando múltiples implementaciones para: {task.title}")
        
        # Determinar número de implementaciones basado en prioridad
        num_implementations = self._determine_implementations(task)
        
        successes = 0
        task_dir = self.results_dir / f"task_{task.id}"
        
        for i in range(num_implementations):
            self._log(f"  🔄 Implementación {i+1}/{num_implementations}")
            
            # Crear directorio para esta implementación
            impl_dir = task_dir / f"implementation_{i+1}"
            impl_dir.mkdir(exist_ok=True)
            
            # Copiar archivos base si es necesario
            if i == 0 and self.config.get('copy_base_files', True):
                self._copy_base_files(impl_dir)
            
            # Modificar prompt para generar variación
            varied_task = self._create_task_variation(task, i)
            
            # Cambiar directorio de trabajo temporalmente
            original_dir = agent.working_dir
            agent.working_dir = impl_dir
            
            try:
                # Ejecutar tarea
                success = agent.execute_task(varied_task)
                
                if success:
                    successes += 1
                    self.implementations[task.id].append(impl_dir)
                    self._log(f"    ✅ Implementación {i+1} completada")
                else:
                    self._log(f"    ❌ Implementación {i+1} falló")
                    
            finally:
                agent.working_dir = original_dir
        
        # Considerar exitoso si al menos una implementación funcionó
        success = successes > 0
        
        if success:
            self._log(f"  📊 Completadas {successes}/{num_implementations} implementaciones")
            self._log(f"  📁 Revisar resultados en: {task_dir}")
        
        return success
    
    def _determine_implementations(self, task: Task) -> int:
        """Determina número de implementaciones basado en la tarea."""
        # Más implementaciones para tareas críticas
        if task.priority.value >= 4:  # HIGH o CRITICAL
            return self.max_implementations
        elif task.priority.value >= 3:  # MEDIUM
            return (self.min_implementations + self.max_implementations) // 2
        else:
            return self.min_implementations
    
    def _create_task_variation(self, task: Task, variation_index: int) -> Task:
        """Crea una variación de la tarea para generar diferentes enfoques."""
        import copy
        
        varied = copy.deepcopy(task)
        
        # Añadir instrucciones de variación al descripción
        variations = [
            "Implementa esto priorizando simplicidad y claridad",
            "Implementa esto priorizando rendimiento y eficiencia",
            "Implementa esto priorizando seguridad y validación exhaustiva",
            "Implementa esto usando las mejores prácticas más modernas",
            "Implementa esto pensando en escalabilidad y mantenibilidad"
        ]
        
        if variation_index < len(variations):
            varied.description = f"{task.description}\n\nEnfoque: {variations[variation_index]}"
        
        return varied
    
    def _copy_base_files(self, dest_dir: Path):
        """Copia archivos base del proyecto al directorio de implementación."""
        # Lista de archivos/patrones comunes a copiar
        patterns = [
            "package.json",
            "requirements.txt",
            "tsconfig.json",
            ".gitignore",
            "README.md"
        ]
        
        for pattern in patterns:
            for file in self.working_dir.glob(pattern):
                if file.is_file():
                    shutil.copy2(file, dest_dir)
    
    def cleanup(self) -> bool:
        """Proceso de selección y merge de la mejor implementación."""
        self._log("🏆 Proceso de selección de implementación")
        
        for task_id, impl_dirs in self.implementations.items():
            if not impl_dirs:
                continue
                
            self._log(f"\n  📋 Tarea {task_id}:")
            self._log(f"  Implementaciones disponibles: {len(impl_dirs)}")
            
            # Análisis automático básico
            self._analyze_implementations(task_id, impl_dirs)
            
            # Por ahora, informar al usuario para selección manual
            self._log("\n  🤔 Revisa las implementaciones y elige la mejor:")
            for i, impl_dir in enumerate(impl_dirs, 1):
                self._log(f"    {i}. {impl_dir}")
            
            self._log("\n  📝 Para aplicar una implementación:")
            self._log(f"     cp -r {impl_dirs[0]}/* .")
        
        return True
    
    def _analyze_implementations(self, task_id: str, impl_dirs: List[Path]):
        """Analiza y compara implementaciones."""
        self._log("  📊 Análisis automático:")
        
        for i, impl_dir in enumerate(impl_dirs, 1):
            self._log(f"\n    Implementación {i}:")
            
            # Contar archivos
            files = list(impl_dir.rglob("*"))
            file_count = sum(1 for f in files if f.is_file())
            self._log(f"      Archivos: {file_count}")
            
            # Tamaño total
            total_size = sum(f.stat().st_size for f in files if f.is_file())
            self._log(f"      Tamaño: {total_size / 1024:.1f} KB")
            
            # Buscar tests
            test_files = [f for f in files if 'test' in f.name.lower()]
            self._log(f"      Tests: {len(test_files)}")
    
    def can_parallelize(self) -> bool:
        """Redundant mode puede paralelizar las implementaciones."""
        return True
    
    def max_parallel_tasks(self) -> int:
        """Limitado por configuración."""
        return self.config.get('max_parallel', 3)