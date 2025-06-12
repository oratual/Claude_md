#!/usr/bin/env python3
"""
Claude Code Quota Monitor - Monitoreo local de uso sin consumir cuota.
Rastrea prompts, tiempo hasta refresh (5h) y sugiere estrategias de uso.
"""

import time
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path


class ClaudeQuotaMonitor:
    """
    Monitorea el uso de Claude Code y tiempo hasta refresh.
    - Cuota se resetea cada 5 horas
    - Plan Max 20x: ~200-800 prompts por período
    """
    
    QUOTA_PERIOD = 5 * 60 * 60  # 5 horas en segundos
    QUOTA_FILE = Path.home() / '.config' / 'claude-code' / 'quota_tracking.json'
    
    # Límites aproximados por plan
    LIMITS = {
        'max_20x': {
            'conservative': 200,  # Prompts complejos
            'average': 500,       # Uso promedio
            'optimistic': 800     # Prompts simples
        }
    }
    
    def __init__(self, plan='max_20x'):
        self.plan = plan
        self.load_state()
    
    def load_state(self):
        """Carga el estado desde archivo o crea uno nuevo."""
        if self.QUOTA_FILE.exists():
            with open(self.QUOTA_FILE, 'r') as f:
                self.state = json.load(f)
        else:
            self.state = {
                'period_start': time.time(),
                'prompt_count': 0,
                'opus_count': 0,
                'sonnet_count': 0,
                'model_switches': [],
                'morning_activation': None
            }
            self.save_state()
    
    def save_state(self):
        """Guarda el estado actual."""
        self.QUOTA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(self.QUOTA_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def check_reset(self):
        """Verifica si es hora de resetear la cuota."""
        current_time = time.time()
        if current_time - self.state['period_start'] >= self.QUOTA_PERIOD:
            # Guardar estadísticas del período anterior
            self.archive_period()
            # Resetear
            self.state = {
                'period_start': current_time,
                'prompt_count': 0,
                'opus_count': 0,
                'sonnet_count': 0,
                'model_switches': [],
                'morning_activation': None
            }
            self.save_state()
            return True
        return False
    
    def archive_period(self):
        """Guarda estadísticas del período anterior."""
        archive_file = self.QUOTA_FILE.parent / 'quota_history.json'
        history = []
        
        if archive_file.exists():
            with open(archive_file, 'r') as f:
                history = json.load(f)
        
        history.append({
            'period_end': time.time(),
            'stats': self.state.copy()
        })
        
        # Mantener solo últimos 30 días
        cutoff = time.time() - (30 * 24 * 60 * 60)
        history = [h for h in history if h['period_end'] > cutoff]
        
        with open(archive_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def record_prompt(self, model='opus', is_morning_coffee=False):
        """Registra un nuevo prompt."""
        self.check_reset()
        
        self.state['prompt_count'] += 1
        if model == 'opus':
            self.state['opus_count'] += 1
        else:
            self.state['sonnet_count'] += 1
        
        # Registrar activación matutina
        if is_morning_coffee and self.state['prompt_count'] == 1:
            self.state['morning_activation'] = time.time()
        
        self.save_state()
    
    def get_time_remaining(self):
        """Retorna tiempo hasta el próximo reset."""
        elapsed = time.time() - self.state['period_start']
        remaining = self.QUOTA_PERIOD - elapsed
        
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        seconds = int(remaining % 60)
        
        return {
            'total_seconds': remaining,
            'formatted': f"{hours}h {minutes}m {seconds}s",
            'percentage': (elapsed / self.QUOTA_PERIOD) * 100
        }
    
    def get_usage_status(self):
        """Retorna estado actual de uso."""
        limits = self.LIMITS[self.plan]
        current = self.state['prompt_count']
        
        # Calcular porcentaje basado en límite promedio
        percentage = (current / limits['average']) * 100
        
        # Determinar nivel de alerta
        if percentage < 50:
            status = 'green'
            emoji = '🟢'
        elif percentage < 75:
            status = 'yellow' 
            emoji = '🟡'
        elif percentage < 90:
            status = 'orange'
            emoji = '🟠'
        else:
            status = 'red'
            emoji = '🔴'
        
        return {
            'current': current,
            'percentage': percentage,
            'status': status,
            'emoji': emoji,
            'limits': limits,
            'opus_count': self.state['opus_count'],
            'sonnet_count': self.state['sonnet_count']
        }
    
    def get_work_window_analysis(self):
        """Analiza si el refresh estará disponible para horario laboral."""
        time_info = self.get_time_remaining()
        now = datetime.now()
        refresh_time = now + timedelta(seconds=time_info['total_seconds'])
        
        # Horario laboral típico
        work_start = now.replace(hour=9, minute=0, second=0)
        work_end = now.replace(hour=18, minute=0, second=0)
        
        # Si es fin de semana, ajustar al lunes
        if now.weekday() >= 5:  # Sábado o domingo
            days_to_monday = 7 - now.weekday()
            work_start += timedelta(days=days_to_monday)
            work_end += timedelta(days=days_to_monday)
        elif now.hour >= 18:  # Después del trabajo
            work_start += timedelta(days=1)
            work_end += timedelta(days=1)
        
        analysis = {
            'refresh_time': refresh_time.strftime("%H:%M"),
            'refresh_date': refresh_time.strftime("%d/%m"),
            'is_workday': refresh_time.weekday() < 5
        }
        
        # Análisis de conveniencia
        if refresh_time.hour < 9:
            analysis['timing'] = "✅ Refresh antes del trabajo"
        elif 9 <= refresh_time.hour < 18:
            analysis['timing'] = "⚠️ Refresh durante horario laboral"
        else:
            analysis['timing'] = "🌙 Refresh fuera de horario laboral"
        
        # Sugerencia para activación matutina
        if now.hour < 8 and self.state['prompt_count'] == 0:
            optimal_activation = now.replace(hour=4, minute=0)
            if optimal_activation < now:
                optimal_activation += timedelta(days=1)
            analysis['suggestion'] = f"💡 Activar a las {optimal_activation.strftime('%H:%M')} = refresh a las 9:00"
        
        return analysis
    
    def format_status(self):
        """Formatea un reporte completo del estado."""
        time_info = self.get_time_remaining()
        usage_info = self.get_usage_status()
        work_analysis = self.get_work_window_analysis()
        
        # Calcular velocidad de uso
        elapsed_hours = (self.QUOTA_PERIOD - time_info['total_seconds']) / 3600
        if elapsed_hours > 0:
            rate = usage_info['current'] / elapsed_hours
            projected = rate * 5  # Proyección a 5 horas
        else:
            rate = 0
            projected = 0
        
        output = f"""
╔══════════════════════════════════════════════╗
║        Claude Code Quota Monitor 🔍          ║
╠══════════════════════════════════════════════╣
║                                              ║
║ 📊 Uso actual: {usage_info['emoji']} {usage_info['current']} prompts ({usage_info['percentage']:.1f}%)
║                                              ║
║ 🤖 Distribución de modelos:                  ║
║    • Opus 4: {usage_info['opus_count']} prompts                     ║
║    • Sonnet 4: {usage_info['sonnet_count']} prompts                   ║"""
        
        if usage_info['sonnet_count'] > 0:
            output += f"""
║    ⚠️  Cambio a Sonnet detectado!            ║"""
        
        output += f"""
║                                              ║
║ ⏱️  Tiempo hasta refresh: {time_info['formatted']}
║    Progreso: ▓{'█' * int(time_info['percentage'] / 10)}{'░' * (10 - int(time_info['percentage'] / 10))} {time_info['percentage']:.0f}%
║                                              ║
║ 📈 Análisis de uso:                          ║
║    • Velocidad: {rate:.1f} prompts/hora      ║
║    • Proyección 5h: {projected:.0f} prompts  ║
║                                              ║
║ 🕐 Ventana de trabajo:                       ║
║    • Refresh a las {work_analysis['refresh_time']} del {work_analysis['refresh_date']}
║    • {work_analysis['timing']}
║"""
        
        if 'suggestion' in work_analysis:
            output += f"""    • {work_analysis['suggestion']}
║"""
        
        output += f"""                                              ║
║ 📋 Límites Plan Max 20x ($200/mes):          ║
║    • Conservador: {usage_info['limits']['conservative']} prompts          ║
║    • Promedio: {usage_info['limits']['average']} prompts              ║
║    • Optimista: {usage_info['limits']['optimistic']} prompts             ║
╚══════════════════════════════════════════════╝"""
        
        return output
    
    def should_alert(self):
        """Determina si debe alertar al usuario."""
        time_info = self.get_time_remaining()
        usage_info = self.get_usage_status()
        
        alerts = []
        
        # Alerta por uso alto
        if usage_info['percentage'] >= 80:
            alerts.append(f"⚠️ Uso alto: {usage_info['percentage']:.0f}% de la cuota estimada")
        elif usage_info['percentage'] >= 60:
            alerts.append(f"🟡 Uso moderado: {usage_info['percentage']:.0f}% de la cuota")
        
        # Alerta por tiempo
        if time_info['total_seconds'] < 3600:  # Menos de 1 hora
            alerts.append(f"⏰ Refresh pronto: {time_info['formatted']}")
        elif time_info['total_seconds'] < 1800:  # Menos de 30 minutos
            alerts.append(f"🚨 Refresh inminente: {time_info['formatted']}")
        
        # Alerta por cambio de modelo
        if usage_info['sonnet_count'] > 0 and usage_info['opus_count'] > 0:
            ratio = usage_info['sonnet_count'] / usage_info['current'] * 100
            alerts.append(f"🔄 Usando Sonnet en {ratio:.0f}% de los prompts")
        
        # Alerta por velocidad de consumo
        elapsed_hours = (self.QUOTA_PERIOD - time_info['total_seconds']) / 3600
        if elapsed_hours > 0.5:  # Al menos 30 min de datos
            rate = usage_info['current'] / elapsed_hours
            if rate > 100:  # Más de 100 prompts/hora
                alerts.append(f"🚀 Ritmo alto: {rate:.0f} prompts/hora")
        
        return alerts


def main():
    """Script CLI para consultar estado de cuota."""
    monitor = ClaudeQuotaMonitor()
    
    # Parsear argumentos
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == '--record' or command == '-r':
            model = sys.argv[2] if len(sys.argv) > 2 else 'opus'
            monitor.record_prompt(model)
            print(f"✅ Prompt registrado ({model})")
            
            # Mostrar mini-status
            usage = monitor.get_usage_status()
            time_remaining = monitor.get_time_remaining()
            print(f"   Total: {usage['current']} | Tiempo restante: {time_remaining['formatted']}")
            
        elif command == '--reset':
            monitor.state['period_start'] = 0
            monitor.save_state()
            monitor.check_reset()
            print("✅ Cuota reseteada manualmente")
            
        elif command == '--morning' or command == '-m':
            monitor.record_prompt('opus', is_morning_coffee=True)
            print("☕ Activación matutina registrada")
            work_analysis = monitor.get_work_window_analysis()
            print(f"   Refresh a las {work_analysis['refresh_time']}")
            print(f"   {work_analysis['timing']}")
            
        elif command == '--quick' or command == '-q':
            # Vista rápida de una línea
            usage = monitor.get_usage_status()
            time_remaining = monitor.get_time_remaining()
            print(f"{usage['emoji']} {usage['current']}/{usage['limits']['average']} | ⏱️ {time_remaining['formatted']}")
            
        elif command == '--help' or command == '-h':
            print("""
Claude Quota Monitor - Uso:

  claude-quota              Ver estado completo
  claude-quota -q           Vista rápida (una línea)
  claude-quota -r [modelo]  Registrar prompt (opus/sonnet)
  claude-quota -m           Registrar activación matutina
  claude-quota --reset      Resetear contador manualmente
  claude-quota --help       Ver esta ayuda

Ejemplos:
  claude-quota -r opus      Registra un prompt de Opus
  claude-quota -r sonnet    Registra un prompt de Sonnet
  claude-quota -m           Marca inicio de período matutino
""")
        else:
            print(f"❌ Comando desconocido: {command}")
            print("   Usa --help para ver opciones")
    else:
        # Sin argumentos: mostrar estado completo
        print(monitor.format_status())
        
        # Mostrar alertas si las hay
        alerts = monitor.should_alert()
        if alerts:
            print("\n🔔 ALERTAS:")
            for alert in alerts:
                print(f"   {alert}")
        
        print("\n💡 Tip: Usa 'claude-quota -q' para vista rápida")


if __name__ == "__main__":
    main()