#!/usr/bin/env python3
"""
Batman - Task Automation System
Main CLI interface for the Batman task automation system.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import List, Optional
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from logger import get_logger
from task_parser import TaskParser, Task
from task_executor import TaskExecutor, TaskResult, TaskStatus
from dream_mode import DreamMode
from morning_report import generate_morning_report

logger = get_logger()


class Batman:
    """Main Batman application class."""
    
    def __init__(self):
        """Initialize Batman."""
        self.parser = TaskParser()
        self.executor = None
        
    def run_tasks(self, task_files: List[str], force: bool = False, 
                  max_workers: int = 4, tags: Optional[List[str]] = None) -> None:
        """Run tasks from files.
        
        Args:
            task_files: List of task file paths
            force: Force execution ignoring conditions
            max_workers: Maximum concurrent tasks
            tags: Filter tasks by tags
        """
        all_tasks = []
        
        # Parse all task files
        for file_path in task_files:
            try:
                tasks = self.parser.parse_file(file_path)
                all_tasks.extend(tasks)
                logger.info(f"Loaded {len(tasks)} tasks from {file_path}")
            except Exception as e:
                logger.error(f"Error loading tasks from {file_path}: {e}")
        
        if not all_tasks:
            logger.error("No tasks found to execute")
            return
        
        # Filter by tags if specified
        if tags:
            filtered_tasks = []
            for task in all_tasks:
                if any(tag in task.tags for tag in tags):
                    filtered_tasks.append(task)
            all_tasks = filtered_tasks
            logger.info(f"Filtered to {len(all_tasks)} tasks with tags: {tags}")
        
        # Execute tasks
        self.executor = TaskExecutor(max_workers=max_workers)
        
        def on_task_complete(result: TaskResult):
            """Callback for completed tasks."""
            status_symbol = "✓" if result.status == TaskStatus.SUCCESS else "✗"
            print(f"{status_symbol} {result.task_id}: {result.status.value}")
        
        try:
            print(f"\nExecuting {len(all_tasks)} tasks...")
            self.executor.execute_tasks_async(all_tasks, callback=on_task_complete)
            
            # Wait for completion
            results = self.executor.wait_for_completion()
            
            # Print summary
            self._print_summary(results)
            
        finally:
            if self.executor:
                self.executor.shutdown()
    
    def run_single_task(self, task_string: str, force: bool = False) -> None:
        """Run a single task from command line.
        
        Args:
            task_string: Task definition string
            force: Force execution ignoring conditions
        """
        task = self.parser.parse_string(task_string)
        if not task:
            logger.error("Failed to parse task")
            return
        
        self.executor = TaskExecutor(max_workers=1)
        
        try:
            result = self.executor.execute_task(task, force=force)
            
            print(f"\nTask: {task.name}")
            print(f"Status: {result.status.value}")
            print(f"Duration: {result.duration:.2f}s")
            
            if result.output:
                print(f"\nOutput:\n{result.output}")
            if result.error:
                print(f"\nError:\n{result.error}")
                
        finally:
            if self.executor:
                self.executor.shutdown()
    
    def list_tasks(self, task_files: List[str]) -> None:
        """List all tasks from files.
        
        Args:
            task_files: List of task file paths
        """
        all_tasks = []
        
        for file_path in task_files:
            try:
                tasks = self.parser.parse_file(file_path)
                all_tasks.extend(tasks)
            except Exception as e:
                logger.error(f"Error loading tasks from {file_path}: {e}")
        
        if not all_tasks:
            print("No tasks found")
            return
        
        print(f"\nFound {len(all_tasks)} tasks:\n")
        
        for task in all_tasks:
            print(f"ID: {task.id}")
            print(f"  Name: {task.name}")
            print(f"  Priority: {task.priority.name}")
            print(f"  Frequency: {task.frequency.value}")
            if task.schedule:
                print(f"  Schedule: {task.schedule}")
            if task.tags:
                print(f"  Tags: {', '.join(task.tags)}")
            if task.dependencies:
                print(f"  Dependencies: {', '.join(task.dependencies)}")
            print()
    
    def _print_summary(self, results: dict) -> None:
        """Print execution summary."""
        total = len(results)
        success = sum(1 for r in results.values() if r.status == TaskStatus.SUCCESS)
        failed = sum(1 for r in results.values() if r.status == TaskStatus.FAILED)
        skipped = sum(1 for r in results.values() if r.status == TaskStatus.SKIPPED)
        timeout = sum(1 for r in results.values() if r.status == TaskStatus.TIMEOUT)
        
        print(f"\n{'='*50}")
        print(f"Execution Summary:")
        print(f"  Total:    {total}")
        print(f"  Success:  {success} ✓")
        print(f"  Failed:   {failed} ✗")
        print(f"  Skipped:  {skipped} ⚠")
        print(f"  Timeout:  {timeout} ⏱")
        print(f"{'='*50}")
    
    def night_shift(self, skip_shutdown: bool = False) -> None:
        """Run all nightly tasks and shutdown system.
        
        Args:
            skip_shutdown: If True, skip system shutdown
        """
        logger.info("🌙 Starting Batman Night Shift...")
        
        # Look for nightly task files
        task_files = []
        nightly_file = Path("tasks/nightly.txt")
        
        if nightly_file.exists():
            task_files.append(str(nightly_file))
        else:
            # Look for any task files in tasks directory
            tasks_dir = Path("tasks")
            if tasks_dir.exists():
                task_files.extend(str(f) for f in tasks_dir.glob("*.txt"))
        
        if not task_files:
            logger.error("No task files found for night shift")
            print("\n❌ No task files found in 'tasks' directory")
            print("Create tasks/nightly.txt with your nightly tasks")
            return
        
        print("\n🦇 Batman Night Shift Starting...")
        print(f"📋 Loading tasks from: {', '.join(task_files)}")
        
        # Run all tasks
        self.run_tasks(task_files, force=True, max_workers=4)
        
        # Generate morning report
        print("\n📊 Generating morning report...")
        try:
            report = generate_morning_report()
            report_file = Path("logs") / f"night_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            report_file.write_text(report)
            print(f"✓ Report saved to: {report_file}")
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
        
        # Shutdown system
        if not skip_shutdown:
            print("\n🌙 All tasks completed. Shutting down system...")
            print("💤 Good night!")
            
            import time
            time.sleep(5)  # Give user time to see the message
            
            try:
                if sys.platform == "linux":
                    # Check if we're in WSL
                    if Path("/proc/sys/fs/binfmt_misc/WSLInterop").exists():
                        # We're in WSL - shutdown Windows
                        logger.info("Shutting down Windows from WSL...")
                        os.system("powershell.exe -Command 'Stop-Computer -Force'")
                    else:
                        # Native Linux
                        logger.info("Shutting down Linux system...")
                        os.system("sudo shutdown -h now")
                else:
                    logger.error(f"Unsupported platform for shutdown: {sys.platform}")
            except Exception as e:
                logger.error(f"Failed to shutdown system: {e}")
                print(f"\n❌ Could not shutdown system: {e}")
        else:
            print("\n✅ Night shift completed (shutdown skipped)")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Batman - Task Automation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run tasks from a file
  batman run tasks.txt
  
  # Run tasks with specific tags
  batman run tasks.txt --tags backup,maintenance
  
  # List all tasks
  batman list tasks.txt
  
  # Run a single command
  batman exec "echo Hello Batman"
  
  # Generate morning report
  batman morning-report
  
  # Enter dream mode for analysis
  batman dream
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run tasks from files')
    run_parser.add_argument('files', nargs='+', help='Task file(s) to execute')
    run_parser.add_argument('--force', '-f', action='store_true', 
                           help='Force execution ignoring conditions')
    run_parser.add_argument('--workers', '-w', type=int, default=4,
                           help='Maximum concurrent tasks (default: 4)')
    run_parser.add_argument('--tags', '-t', help='Filter tasks by tags (comma-separated)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List tasks from files')
    list_parser.add_argument('files', nargs='+', help='Task file(s) to list')
    
    # Execute command
    exec_parser = subparsers.add_parser('exec', help='Execute a single command')
    exec_parser.add_argument('command', help='Command to execute')
    exec_parser.add_argument('--name', '-n', help='Task name (default: command)')
    exec_parser.add_argument('--id', help='Task ID (default: generated)')
    
    # Morning report command
    morning_parser = subparsers.add_parser('morning-report', 
                                          help='Generate morning report')
    morning_parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    
    # Dream mode command
    dream_parser = subparsers.add_parser('dream', help='Enter dream mode for analysis')
    dream_parser.add_argument('--iterations', '-i', type=int, default=5,
                             help='Number of analysis iterations')
    
    # Night shift command
    night_parser = subparsers.add_parser('night-shift', 
                                        help='Run all nightly tasks and shutdown')
    night_parser.add_argument('--no-shutdown', action='store_true',
                             help='Skip system shutdown after completion')
    
    # Version
    parser.add_argument('--version', '-v', action='version', 
                       version='Batman 1.0.0')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize Batman
    batman = Batman()
    
    try:
        if args.command == 'run':
            tags = args.tags.split(',') if args.tags else None
            batman.run_tasks(args.files, force=args.force, 
                           max_workers=args.workers, tags=tags)
                           
        elif args.command == 'list':
            batman.list_tasks(args.files)
            
        elif args.command == 'exec':
            import uuid
            task_id = args.id or f"cmd-{uuid.uuid4().hex[:8]}"
            task_name = args.name or args.command[:50]
            
            task_string = f"""
# [{task_id}] {task_name}
> {args.command}
"""
            batman.run_single_task(task_string)
            
        elif args.command == 'morning-report':
            report = generate_morning_report()
            if args.output:
                Path(args.output).write_text(report)
                print(f"Report saved to {args.output}")
            else:
                print(report)
                
        elif args.command == 'dream':
            dream = DreamMode()
            dream.interactive_mode(max_iterations=args.iterations)
            
        elif args.command == 'night-shift':
            batman.night_shift(skip_shutdown=args.no_shutdown)
            
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()