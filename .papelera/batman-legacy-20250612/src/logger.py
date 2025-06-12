#!/usr/bin/env python3
"""
Batman Logger Module
Provides centralized logging for all Batman operations.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)


class BatmanLogger:
    """Custom logger for Batman task automation system."""
    
    def __init__(self, name: str = "batman", log_level: str = "INFO"):
        """Initialize Batman logger.
        
        Args:
            name: Logger name
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Console handler with color coding
        self._setup_console_handler()
        
        # File handler with rotation
        self._setup_file_handler()
        
    def _setup_console_handler(self):
        """Setup colored console output."""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Color codes for different log levels
        class ColoredFormatter(logging.Formatter):
            """Add colors to log levels."""
            
            COLORS = {
                'DEBUG': '\033[36m',    # Cyan
                'INFO': '\033[32m',     # Green
                'WARNING': '\033[33m',  # Yellow
                'ERROR': '\033[31m',    # Red
                'CRITICAL': '\033[35m', # Magenta
            }
            RESET = '\033[0m'
            
            def format(self, record):
                log_color = self.COLORS.get(record.levelname, self.RESET)
                record.levelname = f"{log_color}{record.levelname}{self.RESET}"
                return super().format(record)
        
        console_format = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
    def _setup_file_handler(self):
        """Setup rotating file handler."""
        # Main log file
        main_log = LOGS_DIR / f"{self.name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            main_log,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
        
        # Error log file
        error_log = LOGS_DIR / f"{self.name}_errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_format)
        self.logger.addHandler(error_handler)
    
    def get_logger(self) -> logging.Logger:
        """Return the configured logger instance."""
        return self.logger


class TaskLogger:
    """Specialized logger for individual task execution."""
    
    def __init__(self, task_id: str):
        """Initialize task-specific logger.
        
        Args:
            task_id: Unique task identifier
        """
        self.task_id = task_id
        self.task_log_dir = LOGS_DIR / "tasks"
        self.task_log_dir.mkdir(exist_ok=True)
        
        # Create task-specific log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.task_log_dir / f"{task_id}_{timestamp}.log"
        
        # Setup logger
        self.logger = logging.getLogger(f"batman.task.{task_id}")
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        
        # File handler for this specific task
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
    def log_command(self, command: str, output: Optional[str] = None, 
                    error: Optional[str] = None, return_code: Optional[int] = None):
        """Log command execution details."""
        self.logger.info(f"Executing command: {command}")
        if output:
            self.logger.info(f"Output: {output[:500]}...")  # Truncate long outputs
        if error:
            self.logger.error(f"Error: {error}")
        if return_code is not None:
            self.logger.info(f"Return code: {return_code}")
    
    def get_log_file(self) -> Path:
        """Return the path to this task's log file."""
        return self.log_file


# Global logger instance
_batman_logger = None

def get_logger(name: str = "batman", log_level: str = "INFO") -> logging.Logger:
    """Get or create the global Batman logger.
    
    Args:
        name: Logger name
        log_level: Logging level
        
    Returns:
        Configured logger instance
    """
    global _batman_logger
    if _batman_logger is None:
        _batman_logger = BatmanLogger(name, log_level)
    return _batman_logger.get_logger()


def create_task_logger(task_id: str) -> TaskLogger:
    """Create a new task-specific logger.
    
    Args:
        task_id: Unique task identifier
        
    Returns:
        TaskLogger instance
    """
    return TaskLogger(task_id)


# Example usage
if __name__ == "__main__":
    # Test the logger
    logger = get_logger()
    
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
    
    # Test task logger
    task_logger = create_task_logger("test_task_001")
    task_logger.log_command("echo 'Hello Batman'", output="Hello Batman", return_code=0)
    print(f"Task log saved to: {task_logger.get_log_file()}")