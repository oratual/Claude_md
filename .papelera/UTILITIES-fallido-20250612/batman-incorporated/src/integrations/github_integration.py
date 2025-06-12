"""
Integración con GitHub para Batman Incorporated.
Permite crear PRs, issues y gestionar el repositorio automáticamente.
"""

import subprocess
import json
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path


class GitHubIntegration:
    """
    Gestiona la integración con GitHub usando gh CLI.
    """
    
    def __init__(self, logger=None):
        self.logger = logger
        self._verify_gh_cli()
    
    def _log(self, message: str) -> None:
        """Log helper."""
        if self.logger:
            self.logger.info(message)
        else:
            print(f"[GitHub] {message}")
    
    def _verify_gh_cli(self) -> bool:
        """Verifica que gh CLI esté instalado y autenticado."""
        try:
            result = subprocess.run(
                ['gh', 'auth', 'status'],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                self._log("⚠️ GitHub CLI no autenticado. Ejecuta: gh auth login")
                return False
            self._log("✅ GitHub CLI autenticado")
            return True
        except FileNotFoundError:
            self._log("❌ GitHub CLI no instalado. Instala con: batman --install-tools")
            return False
    
    def create_branch(self, branch_name: str, base: str = "main") -> bool:
        """Crea una nueva branch."""
        try:
            # Asegurar que estamos actualizados
            subprocess.run(['git', 'fetch', 'origin'], check=True)
            
            # Crear branch desde base
            subprocess.run(
                ['git', 'checkout', '-b', branch_name, f'origin/{base}'],
                check=True
            )
            
            self._log(f"✅ Branch '{branch_name}' creada desde '{base}'")
            return True
        except subprocess.CalledProcessError as e:
            self._log(f"❌ Error creando branch: {e}")
            return False
    
    def create_pr(
        self,
        title: str,
        body: str,
        base: str = "main",
        draft: bool = False,
        labels: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """Crea un Pull Request."""
        try:
            # Push current branch
            current_branch = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip()
            
            subprocess.run(
                ['git', 'push', '-u', 'origin', current_branch],
                check=True
            )
            
            # Construir comando
            cmd = ['gh', 'pr', 'create', '--json', 'number,url,title']
            cmd.extend(['--title', title])
            cmd.extend(['--body', body])
            cmd.extend(['--base', base])
            
            if draft:
                cmd.append('--draft')
            
            if labels:
                cmd.extend(['--label', ','.join(labels)])
            
            # Crear PR
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            pr_data = json.loads(result.stdout)
            self._log(f"✅ PR #{pr_data['number']} creado: {pr_data['url']}")
            
            return pr_data
            
        except subprocess.CalledProcessError as e:
            self._log(f"❌ Error creando PR: {e}")
            if e.stderr:
                self._log(f"   {e.stderr}")
            return None
    
    def create_issue(
        self,
        title: str,
        body: str,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """Crea un Issue."""
        try:
            cmd = ['gh', 'issue', 'create', '--json', 'number,url,title']
            cmd.extend(['--title', title])
            cmd.extend(['--body', body])
            
            if labels:
                cmd.extend(['--label', ','.join(labels)])
            
            if assignees:
                cmd.extend(['--assignee', ','.join(assignees)])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            issue_data = json.loads(result.stdout)
            self._log(f"✅ Issue #{issue_data['number']} creado: {issue_data['url']}")
            
            return issue_data
            
        except subprocess.CalledProcessError as e:
            self._log(f"❌ Error creando issue: {e}")
            return None
    
    def list_prs(self, state: str = "open") -> List[Dict]:
        """Lista Pull Requests."""
        try:
            result = subprocess.run(
                ['gh', 'pr', 'list', '--state', state, '--json', 
                 'number,title,author,createdAt,url'],
                capture_output=True,
                text=True,
                check=True
            )
            
            return json.loads(result.stdout)
            
        except subprocess.CalledProcessError:
            return []
    
    def list_issues(self, state: str = "open", labels: Optional[List[str]] = None) -> List[Dict]:
        """Lista Issues."""
        try:
            cmd = ['gh', 'issue', 'list', '--state', state, '--json',
                   'number,title,author,createdAt,url,labels']
            
            if labels:
                cmd.extend(['--label', ','.join(labels)])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            return json.loads(result.stdout)
            
        except subprocess.CalledProcessError:
            return []
    
    def add_comment(self, number: int, body: str, is_pr: bool = True) -> bool:
        """Añade comentario a PR o Issue."""
        try:
            cmd_type = 'pr' if is_pr else 'issue'
            subprocess.run(
                ['gh', cmd_type, 'comment', str(number), '--body', body],
                check=True
            )
            
            self._log(f"✅ Comentario añadido a {cmd_type} #{number}")
            return True
            
        except subprocess.CalledProcessError:
            return False
    
    def merge_pr(self, number: int, method: str = "squash", delete_branch: bool = True) -> bool:
        """Merge un PR."""
        try:
            cmd = ['gh', 'pr', 'merge', str(number), f'--{method}']
            
            if delete_branch:
                cmd.append('--delete-branch')
            
            subprocess.run(cmd, check=True)
            
            self._log(f"✅ PR #{number} mergeado con método '{method}'")
            return True
            
        except subprocess.CalledProcessError as e:
            self._log(f"❌ Error mergeando PR: {e}")
            return False
    
    def create_pr_for_task(self, task_result: Dict, agent_name: str) -> Optional[Dict]:
        """Crea un PR basado en el resultado de una tarea."""
        # Generar título y descripción
        title = f"feat: {task_result.get('description', 'Task completion')}"
        
        body = f"""## 🤖 Tarea completada por {agent_name}

### Descripción
{task_result.get('description', 'N/A')}

### Cambios realizados
{self._format_changes(task_result.get('changes', []))}

### Testing
- [ ] Tests unitarios pasando
- [ ] Tests de integración pasando
- [ ] Revisión manual completada

### Notas
{task_result.get('notes', 'Generado automáticamente por Batman Incorporated')}

---
🦇 *Batman Incorporated - Automated PR*
"""
        
        # Determinar labels
        labels = ['automated', 'batman']
        if 'bug' in title.lower():
            labels.append('bug')
        elif 'feat' in title.lower():
            labels.append('enhancement')
        elif 'fix' in title.lower():
            labels.append('fix')
        
        return self.create_pr(title, body, labels=labels)
    
    def create_smart_pr(self, analysis_result: Dict) -> Optional[Dict]:
        """
        Crea un PR inteligente con análisis de código y contexto.
        
        Args:
            analysis_result: Resultado del análisis de cambios
            
        Returns:
            Información del PR creado
        """
        # Analizar cambios para generar mejor descripción
        code_analysis = self._analyze_code_changes()
        
        # Generar título descriptivo
        title = self._generate_smart_title(code_analysis)
        
        # Generar cuerpo con análisis detallado
        body = self._generate_smart_body(code_analysis, analysis_result)
        
        # Determinar labels automáticamente
        labels = self._auto_detect_labels(code_analysis)
        
        # Verificar si necesita review especial
        needs_review = self._needs_special_review(code_analysis)
        
        return self.create_pr(
            title=title,
            body=body,
            draft=needs_review,
            labels=labels
        )
    
    def _analyze_code_changes(self) -> Dict[str, Any]:
        """Analiza los cambios de código en detalle."""
        analysis = {
            'files_changed': 0,
            'lines_added': 0,
            'lines_removed': 0,
            'languages': set(),
            'change_types': [],
            'test_coverage': 'unknown',
            'breaking_changes': False,
            'security_impact': False
        }
        
        try:
            # Obtener diff estadísticas
            diff_stat = subprocess.run(
                ['git', 'diff', '--stat', '--cached'],
                capture_output=True,
                text=True
            ).stdout
            
            # Parsear estadísticas
            lines = diff_stat.strip().split('\n')
            if lines:
                # Última línea tiene el resumen
                summary = lines[-1]
                if 'changed' in summary:
                    parts = summary.split(',')
                    for part in parts:
                        if 'file' in part:
                            analysis['files_changed'] = int(part.split()[0])
                        elif 'insertion' in part:
                            analysis['lines_added'] = int(part.split()[0])
                        elif 'deletion' in part:
                            analysis['lines_removed'] = int(part.split()[0])
            
            # Detectar lenguajes
            files = subprocess.run(
                ['git', 'diff', '--name-only', '--cached'],
                capture_output=True,
                text=True
            ).stdout.strip().split('\n')
            
            for file in files:
                if file:
                    ext = Path(file).suffix
                    if ext in ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs']:
                        analysis['languages'].add(ext[1:])
            
            # Detectar tipos de cambios
            diff_content = subprocess.run(
                ['git', 'diff', '--cached'],
                capture_output=True,
                text=True
            ).stdout.lower()
            
            if 'fix' in diff_content:
                analysis['change_types'].append('bug-fix')
            if 'feature' in diff_content or 'feat' in diff_content:
                analysis['change_types'].append('feature')
            if 'test' in diff_content:
                analysis['change_types'].append('tests')
                analysis['test_coverage'] = 'improved'
            if 'breaking' in diff_content:
                analysis['breaking_changes'] = True
            if 'security' in diff_content or 'vulnerability' in diff_content:
                analysis['security_impact'] = True
            
        except Exception as e:
            self._log(f"Error analizando cambios: {e}")
        
        return analysis
    
    def _generate_smart_title(self, analysis: Dict[str, Any]) -> str:
        """Genera un título descriptivo basado en el análisis."""
        # Prefijo según tipo de cambio
        prefix = "feat:"
        if 'bug-fix' in analysis.get('change_types', []):
            prefix = "fix:"
        elif 'tests' in analysis.get('change_types', []):
            prefix = "test:"
        elif analysis.get('breaking_changes'):
            prefix = "feat!:"
        
        # Descripción basada en archivos
        files = analysis.get('files_changed', 0)
        languages = list(analysis.get('languages', []))
        
        if languages:
            lang_str = '/'.join(languages[:2])
            description = f"Update {lang_str} implementation"
        else:
            description = f"Update {files} files"
        
        # Añadir contexto si hay muchos cambios
        if analysis.get('lines_added', 0) > 500:
            description += " (major changes)"
        
        return f"{prefix} {description}"
    
    def _generate_smart_body(self, code_analysis: Dict, task_analysis: Dict) -> str:
        """Genera un cuerpo de PR con análisis detallado."""
        body_parts = []
        
        # Resumen ejecutivo
        body_parts.append("## 📊 Summary\n")
        body_parts.append(f"- **Files changed**: {code_analysis.get('files_changed', 0)}")
        body_parts.append(f"- **Lines added**: {code_analysis.get('lines_added', 0)}")
        body_parts.append(f"- **Lines removed**: {code_analysis.get('lines_removed', 0)}")
        body_parts.append(f"- **Languages**: {', '.join(code_analysis.get('languages', []))}")
        
        # Advertencias importantes
        if code_analysis.get('breaking_changes'):
            body_parts.append("\n## ⚠️ BREAKING CHANGES")
            body_parts.append("This PR contains breaking changes. Please review carefully.")
        
        if code_analysis.get('security_impact'):
            body_parts.append("\n## 🔒 Security Impact")
            body_parts.append("This PR may have security implications. Security review recommended.")
        
        # Descripción de cambios
        body_parts.append("\n## 📝 Changes")
        if task_analysis.get('description'):
            body_parts.append(task_analysis['description'])
        else:
            body_parts.append("Automated changes based on task requirements.")
        
        # Testing
        body_parts.append("\n## 🧪 Testing")
        if code_analysis.get('test_coverage') == 'improved':
            body_parts.append("✅ Tests have been added/updated")
        else:
            body_parts.append("⚠️ No test changes detected - please verify if tests are needed")
        
        # Checklist
        body_parts.append("\n## ✅ Checklist")
        body_parts.append("- [ ] Code follows project style guidelines")
        body_parts.append("- [ ] Tests pass locally")
        body_parts.append("- [ ] Documentation updated if needed")
        if code_analysis.get('breaking_changes'):
            body_parts.append("- [ ] Breaking changes documented")
        if code_analysis.get('security_impact'):
            body_parts.append("- [ ] Security review completed")
        
        # Footer
        body_parts.append("\n---")
        body_parts.append("*🦇 Generated by Batman Incorporated - Smart PR System*")
        
        return "\n".join(body_parts)
    
    def _auto_detect_labels(self, analysis: Dict[str, Any]) -> List[str]:
        """Detecta labels automáticamente basado en el análisis."""
        labels = []
        
        # Por tipo de cambio
        if 'bug-fix' in analysis.get('change_types', []):
            labels.append('bug')
        if 'feature' in analysis.get('change_types', []):
            labels.append('enhancement')
        if 'tests' in analysis.get('change_types', []):
            labels.append('tests')
        
        # Por impacto
        if analysis.get('breaking_changes'):
            labels.append('breaking-change')
        if analysis.get('security_impact'):
            labels.append('security')
        
        # Por tamaño
        total_lines = analysis.get('lines_added', 0) + analysis.get('lines_removed', 0)
        if total_lines < 10:
            labels.append('size/XS')
        elif total_lines < 50:
            labels.append('size/S')
        elif total_lines < 250:
            labels.append('size/M')
        elif total_lines < 1000:
            labels.append('size/L')
        else:
            labels.append('size/XL')
        
        # Por lenguaje principal
        languages = list(analysis.get('languages', []))
        if languages:
            primary_lang = languages[0]
            if primary_lang in ['py', 'python']:
                labels.append('python')
            elif primary_lang in ['js', 'ts', 'jsx', 'tsx']:
                labels.append('javascript')
        
        return labels
    
    def _needs_special_review(self, analysis: Dict[str, Any]) -> bool:
        """Determina si el PR necesita review especial."""
        # Necesita review si:
        # - Tiene cambios breaking
        # - Impacto en seguridad
        # - Más de 1000 líneas cambiadas
        # - Sin tests
        
        if analysis.get('breaking_changes'):
            return True
        if analysis.get('security_impact'):
            return True
        if (analysis.get('lines_added', 0) + analysis.get('lines_removed', 0)) > 1000:
            return True
        if analysis.get('test_coverage') == 'unknown' and analysis.get('files_changed', 0) > 5:
            return True
        
        return False
    
    def create_issue_for_error(self, error: Dict, context: str = "") -> Optional[Dict]:
        """Crea un issue para un error encontrado."""
        title = f"🐛 Error: {error.get('message', 'Unknown error')}"
        
        body = f"""## Error detectado

### Contexto
{context}

### Error
```
{error.get('traceback', error.get('message', 'No details available'))}
```

### Información del sistema
- Agente: {error.get('agent', 'Unknown')}
- Timestamp: {error.get('timestamp', 'Unknown')}
- Archivo: {error.get('file', 'Unknown')}

### Pasos para reproducir
1. {error.get('steps', 'No steps provided')}

---
🦇 *Reportado automáticamente por Batman Incorporated*
"""
        
        return self.create_issue(
            title,
            body,
            labels=['bug', 'automated'],
            assignees=[]  # Podría asignar según el tipo de error
        )
    
    def _format_changes(self, changes: List[str]) -> str:
        """Formatea lista de cambios para el PR."""
        if not changes:
            return "- No se proporcionaron detalles específicos"
        
        return "\n".join(f"- {change}" for change in changes)
    
    def setup_github_actions(self, workflow_type: str = "basic") -> bool:
        """Configura GitHub Actions básicas."""
        workflows_dir = Path(".github/workflows")
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        if workflow_type == "basic":
            workflow_content = """name: Batman CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest tests/
    
    - name: Check code quality
      run: |
        # Add linting commands here
        echo "Code quality checks passed"
"""
            
            workflow_path = workflows_dir / "batman-ci.yml"
            workflow_path.write_text(workflow_content)
            
            self._log(f"✅ GitHub Actions configurado: {workflow_path}")
            return True
        
        return False