export class StatsPanel {
    constructor(container) {
        this.container = container;
        this.stats = {
            totalTasks: 0,
            completedTasks: 0,
            activeAgents: 0,
            filesModified: 0,
            successRate: 0,
            avgTaskTime: '00:00'
        };
        this.charts = {};
        this.init();
    }

    init() {
        this.render();
        this.initializeCharts();
    }

    render() {
        this.container.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card" data-stat="totalTasks">
                    <div class="stat-icon">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M9 11H3v10h6V11zm6-7h-6v18h6V4zm6 3h-6v14h6V7z"/>
                        </svg>
                    </div>
                    <div class="stat-content">
                        <h3>Total Tasks</h3>
                        <div class="stat-value" id="total-tasks">0</div>
                        <div class="stat-change">
                            <span class="change-value">+0</span>
                            <span class="change-label">today</span>
                        </div>
                    </div>
                    <canvas class="stat-sparkline" width="100" height="30"></canvas>
                </div>

                <div class="stat-card" data-stat="completedTasks">
                    <div class="stat-icon success">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <polyline points="20 6 9 17 4 12"/>
                        </svg>
                    </div>
                    <div class="stat-content">
                        <h3>Completed</h3>
                        <div class="stat-value" id="completed-tasks">0</div>
                        <div class="stat-progress">
                            <div class="progress-mini">
                                <div class="progress-mini-fill" style="width: 0%"></div>
                            </div>
                            <span class="progress-label">0%</span>
                        </div>
                    </div>
                </div>

                <div class="stat-card" data-stat="activeAgents">
                    <div class="stat-icon active">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                            <circle cx="9" cy="7" r="4"/>
                            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                        </svg>
                    </div>
                    <div class="stat-content">
                        <h3>Active Agents</h3>
                        <div class="stat-value" id="active-agents">0</div>
                        <div class="agent-indicators">
                            <span class="agent-indicator" data-agent="alfred" title="Alfred"></span>
                            <span class="agent-indicator" data-agent="robin" title="Robin"></span>
                            <span class="agent-indicator" data-agent="oracle" title="Oracle"></span>
                            <span class="agent-indicator" data-agent="batgirl" title="Batgirl"></span>
                            <span class="agent-indicator" data-agent="lucius" title="Lucius"></span>
                        </div>
                    </div>
                </div>

                <div class="stat-card" data-stat="filesModified">
                    <div class="stat-icon">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
                            <polyline points="13 2 13 9 20 9"/>
                        </svg>
                    </div>
                    <div class="stat-content">
                        <h3>Files Modified</h3>
                        <div class="stat-value" id="files-modified">0</div>
                        <div class="file-types">
                            <span class="file-type" data-type="js">JS: 0</span>
                            <span class="file-type" data-type="py">PY: 0</span>
                            <span class="file-type" data-type="css">CSS: 0</span>
                        </div>
                    </div>
                </div>

                <div class="stat-card wide" data-stat="performance">
                    <div class="stat-header">
                        <h3>Performance Overview</h3>
                        <div class="time-range-selector">
                            <button class="time-range active" data-range="1h">1H</button>
                            <button class="time-range" data-range="24h">24H</button>
                            <button class="time-range" data-range="7d">7D</button>
                        </div>
                    </div>
                    <div class="performance-chart">
                        <canvas id="performance-chart" width="400" height="150"></canvas>
                    </div>
                    <div class="performance-stats">
                        <div class="perf-stat">
                            <span class="perf-label">Success Rate</span>
                            <span class="perf-value">0%</span>
                        </div>
                        <div class="perf-stat">
                            <span class="perf-label">Avg Task Time</span>
                            <span class="perf-value">00:00</span>
                        </div>
                        <div class="perf-stat">
                            <span class="perf-label">Throughput</span>
                            <span class="perf-value">0/hr</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    initializeCharts() {
        // Initialize sparkline for total tasks
        const sparklineCanvas = this.container.querySelector('[data-stat="totalTasks"] .stat-sparkline');
        if (sparklineCanvas) {
            this.charts.taskSparkline = this.createSparkline(sparklineCanvas);
        }

        // Initialize performance chart
        const perfCanvas = this.container.querySelector('#performance-chart');
        if (perfCanvas) {
            this.charts.performance = this.createPerformanceChart(perfCanvas);
        }

        // Attach event listeners for time range selector
        this.container.querySelectorAll('.time-range').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.handleTimeRangeChange(e.target.dataset.range);
            });
        });
    }

    createSparkline(canvas) {
        const ctx = canvas.getContext('2d');
        const data = new Array(20).fill(0);
        
        const draw = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.strokeStyle = 'rgba(159, 122, 234, 0.8)';
            ctx.lineWidth = 2;
            ctx.beginPath();
            
            const stepX = canvas.width / (data.length - 1);
            const maxValue = Math.max(...data, 1);
            
            data.forEach((value, index) => {
                const x = index * stepX;
                const y = canvas.height - (value / maxValue) * canvas.height * 0.8 - 5;
                
                if (index === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });
            
            ctx.stroke();
        };
        
        return { data, draw };
    }

    createPerformanceChart(canvas) {
        const ctx = canvas.getContext('2d');
        const chart = {
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Tasks Completed',
                        data: [],
                        color: '#48bb78'
                    },
                    {
                        label: 'Active Agents',
                        data: [],
                        color: '#9f7aea'
                    }
                ]
            }
        };

        const draw = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Draw grid
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
            ctx.lineWidth = 1;
            
            for (let i = 0; i <= 5; i++) {
                const y = (canvas.height / 5) * i;
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(canvas.width, y);
                ctx.stroke();
            }

            // Draw datasets
            chart.data.datasets.forEach((dataset, datasetIndex) => {
                if (dataset.data.length === 0) return;
                
                ctx.strokeStyle = dataset.color;
                ctx.lineWidth = 2;
                ctx.beginPath();
                
                const stepX = canvas.width / (dataset.data.length - 1);
                const maxValue = Math.max(...dataset.data.flat(), 5);
                
                dataset.data.forEach((value, index) => {
                    const x = index * stepX;
                    const y = canvas.height - (value / maxValue) * canvas.height * 0.9 - 10;
                    
                    if (index === 0) {
                        ctx.moveTo(x, y);
                    } else {
                        ctx.lineTo(x, y);
                    }
                    
                    // Draw point
                    ctx.fillStyle = dataset.color;
                    ctx.beginPath();
                    ctx.arc(x, y, 3, 0, Math.PI * 2);
                    ctx.fill();
                });
                
                ctx.stroke();
            });
        };

        return { ...chart, draw };
    }

    update(newStats) {
        Object.keys(newStats).forEach(key => {
            if (this.stats[key] !== newStats[key]) {
                this.stats[key] = newStats[key];
                this.updateStatDisplay(key, newStats[key]);
            }
        });

        // Update charts
        if (this.charts.taskSparkline) {
            this.charts.taskSparkline.data.shift();
            this.charts.taskSparkline.data.push(this.stats.totalTasks);
            this.charts.taskSparkline.draw();
        }

        // Update agent indicators
        this.updateAgentIndicators(newStats.activeAgentsList || []);
    }

    updateStatDisplay(statKey, value) {
        const element = document.getElementById(statKey.replace(/([A-Z])/g, '-$1').toLowerCase());
        if (element) {
            const oldValue = parseInt(element.textContent) || 0;
            element.textContent = value;
            
            if (oldValue !== value) {
                element.classList.add('updating');
                setTimeout(() => element.classList.remove('updating'), 400);
            }

            // Update progress bar for completed tasks
            if (statKey === 'completedTasks') {
                this.updateCompletionProgress();
            }
        }
    }

    updateCompletionProgress() {
        const progress = this.stats.totalTasks > 0 
            ? Math.round((this.stats.completedTasks / this.stats.totalTasks) * 100)
            : 0;
        
        const progressFill = this.container.querySelector('[data-stat="completedTasks"] .progress-mini-fill');
        const progressLabel = this.container.querySelector('[data-stat="completedTasks"] .progress-label');
        
        if (progressFill) progressFill.style.width = `${progress}%`;
        if (progressLabel) progressLabel.textContent = `${progress}%`;
    }

    updateAgentIndicators(activeAgents) {
        this.container.querySelectorAll('.agent-indicator').forEach(indicator => {
            const agentName = indicator.dataset.agent;
            const isActive = activeAgents.includes(agentName);
            indicator.classList.toggle('active', isActive);
        });
    }

    handleTimeRangeChange(range) {
        this.container.querySelectorAll('.time-range').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.range === range);
        });

        // Emit event for range change
        const event = new CustomEvent('time-range-change', {
            detail: { range },
            bubbles: true
        });
        this.container.dispatchEvent(event);
    }

    updatePerformanceChart(data) {
        if (this.charts.performance) {
            this.charts.performance.data = data;
            this.charts.performance.draw();
        }
    }

    destroy() {
        this.charts = {};
        this.container.innerHTML = '';
    }
}