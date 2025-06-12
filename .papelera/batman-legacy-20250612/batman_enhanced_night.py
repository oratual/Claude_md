#!/usr/bin/env python3
"""
Batman Enhanced Night Mode - Sistema nocturno mejorado con todas las integraciones
Combina GitHub, MCPs, y herramientas del sistema para máxima efectividad
"""

import os
import sys
import json
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
import yaml
import argparse
import signal
import shutil
from dataclasses import dataclass
from enum import Enum

# Importar componentes de Batman
sys.path.append(str(Path(__file__).parent))

from batman_github_integration import BatmanGitHubIntegration, IssueType, IssueSeverity
from batman_mcp_manager import MCPManager, BatmanMCPInterface
from src.task_manager import TaskManager, Task as TaskObj, TaskType, TaskPriority


class AnalysisType(Enum):
    """Tipos de análisis que Batman puede realizar"""
    DISK_USAGE = "disk_usage"
    LOG_ANALYSIS = "log_analysis"
    SECURITY_AUDIT = "security_audit"
    PERFORMANCE_METRICS = "performance_metrics"
    CODE_QUALITY = "code_quality"
    DEPENDENCY_CHECK = "dependency_check"


@dataclass
class Discovery:
    """Representa un descubrimiento durante el análisis"""
    type: str
    severity: str
    title: str
    description: str
    details: str
    location: str = ""
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []


class BatmanEnhancedNight:
    """Sistema nocturno mejorado de Batman"""
    
    def __init__(self, config_path: str = "~/.batman/enhanced_config.yaml"):
        self.config_path = Path(config_path).expanduser()
        self.config = self.load_config()
        self.logger = self.setup_logging()
        
        # Inicializar componentes
        self.github = BatmanGitHubIntegration() if self.config.get('github_enabled', True) else None
        self.mcp_manager = MCPManager()
        self.mcp = BatmanMCPInterface(self.mcp_manager)
        self.task_manager = TaskManager()
        
        # Estado de ejecución
        self.discoveries = []
        self.optimizations = []
        self.alerts = []
        self.metrics = {}
        self.start_time = datetime.now()
        
        # Herramientas del sistema
        self.system_tools = self.check_system_tools()
        
    def load_config(self) -> Dict:
        """Carga configuración"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        else:
            # Configuración por defecto
            default_config = {
                'github_enabled': True,
                'github_repo': 'lauta/glados',
                'mcp_enabled': True,
                'analyses': {
                    'disk_usage': {
                        'enabled': True,
                        'threshold_gb': 100,
                        'large_file_mb': 100
                    },
                    'log_analysis': {
                        'enabled': True,
                        'error_threshold': 10,
                        'patterns': ['ERROR', 'CRITICAL', 'FAILED']
                    },
                    'security_audit': {
                        'enabled': True,
                        'check_permissions': True,
                        'check_ports': True
                    },
                    'performance_metrics': {
                        'enabled': True,
                        'cpu_threshold': 80,
                        'memory_threshold': 90
                    }
                },
                'optimizations': {
                    'auto_cleanup': True,
                    'compress_logs': True,
                    'optimize_git': True
                },
                'reporting': {
                    'create_github_issues': True,
                    'daily_summary': True,
                    'alert_threshold': 'high'
                }
            }
            
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False)
                
            return default_config
            
    def setup_logging(self) -> logging.Logger:
        """Configura logging"""
        logger = logging.getLogger('batman_enhanced')
        logger.setLevel(logging.INFO)
        
        # Handler para archivo
        log_dir = Path.home() / '.batman' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"enhanced_{datetime.now():%Y%m%d}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        
        # Handler para consola con color
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('🦇 %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
        
    def check_system_tools(self) -> Dict[str, bool]:
        """Verifica qué herramientas del sistema están disponibles"""
        tools = {
            'ripgrep': shutil.which('rg') is not None,
            'fd': shutil.which('fdfind') or shutil.which('fd') is not None,
            'bat': shutil.which('batcat') or shutil.which('bat') is not None,
            'jq': shutil.which('jq') is not None,
            'exa': shutil.which('exa') is not None,
            'gh': shutil.which('gh') is not None,
            'git': shutil.which('git') is not None
        }
        
        self.logger.info(f"Herramientas disponibles: {[k for k, v in tools.items() if v]}")
        return tools
        
    def analyze_disk_usage(self) -> List[Discovery]:
        """Analiza uso de disco"""
        discoveries = []
        config = self.config['analyses']['disk_usage']
        
        if not config['enabled']:
            return discoveries
            
        self.logger.info("Analizando uso de disco...")
        
        # Usar df para obtener uso general
        df_result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
        
        # Buscar archivos grandes
        if self.system_tools['fd']:
            # Usar fd para buscar archivos grandes
            cmd = ['fdfind', '--type', 'f', '--size', f'+{config["large_file_mb"]}M']
        else:
            # Fallback a find
            cmd = ['find', '/', '-type', 'f', '-size', f'+{config["large_file_mb"]}M', '2>/dev/null']
            
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            large_files = result.stdout.strip().split('\n') if result.stdout else []
            
            if large_files and large_files[0]:
                discovery = Discovery(
                    type='disk_usage',
                    severity='medium' if len(large_files) < 10 else 'high',
                    title=f'Encontrados {len(large_files)} archivos grandes',
                    description=f'Archivos mayores a {config["large_file_mb"]}MB detectados',
                    details='\n'.join(large_files[:20]),
                    recommendations=[
                        'Revisar si estos archivos son necesarios',
                        'Considerar compresión o archivado',
                        'Mover a almacenamiento externo si es posible'
                    ]
                )
                discoveries.append(discovery)
                
        except subprocess.TimeoutExpired:
            self.logger.warning("Timeout buscando archivos grandes")
            
        # Analizar directorios con más uso
        try:
            du_cmd = ['du', '-h', '--max-depth=2', '/home', '2>/dev/null', '|', 'sort', '-hr', '|', 'head', '-20']
            result = subprocess.run(' '.join(du_cmd), shell=True, capture_output=True, text=True)
            
            if result.stdout:
                discovery = Discovery(
                    type='disk_usage',
                    severity='info',
                    title='Directorios con mayor uso de espacio',
                    description='Top 20 directorios por uso de disco',
                    details=result.stdout,
                    recommendations=['Revisar contenido de directorios grandes']
                )
                discoveries.append(discovery)
                
        except Exception as e:
            self.logger.error(f"Error analizando directorios: {e}")
            
        # Guardar en memoria MCP si está disponible
        if self.mcp:
            self.mcp.use_memory_mcp('store', 
                key='last_disk_analysis', 
                value={
                    'timestamp': datetime.now().isoformat(),
                    'large_files_count': len(large_files),
                    'discoveries': len(discoveries)
                }
            )
            
        return discoveries
        
    def analyze_logs(self) -> List[Discovery]:
        """Analiza logs del sistema"""
        discoveries = []
        config = self.config['analyses']['log_analysis']
        
        if not config['enabled']:
            return discoveries
            
        self.logger.info("Analizando logs del sistema...")
        
        # Usar ripgrep si está disponible
        if self.system_tools['ripgrep']:
            for pattern in config['patterns']:
                cmd = ['rg', '-i', pattern, '/var/log/', '--type-add', 'log:*.log', '-t', 'log', '-c']
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.stdout:
                        matches = result.stdout.strip().split('\n')
                        total_matches = sum(int(m.split(':')[-1]) for m in matches if ':' in m)
                        
                        if total_matches > config['error_threshold']:
                            discovery = Discovery(
                                type='log_analysis',
                                severity='high' if total_matches > 100 else 'medium',
                                title=f'Alto número de {pattern} en logs',
                                description=f'Encontradas {total_matches} ocurrencias de {pattern}',
                                details='\n'.join(matches[:10]),
                                recommendations=[
                                    f'Investigar causa de errores {pattern}',
                                    'Revisar servicios afectados',
                                    'Considerar rotación de logs más frecuente'
                                ]
                            )
                            discoveries.append(discovery)
                            
                except Exception as e:
                    self.logger.error(f"Error buscando {pattern}: {e}")
                    
        # Analizar systemd journal
        try:
            # Últimas 24 horas de errores
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            cmd = ['journalctl', '--since', yesterday, '-p', 'err', '--no-pager']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.stdout:
                error_lines = result.stdout.strip().split('\n')
                if len(error_lines) > 50:
                    discovery = Discovery(
                        type='log_analysis',
                        severity='high',
                        title='Múltiples errores en journal',
                        description=f'{len(error_lines)} errores en las últimas 24 horas',
                        details='\n'.join(error_lines[:20]),
                        recommendations=[
                            'Revisar servicios con errores frecuentes',
                            'Verificar estado de servicios críticos'
                        ]
                    )
                    discoveries.append(discovery)
                    
        except Exception as e:
            self.logger.error(f"Error analizando journal: {e}")
            
        return discoveries
        
    def security_audit(self) -> List[Discovery]:
        """Realiza auditoría básica de seguridad"""
        discoveries = []
        config = self.config['analyses']['security_audit']
        
        if not config['enabled']:
            return discoveries
            
        self.logger.info("Realizando auditoría de seguridad...")
        
        # Verificar permisos inseguros
        if config['check_permissions']:
            # Archivos con permisos 777
            cmd = ['find', os.path.expanduser('~'), '-type', 'f', '-perm', '777', '2>/dev/null']
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.stdout:
                    insecure_files = result.stdout.strip().split('\n')
                    if insecure_files and insecure_files[0]:
                        discovery = Discovery(
                            type='security',
                            severity='high',
                            title='Archivos con permisos inseguros (777)',
                            description=f'{len(insecure_files)} archivos con permisos world-writable',
                            details='\n'.join(insecure_files[:20]),
                            recommendations=[
                                'Cambiar permisos a valores más restrictivos',
                                'Usar chmod 644 para archivos normales',
                                'Usar chmod 755 para ejecutables'
                            ]
                        )
                        discoveries.append(discovery)
                        
            except Exception as e:
                self.logger.error(f"Error verificando permisos: {e}")
                
        # Verificar puertos abiertos
        if config['check_ports']:
            try:
                result = subprocess.run(['ss', '-tulpn'], capture_output=True, text=True)
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    listening_ports = [l for l in lines if 'LISTEN' in l]
                    
                    # Buscar puertos no estándar
                    suspicious = []
                    for line in listening_ports:
                        parts = line.split()
                        if len(parts) > 4:
                            addr = parts[4]
                            if ':' in addr:
                                port = addr.split(':')[-1]
                                try:
                                    port_num = int(port)
                                    # Puertos comunes que esperamos
                                    common_ports = [22, 80, 443, 3306, 5432, 6379, 8080, 8443]
                                    if port_num > 1024 and port_num not in common_ports:
                                        suspicious.append(line)
                                except:
                                    pass
                                    
                    if suspicious:
                        discovery = Discovery(
                            type='security',
                            severity='medium',
                            title='Puertos no estándar abiertos',
                            description=f'{len(suspicious)} servicios escuchando en puertos inusuales',
                            details='\n'.join(suspicious),
                            recommendations=[
                                'Verificar si estos servicios son necesarios',
                                'Considerar firewall para restringir acceso',
                                'Documentar servicios legítimos'
                            ]
                        )
                        discoveries.append(discovery)
                        
            except Exception as e:
                self.logger.error(f"Error verificando puertos: {e}")
                
        return discoveries
        
    def performance_metrics(self) -> List[Discovery]:
        """Analiza métricas de rendimiento"""
        discoveries = []
        config = self.config['analyses']['performance_metrics']
        
        if not config['enabled']:
            return discoveries
            
        self.logger.info("Analizando métricas de rendimiento...")
        
        # CPU usage
        try:
            result = subprocess.run(['mpstat', '1', '1'], capture_output=True, text=True)
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if '%idle' in line:
                        continue
                    if 'all' in line and '%' in line:
                        parts = line.split()
                        if len(parts) > 11:
                            idle = float(parts[-1])
                            cpu_usage = 100 - idle
                            
                            if cpu_usage > config['cpu_threshold']:
                                discovery = Discovery(
                                    type='performance',
                                    severity='high',
                                    title='Alto uso de CPU detectado',
                                    description=f'CPU al {cpu_usage:.1f}% de uso',
                                    details=result.stdout,
                                    recommendations=[
                                        'Identificar procesos consumiendo CPU',
                                        'Optimizar aplicaciones pesadas',
                                        'Considerar escalamiento horizontal'
                                    ]
                                )
                                discoveries.append(discovery)
                                
        except FileNotFoundError:
            # mpstat no disponible, usar top
            try:
                result = subprocess.run(['top', '-bn1'], capture_output=True, text=True)
                # Parsear output de top...
            except:
                self.logger.warning("No se pudo obtener métricas de CPU")
                
        # Memory usage
        try:
            result = subprocess.run(['free', '-h'], capture_output=True, text=True)
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'Mem:' in line:
                        parts = line.split()
                        if len(parts) > 2:
                            # Intentar calcular porcentaje usado
                            self.metrics['memory_info'] = line
                            
        except Exception as e:
            self.logger.error(f"Error obteniendo métricas de memoria: {e}")
            
        # Procesos pesados
        try:
            # Top 10 procesos por CPU
            cmd = "ps aux --sort=-%cpu | head -11"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.stdout:
                self.metrics['top_cpu_processes'] = result.stdout
                
                # Verificar si algún proceso usa más del 50% CPU
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines[:5]:
                    parts = line.split()
                    if len(parts) > 2:
                        try:
                            cpu = float(parts[2])
                            if cpu > 50:
                                discovery = Discovery(
                                    type='performance',
                                    severity='medium',
                                    title=f'Proceso con alto uso de CPU: {parts[10]}',
                                    description=f'Proceso usando {cpu}% de CPU',
                                    details=line,
                                    recommendations=[
                                        'Verificar si el proceso es normal',
                                        'Considerar optimización o límites'
                                    ]
                                )
                                discoveries.append(discovery)
                        except:
                            pass
                            
        except Exception as e:
            self.logger.error(f"Error analizando procesos: {e}")
            
        return discoveries
        
    def apply_optimizations(self) -> List[Dict]:
        """Aplica optimizaciones seguras al sistema"""
        optimizations = []
        
        if not self.config['optimizations']['auto_cleanup']:
            return optimizations
            
        self.logger.info("Aplicando optimizaciones...")
        
        # Limpiar archivos temporales antiguos
        try:
            # Solo en /tmp y con más de 7 días
            cmd = ['find', '/tmp', '-type', 'f', '-mtime', '+7', '-size', '+1M']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.stdout:
                old_files = result.stdout.strip().split('\n')
                if old_files and old_files[0]:
                    # En modo test no borrar
                    if not getattr(self, 'test_mode', False):
                        for file in old_files[:10]:  # Limitar a 10 archivos
                            try:
                                Path(file).unlink()
                                self.logger.info(f"Eliminado: {file}")
                            except:
                                pass
                                
                    optimization = {
                        'type': 'cleanup',
                        'description': f'Limpieza de {len(old_files)} archivos temporales antiguos',
                        'applied': not getattr(self, 'test_mode', False),
                        'details': '\n'.join(old_files[:5])
                    }
                    optimizations.append(optimization)
                    
        except Exception as e:
            self.logger.error(f"Error en limpieza: {e}")
            
        # Comprimir logs antiguos
        if self.config['optimizations']['compress_logs']:
            try:
                # Buscar logs sin comprimir de más de 3 días
                cmd = ['find', '/var/log', '-name', '*.log', '-mtime', '+3', '-size', '+10M', '2>/dev/null']
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.stdout:
                    logs_to_compress = result.stdout.strip().split('\n')
                    compressed = 0
                    
                    for log_file in logs_to_compress[:5]:  # Limitar
                        if log_file and not getattr(self, 'test_mode', False):
                            try:
                                subprocess.run(['gzip', log_file])
                                compressed += 1
                            except:
                                pass
                                
                    if compressed > 0:
                        optimization = {
                            'type': 'compression',
                            'description': f'Comprimidos {compressed} archivos de log',
                            'applied': True,
                            'details': f'Liberado espacio comprimiendo logs antiguos'
                        }
                        optimizations.append(optimization)
                        
            except Exception as e:
                self.logger.error(f"Error comprimiendo logs: {e}")
                
        # Optimizar repositorios git
        if self.config['optimizations']['optimize_git']:
            try:
                # Buscar repos git
                git_dirs = []
                for root, dirs, files in os.walk(os.path.expanduser('~')):
                    if '.git' in dirs:
                        git_dirs.append(root)
                        if len(git_dirs) >= 5:  # Limitar
                            break
                            
                for repo in git_dirs:
                    try:
                        # Solo gc, no operaciones destructivas
                        if not getattr(self, 'test_mode', False):
                            subprocess.run(['git', 'gc', '--auto'], cwd=repo)
                            
                        optimization = {
                            'type': 'git_optimization',
                            'description': f'Optimizado repositorio: {Path(repo).name}',
                            'applied': not getattr(self, 'test_mode', False),
                            'details': 'Ejecutado git gc --auto'
                        }
                        optimizations.append(optimization)
                        
                    except:
                        pass
                        
            except Exception as e:
                self.logger.error(f"Error optimizando git: {e}")
                
        return optimizations
        
    def generate_report(self) -> Dict:
        """Genera reporte completo de la ejecución"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        # Recopilar métricas del sistema
        system_metrics = {
            'hostname': os.uname().nodename,
            'start_time': self.start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration': str(duration),
            'tools_available': [k for k, v in self.system_tools.items() if v],
            **self.metrics
        }
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_tasks': len(self.discoveries) + len(self.optimizations),
            'successful_tasks': len([d for d in self.discoveries if d.severity != 'critical']),
            'failed_tasks': 0,
            'discoveries': [
                {
                    'type': d.type,
                    'severity': d.severity,
                    'title': d.title,
                    'summary': d.description
                }
                for d in self.discoveries
            ],
            'optimizations': self.optimizations,
            'alerts': [
                {
                    'severity': d.severity,
                    'title': d.title,
                    'message': d.description
                }
                for d in self.discoveries if d.severity in ['critical', 'high']
            ],
            'system_metrics': json.dumps(system_metrics, indent=2),
            'recommendations': self._generate_recommendations(),
            'execution_time': str(duration)
        }
        
        return report
        
    def _generate_recommendations(self) -> List[str]:
        """Genera recomendaciones basadas en los descubrimientos"""
        recommendations = set()
        
        # Basadas en severidad
        critical_count = len([d for d in self.discoveries if d.severity == 'critical'])
        high_count = len([d for d in self.discoveries if d.severity == 'high'])
        
        if critical_count > 0:
            recommendations.add("🚨 Atender problemas críticos inmediatamente")
            
        if high_count > 3:
            recommendations.add("⚠️ Múltiples problemas de alta severidad requieren atención")
            
        # Basadas en tipo
        security_issues = [d for d in self.discoveries if d.type == 'security']
        if security_issues:
            recommendations.add("🔒 Revisar y corregir problemas de seguridad identificados")
            
        performance_issues = [d for d in self.discoveries if d.type == 'performance']
        if performance_issues:
            recommendations.add("⚡ Optimizar rendimiento del sistema")
            
        # Recomendaciones específicas de descubrimientos
        for discovery in self.discoveries[:5]:  # Top 5
            recommendations.update(discovery.recommendations)
            
        return list(recommendations)[:10]  # Limitar a 10
        
    def run(self, test_mode: bool = False):
        """Ejecuta el análisis nocturno completo"""
        self.test_mode = test_mode
        self.logger.info(f"🦇 Batman Enhanced Night iniciando... {'(MODO TEST)' if test_mode else ''}")
        
        # Ejecutar análisis
        analyses = [
            ("Uso de disco", self.analyze_disk_usage),
            ("Logs del sistema", self.analyze_logs),
            ("Seguridad", self.security_audit),
            ("Rendimiento", self.performance_metrics)
        ]
        
        for name, analysis_func in analyses:
            try:
                self.logger.info(f"Ejecutando análisis: {name}")
                discoveries = analysis_func()
                self.discoveries.extend(discoveries)
                self.logger.info(f"  Descubrimientos: {len(discoveries)}")
            except Exception as e:
                self.logger.error(f"Error en análisis {name}: {e}")
                
        # Aplicar optimizaciones
        if not test_mode or self.config.get('test_optimizations', False):
            self.optimizations = self.apply_optimizations()
            
        # Generar reporte
        report = self.generate_report()
        
        # Guardar reporte local
        report_dir = Path.home() / '.batman' / 'reports'
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = report_dir / f"enhanced_report_{datetime.now():%Y%m%d_%H%M%S}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        self.logger.info(f"Reporte guardado en: {report_file}")
        
        # Crear issues en GitHub si está habilitado
        if self.github and self.config['reporting']['create_github_issues'] and not test_mode:
            # Issues para descubrimientos críticos
            for discovery in self.discoveries:
                if discovery.severity in ['critical', 'high']:
                    try:
                        issue_data = {
                            'type': discovery.type,
                            'severity': discovery.severity,
                            'title': discovery.title,
                            'description': discovery.description,
                            'details': discovery.details,
                            'location': discovery.location,
                            'recommendations': '\n'.join(f'- {r}' for r in discovery.recommendations)
                        }
                        
                        issue_num = self.github.create_discovery_issue(issue_data)
                        if issue_num:
                            self.logger.info(f"Issue creado: #{issue_num} - {discovery.title}")
                            
                    except Exception as e:
                        self.logger.error(f"Error creando issue: {e}")
                        
            # Reporte diario
            if self.config['reporting']['daily_summary']:
                try:
                    summary_num = self.github.create_nightly_report_issue(report)
                    if summary_num:
                        self.logger.info(f"Reporte diario creado: #{summary_num}")
                except Exception as e:
                    self.logger.error(f"Error creando reporte diario: {e}")
                    
        # Mostrar resumen
        print("\n" + "="*60)
        print("🦇 BATMAN ENHANCED - RESUMEN DE EJECUCIÓN")
        print("="*60)
        print(f"Descubrimientos: {len(self.discoveries)}")
        print(f"  - Críticos: {len([d for d in self.discoveries if d.severity == 'critical'])}")
        print(f"  - Altos: {len([d for d in self.discoveries if d.severity == 'high'])}")
        print(f"  - Medios: {len([d for d in self.discoveries if d.severity == 'medium'])}")
        print(f"Optimizaciones aplicadas: {len(self.optimizations)}")
        print(f"Duración: {report['execution_time']}")
        print(f"\nReporte completo: {report_file}")
        print("="*60)
        
        return report


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Batman Enhanced Night Mode')
    parser.add_argument('--test', action='store_true', help='Ejecutar en modo test (no aplica cambios)')
    parser.add_argument('--analyze-only', action='store_true', help='Solo análisis, sin optimizaciones')
    parser.add_argument('--config', help='Archivo de configuración alternativo')
    
    args = parser.parse_args()
    
    # Crear instancia
    config_path = args.config if args.config else "~/.batman/enhanced_config.yaml"
    batman = BatmanEnhancedNight(config_path)
    
    if args.analyze_only:
        batman.config['optimizations']['auto_cleanup'] = False
        batman.config['optimizations']['compress_logs'] = False
        batman.config['optimizations']['optimize_git'] = False
        
    # Ejecutar
    try:
        batman.run(test_mode=args.test)
    except KeyboardInterrupt:
        print("\n🦇 Batman interrumpido por usuario")
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()