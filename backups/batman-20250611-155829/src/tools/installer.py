"""
Instalador de herramientas sin sudo.
Descarga e instala binarios en ~/.local/bin
"""

import os
import sys
import shutil
import urllib.request
import tarfile
import zipfile
from pathlib import Path
from typing import Dict, Any, Optional


class ToolInstaller:
    """Instala herramientas del Arsenal sin necesidad de sudo."""
    
    # Definición de herramientas y sus URLs de descarga
    TOOLS = {
        'rg': {
            'name': 'ripgrep',
            'version': '14.1.0',
            'url': 'https://github.com/BurntSushi/ripgrep/releases/download/{version}/ripgrep-{version}-x86_64-unknown-linux-musl.tar.gz',
            'binary': 'rg',
            'extract_type': 'tar',
            'description': 'Búsqueda de texto ultrarrápida'
        },
        'fd': {
            'name': 'fd',
            'version': 'v9.0.0',
            'url': 'https://github.com/sharkdp/fd/releases/download/{version}/fd-{version}-x86_64-unknown-linux-musl.tar.gz',
            'binary': 'fd',
            'extract_type': 'tar',
            'description': 'Búsqueda moderna de archivos'
        },
        'bat': {
            'name': 'bat',
            'version': 'v0.24.0',
            'url': 'https://github.com/sharkdp/bat/releases/download/{version}/bat-{version}-x86_64-unknown-linux-musl.tar.gz',
            'binary': 'bat',
            'extract_type': 'tar',
            'description': 'Cat con sintaxis highlighting'
        },
        'delta': {
            'name': 'delta',
            'version': '0.17.0',
            'url': 'https://github.com/dandavison/delta/releases/download/{version}/delta-{version}-x86_64-unknown-linux-musl.tar.gz',
            'binary': 'delta',
            'extract_type': 'tar',
            'description': 'Diffs visuales con highlighting'
        },
        'sd': {
            'name': 'sd',
            'version': 'v1.0.0',
            'url': 'https://github.com/chmln/sd/releases/download/{version}/sd-{version}-x86_64-unknown-linux-musl.tar.gz',
            'binary': 'sd',
            'extract_type': 'tar',
            'description': 'Reemplazo de texto moderno (mejor que sed)'
        },
        'procs': {
            'name': 'procs',
            'version': 'v0.14.4',
            'url': 'https://github.com/dalance/procs/releases/download/{version}/procs-{version}-x86_64-linux.zip',
            'binary': 'procs',
            'extract_type': 'zip',
            'description': 'Visualizador de procesos moderno'
        }
    }
    
    def __init__(self):
        self.local_bin = Path.home() / '.local' / 'bin'
        self.temp_dir = Path('/tmp/batman-tools')
        
    def ensure_local_bin(self) -> bool:
        """Asegura que ~/.local/bin existe y está en PATH."""
        # Crear directorio si no existe
        self.local_bin.mkdir(parents=True, exist_ok=True)
        
        # Verificar si está en PATH
        paths = os.environ.get('PATH', '').split(':')
        if str(self.local_bin) not in paths:
            print(f"⚠️  {self.local_bin} no está en tu PATH")
            print("   Añádelo con: echo 'export PATH=\"$HOME/.local/bin:$PATH\"' >> ~/.bashrc")
            print("   Luego: source ~/.bashrc")
            return False
        return True
    
    def is_installed(self, tool_key: str) -> bool:
        """Verifica si una herramienta está instalada."""
        tool = self.TOOLS.get(tool_key)
        if not tool:
            return False
        return shutil.which(tool['binary']) is not None
    
    def download_file(self, url: str, dest: Path) -> bool:
        """Descarga un archivo con progreso."""
        try:
            print(f"  📥 Descargando de {url}")
            
            def download_progress(block_num, block_size, total_size):
                downloaded = block_num * block_size
                percent = min(downloaded * 100 / total_size, 100)
                sys.stdout.write(f'\r  Progreso: {percent:.1f}%')
                sys.stdout.flush()
            
            urllib.request.urlretrieve(url, dest, download_progress)
            print()  # Nueva línea después del progreso
            return True
        except Exception as e:
            print(f"\n  ❌ Error al descargar: {e}")
            return False
    
    def extract_archive(self, archive_path: Path, extract_type: str) -> Optional[Path]:
        """Extrae un archivo tar.gz o zip."""
        extract_dir = archive_path.parent / 'extracted'
        extract_dir.mkdir(exist_ok=True)
        
        try:
            if extract_type == 'tar':
                with tarfile.open(archive_path, 'r:gz') as tar:
                    tar.extractall(extract_dir)
            elif extract_type == 'zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_file:
                    zip_file.extractall(extract_dir)
            return extract_dir
        except Exception as e:
            print(f"  ❌ Error al extraer: {e}")
            return None
    
    def find_binary(self, extract_dir: Path, binary_name: str) -> Optional[Path]:
        """Busca el binario en el directorio extraído."""
        # Buscar en el directorio principal
        binary_path = extract_dir / binary_name
        if binary_path.exists():
            return binary_path
        
        # Buscar recursivamente
        for path in extract_dir.rglob(binary_name):
            if path.is_file():
                return path
        
        return None
    
    def install_tool(self, tool_key: str) -> bool:
        """Instala una herramienta específica."""
        tool = self.TOOLS.get(tool_key)
        if not tool:
            print(f"❌ Herramienta desconocida: {tool_key}")
            return False
        
        if self.is_installed(tool_key):
            print(f"✅ {tool['name']} ya está instalado")
            return True
        
        print(f"\n🔧 Instalando {tool['name']} ({tool['description']})")
        
        # Crear directorio temporal
        self.temp_dir.mkdir(exist_ok=True)
        
        # Construir URL con versión
        url = tool['url'].format(version=tool['version'])
        archive_name = url.split('/')[-1]
        archive_path = self.temp_dir / archive_name
        
        # Descargar
        if not self.download_file(url, archive_path):
            return False
        
        # Extraer
        extract_dir = self.extract_archive(archive_path, tool['extract_type'])
        if not extract_dir:
            return False
        
        # Buscar binario
        binary_path = self.find_binary(extract_dir, tool['binary'])
        if not binary_path:
            print(f"  ❌ No se encontró el binario {tool['binary']}")
            return False
        
        # Copiar a ~/.local/bin
        dest_path = self.local_bin / tool['binary']
        try:
            shutil.copy2(binary_path, dest_path)
            dest_path.chmod(0o755)  # Hacer ejecutable
            print(f"  ✅ {tool['name']} instalado en {dest_path}")
            return True
        except Exception as e:
            print(f"  ❌ Error al instalar: {e}")
            return False
        finally:
            # Limpiar archivos temporales
            if archive_path.exists():
                archive_path.unlink()
            if extract_dir and extract_dir.exists():
                shutil.rmtree(extract_dir)
    
    def install_all(self, force: bool = False) -> Dict[str, bool]:
        """Instala todas las herramientas disponibles."""
        print("🦇 Batman Tool Installer - Instalación sin sudo")
        print("=" * 50)
        
        # Verificar ~/.local/bin
        self.ensure_local_bin()
        
        results = {}
        for tool_key in self.TOOLS:
            if not force and self.is_installed(tool_key):
                results[tool_key] = True
                continue
            
            results[tool_key] = self.install_tool(tool_key)
        
        # Limpiar directorio temporal
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        
        # Resumen
        print("\n📊 Resumen de instalación:")
        print("-" * 30)
        for tool_key, success in results.items():
            tool = self.TOOLS[tool_key]
            status = "✅ Instalado" if success else "❌ Falló"
            print(f"{tool['name']:10} {status}")
        
        # Verificar herramientas adicionales que requieren otros métodos
        print("\n📝 Herramientas adicionales:")
        print("-" * 30)
        
        additional_tools = {
            'gh': ('GitHub CLI', 'https://cli.github.com/'),
            'jq': ('JSON processor', 'https://stedolan.github.io/jq/'),
            'exa': ('Modern ls', 'cargo install exa'),
            'zoxide': ('Smart cd', 'cargo install zoxide'),
        }
        
        for cmd, (name, install_info) in additional_tools.items():
            if shutil.which(cmd):
                print(f"{name:15} ✅ Instalado")
            else:
                print(f"{name:15} ⚠️  No instalado - Ver: {install_info}")
        
        return results
    
    def check_status(self) -> None:
        """Muestra el estado de todas las herramientas."""
        print("🔍 Estado de herramientas del Arsenal:")
        print("=" * 40)
        
        for tool_key, tool in self.TOOLS.items():
            installed = self.is_installed(tool_key)
            status = "✅" if installed else "❌"
            print(f"{status} {tool['name']:12} - {tool['description']}")
        
        print("\nHerramientas adicionales:")
        print("-" * 40)
        
        additional = ['gh', 'jq', 'exa', 'zoxide', 'tldr', 'ncdu', 'cloc', 'htop']
        for cmd in additional:
            installed = shutil.which(cmd) is not None
            status = "✅" if installed else "❌"
            print(f"{status} {cmd}")


def main():
    """Función principal para uso directo del script."""
    installer = ToolInstaller()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--check':
        installer.check_status()
    else:
        installer.install_all()


if __name__ == '__main__':
    main()