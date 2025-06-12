# Batman Incorporated Examples

## Table of Contents

1. [Quick Start](#quick-start)
2. [Basic Usage Examples](#basic-usage-examples)
3. [Real-World Scenarios](#real-world-scenarios)
4. [Advanced Examples](#advanced-examples)
5. [Integration Examples](#integration-examples)
6. [Troubleshooting Examples](#troubleshooting-examples)

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/oratual/Batman-Incorporated.git
cd Batman-Incorporated

# Run setup
./setup.sh

# Install modern tools (optional but recommended)
./batman.py --install-tools
```

### Your First Command

```bash
# Simple task (simulated agents)
./batman.py "create a hello world Python script"

# With real Claude agents
./batman.py "create a hello world Python script" --real-agents
```

## Basic Usage Examples

### 1. Creating a Simple Script

```bash
# Batman will analyze, assign to appropriate agent, and execute
./batman.py "create a Python script that counts words in a file"
```

**What happens:**
1. Batman analyzes the task
2. Assigns to Alfred (backend development)
3. Creates the script with proper error handling
4. Adds basic documentation

### 2. Building a Web API

```bash
# Complex task involving multiple agents
./batman.py "create a REST API for a todo list with authentication" --real-agents
```

**Agent assignments:**
- **Alfred**: API design and implementation
- **Robin**: Database setup and deployment config
- **Oracle**: Security review and testing
- **Batgirl**: API documentation and examples
- **Lucius**: Performance optimization suggestions

### 3. Fixing Bugs

```bash
# Batman will find and fix the bug
./batman.py "fix the authentication bug in src/auth.py" --mode fast
```

**Fast mode**: Direct execution without isolation, perfect for quick fixes.

### 4. Adding Tests

```bash
# Oracle specializes in testing
./batman.py "add comprehensive tests for the user service"
```

**Oracle will:**
- Analyze existing code
- Create unit tests
- Add integration tests
- Setup test fixtures
- Ensure good coverage

## Real-World Scenarios

### Scenario 1: Full-Stack Feature Development

```bash
./batman.py "implement user profile feature with avatar upload" --real-agents --mode safe
```

**Execution flow:**

```yaml
Analysis:
  - Backend API for profile management
  - File upload handling
  - Frontend profile page
  - Image optimization
  - Security considerations

Agent Assignments:
  Alfred:
    - Create profile model
    - Implement CRUD API
    - Add file upload endpoint
  
  Batgirl:
    - Design profile UI
    - Create upload component
    - Add image preview
  
  Robin:
    - Setup S3 bucket
    - Configure CDN
    - Add deployment scripts
  
  Oracle:
    - Security audit
    - Write tests
    - Validate file types
  
  Lucius:
    - Image optimization research
    - Performance recommendations
```

### Scenario 2: Refactoring Legacy Code

```bash
./batman.py "refactor the legacy payment system to use modern patterns" --mode redundant
```

**Redundant mode benefits:**
- Multiple agents propose solutions
- Compare different approaches
- Select best implementation
- Higher quality output

### Scenario 3: Emergency Hotfix

```bash
./batman.py "URGENT: fix the memory leak in production" --mode fast --real-agents
```

**Fast mode for emergencies:**
```python
# Batman quickly:
# 1. Identifies the leak
# 2. Implements fix
# 3. Adds monitoring
# 4. Creates hotfix branch
# 5. Prepares deployment
```

### Scenario 4: Documentation Sprint

```bash
./batman.py "document all APIs and create user guides" --real-agents
```

**Lucius leads with support from all agents:**
```markdown
Generated Documentation:
- API Reference (OpenAPI spec)
- User Guides
- Developer Tutorials
- Architecture Diagrams
- Deployment Guide
```

## Advanced Examples

### 1. Parallel Task Execution (Infinity Mode)

```bash
# Launch parallel execution for independent tasks
./batman.py "migrate all JavaScript files to TypeScript" --mode infinity --real-agents
```

**Setup required:**
```bash
# Terminal 1: Monitor
./monitor_parallel_progress.sh

# Terminal 2-N: Agent instances
# Batman will provide instructions for launching agents
```

### 2. Custom Configuration

```yaml
# custom_config.yaml
agents:
  alfred:
    model: "claude-3-opus-20240229"  # Use Opus for complex tasks
  robin:
    enabled: false  # Disable if not needed

execution:
  max_parallel_agents: 10
  timeout_minutes: 60

features:
  dream_mode: true  # Enable experimental features
```

```bash
./batman.py "implement complex feature" --config custom_config.yaml
```

### 3. Batch Operations

```python
# batch_tasks.py
from src.core.batman import BatmanIncorporated
from src.core.task import Task, TaskBatch, TaskType

batman = BatmanIncorporated()

# Create batch of related tasks
batch = TaskBatch("E-commerce Platform", [
    Task("Setup database schema", type=TaskType.INFRASTRUCTURE),
    Task("Create product API", type=TaskType.DEVELOPMENT),
    Task("Implement shopping cart", type=TaskType.DEVELOPMENT),
    Task("Add payment integration", type=TaskType.DEVELOPMENT),
    Task("Create admin dashboard", type=TaskType.DEVELOPMENT),
    Task("Write integration tests", type=TaskType.TESTING),
    Task("Setup CI/CD", type=TaskType.INFRASTRUCTURE),
])

# Execute with progress tracking
results = batman.execute_batch(batch, mode="safe", real_agents=True)
```

### 4. Continuous Development Mode

```bash
# Start Batman in auto mode for 24/7 development
./batman.py --auto --real-agents
```

**Auto mode features:**
- Monitors task queue
- Automatically assigns agents
- Manages resource allocation
- Generates daily reports
- Handles failures gracefully

## Integration Examples

### 1. GitHub Workflow

```bash
# Create feature with automatic PR
./batman.py "implement user notifications feature and create PR" --real-agents
```

**Batman will:**
1. Create feature branch
2. Implement the feature
3. Run tests
4. Create pull request
5. Add reviewers

### 2. CI/CD Integration

```yaml
# .github/workflows/batman.yml
name: Batman Automated Tasks

on:
  issues:
    types: [labeled]

jobs:
  batman-execute:
    if: contains(github.event.label.name, 'batman-task')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Batman
        run: ./setup.sh
      - name: Execute Task
        run: |
          ./batman.py "${{ github.event.issue.title }}" \
            --real-agents \
            --mode safe
      - name: Create PR
        run: |
          gh pr create \
            --title "Batman: ${{ github.event.issue.title }}" \
            --body "Automated implementation by Batman Incorporated"
```

### 3. MCP Integration

```python
# Enable shared context between agents
from src.integrations.mcp_integration import MCPIntegration

mcp = MCPIntegration()

# Share API design across agents
mcp.share_context("api_design", {
    "endpoints": ["/users", "/products", "/orders"],
    "authentication": "JWT",
    "rate_limiting": "100 req/min"
})

# Agents automatically use shared context
batman.execute_task("implement the API based on shared design")
```

### 4. Arsenal Tools Integration

```bash
# Batman automatically uses best available tools
./batman.py "find all TODO comments and create issues" --real-agents
```

**Arsenal will use:**
- `ripgrep` for fast searching
- `gh` for issue creation
- `bat` for code preview
- `fd` for file discovery

## Troubleshooting Examples

### 1. Debugging Failed Tasks

```bash
# Enable verbose mode for detailed output
./batman.py "complex task" --verbose --real-agents

# Check logs
tail -f logs/batman-session-*.log
```

### 2. Handling Agent Failures

```python
# Automatic retry with different agent
from src.core.batman import BatmanIncorporated

batman = BatmanIncorporated()
batman.config.set("execution.retry_failed_tasks", True)
batman.config.set("execution.max_retries", 3)
```

### 3. Resource Management

```bash
# Monitor resource usage
./batman.py --status

# Output:
# 🦇 Batman Incorporated Status
# ├── Active Agents: 3/5
# ├── Tasks in Queue: 12
# ├── Completed Today: 45
# └── System Load: 65%
```

### 4. Quota Management

```bash
# Check Claude quota before large tasks
claude-quota -q

# If low, use simulated mode for testing
./batman.py "test task" --mode fast  # No --real-agents
```

## Common Patterns

### 1. Feature Development Pattern

```bash
# Step 1: Design
./batman.py "design database schema for blog platform"

# Step 2: Implement
./batman.py "implement blog API based on the schema" --real-agents

# Step 3: Test
./batman.py "add comprehensive tests for blog API"

# Step 4: Deploy
./batman.py "create deployment configuration for blog API"
```

### 2. Refactoring Pattern

```bash
# Analyze first
./batman.py "analyze code quality in src/ and identify issues"

# Then refactor systematically
./batman.py "refactor identified issues with modern patterns" --mode safe
```

### 3. Documentation Pattern

```bash
# Generate all documentation
./batman.py "create complete documentation for the project"

# Batman coordinates:
# - Lucius: Technical documentation
# - Batgirl: User guides
# - Alfred: API documentation
# - Robin: Deployment guides
```

## Tips and Best Practices

### 1. Task Description Tips

```bash
# ❌ Too vague
./batman.py "fix the bug"

# ✅ Specific and actionable
./batman.py "fix the null pointer exception in UserService.authenticate() when email is empty"

# ❌ Too broad
./batman.py "make a website"

# ✅ Scoped and clear
./batman.py "create a landing page with email signup form using React and Tailwind"
```

### 2. Mode Selection Guide

| Mode | Use When | Example |
|------|----------|---------|
| Safe | Multiple file changes | Major features |
| Fast | Quick fixes | Hotfixes, small updates |
| Redundant | Quality critical | Payment systems, auth |
| Infinity | Many independent tasks | Large refactoring |

### 3. Performance Optimization

```bash
# Install modern tools for better performance
./batman.py --install-tools

# Use parallel execution for independent tasks
./batman.py "update all documentation" --mode infinity

# Cache shared context with MCP
./batman.py "implement features based on shared design patterns"
```

### 4. Monitoring and Logging

```bash
# Real-time monitoring
tail -f logs/batman-session-*.log | grep -E "(Chapter|✅|❌)"

# View session report
cat logs/reports/session-*.md

# Check agent performance
./batman.py --status --verbose
```

## Example Projects Built with Batman

### 1. E-commerce API
```bash
./batman.py "create a complete e-commerce REST API with products, cart, and checkout"
```

### 2. Real-time Chat Application
```bash
./batman.py "build a real-time chat app with websockets and user authentication"
```

### 3. Data Pipeline
```bash
./batman.py "create a data pipeline that processes CSV files and stores in PostgreSQL"
```

### 4. CLI Tool
```bash
./batman.py "build a CLI tool for managing Docker containers with Python"
```

---

For more details on the API, see [API.md](API.md).
For architecture information, see [ARCHITECTURE.md](ARCHITECTURE.md).