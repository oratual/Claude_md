#!/usr/bin/env python3
"""
ChapterLogger - Sistema de logging narrativo por capítulos para GLADOS
Proporciona logs estructurados y legibles que narran el progreso del trabajo automático
"""

import os
import sys
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
from enum import Enum
from pathlib import Path
import threading
import time


class LogLevel(Enum):
    """Niveles de logging con iconos"""
    INFO = ("ℹ️", "info")
    SUCCESS = ("✅", "success") 
    WARNING = ("⚠️", "warning")
    ERROR = ("❌", "error")
    DEBUG = ("🐛", "debug")
    PROGRESS = ("→", "progress")
    DISCOVERY = ("💡", "discovery")
    ACTION = ("🔧", "action")
    TEST = ("🧪", "test")
    ANALYSIS = ("🔍", "analysis")


class ChapterLogger:
    """Sistema de logging narrativo por capítulos"""
    
    def __init__(self, session_name: str = "GLADOS Auto Session", 
                 log_dir: str = "~/.glados/logs"):
        self.session_name = session_name
        self.log_dir = Path(log_dir).expanduser()
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Estado del capítulo
        self.current_chapter = 0
        self.chapter_start = None
        self.chapter_logs = []
        self.chapter_stats = {}
        
        # Sesión
        self.session_start = datetime.now()
        self.session_id = self.session_start.strftime("%Y%m%d_%H%M%S")
        self.session_logs = []
        self.chapters_completed = []
        
        # Archivos de log
        self.log_file = self.log_dir / f"session_{self.session_id}.log"
        self.json_file = self.log_dir / f"session_{self.session_id}.json"
        self.current_log_file = self.log_dir / "current.log"
        
        # UI callback para actualización en tiempo real
        self.ui_callback = None
        
        # Iniciar sesión
        self._init_session()
        
    def _init_session(self):
        """Inicializa una nueva sesión de logging"""
        header = f"""
╔════════════════════════════════════════════════════════════════╗
║                    {self.session_name:^40}                     ║
║                    Sesión: {self.session_id}                   ║
║                    Inicio: {self.session_start.strftime("%Y-%m-%d %H:%M:%S")}              ║
╚════════════════════════════════════════════════════════════════╝
"""
        self._write_log(header)
        
    def start_chapter(self, title: str, objective: str, tasks: List[str] = None):
        """Inicia un nuevo capítulo en el log"""
        # Cerrar capítulo anterior si existe
        if self.current_chapter > 0:
            self.end_chapter("Capítulo completado automáticamente")
            
        self.current_chapter += 1
        self.chapter_start = datetime.now()
        self.chapter_logs = []
        self.chapter_stats = {
            'title': title,
            'objective': objective,
            'tasks': tasks or [],
            'completed_tasks': [],
            'warnings': 0,
            'errors': 0,
            'discoveries': 0
        }
        
        # Log del capítulo
        chapter_header = f"\n📖 CAPÍTULO {self.current_chapter}: {title.upper()}"
        separator = "━" * 60
        
        self.log(chapter_header, direct=True)
        self.log(separator, direct=True)
        self.log(f"🎯 Objetivo: {objective}", level=LogLevel.INFO)
        
        if tasks:
            self.log("📋 Tareas planificadas:", level=LogLevel.INFO)
            for i, task in enumerate(tasks, 1):
                self.log(f"  {i}. {task}", level=LogLevel.INFO)
        
        self.log("")  # Línea en blanco
        
    def log(self, message: str, level: LogLevel = LogLevel.PROGRESS, 
            indent: int = 0, direct: bool = False):
        """Registra un mensaje con el nivel y formato apropiado"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Formato según si es directo o con nivel
        if direct:
            formatted = f"[{timestamp}] {message}"
        else:
            icon = level.value[0]
            indent_str = "  " * indent
            formatted = f"[{timestamp}] {icon} {indent_str}{message}"
        
        # Actualizar estadísticas
        if level == LogLevel.WARNING:
            self.chapter_stats['warnings'] += 1
        elif level == LogLevel.ERROR:
            self.chapter_stats['errors'] += 1
        elif level == LogLevel.DISCOVERY:
            self.chapter_stats['discoveries'] += 1
            
        # Guardar en memoria
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'chapter': self.current_chapter,
            'level': level.value[1] if not direct else 'direct',
            'message': message,
            'formatted': formatted
        }
        
        self.chapter_logs.append(log_entry)
        self.session_logs.append(log_entry)
        
        # Escribir a archivo y consola
        self._write_log(formatted)
        print(formatted)
        
        # Callback para UI
        if self.ui_callback:
            self.ui_callback(log_entry)
            
    def log_task_start(self, task_name: str):
        """Registra el inicio de una tarea"""
        self.log(f"📝 Iniciando: {task_name}", level=LogLevel.INFO)
        
    def log_task_complete(self, task_name: str, summary: str = None):
        """Registra la finalización de una tarea"""
        self.chapter_stats['completed_tasks'].append(task_name)
        msg = f"Completado: {task_name}"
        if summary:
            msg += f" - {summary}"
        self.log(msg, level=LogLevel.SUCCESS)
        
    def log_progress(self, message: str, percentage: Optional[int] = None):
        """Registra progreso con barra opcional"""
        if percentage is not None:
            bar_length = 20
            filled = int(bar_length * percentage / 100)
            bar = "▓" * filled + "░" * (bar_length - filled)
            self.log(f"{message} [{bar}] {percentage}%", level=LogLevel.PROGRESS)
        else:
            self.log(message, level=LogLevel.PROGRESS)
            
    def log_discovery(self, title: str, description: str, severity: str = "info"):
        """Registra un descubrimiento o hallazgo importante"""
        self.log(f"Descubrimiento: {title}", level=LogLevel.DISCOVERY)
        self.log(f"└─ {description}", level=LogLevel.INFO, indent=1)
        if severity in ["warning", "error"]:
            self.log(f"└─ Severidad: {severity}", level=LogLevel.WARNING, indent=1)
            
    def log_subtask(self, message: str, parent_indent: int = 0):
        """Registra una subtarea con indentación"""
        self.log(f"├─ {message}", level=LogLevel.PROGRESS, indent=parent_indent + 1)
        
    def log_subtask_complete(self, message: str, parent_indent: int = 0):
        """Registra completación de subtarea"""
        self.log(f"└─ ✓ {message}", level=LogLevel.SUCCESS, indent=parent_indent + 1)
        
    def end_chapter(self, summary: str):
        """Cierra el capítulo actual con un resumen"""
        if not self.chapter_start:
            return
            
        duration = datetime.now() - self.chapter_start
        minutes = int(duration.total_seconds() / 60)
        seconds = int(duration.total_seconds() % 60)
        
        self.log("")  # Línea en blanco
        self.log(f"📊 Resumen del Capítulo {self.current_chapter}:", level=LogLevel.INFO)
        self.log(f"├─ Duración: {minutes}min {seconds}s", level=LogLevel.INFO)
        self.log(f"├─ Tareas completadas: {len(self.chapter_stats['completed_tasks'])}/{len(self.chapter_stats['tasks'])}", level=LogLevel.INFO)
        
        if self.chapter_stats['discoveries'] > 0:
            self.log(f"├─ Descubrimientos: {self.chapter_stats['discoveries']}", level=LogLevel.DISCOVERY)
        if self.chapter_stats['warnings'] > 0:
            self.log(f"├─ Advertencias: {self.chapter_stats['warnings']}", level=LogLevel.WARNING)
        if self.chapter_stats['errors'] > 0:
            self.log(f"├─ Errores: {self.chapter_stats['errors']}", level=LogLevel.ERROR)
            
        self.log(f"└─ {summary}", level=LogLevel.SUCCESS)
        self.log("─" * 60 + "\n", direct=True)
        
        # Guardar capítulo completado
        self.chapters_completed.append({
            'number': self.current_chapter,
            'title': self.chapter_stats['title'],
            'duration': str(duration),
            'stats': self.chapter_stats.copy(),
            'logs': self.chapter_logs.copy()
        })
        
        # Guardar estado JSON
        self._save_json_state()
        
    def get_chapter_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen del capítulo actual"""
        return {
            'number': self.current_chapter,
            'title': self.chapter_stats.get('title', ''),
            'completed_tasks': len(self.chapter_stats.get('completed_tasks', [])),
            'total_tasks': len(self.chapter_stats.get('tasks', [])),
            'warnings': self.chapter_stats.get('warnings', 0),
            'errors': self.chapter_stats.get('errors', 0),
            'discoveries': self.chapter_stats.get('discoveries', 0)
        }
        
    def get_session_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen de toda la sesión"""
        total_duration = datetime.now() - self.session_start
        
        return {
            'session_id': self.session_id,
            'duration': str(total_duration),
            'chapters_completed': len(self.chapters_completed),
            'total_tasks': sum(len(ch['stats']['completed_tasks']) for ch in self.chapters_completed),
            'total_warnings': sum(ch['stats']['warnings'] for ch in self.chapters_completed),
            'total_errors': sum(ch['stats']['errors'] for ch in self.chapters_completed),
            'total_discoveries': sum(ch['stats']['discoveries'] for ch in self.chapters_completed)
        }
        
    def _write_log(self, message: str):
        """Escribe a los archivos de log"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(message + '\n')
            
        # También escribir al log actual para tail -f
        with open(self.current_log_file, 'w', encoding='utf-8') as f:
            # Escribir últimas 100 líneas
            recent_logs = self.session_logs[-100:]
            for log in recent_logs:
                f.write(log['formatted'] + '\n')
                
    def _save_json_state(self):
        """Guarda el estado completo en formato JSON"""
        state = {
            'session': {
                'id': self.session_id,
                'name': self.session_name,
                'start': self.session_start.isoformat(),
                'current_time': datetime.now().isoformat()
            },
            'current_chapter': self.current_chapter,
            'chapters_completed': self.chapters_completed,
            'summary': self.get_session_summary()
        }
        
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
            
    def set_ui_callback(self, callback):
        """Establece un callback para actualizar la UI en tiempo real"""
        self.ui_callback = callback


# Ejemplo de uso
if __name__ == "__main__":
    logger = ChapterLogger("Test Session")
    
    # Capítulo 1
    logger.start_chapter(
        "Inicialización del Sistema",
        "Preparar el entorno y cargar configuraciones",
        ["Cargar configuración", "Verificar dependencias", "Conectar servicios"]
    )
    
    logger.log_task_start("Cargar configuración")
    logger.log_subtask("Leyendo config.yaml")
    logger.log_subtask_complete("Configuración cargada correctamente")
    logger.log_task_complete("Cargar configuración", "3 archivos procesados")
    
    logger.log_discovery(
        "Configuración desactualizada",
        "El archivo config.yaml usa formato antiguo",
        "warning"
    )
    
    logger.log_progress("Verificando dependencias", 75)
    
    logger.end_chapter("Inicialización completada con 1 advertencia")
    
    # Resumen
    print(json.dumps(logger.get_session_summary(), indent=2))