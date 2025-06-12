export class AgentCard {
    constructor(agentId, agentData) {
        this.agentId = agentId;
        this.agentData = agentData;
        this.element = null;
        this.progressAnimation = null;
    }

    render() {
        const article = document.createElement('article');
        article.className = 'agent-card';
        article.id = `agent-${this.agentId}`;
        article.setAttribute('role', 'region');
        article.setAttribute('aria-label', `${this.agentData.name} agent status`);

        article.innerHTML = `
            <div class="agent-header">
                <div class="agent-info">
                    <h2>${this.agentData.icon} ${this.agentData.name}</h2>
                    <span class="agent-role">${this.agentData.role}</span>
                </div>
                <div class="agent-status">
                    <span class="status-badge ${this.agentData.status}" role="status" aria-live="polite">
                        ${this.agentData.status.toUpperCase()}
                    </span>
                </div>
            </div>
            
            <div class="agent-task">
                <h3>Current Task</h3>
                <p class="task-description" aria-live="polite">
                    ${this.agentData.task || 'Waiting for assignment...'}
                </p>
            </div>
            
            <div class="agent-progress" role="progressbar" 
                 aria-valuenow="${this.agentData.progress || 0}" 
                 aria-valuemin="0" 
                 aria-valuemax="100">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${this.agentData.progress || 0}%"></div>
                </div>
                <span class="progress-text" aria-hidden="true">${this.agentData.progress || 0}%</span>
            </div>
            
            <div class="agent-metrics">
                <div class="metric">
                    <span class="metric-label">Lines Changed</span>
                    <span class="metric-value" data-metric="lines">${this.agentData.linesChanged || 0}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Time Active</span>
                    <span class="metric-value" data-metric="time">${this.agentData.timeActive || '--:--'}</span>
                </div>
            </div>
            
            <div class="agent-files">
                <h3>Recent Files</h3>
                <ul class="file-list" aria-label="Recently modified files">
                    ${this.renderFileList()}
                </ul>
            </div>
            
            <div class="agent-actions">
                <button class="action-button" data-action="view-details" aria-label="View agent details">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                        <circle cx="12" cy="12" r="3"/>
                    </svg>
                    Details
                </button>
                <button class="action-button" data-action="view-logs" aria-label="View agent logs">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                        <polyline points="14 2 14 8 20 8"/>
                        <line x1="16" y1="13" x2="8" y2="13"/>
                        <line x1="16" y1="17" x2="8" y2="17"/>
                        <polyline points="10 9 9 9 8 9"/>
                    </svg>
                    Logs
                </button>
            </div>
        `;

        this.element = article;
        this.attachEventListeners();
        return article;
    }

    renderFileList() {
        if (!this.agentData.files || this.agentData.files.length === 0) {
            return '<li class="empty-state">No files modified yet</li>';
        }

        return this.agentData.files.map(file => `
            <li title="${file}">
                <span class="file-icon">📄</span>
                <span class="file-name">${this.truncateFilePath(file)}</span>
            </li>
        `).join('');
    }

    truncateFilePath(path, maxLength = 30) {
        if (path.length <= maxLength) return path;
        
        const parts = path.split('/');
        const filename = parts.pop();
        
        if (filename.length > maxLength) {
            return '...' + filename.slice(-(maxLength - 3));
        }
        
        let truncated = filename;
        for (let i = parts.length - 1; i >= 0; i--) {
            const newPath = parts[i] + '/' + truncated;
            if (newPath.length > maxLength) {
                return '.../' + truncated;
            }
            truncated = newPath;
        }
        
        return truncated;
    }

    update(updates) {
        if (!this.element) return;

        if (updates.status !== undefined) {
            this.updateStatus(updates.status);
        }

        if (updates.task !== undefined) {
            this.updateTask(updates.task);
        }

        if (updates.progress !== undefined) {
            this.updateProgress(updates.progress);
        }

        if (updates.files !== undefined) {
            this.updateFiles(updates.files);
        }

        if (updates.linesChanged !== undefined) {
            this.updateMetric('lines', updates.linesChanged);
        }

        if (updates.timeActive !== undefined) {
            this.updateMetric('time', updates.timeActive);
        }
    }

    updateStatus(status) {
        const badge = this.element.querySelector('.status-badge');
        badge.className = `status-badge ${status}`;
        badge.textContent = status.toUpperCase();

        this.element.classList.toggle('agent-active', status === 'active');
    }

    updateTask(task) {
        const taskDesc = this.element.querySelector('.task-description');
        taskDesc.textContent = task || 'Waiting for assignment...';
        
        if (task) {
            this.addNotification('Task assigned', 'info');
        }
    }

    updateProgress(progress) {
        const progressBar = this.element.querySelector('.agent-progress');
        const progressFill = this.element.querySelector('.progress-fill');
        const progressText = this.element.querySelector('.progress-text');

        progressBar.setAttribute('aria-valuenow', progress);
        progressText.textContent = `${progress}%`;

        // Animate progress change
        if (this.progressAnimation) {
            cancelAnimationFrame(this.progressAnimation);
        }

        const currentWidth = parseFloat(progressFill.style.width) || 0;
        const targetWidth = progress;
        const duration = 500; // ms
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easeProgress = this.easeInOutCubic(progress);
            
            const width = currentWidth + (targetWidth - currentWidth) * easeProgress;
            progressFill.style.width = `${width}%`;

            if (progress < 1) {
                this.progressAnimation = requestAnimationFrame(animate);
            }
        };

        this.progressAnimation = requestAnimationFrame(animate);
    }

    updateFiles(files) {
        const fileList = this.element.querySelector('.file-list');
        fileList.innerHTML = this.renderFileList();
    }

    updateMetric(metric, value) {
        const metricElement = this.element.querySelector(`[data-metric="${metric}"]`);
        if (metricElement) {
            const oldValue = metricElement.textContent;
            metricElement.textContent = value;
            
            if (oldValue !== value) {
                metricElement.classList.add('metric-updated');
                setTimeout(() => metricElement.classList.remove('metric-updated'), 1000);
            }
        }
    }

    addNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `agent-notification ${type}`;
        notification.textContent = message;
        
        this.element.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    attachEventListeners() {
        this.element.querySelectorAll('.action-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                this.handleAction(action);
            });
        });
    }

    handleAction(action) {
        const event = new CustomEvent('agent-action', {
            detail: { agentId: this.agentId, action },
            bubbles: true
        });
        this.element.dispatchEvent(event);
    }

    easeInOutCubic(t) {
        return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    }

    destroy() {
        if (this.progressAnimation) {
            cancelAnimationFrame(this.progressAnimation);
        }
        if (this.element) {
            this.element.remove();
        }
    }
}