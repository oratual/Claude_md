# Batman Incorporated API Reference

## Table of Contents

1. [Command Line Interface](#command-line-interface)
2. [Core APIs](#core-apis)
3. [Agent APIs](#agent-apis)
4. [Execution Mode APIs](#execution-mode-apis)
5. [Utility APIs](#utility-apis)
6. [Configuration API](#configuration-api)
7. [Extension Points](#extension-points)

## Command Line Interface

### Basic Usage

```bash
batman "task description" [options]
```

### Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--mode` | `-m` | Execution mode (safe/fast/redundant/infinity) | `batman "create API" --mode safe` |
| `--real-agents` | `-r` | Use actual Claude CLI agents | `batman "fix bug" --real-agents` |
| `--auto` | `-a` | Enable automatic 24/7 mode | `batman --auto` |
| `--status` | `-s` | Show system status | `batman --status` |
| `--install-tools` | | Install Arsenal tools | `batman --install-tools` |
| `--config` | `-c` | Custom config file | `batman "task" --config custom.yaml` |
| `--verbose` | `-v` | Verbose output | `batman "task" -v` |
| `--help` | `-h` | Show help | `batman --help` |

### Execution Modes

- **safe** (default): Creates isolated Git worktrees for each agent
- **fast**: Direct execution on main branch
- **redundant**: Multiple agents work on same task
- **infinity**: Parallel execution with multiple instances

## Core APIs

### BatmanIncorporated Class

The main orchestrator that coordinates all agents and execution.

```python
from src.core.batman import BatmanIncorporated
from src.core.config import Config

# Initialize
config = Config()
batman = BatmanIncorporated(config)

# Execute a task
result = batman.execute_task(
    task_description="implement user authentication",
    mode="safe",
    real_agents=True
)

# Analyze and plan tasks
tasks = batman._analyze_and_plan("create REST API for blog")

# Determine optimal execution mode
mode = batman._determine_execution_mode(tasks)

# Generate session report
report = batman._generate_session_report(session_data)
```

### Task System

#### Task Class

```python
from src.core.task import Task, TaskStatus, TaskPriority, TaskType

# Create a task
task = Task(
    title="Implement login API",
    description="Create JWT-based authentication",
    type=TaskType.DEVELOPMENT,
    priority=TaskPriority.HIGH,
    assigned_to="alfred",
    dependencies=["setup-database", "create-user-model"]
)

# Task lifecycle
task.start()  # Set status to IN_PROGRESS
task.update_progress(0.5, "Database models created")
task.complete("Successfully implemented login API")

# Check readiness (all dependencies completed)
if task.is_ready():
    execute_task(task)

# Access properties
print(task.status)  # TaskStatus.COMPLETED
print(task.duration)  # Time taken
print(task.result)  # Completion message
```

#### TaskBatch Class

```python
from src.core.task import TaskBatch

# Create a batch of related tasks
batch = TaskBatch(
    title="User Authentication Feature",
    tasks=[
        Task("Setup database", type=TaskType.INFRASTRUCTURE),
        Task("Create user model", type=TaskType.DEVELOPMENT),
        Task("Implement JWT", type=TaskType.DEVELOPMENT),
        Task("Write tests", type=TaskType.TESTING)
    ]
)

# Batch operations
batch.start_all()
ready_tasks = batch.get_ready_tasks()
batch.complete_all()

# Get statistics
stats = batch.get_statistics()
print(f"Completed: {stats['completed']}/{stats['total']}")
```

### Configuration System

```python
from src.core.config import Config

# Load configuration
config = Config("custom_config.yaml")

# Access configuration values
alfred_enabled = config.get("agents.alfred.enabled")
max_parallel = config.get("execution.max_parallel_agents", default=5)

# Set configuration values
config.set("execution.mode", "safe")

# Access nested configuration
tool_preferences = config.get("tools.preferences")

# Save configuration
config.save("updated_config.yaml")

# Variable expansion
base_path = config.get("paths.base")  # Expands ${HOME}/glados
```

### Arsenal (Tool Management)

```python
from src.core.arsenal import Arsenal

arsenal = Arsenal()

# Get optimal tool for operation
search_tool = arsenal.get_tool("search")  # Returns "rg" if available

# Use Arsenal's unified API
results = arsenal.search_text("TODO", "src/")
files = arsenal.find_files("*.py", "src/")
arsenal.view_file("src/core/batman.py")

# Check tool availability
if arsenal.has_tool("ripgrep"):
    # Use advanced features
    arsenal.search_with_context("pattern", "src/", context_lines=3)

# Get tool suggestions
suggestions = arsenal.get_missing_tools()
arsenal.install_tools(suggestions)
```

## Agent APIs

### BaseAgent (Abstract Class)

All agents inherit from this base class.

```python
from src.agents.base import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self, logger):
        super().__init__("CustomAgent", logger)
        self.specialties = ["custom", "special"]
    
    def should_handle_task(self, task_description):
        # Implement task matching logic
        return any(word in task_description.lower() 
                  for word in self.specialties)
```

### Agent Execution

```python
from src.agents.alfred import AlfredAgent
from src.core.task import Task

# Create agent
alfred = AlfredAgent(logger)

# Execute a task
task = Task("Create REST API", type=TaskType.DEVELOPMENT)
success = alfred.execute_task(
    task,
    mode="safe",
    real_agent=True,
    context_files=["README.md", "requirements.txt"]
)

# Check agent specialties
if alfred.should_handle_task("implement backend API"):
    alfred.execute_task(task)

# Get agent statistics
stats = alfred.get_statistics()
print(f"Tasks completed: {stats['tasks_completed']}")
```

### Specialized Agents

```python
from src.agents import (
    AlfredAgent,  # Senior developer
    RobinAgent,   # DevOps & junior dev
    OracleAgent,  # QA & security
    BatgirlAgent, # Frontend specialist
    LuciusAgent   # R&D & innovation
)

# Each agent has specific strengths
agents = {
    "backend": AlfredAgent(logger),
    "infrastructure": RobinAgent(logger),
    "testing": OracleAgent(logger),
    "frontend": BatgirlAgent(logger),
    "research": LuciusAgent(logger)
}

# Assign tasks based on specialty
for task in tasks:
    for agent_type, agent in agents.items():
        if agent.should_handle_task(task.description):
            agent.execute_task(task)
            break
```

## Execution Mode APIs

### Safe Mode

```python
from src.execution.safe_mode import SafeMode

safe_mode = SafeMode(config, logger)

# Execute tasks with isolation
results = safe_mode.execute(
    tasks,
    agents={"alfred": alfred, "robin": robin},
    real_agents=True
)

# Safe mode automatically:
# 1. Creates Git worktrees for each agent
# 2. Executes tasks in isolation
# 3. Merges results back to main
# 4. Cleans up worktrees
```

### Fast Mode

```python
from src.execution.fast_mode import FastMode

fast_mode = FastMode(config, logger)

# Execute directly on main branch
results = fast_mode.execute(
    tasks,
    agents={"alfred": alfred},
    real_agents=True
)
```

### Redundant Mode

```python
from src.execution.redundant_mode import RedundantMode

redundant_mode = RedundantMode(config, logger)

# Multiple agents work on same task
results = redundant_mode.execute(
    tasks,
    agents={"alfred": alfred, "robin": robin, "oracle": oracle},
    real_agents=True,
    strategy="voting"  # or "best", "merge"
)
```

### Infinity Mode

```python
from src.execution.infinity_mode import InfinityMode

infinity_mode = InfinityMode(config, logger)

# Launch parallel execution
infinity_mode.execute(
    tasks,
    agents=all_agents,
    real_agents=True,
    max_parallel=10
)

# Note: Requires manual terminal management
# Each agent runs in separate terminal
```

## Utility APIs

### ChapterLogger

Narrative logging system for clear progress tracking.

```python
from src.features.chapter_logger import ChapterLogger

logger = ChapterLogger("batman-session-001")

# Start a chapter
logger.chapter("🔍 Analysis Phase")
logger.log("Analyzing task requirements...")
logger.indent()
logger.log("Found 3 subtasks")
logger.log("Estimated time: 2 hours")
logger.unindent()

# Log with different levels
logger.success("✅ Database connection established")
logger.warning("⚠️ Missing API documentation")
logger.error("❌ Test failed: user_authentication")

# Conditional logging
logger.discovery("💡 Found existing authentication module")
logger.decision("🤔 Decided to refactor rather than rewrite")

# Save narrative log
logger.save()
```

### SessionReporter

Generate comprehensive session reports.

```python
from src.features.session_reporter import SessionReporter

reporter = SessionReporter(config)

# Generate report after session
report = reporter.generate_report(
    session_id="batman-session-001",
    tasks=completed_tasks,
    agents=used_agents,
    start_time=start,
    end_time=end
)

# Report includes:
# - Executive summary
# - Task breakdown
# - Agent performance
# - Timeline
# - Artifacts created
# - Recommendations

# Auto-commit to repository
reporter.commit_report(report)
```

### GitHub Integration

```python
from src.integrations.github_integration import GitHubIntegration

github = GitHubIntegration(logger)

# Create pull request
pr_url = github.create_pr(
    title="feat: Add user authentication",
    branch="feature/auth",
    body="Implements JWT-based authentication"
)

# Manage issues
issue = github.create_issue(
    title="Add rate limiting",
    body="Need to implement API rate limiting",
    labels=["enhancement", "backend"]
)

# Setup CI/CD
github.setup_ci(
    test_command="python -m pytest",
    lint_command="ruff check ."
)

# Get PR feedback
comments = github.get_pr_comments(pr_number=123)
```

### MCP Integration

```python
from src.integrations.mcp_integration import MCPIntegration

mcp = MCPIntegration(config)

# Share context between agents
mcp.share_context(
    key="api_design",
    value={"endpoints": [...], "schemas": {...}},
    agents=["alfred", "oracle"]
)

# Retrieve shared context
api_design = mcp.get_context("api_design")

# Persistent knowledge
mcp.store_knowledge(
    category="patterns",
    key="authentication",
    value="JWT implementation pattern used"
)
```

## Configuration API

### YAML Configuration Structure

```yaml
# config/default_config.yaml
agents:
  alfred:
    enabled: true
    specialties: ["backend", "api", "architecture"]
    model: "claude-3-opus-20240229"
  
  robin:
    enabled: true
    specialties: ["devops", "automation", "infrastructure"]

execution:
  default_mode: "safe"
  max_parallel_agents: 5
  timeout_minutes: 30

tools:
  preferences:
    search: "ripgrep"  # Falls back to grep
    find: "fd"         # Falls back to find
    view: "bat"        # Falls back to cat

paths:
  base: "${HOME}/glados/batman-incorporated"
  logs: "${paths.base}/logs"
  tasks: "${paths.base}/tasks"

features:
  chapter_logging: true
  session_reports: true
  github_integration: true
  mcp_integration: false
```

### Dynamic Configuration

```python
# Runtime configuration updates
config.set("agents.alfred.model", "claude-3-sonnet-20240229")
config.set("execution.max_parallel_agents", 10)

# Feature flags
if config.get("features.dream_mode"):
    enable_experimental_features()

# Environment-specific config
if config.get("environment") == "production":
    config.set("execution.safety_checks", True)
```

## Extension Points

### Creating Custom Agents

```python
from src.agents.base import BaseAgent

class DataScienceAgent(BaseAgent):
    def __init__(self, logger):
        super().__init__("DataScientist", logger)
        self.specialties = [
            "data analysis", "machine learning",
            "visualization", "statistics"
        ]
    
    def should_handle_task(self, task_description):
        keywords = ["analyze", "predict", "visualize", "dataset"]
        return any(kw in task_description.lower() for kw in keywords)
```

### Creating Custom Execution Modes

```python
from src.execution.base import ExecutionMode

class StreamMode(ExecutionMode):
    """Execute tasks as a continuous stream"""
    
    def execute(self, tasks, agents, real_agents=False):
        for task in tasks:
            # Assign to next available agent
            agent = self.get_next_available_agent(agents)
            result = agent.execute_task(task, real_agent=real_agents)
            self.stream_result(result)
```

### Custom Tools in Arsenal

```python
# Register a custom tool
arsenal.register_tool(
    operation="analyze",
    tool_name="custom-analyzer",
    command="analyzer --deep {pattern} {path}",
    check_command="analyzer --version"
)

# Use custom tool
results = arsenal.analyze_code("complexity", "src/")
```

### Plugin System (Future)

```python
# plugins/security_scanner.py
class SecurityScannerPlugin:
    def on_task_complete(self, task, result):
        # Scan code for vulnerabilities
        vulnerabilities = self.scan(result.files_changed)
        if vulnerabilities:
            self.alert(vulnerabilities)
    
    def on_session_start(self, session):
        # Initialize security monitoring
        self.monitor = SecurityMonitor(session)

# Register plugin
batman.register_plugin(SecurityScannerPlugin())
```

## Error Handling

```python
from src.core.exceptions import (
    BatmanException,
    AgentException,
    TaskException,
    ConfigException
)

try:
    batman.execute_task("complex task")
except AgentException as e:
    logger.error(f"Agent failed: {e.agent_name} - {e.message}")
    # Retry with different agent
except TaskException as e:
    logger.error(f"Task failed: {e.task_id} - {e.message}")
    # Mark task as failed, continue with others
except BatmanException as e:
    logger.error(f"System error: {e.message}")
    # Graceful shutdown
```

## Best Practices

1. **Task Granularity**: Break complex tasks into smaller, focused subtasks
2. **Agent Selection**: Let the system choose agents based on specialties
3. **Mode Selection**: Use safe mode for complex multi-file changes
4. **Context Files**: Provide relevant context files for better agent performance
5. **Error Recovery**: Implement retry logic for failed tasks
6. **Logging**: Use ChapterLogger for clear progress tracking
7. **Configuration**: Use YAML configs for reproducible setups

## Performance Tips

1. **Parallel Execution**: Use infinity mode for independent tasks
2. **Tool Selection**: Install modern tools (ripgrep, fd) for better performance
3. **Caching**: MCP integration provides knowledge persistence
4. **Batch Operations**: Group related tasks in TaskBatch
5. **Resource Limits**: Configure max_parallel_agents based on system resources

---

For more examples and tutorials, see [EXAMPLES.md](EXAMPLES.md).
For system architecture details, see [ARCHITECTURE.md](ARCHITECTURE.md).