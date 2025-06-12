#!/usr/bin/env python3
"""
Batman Enhanced UI - Interfaz gráfica web para configuración
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import yaml
import json
from pathlib import Path
from datetime import datetime
import subprocess
from werkzeug.utils import secure_filename
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'batman-enhanced-secret-key'
app.config['UPLOAD_FOLDER'] = Path.home() / '.batman' / 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Crear directorio de uploads si no existe
app.config['UPLOAD_FOLDER'].mkdir(parents=True, exist_ok=True)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rutas de configuración
BATMAN_HOME = Path.home() / '.batman'
CONFIG_PATH = BATMAN_HOME / 'enhanced_config.yaml'
TASKS_PATH = BATMAN_HOME / 'tasks'
RULES_PATH = BATMAN_HOME / 'rules'
TEMPLATES_PATH = BATMAN_HOME / 'templates'

# Asegurar que existen los directorios
for path in [BATMAN_HOME, TASKS_PATH, RULES_PATH, TEMPLATES_PATH]:
    path.mkdir(parents=True, exist_ok=True)

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard principal"""
    # Cargar estadísticas
    stats = get_system_stats()
    recent_reports = get_recent_reports()
    active_tasks = get_active_tasks()
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         reports=recent_reports,
                         tasks=active_tasks)

@app.route('/config')
def config():
    """Página de configuración"""
    # Cargar configuración actual
    config_data = load_config()
    return render_template('config.html', config=config_data)

@app.route('/tasks')
def tasks():
    """Página de gestión de tareas"""
    # Cargar todas las tareas
    all_tasks = load_all_tasks()
    return render_template('tasks.html', tasks=all_tasks)

@app.route('/wizard')
def wizard():
    """Wizard de configuración inicial"""
    return render_template('wizard.html')

@app.route('/reports')
def reports():
    """Página de reportes"""
    reports_list = get_all_reports()
    return render_template('reports.html', reports=reports_list)

# API Endpoints

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """API para obtener/actualizar configuración"""
    if request.method == 'GET':
        return jsonify(load_config())
    
    elif request.method == 'POST':
        config_data = request.json
        save_config(config_data)
        return jsonify({'status': 'success', 'message': 'Configuración guardada'})

@app.route('/api/tasks', methods=['GET', 'POST', 'DELETE'])
def api_tasks():
    """API para gestionar tareas"""
    if request.method == 'GET':
        return jsonify(load_all_tasks())
    
    elif request.method == 'POST':
        task_data = request.json
        task_id = save_task(task_data)
        return jsonify({'status': 'success', 'task_id': task_id})
    
    elif request.method == 'DELETE':
        task_id = request.args.get('id')
        delete_task(task_id)
        return jsonify({'status': 'success'})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """API para subir archivos"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = app.config['UPLOAD_FOLDER'] / filename
        file.save(str(filepath))
        
        # Procesar según tipo
        file_type = request.form.get('type', 'context')
        process_uploaded_file(filepath, file_type)
        
        return jsonify({
            'status': 'success',
            'filename': filename,
            'path': str(filepath)
        })

@app.route('/api/test', methods=['POST'])
def test_config():
    """API para probar configuración"""
    test_type = request.json.get('type', 'all')
    
    # Ejecutar Batman en modo test
    result = run_batman_test(test_type)
    
    return jsonify({
        'status': 'success' if result['success'] else 'error',
        'output': result['output'],
        'errors': result.get('errors', [])
    })

@app.route('/api/run', methods=['POST'])
def run_batman():
    """API para ejecutar Batman"""
    mode = request.json.get('mode', 'test')
    
    if mode == 'test':
        cmd = ['python3', '/home/lauta/glados/batman/batman_enhanced_night.py', '--test']
    else:
        cmd = ['python3', '/home/lauta/glados/batman/batman_enhanced_night.py']
    
    # Ejecutar en background
    subprocess.Popen(cmd)
    
    return jsonify({
        'status': 'success',
        'message': f'Batman iniciado en modo {mode}'
    })

@app.route('/api/stats')
def api_stats():
    """API para obtener estadísticas"""
    return jsonify(get_system_stats())

# Funciones auxiliares

def load_config():
    """Carga la configuración actual"""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f)
    else:
        return get_default_config()

def save_config(config_data):
    """Guarda la configuración"""
    with open(CONFIG_PATH, 'w') as f:
        yaml.dump(config_data, f, default_flow_style=False)

def load_all_tasks():
    """Carga todas las tareas"""
    tasks = []
    for task_file in TASKS_PATH.glob('*.yaml'):
        with open(task_file) as f:
            data = yaml.safe_load(f)
            if 'tasks' in data:
                for task in data['tasks']:
                    task['file'] = task_file.name
                    tasks.append(task)
    return tasks

def save_task(task_data):
    """Guarda una nueva tarea"""
    task_id = task_data.get('id', f"task_{datetime.now():%Y%m%d_%H%M%S}")
    filename = f"{task_id}.yaml"
    
    task_file = TASKS_PATH / filename
    
    # Estructura de tarea
    task_doc = {
        'tasks': [task_data]
    }
    
    with open(task_file, 'w') as f:
        yaml.dump(task_doc, f, default_flow_style=False)
    
    return task_id

def delete_task(task_id):
    """Elimina una tarea"""
    for task_file in TASKS_PATH.glob('*.yaml'):
        with open(task_file) as f:
            data = yaml.safe_load(f)
        
        if 'tasks' in data:
            data['tasks'] = [t for t in data['tasks'] if t.get('id') != task_id]
            
            if data['tasks']:
                with open(task_file, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False)
            else:
                task_file.unlink()

def get_system_stats():
    """Obtiene estadísticas del sistema"""
    stats = {
        'tasks_total': len(load_all_tasks()),
        'tasks_pending': 0,
        'tasks_completed': 0,
        'last_run': None,
        'disk_usage': get_disk_usage(),
        'reports_count': len(list((BATMAN_HOME / 'reports').glob('*.json'))) if (BATMAN_HOME / 'reports').exists() else 0
    }
    
    # Obtener última ejecución
    log_files = list((BATMAN_HOME / 'logs').glob('enhanced_*.log')) if (BATMAN_HOME / 'logs').exists() else []
    if log_files:
        latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
        stats['last_run'] = datetime.fromtimestamp(latest_log.stat().st_mtime).isoformat()
    
    return stats

def get_disk_usage():
    """Obtiene uso de disco"""
    try:
        result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            parts = lines[1].split()
            if len(parts) >= 5:
                return parts[4]  # Porcentaje usado
    except:
        pass
    return "Unknown"

def get_recent_reports(limit=5):
    """Obtiene reportes recientes"""
    reports_dir = BATMAN_HOME / 'reports'
    if not reports_dir.exists():
        return []
    
    reports = []
    report_files = sorted(reports_dir.glob('*.json'), key=lambda f: f.stat().st_mtime, reverse=True)
    
    for report_file in report_files[:limit]:
        with open(report_file) as f:
            data = json.load(f)
            reports.append({
                'filename': report_file.name,
                'timestamp': data.get('timestamp', 'Unknown'),
                'discoveries': len(data.get('discoveries', [])),
                'alerts': len(data.get('alerts', []))
            })
    
    return reports

def get_active_tasks():
    """Obtiene tareas activas"""
    # Por ahora retorna las primeras 5 tareas
    all_tasks = load_all_tasks()
    return all_tasks[:5]

def get_all_reports():
    """Obtiene todos los reportes"""
    reports_dir = BATMAN_HOME / 'reports'
    if not reports_dir.exists():
        return []
    
    reports = []
    for report_file in sorted(reports_dir.glob('*.json'), key=lambda f: f.stat().st_mtime, reverse=True):
        with open(report_file) as f:
            data = json.load(f)
            reports.append({
                'filename': report_file.name,
                'timestamp': data.get('timestamp', 'Unknown'),
                'data': data
            })
    
    return reports

def process_uploaded_file(filepath, file_type):
    """Procesa archivo subido según su tipo"""
    if file_type == 'task':
        # Mover a carpeta de tareas
        dest = TASKS_PATH / filepath.name
        filepath.rename(dest)
    elif file_type == 'template':
        # Mover a templates
        dest = TEMPLATES_PATH / filepath.name
        filepath.rename(dest)
    elif file_type == 'rule':
        # Mover a rules
        dest = RULES_PATH / filepath.name
        filepath.rename(dest)

def run_batman_test(test_type):
    """Ejecuta Batman en modo test"""
    try:
        cmd = ['python3', '/home/lauta/glados/batman/batman_enhanced_night.py', '--test']
        
        if test_type == 'analyze':
            cmd.append('--analyze-only')
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'errors': result.stderr.split('\n') if result.stderr else []
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'output': '',
            'errors': ['Test timeout after 60 seconds']
        }
    except Exception as e:
        return {
            'success': False,
            'output': '',
            'errors': [str(e)]
        }

def get_default_config():
    """Retorna configuración por defecto"""
    return {
        'github_enabled': False,
        'github_repo': '',
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
            'auto_cleanup': False,
            'compress_logs': False,
            'optimize_git': False
        },
        'reporting': {
            'create_github_issues': False,
            'daily_summary': True,
            'alert_threshold': 'high'
        }
    }

if __name__ == '__main__':
    # Crear estructura de carpetas necesarias
    for folder in ['static', 'templates']:
        Path(folder).mkdir(exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)