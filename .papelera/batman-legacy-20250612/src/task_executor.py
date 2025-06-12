#!/usr/bin/env python3
"""
Batman Task Executor Module
Executes tasks with proper error handling, logging, and result tracking.
"""

import os
import subprocess
import threading
import queue
import signal
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass, field
from enum import Enum

from logger import get_logger, create_task_logger
from task_parser import Task, TaskCondition, TaskPriority

logger = get_logger()


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class TaskResult:
    """Result of task execution."""
    task_id: str
    status: TaskStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    output: str = ""
    error: str = ""
    return_code: Optional[int] = None
    log_file: Optional[Path] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration(self) -> Optional[float]:
        """Calculate task duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "output": self.output,
            "error": self.error,
            "return_code": self.return_code,
            "log_file": str(self.log_file) if self.log_file else None,
            "metadata": self.metadata
        }


class ConditionChecker:
    """Checks if task conditions are met."""
    
    @staticmethod
    def check_condition(condition: TaskCondition) -> bool:
        """Check if a single condition is met."""
        try:
            if condition.type == "file_exists":
                path = Path(condition.params.get("path", ""))
                return path.exists()
                
            elif condition.type == "command_success":
                command = condition.params.get("command", "")
                result = subprocess.run(
                    command, 
                    shell=True, 
                    capture_output=True,
                    timeout=30
                )
                return result.returncode == 0
                
            elif condition.type == "time_range":
                start_time = datetime.strptime(condition.params.get("start", "00:00"), "%H:%M").time()
                end_time = datetime.strptime(condition.params.get("end", "23:59"), "%H:%M").time()
                current_time = datetime.now().time()
                
                if start_time <= end_time:
                    return start_time <= current_time <= end_time
                else:
                    # Handle overnight ranges (e.g., 22:00-06:00)
                    return current_time >= start_time or current_time <= end_time
                    
            else:
                logger.warning(f"Unknown condition type: {condition.type}")
                return True
                
        except Exception as e:
            logger.error(f"Error checking condition {condition}: {e}")
            return False
    
    @staticmethod
    def check_all_conditions(task: Task) -> Tuple[bool, List[str]]:
        """Check all conditions for a task.
        
        Returns:
            Tuple of (all_conditions_met, list_of_failed_conditions)
        """
        failed_conditions = []
        
        for condition in task.conditions:
            if not ConditionChecker.check_condition(condition):
                failed_conditions.append(str(condition))
        
        return len(failed_conditions) == 0, failed_conditions


class TaskExecutor:
    """Executes tasks with proper isolation and resource management."""
    
    def __init__(self, max_workers: int = 4, default_timeout: int = 300):
        """Initialize task executor.
        
        Args:
            max_workers: Maximum number of concurrent tasks
            default_timeout: Default timeout in seconds
        """
        self.max_workers = max_workers
        self.default_timeout = default_timeout
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running_tasks: Dict[str, subprocess.Popen] = {}
        self.task_futures: Dict[str, Future] = {}
        self.results: Dict[str, TaskResult] = {}
        self._lock = threading.Lock()
        
    def execute_task(self, task: Task, force: bool = False) -> TaskResult:
        """Execute a single task.
        
        Args:
            task: Task to execute
            force: Force execution even if conditions aren't met
            
        Returns:
            TaskResult object
        """
        logger.info(f"Executing task: {task.name} (ID: {task.id})")
        
        # Create task-specific logger
        task_logger = create_task_logger(task.id)
        
        # Initialize result
        result = TaskResult(
            task_id=task.id,
            status=TaskStatus.PENDING,
            start_time=datetime.now(),
            log_file=task_logger.get_log_file()
        )
        
        try:
            # Check conditions
            if not force and task.conditions:
                conditions_met, failed = ConditionChecker.check_all_conditions(task)
                if not conditions_met:
                    logger.info(f"Task {task.id} skipped - conditions not met: {failed}")
                    result.status = TaskStatus.SKIPPED
                    result.metadata["failed_conditions"] = failed
                    result.end_time = datetime.now()
                    return result
            
            # Check dependencies
            if task.dependencies:
                unmet_deps = self._check_dependencies(task.dependencies)
                if unmet_deps:
                    logger.info(f"Task {task.id} skipped - unmet dependencies: {unmet_deps}")
                    result.status = TaskStatus.SKIPPED
                    result.metadata["unmet_dependencies"] = unmet_deps
                    result.end_time = datetime.now()
                    return result
            
            # Update status to running
            result.status = TaskStatus.RUNNING
            
            # Prepare environment
            env = os.environ.copy()
            env.update(task.environment)
            
            # Prepare command
            if isinstance(task.command, list):
                cmd = task.command
                shell = False
            else:
                cmd = task.command
                shell = True
            
            # Set working directory
            cwd = task.working_directory or os.getcwd()
            
            # Determine timeout
            timeout = task.timeout or self.default_timeout
            
            logger.debug(f"Executing command: {cmd}")
            task_logger.log_command(cmd)
            
            # Execute command
            process = subprocess.Popen(
                cmd,
                shell=shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=cwd,
                text=True,
                preexec_fn=os.setsid if os.name == 'posix' else None
            )
            
            # Track running process
            with self._lock:
                self.running_tasks[task.id] = process
            
            try:
                # Wait for completion with timeout
                stdout, stderr = process.communicate(timeout=timeout)
                return_code = process.returncode
                
                # Log output
                task_logger.log_command(cmd, output=stdout, error=stderr, return_code=return_code)
                
                # Update result
                result.output = stdout
                result.error = stderr
                result.return_code = return_code
                
                if return_code == 0:
                    result.status = TaskStatus.SUCCESS
                    logger.info(f"Task {task.id} completed successfully")
                else:
                    result.status = TaskStatus.FAILED
                    logger.error(f"Task {task.id} failed with return code {return_code}")
                    
            except subprocess.TimeoutExpired:
                logger.error(f"Task {task.id} timed out after {timeout} seconds")
                result.status = TaskStatus.TIMEOUT
                
                # Kill the process group
                if os.name == 'posix':
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    time.sleep(2)  # Give it time to terminate
                    if process.poll() is None:
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                else:
                    process.terminate()
                    time.sleep(2)
                    if process.poll() is None:
                        process.kill()
                
                # Get any partial output
                try:
                    stdout, stderr = process.communicate(timeout=5)
                    result.output = stdout or ""
                    result.error = stderr or ""
                except:
                    pass
                    
            finally:
                # Remove from running tasks
                with self._lock:
                    self.running_tasks.pop(task.id, None)
                    
        except Exception as e:
            logger.error(f"Error executing task {task.id}: {e}")
            result.status = TaskStatus.FAILED
            result.error = str(e)
            
        finally:
            result.end_time = datetime.now()
            
        return result
    
    def execute_tasks_async(self, tasks: List[Task], 
                           callback: Optional[Callable[[TaskResult], None]] = None) -> None:
        """Execute multiple tasks asynchronously.
        
        Args:
            tasks: List of tasks to execute
            callback: Optional callback for each completed task
        """
        def task_wrapper(task: Task) -> TaskResult:
            result = self.execute_task(task)
            self.results[task.id] = result
            
            if callback:
                try:
                    callback(result)
                except Exception as e:
                    logger.error(f"Error in task callback: {e}")
                    
            return result
        
        # Sort tasks by priority
        sorted_tasks = sorted(tasks, key=lambda t: t.priority.value, reverse=True)
        
        # Submit tasks
        for task in sorted_tasks:
            future = self.executor.submit(task_wrapper, task)
            self.task_futures[task.id] = future
    
    def wait_for_completion(self, timeout: Optional[float] = None) -> Dict[str, TaskResult]:
        """Wait for all tasks to complete.
        
        Args:
            timeout: Maximum time to wait
            
        Returns:
            Dictionary of task results
        """
        futures = list(self.task_futures.values())
        
        if futures:
            if timeout:
                from concurrent.futures import wait, TimeoutError
                done, not_done = wait(futures, timeout=timeout)
                
                # Cancel timed out tasks
                for future in not_done:
                    future.cancel()
            else:
                # Wait for all to complete
                for future in futures:
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"Task future error: {e}")
        
        return self.results
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task.
        
        Args:
            task_id: ID of task to cancel
            
        Returns:
            True if cancelled, False otherwise
        """
        with self._lock:
            # Cancel future if not started
            future = self.task_futures.get(task_id)
            if future and not future.done():
                cancelled = future.cancel()
                if cancelled:
                    logger.info(f"Cancelled task {task_id} before execution")
                    return True
            
            # Kill running process
            process = self.running_tasks.get(task_id)
            if process:
                logger.info(f"Killing running task {task_id}")
                if os.name == 'posix':
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                else:
                    process.terminate()
                return True
        
        return False
    
    def _check_dependencies(self, dependencies: List[str]) -> List[str]:
        """Check which dependencies are not met.
        
        Args:
            dependencies: List of task IDs
            
        Returns:
            List of unmet dependency IDs
        """
        unmet = []
        for dep_id in dependencies:
            result = self.results.get(dep_id)
            if not result or result.status != TaskStatus.SUCCESS:
                unmet.append(dep_id)
        return unmet
    
    def shutdown(self, wait: bool = True) -> None:
        """Shutdown the executor.
        
        Args:
            wait: Wait for running tasks to complete
        """
        logger.info("Shutting down task executor")
        
        # Cancel all pending tasks
        for task_id, future in self.task_futures.items():
            if not future.done():
                future.cancel()
        
        # Kill all running processes
        with self._lock:
            for task_id, process in self.running_tasks.items():
                if process.poll() is None:
                    logger.warning(f"Force killing task {task_id}")
                    if os.name == 'posix':
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    else:
                        process.kill()
        
        # Shutdown executor
        self.executor.shutdown(wait=wait)


# Example usage
if __name__ == "__main__":
    from task_parser import TaskParser
    
    # Create sample tasks
    task_text = """
# [test-echo] Test Echo Command
priority: normal
> echo "Hello from Batman!"

# [test-sleep] Test Sleep Command
priority: low
timeout: 5
> sleep 2 && echo "Woke up!"

# [test-fail] Test Failing Command
priority: high
> exit 1
"""
    
    # Parse tasks
    parser = TaskParser()
    task_file = Path("test_executor_tasks.txt")
    task_file.write_text(task_text)
    tasks = parser.parse_file(task_file)
    
    # Execute tasks
    executor = TaskExecutor(max_workers=2)
    
    def on_complete(result: TaskResult):
        print(f"Task {result.task_id} completed with status: {result.status.value}")
        print(f"  Duration: {result.duration:.2f}s")
        if result.output:
            print(f"  Output: {result.output.strip()}")
        if result.error:
            print(f"  Error: {result.error.strip()}")
    
    # Execute all tasks
    executor.execute_tasks_async(tasks, callback=on_complete)
    
    # Wait for completion
    results = executor.wait_for_completion()
    
    print("\n=== Final Results ===")
    for task_id, result in results.items():
        print(f"{task_id}: {result.status.value}")
    
    # Cleanup
    executor.shutdown()
    task_file.unlink()