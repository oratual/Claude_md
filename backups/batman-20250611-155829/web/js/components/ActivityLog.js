export class ActivityLog {
    constructor(container) {
        this.container = container;
        this.logs = [];
        this.maxLogs = 100;
        this.filters = {
            search: '',
            type: 'all'
        };
        this.virtualScroll = null;
        this.init();
    }

    init() {
        this.render();
        this.setupVirtualScroll();
        this.attachEventListeners();
    }

    render() {
        this.container.innerHTML = `
            <div class="activity-header">
                <h2>🔍 Activity Log</h2>
                <div class="activity-controls">
                    <div class="search-wrapper">
                        <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <circle cx="11" cy="11" r="8"/>
                            <path d="m21 21-4.35-4.35"/>
                        </svg>
                        <input type="search" 
                               class="search-input" 
                               id="log-search" 
                               placeholder="Search logs..." 
                               aria-label="Search activity logs">
                    </div>
                    <div class="filter-wrapper">
                        <select class="filter-select" id="log-filter" aria-label="Filter logs by type">
                            <option value="all">All Types</option>
                            <option value="success">Success</option>
                            <option value="warning">Warning</option>
                            <option value="error">Error</option>
                            <option value="info">Info</option>
                        </select>
                    </div>
                    <button class="clear-logs-btn" aria-label="Clear all logs">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <polyline points="3 6 5 6 21 6"/>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                        </svg>
                    </button>
                </div>
            </div>
            <div class="activity-log" id="activity-log" role="feed" aria-live="polite" aria-label="Real-time activity feed">
                <div class="log-viewport">
                    <div class="log-content"></div>
                </div>
                <div class="log-empty-state" style="display: none;">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" opacity="0.3">
                        <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                        <path d="M2 17l10 5 10-5"/>
                        <path d="M2 12l10 5 10-5"/>
                    </svg>
                    <p>No activity logs yet</p>
                </div>
            </div>
        `;
    }

    setupVirtualScroll() {
        const viewport = this.container.querySelector('.log-viewport');
        const content = this.container.querySelector('.log-content');
        
        this.virtualScroll = {
            viewport,
            content,
            itemHeight: 60, // Approximate height of each log entry
            visibleItems: Math.ceil(viewport.clientHeight / 60),
            scrollTop: 0
        };

        viewport.addEventListener('scroll', () => this.handleScroll());
    }

    handleScroll() {
        const { viewport } = this.virtualScroll;
        this.virtualScroll.scrollTop = viewport.scrollTop;
        this.renderVisibleLogs();
    }

    addLog(logData) {
        const log = {
            id: Date.now() + Math.random(),
            timestamp: logData.timestamp || new Date().toLocaleTimeString('en-US', { hour12: false }),
            message: logData.message,
            type: logData.type || 'info',
            agent: logData.agent,
            details: logData.details,
            raw: logData
        };

        this.logs.unshift(log);

        // Maintain max logs
        if (this.logs.length > this.maxLogs) {
            this.logs = this.logs.slice(0, this.maxLogs);
        }

        this.renderVisibleLogs();
        this.updateEmptyState();

        // Announce new log for screen readers
        this.announceLog(log);
    }

    renderVisibleLogs() {
        const filteredLogs = this.getFilteredLogs();
        const { content, itemHeight, scrollTop } = this.virtualScroll;
        
        const startIndex = Math.floor(scrollTop / itemHeight);
        const endIndex = Math.min(
            startIndex + this.virtualScroll.visibleItems + 2,
            filteredLogs.length
        );

        // Set content height for scrollbar
        content.style.height = `${filteredLogs.length * itemHeight}px`;

        // Clear and render visible items
        content.innerHTML = '';
        
        for (let i = startIndex; i < endIndex; i++) {
            const log = filteredLogs[i];
            if (log) {
                const element = this.createLogElement(log);
                element.style.position = 'absolute';
                element.style.top = `${i * itemHeight}px`;
                element.style.left = '0';
                element.style.right = '0';
                content.appendChild(element);
            }
        }
    }

    getFilteredLogs() {
        return this.logs.filter(log => {
            const matchesType = this.filters.type === 'all' || log.type === this.filters.type;
            const matchesSearch = !this.filters.search || 
                log.message.toLowerCase().includes(this.filters.search.toLowerCase()) ||
                (log.agent && log.agent.toLowerCase().includes(this.filters.search.toLowerCase()));
            
            return matchesType && matchesSearch;
        });
    }

    createLogElement(log) {
        const div = document.createElement('div');
        div.className = `log-entry ${log.type}`;
        div.setAttribute('role', 'article');
        div.setAttribute('aria-label', `Log entry: ${log.message}`);

        const icon = this.getLogIcon(log.type);
        const agentBadge = log.agent ? `<span class="log-agent">${log.agent}</span>` : '';

        div.innerHTML = `
            <div class="log-icon">${icon}</div>
            <div class="log-content">
                <div class="log-header">
                    <time class="timestamp" datetime="${new Date().toISOString()}">${log.timestamp}</time>
                    ${agentBadge}
                </div>
                <div class="log-message">${this.escapeHtml(log.message)}</div>
                ${log.details ? `<div class="log-details">${this.escapeHtml(log.details)}</div>` : ''}
            </div>
            <button class="log-action" aria-label="View log details" data-log-id="${log.id}">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <circle cx="12" cy="12" r="1"/>
                    <circle cx="19" cy="12" r="1"/>
                    <circle cx="5" cy="12" r="1"/>
                </svg>
            </button>
        `;

        return div;
    }

    getLogIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        return icons[type] || '📋';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    attachEventListeners() {
        const searchInput = this.container.querySelector('#log-search');
        const filterSelect = this.container.querySelector('#log-filter');
        const clearBtn = this.container.querySelector('.clear-logs-btn');

        searchInput.addEventListener('input', (e) => {
            this.filters.search = e.target.value;
            this.renderVisibleLogs();
            this.updateEmptyState();
        });

        filterSelect.addEventListener('change', (e) => {
            this.filters.type = e.target.value;
            this.renderVisibleLogs();
            this.updateEmptyState();
        });

        clearBtn.addEventListener('click', () => {
            if (confirm('Clear all activity logs?')) {
                this.clearLogs();
            }
        });

        this.container.addEventListener('click', (e) => {
            if (e.target.closest('.log-action')) {
                const logId = e.target.closest('.log-action').dataset.logId;
                this.showLogDetails(logId);
            }
        });
    }

    showLogDetails(logId) {
        const log = this.logs.find(l => l.id == logId);
        if (log) {
            const event = new CustomEvent('show-log-details', {
                detail: log,
                bubbles: true
            });
            this.container.dispatchEvent(event);
        }
    }

    clearLogs() {
        this.logs = [];
        this.renderVisibleLogs();
        this.updateEmptyState();
        this.addLog({
            message: 'Activity log cleared',
            type: 'info'
        });
    }

    updateEmptyState() {
        const emptyState = this.container.querySelector('.log-empty-state');
        const viewport = this.container.querySelector('.log-viewport');
        const hasLogs = this.getFilteredLogs().length > 0;

        emptyState.style.display = hasLogs ? 'none' : 'flex';
        viewport.style.display = hasLogs ? 'block' : 'none';
    }

    announceLog(log) {
        const announcement = document.createElement('div');
        announcement.className = 'sr-only';
        announcement.setAttribute('role', 'status');
        announcement.setAttribute('aria-live', 'polite');
        announcement.textContent = `New ${log.type} log: ${log.message}`;
        
        document.body.appendChild(announcement);
        setTimeout(() => announcement.remove(), 1000);
    }

    exportLogs() {
        const logs = this.getFilteredLogs();
        const data = logs.map(log => ({
            timestamp: log.timestamp,
            type: log.type,
            agent: log.agent,
            message: log.message,
            details: log.details
        }));

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `batman-logs-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }

    destroy() {
        this.container.innerHTML = '';
        this.logs = [];
    }
}