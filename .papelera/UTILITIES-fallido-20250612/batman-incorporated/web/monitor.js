// Batman Incorporated Agent Monitor
class AgentMonitor {
    constructor() {
        this.agents = {
            alfred: { name: 'Alfred', status: 'idle', task: '', progress: 0, files: [] },
            robin: { name: 'Robin', status: 'idle', task: '', progress: 0, files: [] },
            oracle: { name: 'Oracle', status: 'idle', task: '', progress: 0, files: [] },
            batgirl: { name: 'Batgirl', status: 'idle', task: '', progress: 0, files: [] },
            lucius: { name: 'Lucius', status: 'idle', task: '', progress: 0, files: [] }
        };
        
        this.stats = {
            totalTasks: 0,
            completedTasks: 0,
            activeAgents: 0,
            filesModified: 0
        };
        
        this.activityLog = [];
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectDelay = 5000;
        
        // Mock data for demonstration when no WebSocket server is available
        this.useMockData = true;
        this.mockInterval = null;
        
        this.init();
    }
    
    init() {
        this.updateClock();
        setInterval(() => this.updateClock(), 1000);
        
        // Try to connect to WebSocket
        this.connectWebSocket();
        
        // If no WebSocket, use mock data
        if (this.useMockData) {
            setTimeout(() => this.startMockUpdates(), 2000);
        }
    }
    
    connectWebSocket() {
        try {
            // Try to connect to a local WebSocket server
            this.ws = new WebSocket('ws://localhost:8765/monitor');
            
            this.ws.onopen = () => {
                this.updateConnectionStatus(true);
                this.addLogEntry('Connected to Batman Incorporated server', 'success');
                this.reconnectAttempts = 0;
                this.useMockData = false;
                
                if (this.mockInterval) {
                    clearInterval(this.mockInterval);
                    this.mockInterval = null;
                }
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleServerUpdate(data);
                } catch (error) {
                    console.error('Error parsing message:', error);
                }
            };
            
            this.ws.onclose = () => {
                this.updateConnectionStatus(false);
                this.addLogEntry('Connection lost. Attempting to reconnect...', 'error');
                this.attemptReconnect();
            };
            
            this.ws.onerror = () => {
                this.updateConnectionStatus(false);
                if (this.reconnectAttempts === 0) {
                    this.addLogEntry('No server detected. Using demonstration mode.', 'warning');
                }
            };
            
        } catch (error) {
            console.error('WebSocket connection error:', error);
            this.updateConnectionStatus(false);
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => this.connectWebSocket(), this.reconnectDelay);
        } else {
            this.addLogEntry('Max reconnection attempts reached. Using offline mode.', 'error');
            this.useMockData = true;
            this.startMockUpdates();
        }
    }
    
    handleServerUpdate(data) {
        if (data.type === 'agent_update') {
            this.updateAgent(data.agent, data.status, data.task, data.progress, data.files);
        } else if (data.type === 'stats_update') {
            this.updateStats(data.stats);
        } else if (data.type === 'log_entry') {
            this.addLogEntry(data.message, data.level);
        }
    }
    
    startMockUpdates() {
        // Simulate agent activities for demonstration
        const mockTasks = [
            { agent: 'alfred', task: 'Implementing API endpoints for user authentication', files: ['src/api/auth.py', 'src/api/users.py'] },
            { agent: 'robin', task: 'Setting up CI/CD pipeline with GitHub Actions', files: ['.github/workflows/ci.yml', 'scripts/deploy.sh'] },
            { agent: 'oracle', task: 'Writing unit tests for core modules', files: ['tests/test_core.py', 'tests/test_api.py'] },
            { agent: 'batgirl', task: 'Creating responsive dashboard components', files: ['components/Dashboard.jsx', 'styles/dashboard.css'] },
            { agent: 'lucius', task: 'Researching WebSocket optimization techniques', files: ['docs/websocket-research.md', 'src/realtime/socket.js'] }
        ];
        
        let taskIndex = 0;
        
        this.mockInterval = setInterval(() => {
            if (taskIndex < mockTasks.length) {
                const task = mockTasks[taskIndex];
                this.simulateAgentWork(task.agent, task.task, task.files);
                taskIndex++;
            } else {
                // Random updates after initial tasks
                const agents = Object.keys(this.agents);
                const randomAgent = agents[Math.floor(Math.random() * agents.length)];
                const randomProgress = Math.floor(Math.random() * 20) + 10;
                
                if (this.agents[randomAgent].status === 'active') {
                    const currentProgress = this.agents[randomAgent].progress;
                    const newProgress = Math.min(100, currentProgress + randomProgress);
                    
                    this.updateAgent(randomAgent, 'active', null, newProgress);
                    
                    if (newProgress >= 100) {
                        this.completeAgentTask(randomAgent);
                    }
                }
            }
        }, 3000);
    }
    
    simulateAgentWork(agentId, task, files) {
        this.updateAgent(agentId, 'active', task, 10, files);
        this.addLogEntry(`${this.agents[agentId].name} started: ${task}`, 'success');
        
        // Simulate progress updates
        let progress = 10;
        const progressInterval = setInterval(() => {
            progress += Math.floor(Math.random() * 20) + 10;
            if (progress >= 100) {
                progress = 100;
                this.updateAgent(agentId, 'active', null, progress);
                setTimeout(() => this.completeAgentTask(agentId), 1000);
                clearInterval(progressInterval);
            } else {
                this.updateAgent(agentId, 'active', null, progress);
            }
        }, 2000);
    }
    
    completeAgentTask(agentId) {
        const agent = this.agents[agentId];
        this.addLogEntry(`${agent.name} completed: ${agent.task}`, 'success');
        this.updateAgent(agentId, 'idle', 'Task completed', 0);
        this.stats.completedTasks++;
        this.updateStatsDisplay();
    }
    
    updateAgent(agentId, status, task, progress, files) {
        const agent = this.agents[agentId];
        
        if (status) {
            const wasActive = agent.status === 'active';
            agent.status = status;
            
            if (status === 'active' && !wasActive) {
                this.stats.activeAgents++;
                this.stats.totalTasks++;
            } else if (status !== 'active' && wasActive) {
                this.stats.activeAgents--;
            }
        }
        
        if (task !== null) {
            agent.task = task;
        }
        
        if (progress !== null) {
            agent.progress = progress;
        }
        
        if (files) {
            agent.files = files;
            this.stats.filesModified += files.length;
        }
        
        this.updateAgentCard(agentId);
        this.updateStatsDisplay();
    }
    
    updateAgentCard(agentId) {
        const agent = this.agents[agentId];
        const card = document.getElementById(`agent-${agentId}`);
        
        if (!card) return;
        
        // Update status badge
        const statusBadge = card.querySelector('.status-badge');
        statusBadge.className = `status-badge ${agent.status}`;
        statusBadge.textContent = agent.status.toUpperCase();
        
        // Update task description
        const taskDesc = card.querySelector('.task-description');
        taskDesc.textContent = agent.task || 'Waiting for assignment...';
        
        // Update progress
        const progressFill = card.querySelector('.progress-fill');
        const progressText = card.querySelector('.progress-text');
        progressFill.style.width = `${agent.progress}%`;
        progressText.textContent = `${agent.progress}%`;
        
        // Update file list
        const fileList = card.querySelector('.file-list');
        fileList.innerHTML = '';
        agent.files.forEach(file => {
            const li = document.createElement('li');
            li.textContent = file;
            li.title = file; // Show full path on hover
            fileList.appendChild(li);
        });
    }
    
    updateStatsDisplay() {
        document.getElementById('total-tasks').textContent = this.stats.totalTasks;
        document.getElementById('completed-tasks').textContent = this.stats.completedTasks;
        document.getElementById('active-agents').textContent = this.stats.activeAgents;
        document.getElementById('files-modified').textContent = this.stats.filesModified;
    }
    
    updateConnectionStatus(connected) {
        const indicator = document.getElementById('connection-status');
        const text = document.getElementById('connection-text');
        
        if (connected) {
            indicator.classList.add('connected');
            text.textContent = 'Connected';
        } else {
            indicator.classList.remove('connected');
            text.textContent = 'Disconnected';
        }
    }
    
    addLogEntry(message, level = 'info') {
        const logContainer = document.getElementById('activity-log');
        const entry = document.createElement('div');
        entry.className = `log-entry ${level}`;
        
        const timestamp = new Date().toLocaleTimeString('en-US', { hour12: false });
        
        entry.innerHTML = `
            <span class="timestamp">${timestamp}</span>
            <span class="message">${message}</span>
        `;
        
        // Add to log array
        this.activityLog.push({ timestamp, message, level });
        
        // Add to DOM and scroll to bottom
        logContainer.appendChild(entry);
        logContainer.scrollTop = logContainer.scrollHeight;
        
        // Limit log entries to prevent memory issues
        if (logContainer.children.length > 100) {
            logContainer.removeChild(logContainer.firstChild);
        }
    }
    
    updateClock() {
        const clock = document.getElementById('clock');
        const now = new Date();
        clock.textContent = now.toLocaleTimeString('en-US', { hour12: false });
    }
    
    // Public API for external updates
    updateFromBash(data) {
        // This method can be called from external scripts to update the monitor
        this.handleServerUpdate(data);
    }
}

// Initialize the monitor when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.agentMonitor = new AgentMonitor();
});

// Handle visibility change to pause/resume updates
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Pause updates when tab is not visible
        if (window.agentMonitor && window.agentMonitor.mockInterval) {
            clearInterval(window.agentMonitor.mockInterval);
        }
    } else {
        // Resume updates when tab becomes visible
        if (window.agentMonitor && window.agentMonitor.useMockData && !window.agentMonitor.mockInterval) {
            window.agentMonitor.startMockUpdates();
        }
    }
});