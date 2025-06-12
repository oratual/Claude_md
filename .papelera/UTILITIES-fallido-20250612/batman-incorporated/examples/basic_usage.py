#!/usr/bin/env python3
"""
Batman Incorporated - Basic Usage Example

This script demonstrates how to use Batman Incorporated programmatically.
It shows common patterns and best practices for integrating Batman into
your Python applications.
"""

import sys
import os
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.batman import BatmanIncorporated
from src.core.config import Config
from src.core.task import Task, TaskType, TaskPriority, TaskBatch
from src.features.chapter_logger import ChapterLogger


def example_1_simple_task():
    """Example 1: Execute a simple task"""
    print("\n=== Example 1: Simple Task ===")
    
    # Initialize Batman
    config = Config()
    batman = BatmanIncorporated(config)
    
    # Execute a simple task
    result = batman.execute_task(
        "Create a Python function that calculates fibonacci numbers",
        mode="fast",  # Use fast mode for simple tasks
        real_agents=False  # Use simulation for example
    )
    
    print(f"Task completed: {result['success']}")
    print(f"Tasks executed: {result['tasks_completed']}")


def example_2_complex_feature():
    """Example 2: Implement a complex feature with multiple agents"""
    print("\n=== Example 2: Complex Feature ===")
    
    # Initialize with custom configuration
    config = Config()
    config.set("execution.default_mode", "safe")  # Use safe mode for complex tasks
    
    batman = BatmanIncorporated(config)
    
    # Execute complex task that requires multiple agents
    result = batman.execute_task(
        "Create a REST API for a todo list with authentication, database, and tests",
        mode="safe",
        real_agents=False
    )
    
    print(f"Agents involved: {result.get('agents_used', [])}")
    print(f"Execution time: {result.get('duration', 'N/A')}")


def example_3_batch_operations():
    """Example 3: Execute multiple related tasks as a batch"""
    print("\n=== Example 3: Batch Operations ===")
    
    batman = BatmanIncorporated()
    
    # Create a batch of related tasks
    tasks = [
        Task(
            title="Setup project structure",
            description="Create directory structure for a web app",
            type=TaskType.INFRASTRUCTURE,
            priority=TaskPriority.HIGH
        ),
        Task(
            title="Create database schema",
            description="Design PostgreSQL schema for user management",
            type=TaskType.DEVELOPMENT,
            priority=TaskPriority.HIGH,
            dependencies=["setup-project-structure"]
        ),
        Task(
            title="Implement user API",
            description="Create CRUD API for user management",
            type=TaskType.DEVELOPMENT,
            priority=TaskPriority.MEDIUM,
            dependencies=["create-database-schema"]
        ),
        Task(
            title="Write API tests",
            description="Add comprehensive test coverage",
            type=TaskType.TESTING,
            priority=TaskPriority.MEDIUM,
            dependencies=["implement-user-api"]
        )
    ]
    
    batch = TaskBatch("User Management System", tasks)
    
    # Execute the batch
    results = batman.execute_batch(batch, mode="safe", real_agents=False)
    
    # Check results
    stats = batch.get_statistics()
    print(f"Completed: {stats['completed']}/{stats['total']} tasks")
    print(f"Success rate: {stats['success_rate']:.1%}")


def example_4_custom_configuration():
    """Example 4: Use custom configuration"""
    print("\n=== Example 4: Custom Configuration ===")
    
    # Create custom configuration
    config = Config()
    
    # Disable specific agents
    config.set("agents.robin.enabled", False)  # Disable Robin for this session
    
    # Set execution preferences
    config.set("execution.max_parallel_agents", 3)
    config.set("execution.timeout_minutes", 45)
    
    # Enable features
    config.set("features.dream_mode", True)  # Enable experimental features
    config.set("features.learning_mode", True)
    
    batman = BatmanIncorporated(config)
    
    # The configuration affects how tasks are executed
    result = batman.execute_task(
        "Optimize the application's performance",
        real_agents=False
    )
    
    print(f"Configuration applied successfully")
    print(f"Available agents: {[a for a in config.get('agents', {}) if config.get(f'agents.{a}.enabled', True)]}")


def example_5_agent_specific_tasks():
    """Example 5: Direct tasks to specific agents"""
    print("\n=== Example 5: Agent-Specific Tasks ===")
    
    batman = BatmanIncorporated()
    
    # Task specifically for Alfred (backend)
    backend_task = Task(
        title="Implement payment processing",
        description="Create secure payment API with Stripe integration",
        type=TaskType.DEVELOPMENT,
        assigned_to="alfred"  # Explicitly assign to Alfred
    )
    
    # Task specifically for Oracle (testing/security)
    security_task = Task(
        title="Security audit",
        description="Perform security audit on payment API",
        type=TaskType.TESTING,
        assigned_to="oracle"  # Explicitly assign to Oracle
    )
    
    # Execute tasks
    results = []
    for task in [backend_task, security_task]:
        result = batman.execute_single_task(task, real_agents=False)
        results.append(result)
        print(f"{task.title} - Assigned to: {task.assigned_to} - Success: {result['success']}")


def example_6_monitoring_progress():
    """Example 6: Monitor task progress with callbacks"""
    print("\n=== Example 6: Progress Monitoring ===")
    
    # Custom logger to capture progress
    class ProgressLogger(ChapterLogger):
        def __init__(self, session_id: str):
            super().__init__(session_id)
            self.progress_callbacks = []
        
        def add_progress_callback(self, callback):
            self.progress_callbacks.append(callback)
        
        def log(self, message: str, level: str = "info"):
            super().log(message, level)
            # Notify callbacks
            for callback in self.progress_callbacks:
                callback(message, level)
    
    # Progress callback
    def on_progress(message: str, level: str):
        if level in ["success", "error"]:
            print(f"  [{level.upper()}] {message}")
    
    # Initialize with custom logger
    config = Config()
    batman = BatmanIncorporated(config)
    
    # Replace logger with custom one
    custom_logger = ProgressLogger("example-session")
    custom_logger.add_progress_callback(on_progress)
    batman.logger = custom_logger
    
    # Execute task with progress monitoring
    batman.execute_task(
        "Create a data visualization dashboard",
        real_agents=False
    )


def example_7_error_handling():
    """Example 7: Handle errors gracefully"""
    print("\n=== Example 7: Error Handling ===")
    
    batman = BatmanIncorporated()
    
    try:
        # Simulate a task that might fail
        result = batman.execute_task(
            "Fix bug in non-existent file /does/not/exist.py",
            mode="fast",
            real_agents=False
        )
        
        if not result['success']:
            print(f"Task failed: {result.get('error', 'Unknown error')}")
            
            # Retry with different approach
            print("Retrying with safe mode...")
            result = batman.execute_task(
                "Search for similar bugs in the codebase and fix them",
                mode="safe",
                real_agents=False
            )
            
    except Exception as e:
        print(f"Error occurred: {e}")
        # Log error for debugging
        batman.logger.error(f"Task execution failed: {str(e)}")


def main():
    """Run all examples"""
    print("Batman Incorporated - Basic Usage Examples")
    print("=" * 50)
    
    examples = [
        example_1_simple_task,
        example_2_complex_feature,
        example_3_batch_operations,
        example_4_custom_configuration,
        example_5_agent_specific_tasks,
        example_6_monitoring_progress,
        example_7_error_handling
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\nError in {example.__name__}: {e}")
            continue
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("\nFor more advanced usage, see the documentation:")
    print("- API Reference: docs/API.md")
    print("- More Examples: docs/EXAMPLES.md")
    print("- Architecture: docs/ARCHITECTURE.md")


if __name__ == "__main__":
    main()