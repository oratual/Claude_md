#!/usr/bin/env python3
"""
Batman Task Parser Module
Parses task files and extracts structured task information.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, time
from dataclasses import dataclass, field
from enum import Enum

from logger import get_logger

logger = get_logger()


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class TaskFrequency(Enum):
    """Task execution frequency."""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    HOURLY = "hourly"
    CUSTOM = "custom"


@dataclass
class TaskCondition:
    """Represents a condition for task execution."""
    type: str  # 'file_exists', 'command_success', 'time_range', etc.
    params: Dict[str, Any]
    
    def __str__(self):
        return f"{self.type}({self.params})"


@dataclass
class Task:
    """Represents a parsed task."""
    id: str
    name: str
    command: str
    priority: TaskPriority = TaskPriority.NORMAL
    frequency: TaskFrequency = TaskFrequency.ONCE
    schedule: Optional[str] = None  # Cron expression or time
    conditions: List[TaskCondition] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    timeout: Optional[int] = None  # seconds
    retry_count: int = 0
    environment: Dict[str, str] = field(default_factory=dict)
    working_directory: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "command": self.command,
            "priority": self.priority.name,
            "frequency": self.frequency.value,
            "schedule": self.schedule,
            "conditions": [{"type": c.type, "params": c.params} for c in self.conditions],
            "dependencies": self.dependencies,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
            "environment": self.environment,
            "working_directory": self.working_directory,
            "tags": self.tags,
            "metadata": self.metadata
        }


class TaskParser:
    """Parses task definitions from various formats."""
    
    # Regex patterns for parsing
    PATTERNS = {
        'task_header': re.compile(r'^#\s*\[([^\]]+)\]\s*(.*)$'),
        'property': re.compile(r'^(\w+):\s*(.+)$'),
        'command': re.compile(r'^>\s*(.+)$'),
        'condition': re.compile(r'^IF\s+(.+)$'),
        'dependency': re.compile(r'^DEPENDS\s+ON\s+(.+)$'),
        'schedule': re.compile(r'^SCHEDULE\s+(.+)$'),
        'tag': re.compile(r'^TAG\s+(.+)$'),
        'env': re.compile(r'^ENV\s+(\w+)=(.+)$'),
    }
    
    def __init__(self):
        """Initialize the task parser."""
        self.tasks: Dict[str, Task] = {}
        
    def parse_file(self, file_path: Union[str, Path]) -> List[Task]:
        """Parse tasks from a file.
        
        Args:
            file_path: Path to the task file
            
        Returns:
            List of parsed tasks
        """
        file_path = Path(file_path)
        logger.info(f"Parsing task file: {file_path}")
        
        if not file_path.exists():
            logger.error(f"Task file not found: {file_path}")
            raise FileNotFoundError(f"Task file not found: {file_path}")
        
        # Determine parser based on file extension
        if file_path.suffix == '.json':
            return self._parse_json(file_path)
        elif file_path.suffix in ['.yaml', '.yml']:
            return self._parse_yaml(file_path)
        else:
            # Default to text format
            return self._parse_text(file_path)
    
    def _parse_text(self, file_path: Path) -> List[Task]:
        """Parse tasks from text format.
        
        Format example:
        # [task-id] Task Name
        priority: high
        frequency: daily
        schedule: 09:00
        > echo "Running task"
        IF file_exists(/tmp/flag.txt)
        DEPENDS ON other-task
        TAG maintenance
        ENV PATH=/custom/path:$PATH
        """
        tasks = []
        current_task = None
        
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#') and not self.PATTERNS['task_header'].match(line):
                continue
            
            # Task header
            match = self.PATTERNS['task_header'].match(line)
            if match:
                # Save previous task if exists
                if current_task:
                    tasks.append(current_task)
                
                task_id = match.group(1).strip()
                task_name = match.group(2).strip() or task_id
                
                current_task = Task(
                    id=task_id,
                    name=task_name,
                    command=""  # Will be set later
                )
                logger.debug(f"Found task: {task_id}")
                continue
            
            if not current_task:
                logger.warning(f"Line {line_num}: Ignoring line outside task definition")
                continue
            
            # Command
            match = self.PATTERNS['command'].match(line)
            if match:
                if current_task.command:
                    current_task.command += "\n" + match.group(1)
                else:
                    current_task.command = match.group(1)
                continue
            
            # Properties
            match = self.PATTERNS['property'].match(line)
            if match:
                prop_name = match.group(1).lower()
                prop_value = match.group(2).strip()
                
                if prop_name == 'priority':
                    try:
                        current_task.priority = TaskPriority[prop_value.upper()]
                    except KeyError:
                        logger.warning(f"Invalid priority: {prop_value}")
                elif prop_name == 'frequency':
                    try:
                        current_task.frequency = TaskFrequency(prop_value.lower())
                    except ValueError:
                        logger.warning(f"Invalid frequency: {prop_value}")
                elif prop_name == 'timeout':
                    current_task.timeout = int(prop_value)
                elif prop_name == 'retry':
                    current_task.retry_count = int(prop_value)
                elif prop_name == 'workdir':
                    current_task.working_directory = prop_value
                continue
            
            # Schedule
            match = self.PATTERNS['schedule'].match(line)
            if match:
                current_task.schedule = match.group(1).strip()
                continue
            
            # Condition
            match = self.PATTERNS['condition'].match(line)
            if match:
                condition_str = match.group(1).strip()
                condition = self._parse_condition(condition_str)
                if condition:
                    current_task.conditions.append(condition)
                continue
            
            # Dependencies
            match = self.PATTERNS['dependency'].match(line)
            if match:
                deps = [d.strip() for d in match.group(1).split(',')]
                current_task.dependencies.extend(deps)
                continue
            
            # Tags
            match = self.PATTERNS['tag'].match(line)
            if match:
                tags = [t.strip() for t in match.group(1).split(',')]
                current_task.tags.extend(tags)
                continue
            
            # Environment variables
            match = self.PATTERNS['env'].match(line)
            if match:
                current_task.environment[match.group(1)] = match.group(2)
                continue
        
        # Don't forget the last task
        if current_task:
            tasks.append(current_task)
        
        logger.info(f"Parsed {len(tasks)} tasks from {file_path}")
        return tasks
    
    def _parse_condition(self, condition_str: str) -> Optional[TaskCondition]:
        """Parse a condition string into a TaskCondition object."""
        # Examples:
        # file_exists(/tmp/flag.txt)
        # command_success(ping -c 1 google.com)
        # time_range(09:00-17:00)
        
        match = re.match(r'(\w+)\(([^)]+)\)', condition_str)
        if not match:
            logger.warning(f"Invalid condition format: {condition_str}")
            return None
        
        condition_type = match.group(1)
        params_str = match.group(2)
        
        # Parse parameters based on condition type
        if condition_type == 'file_exists':
            params = {'path': params_str.strip()}
        elif condition_type == 'command_success':
            params = {'command': params_str.strip()}
        elif condition_type == 'time_range':
            times = params_str.split('-')
            if len(times) == 2:
                params = {'start': times[0].strip(), 'end': times[1].strip()}
            else:
                logger.warning(f"Invalid time range: {params_str}")
                return None
        else:
            # Generic parameter parsing
            params = {'value': params_str.strip()}
        
        return TaskCondition(type=condition_type, params=params)
    
    def _parse_json(self, file_path: Path) -> List[Task]:
        """Parse tasks from JSON format."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        tasks = []
        for task_data in data.get('tasks', []):
            task = self._create_task_from_dict(task_data)
            if task:
                tasks.append(task)
        
        return tasks
    
    def _parse_yaml(self, file_path: Path) -> List[Task]:
        """Parse tasks from YAML format."""
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed. Install with: pip install pyyaml")
            raise ImportError("PyYAML required for parsing YAML files")
        
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        tasks = []
        for task_data in data.get('tasks', []):
            task = self._create_task_from_dict(task_data)
            if task:
                tasks.append(task)
        
        return tasks
    
    def _create_task_from_dict(self, data: Dict[str, Any]) -> Optional[Task]:
        """Create a Task object from a dictionary."""
        try:
            task = Task(
                id=data['id'],
                name=data.get('name', data['id']),
                command=data['command']
            )
            
            # Set optional fields
            if 'priority' in data:
                task.priority = TaskPriority[data['priority'].upper()]
            if 'frequency' in data:
                task.frequency = TaskFrequency(data['frequency'].lower())
            if 'schedule' in data:
                task.schedule = data['schedule']
            if 'timeout' in data:
                task.timeout = int(data['timeout'])
            if 'retry_count' in data:
                task.retry_count = int(data['retry_count'])
            if 'environment' in data:
                task.environment = data['environment']
            if 'working_directory' in data:
                task.working_directory = data['working_directory']
            if 'tags' in data:
                task.tags = data['tags']
            if 'dependencies' in data:
                task.dependencies = data['dependencies']
            if 'conditions' in data:
                for cond in data['conditions']:
                    condition = TaskCondition(
                        type=cond['type'],
                        params=cond.get('params', {})
                    )
                    task.conditions.append(condition)
            
            return task
            
        except KeyError as e:
            logger.error(f"Missing required field in task definition: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating task from dict: {e}")
            return None
    
    def parse_string(self, task_string: str) -> Optional[Task]:
        """Parse a single task from a string."""
        lines = task_string.strip().split('\n')
        
        # Create temporary file-like parsing
        tasks = []
        current_task = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Similar parsing logic as _parse_text but for a single task
            # This is a simplified version
            if line.startswith('# ['):
                match = self.PATTERNS['task_header'].match(line)
                if match:
                    task_id = match.group(1).strip()
                    task_name = match.group(2).strip() or task_id
                    current_task = Task(id=task_id, name=task_name, command="")
            elif line.startswith('>') and current_task:
                match = self.PATTERNS['command'].match(line)
                if match:
                    current_task.command = match.group(1)
        
        return current_task


# Example usage
if __name__ == "__main__":
    # Test the parser
    parser = TaskParser()
    
    # Create a test task file
    test_file = Path("test_tasks.txt")
    test_file.write_text("""
# [backup-db] Daily Database Backup
priority: high
frequency: daily
schedule: 02:00
> pg_dump mydb > /backup/db_$(date +%Y%m%d).sql
IF file_exists(/var/lib/postgresql/data)
TAG backup
TAG database

# [cleanup-logs] Clean old log files
priority: normal
frequency: weekly
> find /var/log -name "*.log" -mtime +30 -delete
DEPENDS ON backup-db
""")
    
    # Parse the file
    tasks = parser.parse_file(test_file)
    
    # Display parsed tasks
    for task in tasks:
        print(f"\nTask: {task.name}")
        print(f"  ID: {task.id}")
        print(f"  Command: {task.command}")
        print(f"  Priority: {task.priority.name}")
        print(f"  Schedule: {task.schedule}")
        print(f"  Tags: {task.tags}")
    
    # Cleanup
    test_file.unlink()