# Batman Incorporated Examples

This directory contains practical examples demonstrating how to use Batman Incorporated's features.

## Example Files

### 1. `basic_usage.py`
Basic examples showing:
- Simple task execution
- Using different execution modes
- Custom configuration
- Batch task processing
- System status checking
- Automatic mode setup

### 2. `advanced_scenarios.py`
Complex real-world scenarios:
- Building microservices architecture
- Performance optimization workflow
- Security audit and remediation
- AI-powered code review
- Emergency hotfix process
- Large-scale technology migration
- Parallel feature development

### 3. `custom_agents.py`
Creating and using custom agents:
- DataScientist agent for ML tasks
- Mobile developer agent
- Blockchain developer agent
- Game developer agent
- Cloud architect agent
- Agent collaboration examples
- Extending Batman with new agents

## Running Examples

### Prerequisites
1. Batman Incorporated installed and configured
2. Claude CLI available in PATH
3. Python 3.8+ with dependencies installed

### Basic Examples
```bash
cd batman-incorporated
python examples/basic_usage.py
```

### Advanced Scenarios
```bash
python examples/advanced_scenarios.py
```

### Custom Agents
```bash
python examples/custom_agents.py
```

## Example Categories

### Task Execution
- Single task execution
- Batch processing
- Mode selection
- Progress monitoring

### Configuration
- Custom settings
- Agent preferences
- Tool selection
- Execution modes

### Integration
- GitHub integration
- MCP context sharing
- Tool arsenal usage
- Report generation

### Advanced Features
- Parallel execution
- Multi-agent coordination
- Emergency workflows
- Performance optimization

## Creating Your Own Examples

When creating custom examples:

1. **Import required modules**:
   ```python
   from src.core.config import Config
   from src.core.batman import BatmanIncorporated
   from src.core.task import Task, TaskType, TaskPriority
   ```

2. **Initialize Batman**:
   ```python
   config = Config()
   batman = BatmanIncorporated(config, verbose=True)
   ```

3. **Execute tasks**:
   ```python
   batman.execute_task("your task description", mode="preferred_mode")
   ```

4. **Handle results**:
   ```python
   if success:
       print("Task completed!")
   else:
       print("Task failed - check logs")
   ```

## Best Practices

1. **Use appropriate execution modes**:
   - `seguro`: For safe, isolated changes
   - `rapido`: For quick, simple tasks
   - `redundante`: For critical tasks needing validation
   - `infinity`: For massively parallel workloads

2. **Leverage agent specialties**:
   - Alfred: Backend and architecture
   - Robin: DevOps and automation
   - Oracle: Testing and security
   - Batgirl: Frontend and UI
   - Lucius: Research and optimization

3. **Monitor progress**:
   - Use verbose mode for debugging
   - Check ChapterLogger output
   - Review session reports

4. **Handle errors gracefully**:
   - Always check return values
   - Use try-except blocks
   - Create GitHub issues for failures

## Common Patterns

### Sequential Task Execution
```python
tasks = ["task1", "task2", "task3"]
for task in tasks:
    if not batman.execute_task(task):
        break  # Stop on failure
```

### Parallel Task Execution
```python
batman.execute_task(
    "implement multiple independent features",
    mode="infinity"
)
```

### Mode Selection Logic
```python
if task_is_critical:
    mode = "redundante"
elif task_is_simple:
    mode = "rapido"
elif has_conflicts:
    mode = "seguro"
else:
    mode = "auto"
```

## Troubleshooting

### Common Issues

1. **Claude CLI not found**:
   - Ensure Claude CLI is installed
   - Check PATH environment variable

2. **Task execution fails**:
   - Check logs in `~/.glados/logs/`
   - Verify file permissions
   - Ensure Git repository is clean

3. **Agent selection issues**:
   - Review task description clarity
   - Check agent specialties match
   - Use verbose mode for debugging

### Debug Mode
```python
# Enable maximum verbosity
config = Config()
config.set("logging.level", "DEBUG")
batman = BatmanIncorporated(config, verbose=True)
```

## Further Resources

- [API Documentation](../docs/API.md)
- [Architecture Guide](../docs/ARCHITECTURE.md)
- [Execution Modes](../docs/EXECUTION_MODES.md)
- [Main README](../README.md)