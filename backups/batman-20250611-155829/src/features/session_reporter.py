#!/usr/bin/env python3
"""
SessionReporter - Generador de informes de sesión para GLADOS
Crea informes detallados en Markdown de las sesiones automáticas
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class SessionReporter:
    """Genera informes detallados de las sesiones de GLADOS"""
    
    def __init__(self, logger, session_stats: Dict[str, Any]):
        self.logger = logger
        self.session_stats = session_stats
        self.report_dir = Path("~/.glados/reports").expanduser()
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_report(self) -> Path:
        """Genera el informe completo de la sesión"""
        session_summary = self.logger.get_session_summary()
        report_path = self.report_dir / f"session_{self.logger.session_id}.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            # Header
            f.write(self._generate_header(session_summary))
            
            # Resumen ejecutivo
            f.write(self._generate_executive_summary(session_summary))
            
            # Capítulos completados
            f.write(self._generate_chapters_section())
            
            # Descubrimientos y optimizaciones
            f.write(self._generate_discoveries_section())
            
            # Estado del proyecto
            f.write(self._generate_project_state())
            
            # Próximos pasos
            f.write(self._generate_next_steps())
            
            # Footer
            f.write(self._generate_footer())
            
        # También guardar versión JSON
        json_path = self.report_dir / f"session_{self.logger.session_id}.json"
        self._save_json_report(json_path, session_summary)
        
        # Crear enlace a último reporte
        latest_path = self.report_dir / "latest.md"
        if latest_path.exists():
            latest_path.unlink()
        latest_path.symlink_to(report_path.name)
        
        return report_path
        
    def _generate_header(self, summary: Dict) -> str:
        """Genera el encabezado del informe"""
        return f"""# 🤖 Informe de Sesión Automática - GLADOS

**ID de Sesión**: `{summary['session_id']}`  
**Fecha**: {datetime.now().strftime('%Y-%m-%d')}  
**Duración Total**: {summary['duration']}  
**Estado**: {'✅ Completado' if summary['total_errors'] == 0 else '⚠️ Completado con errores'}

---

"""
        
    def _generate_executive_summary(self, summary: Dict) -> str:
        """Genera el resumen ejecutivo"""
        tasks_ratio = f"{self.session_stats['tasks_completed']}/{self.session_stats['tasks_completed'] + self.session_stats['tasks_failed']}"
        
        # Manejar files_modified de forma segura
        files_modified_raw = self.session_stats.get('files_modified', [])
        files_count = 0
        if isinstance(files_modified_raw, set):
            files_count = len(files_modified_raw)
        elif isinstance(files_modified_raw, list):
            files_count = len(files_modified_raw)
        
        return f"""## 📊 Resumen Ejecutivo

### Métricas Clave
- **Tareas completadas**: {tasks_ratio} ({self._calculate_percentage(self.session_stats['tasks_completed'], self.session_stats['tasks_completed'] + self.session_stats['tasks_failed'])}%)
- **Capítulos procesados**: {summary['chapters_completed']}
- **Archivos modificados**: {files_count}
- **Tiempo ahorrado estimado**: {self.session_stats.get('time_saved', 0)} minutos
- **Descubrimientos**: {summary['total_discoveries']}
- **Advertencias**: {summary['total_warnings']}
- **Errores**: {summary['total_errors']}

### Logros Principales
"""
        
    def _generate_chapters_section(self) -> str:
        """Genera la sección de capítulos completados"""
        content = "\n## 📖 Capítulos Completados\n\n"
        
        for chapter in self.logger.chapters_completed:
            content += f"### Capítulo {chapter['number']}: {chapter['title']}\n"
            content += f"**Duración**: {chapter['duration']}  \n"
            content += f"**Objetivo**: {chapter['stats']['objective']}  \n\n"
            
            # Tareas completadas
            if chapter['stats']['completed_tasks']:
                content += "#### Tareas Completadas:\n"
                for task in chapter['stats']['completed_tasks']:
                    content += f"- ✅ {task}\n"
                content += "\n"
                
            # Estadísticas del capítulo
            stats = chapter['stats']
            if stats['discoveries'] > 0 or stats['warnings'] > 0 or stats['errors'] > 0:
                content += "#### Estadísticas:\n"
                if stats['discoveries'] > 0:
                    content += f"- 💡 Descubrimientos: {stats['discoveries']}\n"
                if stats['warnings'] > 0:
                    content += f"- ⚠️ Advertencias: {stats['warnings']}\n"
                if stats['errors'] > 0:
                    content += f"- ❌ Errores: {stats['errors']}\n"
                content += "\n"
                
            # Logs relevantes (primeros y últimos)
            if len(chapter['logs']) > 10:
                content += "<details>\n<summary>Ver logs del capítulo</summary>\n\n```\n"
                # Primeros 5 logs
                for log in chapter['logs'][:5]:
                    content += log['formatted'] + "\n"
                content += "...\n"
                # Últimos 5 logs
                for log in chapter['logs'][-5:]:
                    content += log['formatted'] + "\n"
                content += "```\n</details>\n\n"
                
        return content
        
    def _generate_discoveries_section(self) -> str:
        """Genera la sección de descubrimientos y optimizaciones"""
        content = "## 💡 Descubrimientos y Optimizaciones\n\n"
        
        # Descubrimientos
        discoveries = self.session_stats.get('discoveries', [])
        if discoveries:
            content += "### Descubrimientos\n"
            for i, discovery in enumerate(discoveries, 1):
                content += f"{i}. {discovery}\n"
            content += "\n"
            
        # Optimizaciones
        optimizations = self.session_stats.get('optimizations', [])
        if optimizations:
            content += "### Optimizaciones Aplicadas\n"
            for i, opt in enumerate(optimizations, 1):
                content += f"{i}. {opt}\n"
            content += "\n"
            
        # Archivos modificados (convertir set a lista de forma segura)
        files_raw = self.session_stats.get('files_modified', [])
        files = []
        if isinstance(files_raw, set):
            files = list(files_raw)
        elif isinstance(files_raw, list):
            files = files_raw
        
        if files:
            content += "### Archivos Modificados\n"
            for file in files[:10]:  # Máximo 10
                content += f"- `{file}`\n"
            if len(files) > 10:
                content += f"- ... y {len(files) - 10} archivos más\n"
            content += "\n"
            
        return content
        
    def _generate_project_state(self) -> str:
        """Genera la sección del estado del proyecto"""
        content = "## 📍 Estado del Proyecto\n\n"
        
        # Intentar obtener estado de Taskmaster
        try:
            import subprocess
            result = subprocess.run(['task-master', 'list', '--status=all'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                total_tasks = len([l for l in lines if l.strip()])
                
                # Contar por estado
                pending = len([l for l in lines if 'pending' in l.lower()])
                in_progress = len([l for l in lines if 'in-progress' in l.lower()])
                done = len([l for l in lines if 'done' in l.lower()])
                
                content += f"### Progreso de Tareas (Taskmaster)\n"
                content += f"- **Total**: {total_tasks} tareas\n"
                content += f"- **Completadas**: {done} ({self._calculate_percentage(done, total_tasks)}%)\n"
                content += f"- **En progreso**: {in_progress}\n"
                content += f"- **Pendientes**: {pending}\n\n"
                
                # Barra de progreso visual
                progress = self._calculate_percentage(done, total_tasks)
                bar = self._generate_progress_bar(progress)
                content += f"**Progreso Total**: {bar} {progress}%\n\n"
                
        except:
            content += "*No se pudo obtener el estado de Taskmaster*\n\n"
            
        return content
        
    def _generate_next_steps(self) -> str:
        """Genera la sección de próximos pasos"""
        content = "## 🎯 Próximos Pasos Recomendados\n\n"
        
        # Basado en los resultados de la sesión
        if self.session_stats.get('tasks_failed', 0) > 0:
            content += "1. **Revisar tareas fallidas** - Algunas tareas no se completaron exitosamente\n"
            
        if self.logger.get_session_summary()['total_warnings'] > 0:
            content += "2. **Atender advertencias** - Se encontraron situaciones que requieren atención\n"
            
        discoveries = self.session_stats.get('discoveries', [])
        if discoveries:
            content += "3. **Actuar sobre descubrimientos** - Se identificaron oportunidades de mejora\n"
            
        content += "4. **Continuar con tareas pendientes** - Ejecutar `task-master next` para ver la siguiente tarea\n"
        content += "5. **Revisar el historial completo** - Ver `historialDeProyecto.md` para contexto adicional\n"
        
        content += "\n### Comando Sugerido\n"
        content += "```bash\n"
        content += "# Para continuar donde quedó GLADOS:\n"
        content += "task-master next\n"
        content += "\n# O activar otra sesión automática:\n"
        content += "glados auto on\n"
        content += "```\n\n"
        
        return content
        
    def _generate_footer(self) -> str:
        """Genera el pie del informe"""
        return f"""---

*Informe generado automáticamente por GLADOS Auto Mode*  
*Para más detalles, revisa los logs en: `~/.glados/logs/session_{self.logger.session_id}.log`*

🤖 *"The Enrichment Center reminds you that the Weighted Companion Cube will never threaten to stab you and, in fact, cannot speak."* - GLaDOS
"""
        
    def _save_json_report(self, path: Path, summary: Dict):
        """Guarda versión JSON del reporte para procesamiento posterior"""
        # Convertir sets a listas para serialización JSON
        stats_copy = self.session_stats.copy()
        if 'agents_used' in stats_copy and isinstance(stats_copy['agents_used'], set):
            stats_copy['agents_used'] = list(stats_copy['agents_used'])
        if 'files_modified' in stats_copy and isinstance(stats_copy['files_modified'], set):
            stats_copy['files_modified'] = list(stats_copy['files_modified'])
        
        report_data = {
            'session_summary': summary,
            'session_stats': stats_copy,
            'chapters': self.logger.chapters_completed,
            'generated_at': datetime.now().isoformat()
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
            
    def _calculate_percentage(self, part: int, total: int) -> int:
        """Calcula porcentaje de manera segura"""
        if total == 0:
            return 0
        return int((part / total) * 100)
        
    def _generate_progress_bar(self, percentage: int) -> str:
        """Genera una barra de progreso visual"""
        filled = int(20 * percentage / 100)
        empty = 20 - filled
        return f"[{'█' * filled}{'░' * empty}]"


# Ejemplo de uso
if __name__ == "__main__":
    # Este sería llamado desde glados_auto.py
    print("SessionReporter - Generador de informes para GLADOS")