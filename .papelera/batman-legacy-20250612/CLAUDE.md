# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Batman is a nocturnal task automation system designed to run maintenance tasks automatically without user intervention. It reads task definitions from text files and executes them according to schedules, handling errors gracefully.

## Tech Stack

- **Language**: Python 3.10+ (for rapid development and good system integration)
- **Scheduler**: APScheduler or cron integration
- **Logging**: Python logging with rotation
- **Config**: YAML/TOML for configuration
- **Testing**: pytest with mock for system calls

## Architecture

### Core Components

1. **Task Parser** (`src/parser.py`)
   - Reads task definition files
   - Validates syntax
   - Returns Task objects

2. **Task Executor** (`src/executor.py`)
   - Executes commands safely
   - Handles timeouts
   - Implements retry logic
   - Captures output/errors

3. **Scheduler** (`src/scheduler.py`)
   - Manages task scheduling
   - Integrates with system cron or runs standalone
   - Handles missed executions

4. **Error Handler** (`src/error_handler.py`)
   - Graceful error handling
   - Notification system (email/log)
   - Fallback strategies

5. **Logger** (`src/logger.py`)
   - Structured logging
   - Log rotation
   - Different levels for different components

## Task File Format

```
# Comment
TASK: task_identifier
SCHEDULE: cron_expression or keywords (daily, hourly, etc.)
COMMAND: shell command to execute
RETRY: number of retries (default: 1)
TIMEOUT: seconds before timeout (default: 300)
ON_ERROR: continue|stop|notify (default: continue)
WORKING_DIR: /path/to/dir (optional)
ENV: KEY=value (optional, multiple allowed)
```

## Development Commands

### Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test
pytest tests/test_parser.py
```

### Running
```bash
# Development mode (verbose)
python -m batman --debug

# Run specific task file
python -m batman run tasks/maintenance.txt

# Validate task file
python -m batman validate tasks/maintenance.txt
```

## Key Design Decisions

1. **No User Interaction**: All decisions must be made automatically
   - Default to safe options
   - Log decisions for review
   - Never block on input

2. **Robust Error Handling**:
   - Every external call wrapped in try/except
   - Timeouts on all operations
   - Graceful degradation

3. **Security**:
   - Validate all commands before execution
   - Run with minimal privileges
   - Sanitize all inputs
   - No shell injection vulnerabilities

4. **Monitoring**:
   - Health check endpoint
   - Metrics collection
   - Alert on repeated failures

## Common Patterns

### Adding a New Task Type
1. Define parser rules in `src/parser.py`
2. Implement executor in `src/executor.py`
3. Add tests in `tests/test_[component].py`
4. Update documentation

### Error Handling Pattern
```python
def execute_task(task):
    for attempt in range(task.retries):
        try:
            result = run_command(task.command, timeout=task.timeout)
            return result
        except TimeoutError:
            logger.warning(f"Timeout on attempt {attempt + 1}")
        except Exception as e:
            logger.error(f"Error on attempt {attempt + 1}: {e}")
    
    # All retries failed
    handle_failure(task)
```

## Claude Squad Task Distribution

When using 4 instances:

1. **Parser Instance** (Branch: feature/task-parser)
   - Work on: src/parser.py, src/models.py
   - Focus: Robust parsing of task files

2. **Executor Instance** (Branch: feature/task-executor)
   - Work on: src/executor.py, src/error_handler.py
   - Focus: Safe command execution with retries

3. **Scheduler Instance** (Branch: feature/scheduler)
   - Work on: src/scheduler.py, src/cron_integration.py
   - Focus: Reliable scheduling system

4. **Testing Instance** (Branch: feature/tests)
   - Work on: tests/*, integration tests
   - Focus: High test coverage, edge cases

## Security Considerations

- Never execute commands with shell=True without validation
- Validate all file paths
- Run with minimal required permissions
- Log all executed commands
- Implement command whitelist/blacklist

## Monitoring & Alerting

- Log to both file and syslog
- Implement health checks
- Alert on:
  - Repeated task failures
  - Scheduler not running
  - Disk space for logs
  - Long-running tasks

## Future Enhancements

- Web UI for task monitoring
- Task dependencies
- Distributed execution
- Docker container support
- Cloud backup integration