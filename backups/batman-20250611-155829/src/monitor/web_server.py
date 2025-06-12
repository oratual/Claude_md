#!/usr/bin/env python3
"""
Batman Incorporated Web Monitor Server
Servidor WebSocket y HTTP para la interfaz de monitoreo
"""

import asyncio
import json
import os
import sys
import time
import websockets
from aiohttp import web
from pathlib import Path
import logging
from typing import Set, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('batman-web-server')

# Rutas de archivos
STATUS_FILE = '/tmp/batman_status.json'
MONITOR_LOG = '/tmp/batman_monitor.log'
WEB_DIR = Path(__file__).parent.parent.parent / 'web'

# Clientes WebSocket conectados
connected_clients: Set[websockets.WebSocketServerProtocol] = set()

class StatusFileHandler(FileSystemEventHandler):
    """Observa cambios en el archivo de estado"""
    def __init__(self, broadcast_func):
        self.broadcast_func = broadcast_func
        self.last_modified = 0
        
    def on_modified(self, event):
        if event.src_path == STATUS_FILE:
            # Evitar múltiples eventos para la misma modificación
            current_time = time.time()
            if current_time - self.last_modified > 0.1:
                self.last_modified = current_time
                asyncio.create_task(self.broadcast_func())

async def read_status() -> dict:
    """Lee el estado actual del archivo JSON"""
    try:
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error leyendo estado: {e}")
    
    # Estado por defecto si no hay archivo
    return {
        'agents': {
            'alfred': {'status': 'inactive', 'current_task': '', 'progress': 0},
            'robin': {'status': 'inactive', 'current_task': '', 'progress': 0},
            'oracle': {'status': 'inactive', 'current_task': '', 'progress': 0},
            'batgirl': {'status': 'inactive', 'current_task': '', 'progress': 0},
            'lucius': {'status': 'inactive', 'current_task': '', 'progress': 0}
        },
        'stats': {
            'total_tasks': 0,
            'completed_tasks': 0,
            'active_agents': 0,
            'files_modified': 0,
            'recent_files': []
        },
        'logs': []
    }

async def read_recent_logs(limit: int = 20) -> list:
    """Lee las últimas líneas del log de actividad"""
    logs = []
    try:
        if os.path.exists(MONITOR_LOG):
            with open(MONITOR_LOG, 'r') as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    line = line.strip()
                    if line:
                        try:
                            # Intentar parsear como JSON
                            log_entry = json.loads(line)
                            logs.append(log_entry)
                        except:
                            # Si no es JSON, crear entrada básica
                            logs.append({
                                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                                'agent': 'system',
                                'message': line,
                                'type': 'info'
                            })
    except Exception as e:
        logger.error(f"Error leyendo logs: {e}")
    
    return logs

async def broadcast_status():
    """Envía el estado actualizado a todos los clientes conectados"""
    if not connected_clients:
        return
        
    status = await read_status()
    logs = await read_recent_logs()
    
    # Combinar estado y logs
    if 'logs' not in status:
        status['logs'] = []
    status['logs'].extend(logs)
    
    message = json.dumps({
        'type': 'status_update',
        'data': status,
        'timestamp': time.time()
    })
    
    # Enviar a todos los clientes
    disconnected_clients = set()
    for client in connected_clients:
        try:
            await client.send(message)
        except websockets.exceptions.ConnectionClosed:
            disconnected_clients.add(client)
        except Exception as e:
            logger.error(f"Error enviando a cliente: {e}")
            disconnected_clients.add(client)
    
    # Limpiar clientes desconectados
    for client in disconnected_clients:
        connected_clients.discard(client)

async def websocket_handler(websocket, path):
    """Maneja conexiones WebSocket"""
    logger.info(f"Nueva conexión WebSocket desde {websocket.remote_address}")
    connected_clients.add(websocket)
    
    try:
        # Enviar estado inicial
        await broadcast_status()
        
        # Mantener conexión abierta
        async for message in websocket:
            try:
                data = json.loads(message)
                # Manejar comandos del cliente si es necesario
                if data.get('type') == 'ping':
                    await websocket.send(json.dumps({'type': 'pong'}))
                elif data.get('type') == 'request_update':
                    await broadcast_status()
            except Exception as e:
                logger.error(f"Error procesando mensaje: {e}")
                
    except websockets.exceptions.ConnectionClosed:
        logger.info("Cliente WebSocket desconectado")
    except Exception as e:
        logger.error(f"Error en WebSocket: {e}")
    finally:
        connected_clients.discard(websocket)

async def http_handler(request):
    """Servidor HTTP para archivos estáticos"""
    path = request.match_info.get('path', 'index.html')
    
    # Seguridad: no permitir rutas fuera del directorio web
    if '..' in path:
        return web.Response(text='Forbidden', status=403)
    
    # Si no hay extensión, asumir .html
    if '.' not in path:
        path = f"{path}.html"
    
    file_path = WEB_DIR / path
    
    # Verificar que el archivo existe
    if not file_path.exists() or not file_path.is_file():
        file_path = WEB_DIR / 'index.html'
    
    # Determinar tipo MIME
    mime_types = {
        '.html': 'text/html',
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.json': 'application/json',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.svg': 'image/svg+xml'
    }
    
    ext = file_path.suffix.lower()
    mime_type = mime_types.get(ext, 'text/plain')
    
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        return web.Response(body=content, content_type=mime_type)
    except Exception as e:
        logger.error(f"Error sirviendo archivo {file_path}: {e}")
        return web.Response(text='Internal Server Error', status=500)

async def start_servers():
    """Inicia los servidores HTTP y WebSocket"""
    logger.info("Iniciando Batman Web Monitor Server...")
    
    # Configurar observador de archivos
    event_handler = StatusFileHandler(broadcast_status)
    observer = Observer()
    observer.schedule(event_handler, '/tmp', recursive=False)
    observer.start()
    
    # Servidor HTTP
    app = web.Application()
    app.router.add_get('/', lambda r: http_handler(r))
    app.router.add_get('/{path:.*}', http_handler)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    logger.info("Servidor HTTP iniciado en http://localhost:8080")
    
    # Servidor WebSocket
    ws_server = await websockets.serve(
        websocket_handler, 
        'localhost', 
        8765,
        ping_interval=30,
        ping_timeout=10
    )
    logger.info("Servidor WebSocket iniciado en ws://localhost:8765")
    
    # Broadcast periódico para mantener UI actualizada
    async def periodic_broadcast():
        while True:
            await asyncio.sleep(5)  # Actualizar cada 5 segundos
            await broadcast_status()
    
    try:
        await asyncio.gather(
            ws_server.wait_closed(),
            periodic_broadcast()
        )
    except KeyboardInterrupt:
        logger.info("Deteniendo servidores...")
    finally:
        observer.stop()
        observer.join()

def main():
    """Punto de entrada principal"""
    try:
        asyncio.run(start_servers())
    except KeyboardInterrupt:
        logger.info("Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()