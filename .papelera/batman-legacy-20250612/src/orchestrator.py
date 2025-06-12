#!/usr/bin/env python3
"""
Batman Orchestrator - Coordina a todos los aliados
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

from logger import get_logger

logger = get_logger("batman.orchestrator")


class AllyType(Enum):
    """Tipos de aliados disponibles."""
    ROBIN = "robin"          # Tareas Linux/Sistema
    CLAUDE = "claude"        # Programación con IA
    ALFRED = "alfred"        # Reportes y análisis
    ORACLE = "oracle"        # Análisis avanzado/Dream mode
    NIGHTWING = "nightwing"  # Tareas de red/seguridad


class AllyStatus(Enum):
    """Estado de los aliados."""
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class Ally:
    """Representa un aliado del equipo Batman."""
    
    def __init__(self, name: AllyType, command: str, description: str):
        self.name = name
        self.command = command
        self.description = description
        self.status = AllyStatus.READY
        self.current_task = None
        self.process = None
        
    def is_available(self) -> bool:
        """Check if ally is available for tasks."""
        return self.status == AllyStatus.READY
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name.value,
            "status": self.status.value,
            "description": self.description,
            "current_task": self.current_task
        }


class BatmanOrchestrator:
    """Batman coordina a todos sus aliados para completar misiones."""
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.allies = self._initialize_allies()
        self.mission_log = []
        self.start_time = datetime.now()
        
        logger.info("🦇 Batman Orchestrator initialized")
        logger.info(f"Available allies: {[a.value for a in AllyType]}")
    
    def _initialize_allies(self) -> Dict[AllyType, Ally]:
        """Initialize all available allies."""
        allies = {
            AllyType.ROBIN: Ally(
                AllyType.ROBIN,
                "python3 robin.py",
                "System tasks and maintenance"
            ),
            AllyType.CLAUDE: Ally(
                AllyType.CLAUDE,
                "claude",  # Will be expanded for Windows/WSL2
                "AI-powered programming"
            ),
            AllyType.ALFRED: Ally(
                AllyType.ALFRED,
                "python3 alfred.py",
                "Reports and analysis"
            ),
            AllyType.ORACLE: Ally(
                AllyType.ORACLE,
                "python3 oracle.py",
                "Advanced analysis and dream mode"
            )
        }
        return allies
    
    def dispatch_ally(self, ally_type: AllyType, task: Dict[str, Any]) -> bool:
        """Dispatch an ally to perform a task.
        
        Args:
            ally_type: Type of ally to dispatch
            task: Task configuration
            
        Returns:
            True if dispatch successful
        """
        ally = self.allies.get(ally_type)
        if not ally:
            logger.error(f"Ally {ally_type} not found")
            return False
        
        if not ally.is_available():
            logger.warning(f"{ally_type.value} is busy with: {ally.current_task}")
            return False
        
        logger.info(f"🚀 Dispatching {ally_type.value} for task: {task.get('name', 'unnamed')}")
        
        ally.status = AllyStatus.BUSY
        ally.current_task = task.get('name')
        
        # Build command based on ally type
        if ally_type == AllyType.ROBIN:
            cmd = self._build_robin_command(task)
        elif ally_type == AllyType.CLAUDE:
            cmd = self._build_claude_command(task)
        else:
            cmd = f"{ally.command} {task.get('args', '')}"
        
        try:
            # Execute command
            if ally_type == AllyType.CLAUDE and sys.platform == "linux":
                # Special handling for Claude on Windows from WSL2
                if Path("/proc/sys/fs/binfmt_misc/WSLInterop").exists():
                    # We're in WSL2 - launch Claude in Windows
                    cmd = self._build_claude_windows_command(task)
            
            ally.process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Log the dispatch
            self.mission_log.append({
                "timestamp": datetime.now().isoformat(),
                "ally": ally_type.value,
                "task": task,
                "status": "dispatched"
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to dispatch {ally_type.value}: {e}")
            ally.status = AllyStatus.ERROR
            ally.current_task = None
            return False
    
    def _build_robin_command(self, task: Dict[str, Any]) -> str:
        """Build command for Robin."""
        task_type = task.get('type', 'execute')
        
        if task_type == 'execute':
            files = task.get('files', ['tasks/robin-system.txt'])
            return f"python3 robin.py execute {' '.join(files)}"
        elif task_type == 'backup':
            return f"python3 robin.py backup {task['source']} {task['destination']}"
        elif task_type == 'clean':
            return f"python3 robin.py clean-logs --days {task.get('days', 30)}"
        else:
            return f"python3 robin.py {task_type}"
    
    def _build_claude_command(self, task: Dict[str, Any]) -> str:
        """Build command for Claude."""
        project = task.get('project', '.')
        instructions = task.get('instructions', '')
        
        # Save instructions to file
        instructions_file = Path("/tmp/claude_instructions.txt")
        instructions_file.write_text(instructions)
        
        return f"cd {project} && claude --instructions {instructions_file}"
    
    def _build_claude_windows_command(self, task: Dict[str, Any]) -> str:
        """Build command to launch Claude in Windows from WSL2."""
        project = task.get('project', '.')
        
        # Convert WSL path to Windows path
        if project.startswith('/home'):
            # Convert /home/user/path to \\wsl$\Ubuntu\home\user\path
            win_path = project.replace('/home', r'\\wsl$\Ubuntu\home')
        else:
            win_path = project
        
        # Use PowerShell to launch Claude
        return f'powershell.exe -Command "cd \'{win_path}\'; claude"'
    
    def check_ally_status(self, ally_type: AllyType) -> AllyStatus:
        """Check the status of an ally."""
        ally = self.allies.get(ally_type)
        if not ally:
            return AllyStatus.OFFLINE
        
        if ally.process and ally.process.poll() is None:
            # Process is still running
            return AllyStatus.BUSY
        elif ally.process and ally.process.poll() == 0:
            # Process completed successfully
            ally.status = AllyStatus.READY
            ally.current_task = None
            
            # Log completion
            self.mission_log.append({
                "timestamp": datetime.now().isoformat(),
                "ally": ally_type.value,
                "status": "completed"
            })
        elif ally.process and ally.process.poll() != 0:
            # Process failed
            ally.status = AllyStatus.ERROR
            
            # Log error
            self.mission_log.append({
                "timestamp": datetime.now().isoformat(),
                "ally": ally_type.value,
                "status": "failed",
                "error": ally.process.stderr.read() if ally.process.stderr else "Unknown error"
            })
        
        return ally.status
    
    def wait_for_ally(self, ally_type: AllyType, timeout: Optional[int] = None) -> bool:
        """Wait for an ally to complete their task.
        
        Args:
            ally_type: Ally to wait for
            timeout: Maximum seconds to wait
            
        Returns:
            True if completed successfully
        """
        ally = self.allies.get(ally_type)
        if not ally or not ally.process:
            return False
        
        try:
            stdout, stderr = ally.process.communicate(timeout=timeout)
            
            if ally.process.returncode == 0:
                logger.info(f"✅ {ally_type.value} completed successfully")
                ally.status = AllyStatus.READY
                ally.current_task = None
                return True
            else:
                logger.error(f"❌ {ally_type.value} failed: {stderr}")
                ally.status = AllyStatus.ERROR
                return False
                
        except subprocess.TimeoutExpired:
            logger.warning(f"⏱️ {ally_type.value} timed out")
            ally.process.kill()
            ally.status = AllyStatus.ERROR
            return False
    
    def coordinate_mission(self, mission_plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Coordinate a complete mission with multiple allies.
        
        Args:
            mission_plan: List of tasks with ally assignments
            
        Returns:
            Mission summary
        """
        logger.info("🦇 Batman coordinating mission...")
        
        results = {
            "start_time": self.start_time.isoformat(),
            "tasks_total": len(mission_plan),
            "tasks_completed": 0,
            "tasks_failed": 0,
            "ally_performance": {}
        }
        
        for task in mission_plan:
            ally_type = AllyType(task.get('ally', 'robin'))
            
            if self.dispatch_ally(ally_type, task):
                # Wait for completion if synchronous
                if task.get('wait', True):
                    success = self.wait_for_ally(ally_type)
                    if success:
                        results["tasks_completed"] += 1
                    else:
                        results["tasks_failed"] += 1
            else:
                results["tasks_failed"] += 1
        
        # Wait for all async tasks
        for ally_type, ally in self.allies.items():
            if ally.status == AllyStatus.BUSY:
                self.wait_for_ally(ally_type)
        
        # Compile ally performance
        for ally_type, ally in self.allies.items():
            completed = sum(1 for log in self.mission_log 
                          if log['ally'] == ally_type.value and log['status'] == 'completed')
            results["ally_performance"][ally_type.value] = {
                "tasks_completed": completed,
                "current_status": ally.status.value
            }
        
        results["end_time"] = datetime.now().isoformat()
        results["mission_log"] = self.mission_log
        
        return results
    
    def generate_mission_report(self, results: Dict[str, Any]) -> str:
        """Generate a mission report."""
        report = ["# 🦇 BATMAN MISSION REPORT"]
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("=" * 50)
        
        report.append(f"\n## Mission Summary")
        report.append(f"- Total Tasks: {results['tasks_total']}")
        report.append(f"- Completed: {results['tasks_completed']} ✅")
        report.append(f"- Failed: {results['tasks_failed']} ❌")
        
        report.append(f"\n## Ally Performance")
        for ally, perf in results['ally_performance'].items():
            report.append(f"- {ally}: {perf['tasks_completed']} tasks, Status: {perf['current_status']}")
        
        return "\n".join(report)


if __name__ == "__main__":
    # Test the orchestrator
    orchestrator = BatmanOrchestrator()
    
    # Example mission
    mission = [
        {
            "ally": "robin",
            "type": "execute",
            "files": ["tasks/robin-system.txt"],
            "name": "System maintenance"
        },
        {
            "ally": "robin",
            "type": "clean",
            "days": 7,
            "name": "Clean old logs"
        }
    ]
    
    results = orchestrator.coordinate_mission(mission)
    print(orchestrator.generate_mission_report(results))