#!/usr/bin/env python3
"""
Morning Report Generator - Reporte claro y efectivo de los sueños de Batman
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class MorningReport:
    """Genera reportes matutinos claros y accionables"""
    
    def __init__(self):
        self.dream_journal = Path("batman_dreams.json")
        self.insights_db = Path("batman_insights.json")
        
    def generate_morning_report(self) -> str:
        """Genera reporte matutino ultra-claro"""
        report = []
        
        # Encabezado
        report.append("# 🌅 REPORTE MATUTINO BATMAN")
        report.append(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("=" * 50)
        
        # 1. DESCUBRIMIENTOS PRINCIPALES (Lo más importante primero)
        report.append("\n## 🎯 ACCIONES RECOMENDADAS HOY\n")
        
        insights = self._get_top_insights()
        for i, insight in enumerate(insights[:3], 1):
            report.append(f"### {i}. {insight['title']}")
            report.append(f"   **Acción**: {insight['action']}")
            report.append(f"   **Beneficio**: {insight['benefit']}")
            report.append(f"   **Confianza**: {'⭐' * int(insight['confidence'] * 5)}")
            report.append(f"   **Comando**: `{insight['command']}`")
            report.append("")
            
        # 2. PROBLEMAS DETECTADOS
        report.append("\n## ⚠️ PROBLEMAS ENCONTRADOS\n")
        
        problems = self._get_detected_problems()
        for problem in problems[:3]:
            report.append(f"- **{problem['issue']}**")
            report.append(f"  - Detectado: {problem['when']}")
            report.append(f"  - Impacto: {problem['impact']}")
            report.append(f"  - Solución: {problem['solution']}")
            report.append("")
            
        # 3. OPTIMIZACIONES DESCUBIERTAS
        report.append("\n## 💡 OPTIMIZACIONES DISPONIBLES\n")
        
        optimizations = self._get_optimizations()
        for opt in optimizations[:3]:
            report.append(f"**{opt['name']}**")
            report.append(f"- Ahorro esperado: {opt['savings']}")
            report.append(f"- Tiempo implementación: {opt['time']}")
            report.append(f"- Riesgo: {opt['risk']}")
            report.append("")
            
        # 4. RESUMEN EJECUTIVO
        report.append("\n## 📊 RESUMEN DE LA NOCHE\n")
        
        stats = self._get_night_stats()
        report.append(f"- Tareas completadas: {stats['completed']}/{stats['total']}")
        report.append(f"- Tiempo soñando: {stats['dream_time']} minutos")
        report.append(f"- Insights generados: {stats['insights']}")
        report.append(f"- Experimentos realizados: {stats['experiments']}")
        
        # 5. DECISIÓN RÁPIDA
        report.append("\n## ✅ DECISIÓN RÁPIDA\n")
        report.append("Si solo puedes hacer UNA cosa hoy:")
        
        top_action = insights[0] if insights else None
        if top_action:
            report.append(f"\n**→ {top_action['action']}**")
            report.append(f"\nEsto {top_action['benefit'].lower()}")
            report.append(f"\nTiempo estimado: {top_action.get('time', '15 minutos')}")
        
        return "\n".join(report)
    
    def _get_top_insights(self) -> List[Dict]:
        """Obtiene insights más importantes"""
        # Simulación - en producción leería de batman_dreams.json
        return [
            {
                'title': 'Paralelizar Backups',
                'action': 'Implementar backup_parallel.sh',
                'benefit': 'Reduce tiempo de backup de 3h a 45min',
                'confidence': 0.91,
                'command': 'bash /opt/batman/scripts/backup_parallel.sh',
                'time': '30 minutos'
            },
            {
                'title': 'Limpieza Inteligente de Logs',
                'action': 'Activar rotación por contenido',
                'benefit': 'Libera 70% espacio en /var/log',
                'confidence': 0.85,
                'command': 'batman enable smart-log-rotation',
                'time': '10 minutos'
            },
            {
                'title': 'Optimización de I/O',
                'action': 'Desfragmentar antes de backups',
                'benefit': 'Previene 80% de timeouts',
                'confidence': 0.78,
                'command': 'batman schedule defrag-before-backup',
                'time': '5 minutos'
            }
        ]
    
    def _get_detected_problems(self) -> List[Dict]:
        """Problemas detectados durante la noche"""
        return [
            {
                'issue': 'Temperatura CPU alta durante backups',
                'when': '03:45 AM',
                'impact': 'Ralentización 40%',
                'solution': 'Reducir workers de 8 a 4'
            },
            {
                'issue': 'Fragmentación disco > 20%',
                'when': 'Análisis 04:15 AM',
                'impact': 'I/O 3x más lento',
                'solution': 'Programar defrag semanal'
            }
        ]
    
    def _get_optimizations(self) -> List[Dict]:
        """Optimizaciones descubiertas"""
        return [
            {
                'name': 'Compresión ZStd para logs',
                'savings': '60% espacio, 4x más rápido',
                'time': '20 minutos',
                'risk': 'Bajo'
            },
            {
                'name': 'Cache de metadatos',
                'savings': '50% menos I/O en scans',
                'time': '1 hora',
                'risk': 'Medio'
            }
        ]
    
    def _get_night_stats(self) -> Dict:
        """Estadísticas de la noche"""
        return {
            'completed': 23,
            'total': 25,
            'dream_time': 47,
            'insights': 7,
            'experiments': 3
        }
    
    def save_html_report(self, content: str):
        """Guarda versión HTML del reporte"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Batman Morning Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: auto; padding: 20px; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #7f8c8d; }}
        code {{ background: #ecf0f1; padding: 2px 5px; border-radius: 3px; }}
        .action {{ background: #e8f5e9; padding: 10px; border-left: 4px solid #4caf50; margin: 10px 0; }}
        .problem {{ background: #fff3cd; padding: 10px; border-left: 4px solid #ff9800; margin: 10px 0; }}
        .optimization {{ background: #e3f2fd; padding: 10px; border-left: 4px solid #2196f3; margin: 10px 0; }}
    </style>
</head>
<body>
{content.replace('# ', '<h1>').replace('## ', '</h1><h2>').replace('### ', '</h2><h3>').replace('\n', '</h3><p>').replace('**', '<strong>').replace('`', '<code>')}
</body>
</html>
"""
        
        filename = f"morning_report_{datetime.now().strftime('%Y%m%d')}.html"
        with open(filename, 'w') as f:
            f.write(html)
        
        return filename


def generate_morning_report():
    """Función principal para generar reporte"""
    reporter = MorningReport()
    
    # Generar reporte
    report = reporter.generate_morning_report()
    
    # Mostrar en consola
    print(report)
    
    # Guardar versión HTML
    html_file = reporter.save_html_report(report)
    print(f"\n📄 Reporte HTML guardado en: {html_file}")
    
    # Guardar versión texto
    txt_file = f"morning_report_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(txt_file, 'w') as f:
        f.write(report)
    print(f"📄 Reporte TXT guardado en: {txt_file}")
    
    return report


if __name__ == "__main__":
    generate_morning_report()