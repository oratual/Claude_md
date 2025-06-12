#!/usr/bin/env python3
"""
Batman GitHub Integration - Integración completa con GitHub para automatización
Usa GitHub CLI (gh) que ya está autenticado en el sistema
"""

import subprocess
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import time
import yaml
import os
from dataclasses import dataclass
from enum import Enum


class IssueType(Enum):
    """Tipos de issues que Batman puede crear"""
    SECURITY = "security"
    PERFORMANCE = "performance"
    BUG = "bug"
    OPTIMIZATION = "optimization"
    DISCOVERY = "discovery"
    ALERT = "alert"


class IssueSeverity(Enum):
    """Niveles de severidad"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class GitHubConfig:
    """Configuración de GitHub"""
    owner: str
    repo: str
    default_branch: str = "main"
    project_number: Optional[int] = None
    labels: Dict[str, List[str]] = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = {
                IssueType.SECURITY.value: ["security", "batman-found", "urgent"],
                IssueType.PERFORMANCE.value: ["performance", "batman-found"],
                IssueType.BUG.value: ["bug", "batman-found"],
                IssueType.OPTIMIZATION.value: ["enhancement", "batman-found"],
                IssueType.DISCOVERY.value: ["discovery", "batman-found"],
                IssueType.ALERT.value: ["alert", "batman-found", "needs-attention"]
            }


class GitHubCLI:
    """Wrapper para GitHub CLI (gh)"""
    
    def __init__(self, config: GitHubConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._check_gh_available()
        self._check_auth()
        
    def _check_gh_available(self):
        """Verifica que gh esté instalado"""
        try:
            result = subprocess.run(['gh', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError("GitHub CLI (gh) no está instalado")
            self.logger.info(f"GitHub CLI disponible: {result.stdout.strip()}")
        except FileNotFoundError:
            raise RuntimeError("GitHub CLI (gh) no encontrado. Instala con: sudo apt install gh")
            
    def _check_auth(self):
        """Verifica autenticación"""
        result = subprocess.run(['gh', 'auth', 'status'], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError("No autenticado en GitHub. Ejecuta: gh auth login")
        self.logger.info("GitHub CLI autenticado correctamente")
        
    def run_gh_command(self, args: List[str], json_output: bool = True) -> Dict:
        """Ejecuta comando gh y retorna resultado"""
        cmd = ['gh'] + args
        
        if json_output and '--json' not in args:
            # Buscar qué campos están disponibles para este comando
            if args[0] in ['issue', 'pr'] and args[1] == 'list':
                cmd.extend(['--json', 'number,title,state,createdAt,labels'])
            elif args[0] in ['issue', 'pr'] and args[1] == 'create':
                # create no soporta --json directamente
                json_output = False
                
        self.logger.debug(f"Ejecutando: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            self.logger.error(f"Error ejecutando gh: {result.stderr}")
            raise RuntimeError(f"gh command failed: {result.stderr}")
            
        if json_output and result.stdout:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {'output': result.stdout}
        else:
            return {'output': result.stdout, 'stderr': result.stderr}
            
    def create_issue(self, title: str, body: str, labels: List[str] = None) -> int:
        """Crea un issue y retorna su número"""
        cmd = ['issue', 'create', '--repo', f"{self.config.owner}/{self.config.repo}",
               '--title', title, '--body', body]
        
        if labels:
            cmd.extend(['--label', ','.join(labels)])
            
        result = self.run_gh_command(cmd, json_output=False)
        
        # Extraer número del issue del output
        output = result['output']
        if 'github.com' in output:
            # El output incluye la URL del issue
            issue_number = int(output.split('/')[-1].strip())
            self.logger.info(f"Issue creado: #{issue_number}")
            return issue_number
        else:
            raise RuntimeError(f"No se pudo extraer número de issue: {output}")
            
    def create_pr(self, branch: str, title: str, body: str, draft: bool = True) -> int:
        """Crea un Pull Request"""
        cmd = ['pr', 'create', '--repo', f"{self.config.owner}/{self.config.repo}",
               '--base', self.config.default_branch, '--head', branch,
               '--title', title, '--body', body]
        
        if draft:
            cmd.append('--draft')
            
        result = self.run_gh_command(cmd, json_output=False)
        
        # Extraer número del PR
        output = result['output']
        if 'github.com' in output:
            pr_number = int(output.split('/')[-1].strip())
            self.logger.info(f"PR creado: #{pr_number}")
            return pr_number
        else:
            raise RuntimeError(f"No se pudo extraer número de PR: {output}")
            
    def list_issues(self, state: str = "open", labels: List[str] = None) -> List[Dict]:
        """Lista issues del repositorio"""
        cmd = ['issue', 'list', '--repo', f"{self.config.owner}/{self.config.repo}",
               '--state', state]
        
        if labels:
            cmd.extend(['--label', ','.join(labels)])
            
        return self.run_gh_command(cmd)
        
    def add_to_project(self, item_number: int, item_type: str = "issue"):
        """Agrega un issue o PR a un proyecto"""
        if not self.config.project_number:
            self.logger.warning("No hay proyecto configurado")
            return
            
        cmd = ['project', 'item-add', str(self.config.project_number),
               '--owner', self.config.owner, '--url',
               f"https://github.com/{self.config.owner}/{self.config.repo}/{item_type}s/{item_number}"]
        
        self.run_gh_command(cmd, json_output=False)
        self.logger.info(f"{item_type} #{item_number} agregado al proyecto")


class BatmanGitHubIntegration:
    """Integración de Batman con GitHub"""
    
    def __init__(self, config_path: str = "~/.batman/github_config.yaml"):
        self.config_path = Path(config_path).expanduser()
        self.config = self.load_config()
        self.gh = GitHubCLI(self.config)
        self.logger = logging.getLogger(__name__)
        
        # Rate limiting
        self.last_operation_time = 0
        self.min_operation_interval = 2  # segundos entre operaciones
        
    def load_config(self) -> GitHubConfig:
        """Carga o crea configuración"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                data = yaml.safe_load(f)
                return GitHubConfig(**data)
        else:
            # Configuración por defecto
            default_config = GitHubConfig(
                owner="lauta",  # Cambiar según necesidad
                repo="glados",
                default_branch="main"
            )
            
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump({
                    'owner': default_config.owner,
                    'repo': default_config.repo,
                    'default_branch': default_config.default_branch,
                    'project_number': None
                }, f)
                
            return default_config
            
    def _rate_limit(self):
        """Implementa rate limiting básico"""
        current_time = time.time()
        elapsed = current_time - self.last_operation_time
        
        if elapsed < self.min_operation_interval:
            sleep_time = self.min_operation_interval - elapsed
            self.logger.debug(f"Rate limiting: esperando {sleep_time:.1f}s")
            time.sleep(sleep_time)
            
        self.last_operation_time = time.time()
        
    def create_discovery_issue(self, discovery: Dict) -> Optional[int]:
        """Crea un issue para un descubrimiento de Batman"""
        self._rate_limit()
        
        issue_type = IssueType(discovery.get('type', 'discovery'))
        severity = IssueSeverity(discovery.get('severity', 'medium'))
        
        # Generar título y cuerpo
        title = f"🦇 Batman: {discovery['title']}"
        
        body = f"""## Descubrimiento Automático

**Tipo**: {issue_type.value}
**Severidad**: {severity.value}
**Detectado**: {datetime.now().isoformat()}

### Descripción
{discovery.get('description', 'No description provided')}

### Detalles
```
{discovery.get('details', 'No details available')}
```

### Recomendaciones
{discovery.get('recommendations', '- Revisar manualmente\n- Tomar acción apropiada')}

### Contexto
- **Sistema**: {os.uname().nodename}
- **Usuario**: {os.getenv('USER')}
- **Directorio**: {discovery.get('location', 'Unknown')}

---
*Este issue fue creado automáticamente por Batman durante análisis nocturno*
"""
        
        # Seleccionar labels
        labels = self.config.labels.get(issue_type.value, ['batman-found'])
        if severity in [IssueSeverity.CRITICAL, IssueSeverity.HIGH]:
            labels.append('urgent')
            
        try:
            issue_number = self.gh.create_issue(title, body, labels)
            
            # Agregar a proyecto si está configurado
            if self.config.project_number:
                self.gh.add_to_project(issue_number, "issue")
                
            return issue_number
            
        except Exception as e:
            self.logger.error(f"Error creando issue: {e}")
            return None
            
    def create_optimization_pr(self, branch_name: str, title: str, 
                             files_changed: List[str], 
                             description: str = "") -> Optional[int]:
        """Crea un PR con optimizaciones propuestas"""
        self._rate_limit()
        
        # Primero, crear y cambiar a la rama
        try:
            # Crear rama
            subprocess.run(['git', 'checkout', '-b', branch_name], check=True)
            
            # Agregar archivos
            for file in files_changed:
                subprocess.run(['git', 'add', file], check=True)
                
            # Commit
            commit_msg = f"🦇 Batman: {title}\n\nAutomated optimization by Batman"
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            
            # Push
            subprocess.run(['git', 'push', '-u', 'origin', branch_name], check=True)
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error preparando branch: {e}")
            return None
            
        # Crear PR
        pr_body = f"""## Optimización Automática

### Descripción
{description or 'Optimizaciones automáticas detectadas y aplicadas por Batman.'}

### Archivos Modificados
{chr(10).join(f'- `{f}`' for f in files_changed)}

### Tipo de Cambios
- [ ] 🐛 Bug fix
- [x] ✨ Enhancement
- [ ] 🔧 Configuration change
- [x] 🤖 Automated optimization

### Testing
- [x] Los cambios han sido verificados localmente
- [ ] Requiere revisión manual antes de merge

### Notas
Este PR fue creado automáticamente por Batman durante análisis nocturno.
Por favor revisa los cambios antes de hacer merge.

---
*Generated by Batman at {datetime.now().isoformat()}*
"""
        
        try:
            pr_number = self.gh.create_pr(
                branch_name, 
                f"🦇 {title}", 
                pr_body,
                draft=True
            )
            
            # Agregar a proyecto
            if self.config.project_number:
                self.gh.add_to_project(pr_number, "pr")
                
            return pr_number
            
        except Exception as e:
            self.logger.error(f"Error creando PR: {e}")
            return None
            
    def create_nightly_report_issue(self, report: Dict) -> Optional[int]:
        """Crea un issue con el reporte nocturno"""
        self._rate_limit()
        
        title = f"🦇 Reporte Nocturno - {datetime.now():%Y-%m-%d}"
        
        # Generar resumen
        total_tasks = report.get('total_tasks', 0)
        successful = report.get('successful_tasks', 0)
        failed = report.get('failed_tasks', 0)
        
        body = f"""## Reporte de Actividad Nocturna

### Resumen Ejecutivo
- **Total de tareas**: {total_tasks}
- **Exitosas**: {successful} ✅
- **Fallidas**: {failed} ❌
- **Tasa de éxito**: {(successful/total_tasks*100) if total_tasks > 0 else 0:.1f}%

### Descubrimientos Principales
{self._format_discoveries(report.get('discoveries', []))}

### Optimizaciones Aplicadas
{self._format_optimizations(report.get('optimizations', []))}

### Alertas
{self._format_alerts(report.get('alerts', []))}

### Métricas del Sistema
```
{report.get('system_metrics', 'No metrics available')}
```

### Próximas Acciones Recomendadas
{self._format_recommendations(report.get('recommendations', []))}

---
*Reporte generado automáticamente por Batman*
*Tiempo de ejecución: {report.get('execution_time', 'Unknown')}*
"""
        
        labels = ['batman-report', 'nightly']
        
        # Si hay alertas críticas, marcar como urgente
        if any(alert.get('severity') == 'critical' for alert in report.get('alerts', [])):
            labels.append('urgent')
            
        try:
            return self.gh.create_issue(title, body, labels)
        except Exception as e:
            self.logger.error(f"Error creando reporte: {e}")
            return None
            
    def _format_discoveries(self, discoveries: List[Dict]) -> str:
        """Formatea lista de descubrimientos"""
        if not discoveries:
            return "*No se encontraron descubrimientos significativos*"
            
        formatted = []
        for d in discoveries[:5]:  # Limitar a 5 principales
            emoji = "🔍" if d.get('type') == 'analysis' else "⚠️"
            formatted.append(f"{emoji} **{d.get('title', 'Sin título')}**: {d.get('summary', '')}")
            
        return "\n".join(formatted)
        
    def _format_optimizations(self, optimizations: List[Dict]) -> str:
        """Formatea lista de optimizaciones"""
        if not optimizations:
            return "*No se aplicaron optimizaciones*"
            
        formatted = []
        for opt in optimizations:
            status = "✅" if opt.get('applied') else "⏸️"
            formatted.append(f"{status} {opt.get('description', 'Sin descripción')}")
            
        return "\n".join(formatted)
        
    def _format_alerts(self, alerts: List[Dict]) -> str:
        """Formatea alertas"""
        if not alerts:
            return "*No hay alertas*"
            
        formatted = []
        severity_emoji = {
            'critical': '🚨',
            'high': '⚠️',
            'medium': '📢',
            'low': 'ℹ️'
        }
        
        for alert in alerts:
            emoji = severity_emoji.get(alert.get('severity', 'medium'), '📢')
            formatted.append(f"{emoji} **{alert.get('title', 'Alerta')}**: {alert.get('message', '')}")
            
        return "\n".join(formatted)
        
    def _format_recommendations(self, recommendations: List[str]) -> str:
        """Formatea recomendaciones"""
        if not recommendations:
            return "*No hay recomendaciones específicas*"
            
        return "\n".join(f"- [ ] {rec}" for rec in recommendations)
        
    def check_existing_issues(self, title_pattern: str) -> List[Dict]:
        """Busca issues existentes por patrón de título"""
        try:
            all_issues = self.gh.list_issues(state="all", labels=["batman-found"])
            
            matching = []
            for issue in all_issues:
                if title_pattern.lower() in issue.get('title', '').lower():
                    matching.append(issue)
                    
            return matching
            
        except Exception as e:
            self.logger.error(f"Error buscando issues: {e}")
            return []
            
    def update_issue_comment(self, issue_number: int, comment: str):
        """Agrega un comentario a un issue existente"""
        self._rate_limit()
        
        try:
            cmd = ['issue', 'comment', str(issue_number), 
                   '--repo', f"{self.config.owner}/{self.config.repo}",
                   '--body', comment]
            
            self.gh.run_gh_command(cmd, json_output=False)
            self.logger.info(f"Comentario agregado a issue #{issue_number}")
            
        except Exception as e:
            self.logger.error(f"Error agregando comentario: {e}")


# Funciones de utilidad para integración con Batman
def create_security_alert(integration: BatmanGitHubIntegration, 
                         title: str, details: str, 
                         severity: str = "high") -> Optional[int]:
    """Crea una alerta de seguridad rápidamente"""
    discovery = {
        'type': 'security',
        'severity': severity,
        'title': title,
        'description': 'Alerta de seguridad detectada automáticamente',
        'details': details,
        'recommendations': '- Revisar inmediatamente\n- Aplicar parches necesarios\n- Verificar logs'
    }
    
    return integration.create_discovery_issue(discovery)


def create_performance_report(integration: BatmanGitHubIntegration,
                            metrics: Dict) -> Optional[int]:
    """Crea un reporte de rendimiento"""
    discovery = {
        'type': 'performance',
        'severity': 'medium',
        'title': f"Análisis de Rendimiento - {datetime.now():%Y-%m-%d}",
        'description': 'Métricas de rendimiento del sistema',
        'details': json.dumps(metrics, indent=2),
        'recommendations': '- Optimizar procesos pesados\n- Considerar escalamiento'
    }
    
    return integration.create_discovery_issue(discovery)


# Ejemplo de uso
if __name__ == "__main__":
    import sys
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Crear integración
    try:
        batman_gh = BatmanGitHubIntegration()
        
        if len(sys.argv) > 1 and sys.argv[1] == "test":
            # Modo test - crear issue de prueba
            test_discovery = {
                'type': 'discovery',
                'severity': 'low',
                'title': 'Test de Integración GitHub',
                'description': 'Este es un issue de prueba para verificar la integración',
                'details': 'Timestamp: ' + datetime.now().isoformat(),
                'location': os.getcwd()
            }
            
            issue_num = batman_gh.create_discovery_issue(test_discovery)
            if issue_num:
                print(f"✅ Issue de prueba creado: #{issue_num}")
            else:
                print("❌ Error creando issue de prueba")
                
        else:
            print("Batman GitHub Integration configurada correctamente")
            print(f"Repositorio: {batman_gh.config.owner}/{batman_gh.config.repo}")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)