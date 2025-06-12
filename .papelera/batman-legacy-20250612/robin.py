#!/usr/bin/env python3
"""
Robin - Linux Task Executor
El fiel compañero de Batman para ejecutar tareas del sistema.
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from logger import get_logger
from task_parser import TaskParser
from task_executor import TaskExecutor

logger = get_logger("robin")


class Robin:
    """Robin maneja todas las tareas de sistema Linux."""
    
    def __init__(self):
        """Initialize Robin."""
        self.parser = TaskParser()
        self.executor = None
        logger.info("🐦 Robin initialized - Ready for system tasks!")
    
    def execute_system_tasks(self, task_files: list, max_workers: int = 4) -> dict:
        """Execute system maintenance tasks.
        
        Args:
            task_files: List of task files to execute
            max_workers: Maximum concurrent tasks
            
        Returns:
            Dictionary with execution results
        """
        logger.info(f"Robin executing {len(task_files)} task files")
        
        all_tasks = []
        for file_path in task_files:
            try:
                tasks = self.parser.parse_file(file_path)
                # Filter only system/maintenance tasks
                system_tasks = [t for t in tasks if any(tag in ['system', 'maintenance', 'backup', 'cleanup'] 
                                                       for tag in t.tags)]
                all_tasks.extend(system_tasks)
            except Exception as e:
                logger.error(f"Error loading tasks from {file_path}: {e}")
        
        if not all_tasks:
            logger.warning("No system tasks found")
            return {}
        
        logger.info(f"Found {len(all_tasks)} system tasks to execute")
        
        # Execute tasks
        self.executor = TaskExecutor(max_workers=max_workers)
        
        try:
            self.executor.execute_tasks_async(all_tasks)
            results = self.executor.wait_for_completion()
            
            # Log summary
            success = sum(1 for r in results.values() if r.status.value == "success")
            logger.info(f"Robin completed: {success}/{len(results)} tasks successful")
            
            return results
            
        finally:
            if self.executor:
                self.executor.shutdown()
    
    def clean_logs(self, days: int = 30) -> dict:
        """Clean old log files.
        
        Args:
            days: Delete logs older than this many days
            
        Returns:
            Cleanup statistics
        """
        logger.info(f"Cleaning logs older than {days} days")
        
        stats = {
            "files_deleted": 0,
            "space_freed": 0,
            "errors": []
        }
        
        # Clean logs directory
        logs_dir = Path("logs")
        if logs_dir.exists():
            import os
            import time
            
            cutoff_time = time.time() - (days * 24 * 60 * 60)
            
            for log_file in logs_dir.glob("**/*.log*"):
                try:
                    if os.path.getmtime(log_file) < cutoff_time:
                        size = log_file.stat().st_size
                        log_file.unlink()
                        stats["files_deleted"] += 1
                        stats["space_freed"] += size
                        logger.debug(f"Deleted: {log_file}")
                except Exception as e:
                    stats["errors"].append(f"{log_file}: {e}")
        
        logger.info(f"Cleaned {stats['files_deleted']} files, freed {stats['space_freed']/1024/1024:.2f} MB")
        return stats
    
    def system_health_check(self) -> dict:
        """Perform system health check.
        
        Returns:
            System health status
        """
        logger.info("Performing system health check")
        
        import psutil
        import subprocess
        
        health = {
            "disk_usage": {},
            "memory": {},
            "cpu": {},
            "services": {},
            "network": {}
        }
        
        # Disk usage
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                health["disk_usage"][partition.mountpoint] = {
                    "total_gb": usage.total / (1024**3),
                    "used_gb": usage.used / (1024**3),
                    "free_gb": usage.free / (1024**3),
                    "percent": usage.percent
                }
            except:
                pass
        
        # Memory
        mem = psutil.virtual_memory()
        health["memory"] = {
            "total_gb": mem.total / (1024**3),
            "available_gb": mem.available / (1024**3),
            "percent": mem.percent
        }
        
        # CPU
        health["cpu"] = {
            "percent": psutil.cpu_percent(interval=1),
            "cores": psutil.cpu_count()
        }
        
        # Check if we're in WSL
        if Path("/proc/sys/fs/binfmt_misc/WSLInterop").exists():
            health["environment"] = "WSL2"
        else:
            health["environment"] = "Native Linux"
        
        return health
    
    def create_backup(self, source: str, destination: str, compress: bool = True) -> dict:
        """Create backup of directory or file.
        
        Args:
            source: Source path
            destination: Destination path
            compress: Whether to compress the backup
            
        Returns:
            Backup result
        """
        from datetime import datetime
        
        logger.info(f"Creating backup: {source} -> {destination}")
        
        source_path = Path(source)
        if not source_path.exists():
            raise FileNotFoundError(f"Source not found: {source}")
        
        # Add timestamp to destination
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest_path = Path(destination)
        
        if compress:
            backup_file = dest_path / f"{source_path.name}_{timestamp}.tar.gz"
            cmd = f"tar -czf {backup_file} -C {source_path.parent} {source_path.name}"
        else:
            backup_file = dest_path / f"{source_path.name}_{timestamp}"
            cmd = f"cp -r {source} {backup_file}"
        
        import subprocess
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            size = backup_file.stat().st_size if backup_file.exists() else 0
            logger.info(f"Backup created: {backup_file} ({size/1024/1024:.2f} MB)")
            return {
                "success": True,
                "backup_file": str(backup_file),
                "size_mb": size / 1024 / 1024
            }
        else:
            logger.error(f"Backup failed: {result.stderr}")
            return {
                "success": False,
                "error": result.stderr
            }


def main():
    """Main entry point for Robin."""
    parser = argparse.ArgumentParser(
        description="Robin - Linux Task Executor",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Execute tasks
    exec_parser = subparsers.add_parser('execute', help='Execute system tasks')
    exec_parser.add_argument('files', nargs='+', help='Task files')
    exec_parser.add_argument('--workers', '-w', type=int, default=4, help='Max workers')
    
    # Clean logs
    clean_parser = subparsers.add_parser('clean-logs', help='Clean old logs')
    clean_parser.add_argument('--days', '-d', type=int, default=30, help='Days to keep')
    
    # Health check
    health_parser = subparsers.add_parser('health', help='System health check')
    
    # Backup
    backup_parser = subparsers.add_parser('backup', help='Create backup')
    backup_parser.add_argument('source', help='Source path')
    backup_parser.add_argument('destination', help='Destination path')
    backup_parser.add_argument('--no-compress', action='store_true', help='Skip compression')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    robin = Robin()
    
    try:
        if args.command == 'execute':
            results = robin.execute_system_tasks(args.files, args.workers)
            # Print summary
            total = len(results)
            success = sum(1 for r in results.values() if r.status.value == "success")
            print(f"\n🐦 Robin completed: {success}/{total} tasks successful")
            
        elif args.command == 'clean-logs':
            stats = robin.clean_logs(args.days)
            print(f"\n🧹 Cleaned {stats['files_deleted']} files")
            print(f"💾 Freed {stats['space_freed']/1024/1024:.2f} MB")
            
        elif args.command == 'health':
            health = robin.system_health_check()
            print("\n🏥 System Health Check:")
            print(f"Environment: {health['environment']}")
            print(f"CPU Usage: {health['cpu']['percent']}%")
            print(f"Memory Usage: {health['memory']['percent']}%")
            for mount, usage in health['disk_usage'].items():
                print(f"Disk {mount}: {usage['percent']}% used")
                
        elif args.command == 'backup':
            result = robin.create_backup(
                args.source, 
                args.destination, 
                compress=not args.no_compress
            )
            if result['success']:
                print(f"\n✅ Backup created: {result['backup_file']}")
                print(f"📦 Size: {result['size_mb']:.2f} MB")
            else:
                print(f"\n❌ Backup failed: {result['error']}")
                
    except Exception as e:
        logger.error(f"Robin error: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()