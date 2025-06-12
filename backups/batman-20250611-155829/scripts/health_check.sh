#!/bin/bash
# Batman Incorporated - Health Check Script
# Author: Robin (DevOps Engineer)
# Purpose: Monitor system health and report status

set -euo pipefail

# Colors
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly RED='\033[0;31m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Configuration
readonly BATMAN_DIR="${BATMAN_HOME:-/opt/batman-incorporated/current}"
readonly CONFIG_DIR="${BATMAN_CONFIG_DIR:-$HOME/.glados/batman-incorporated}"
readonly LOG_DIR="${CONFIG_DIR}/logs"
readonly CACHE_DIR="${CONFIG_DIR}/cache"
readonly CHECK_TIMEOUT=10
readonly WARNING_THRESHOLD_CPU=80
readonly WARNING_THRESHOLD_MEM=85
readonly WARNING_THRESHOLD_DISK=90
readonly ERROR_THRESHOLD_CPU=95
readonly ERROR_THRESHOLD_MEM=95
readonly ERROR_THRESHOLD_DISK=95

# Exit codes
readonly EXIT_SUCCESS=0
readonly EXIT_WARNING=1
readonly EXIT_ERROR=2

# Health status tracking
declare -A health_status
health_status[overall]="healthy"
health_status[warnings]=0
health_status[errors]=0

# Logging functions
log_check() {
    echo -e "${BLUE}[CHECK]${NC} $1"
}

log_ok() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    ((health_status[warnings]++))
    health_status[overall]="warning"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    ((health_status[errors]++))
    health_status[overall]="error"
}

# Display header
display_header() {
    echo -e "\n${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║       🦇 BATMAN INCORPORATED HEALTH CHECK 🦇           ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
    echo -e "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')\n"
}

# Check Python environment
check_python() {
    log_check "Python environment"
    
    if [[ -d "$BATMAN_DIR/venv" ]]; then
        if source "$BATMAN_DIR/venv/bin/activate" 2>/dev/null; then
            local python_version=$(python --version 2>&1 | cut -d' ' -f2)
            log_ok "Virtual environment active (Python $python_version)"
            
            # Check required packages
            local missing_packages=()
            for package in pyyaml click rich gitpython; do
                if ! python -c "import $package" 2>/dev/null; then
                    missing_packages+=("$package")
                fi
            done
            
            if [[ ${#missing_packages[@]} -gt 0 ]]; then
                log_error "Missing packages: ${missing_packages[*]}"
            else
                log_ok "All required packages installed"
            fi
        else
            log_error "Cannot activate virtual environment"
        fi
    else
        log_error "Virtual environment not found at $BATMAN_DIR/venv"
    fi
}

# Check Batman CLI
check_batman_cli() {
    log_check "Batman CLI"
    
    if command -v batman &>/dev/null; then
        if timeout $CHECK_TIMEOUT batman --help &>/dev/null; then
            log_ok "Batman CLI is responsive"
        else
            log_error "Batman CLI not responding"
        fi
    else
        log_warning "Batman CLI not in PATH"
    fi
}

# Check configuration
check_configuration() {
    log_check "Configuration files"
    
    if [[ -f "$CONFIG_DIR/config.yaml" ]]; then
        if [[ -r "$CONFIG_DIR/config.yaml" ]]; then
            # Validate YAML syntax
            if command -v python3 &>/dev/null; then
                if python3 -c "import yaml; yaml.safe_load(open('$CONFIG_DIR/config.yaml'))" 2>/dev/null; then
                    log_ok "Configuration file valid"
                else
                    log_error "Configuration file has invalid YAML syntax"
                fi
            else
                log_ok "Configuration file exists (syntax not checked)"
            fi
        else
            log_error "Configuration file not readable"
        fi
    else
        log_error "Configuration file not found at $CONFIG_DIR/config.yaml"
    fi
}

# Check directories
check_directories() {
    log_check "Directory structure"
    
    local required_dirs=(
        "$CONFIG_DIR"
        "$LOG_DIR"
        "$CACHE_DIR"
        "$CONFIG_DIR/tasks"
        "$CONFIG_DIR/reports"
    )
    
    local missing_dirs=()
    for dir in "${required_dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            missing_dirs+=("$dir")
        fi
    done
    
    if [[ ${#missing_dirs[@]} -eq 0 ]]; then
        log_ok "All required directories exist"
    else
        log_error "Missing directories: ${missing_dirs[*]}"
    fi
    
    # Check permissions
    if [[ -w "$CONFIG_DIR" ]]; then
        log_ok "Configuration directory is writable"
    else
        log_error "Configuration directory is not writable"
    fi
}

# Check disk space
check_disk_space() {
    log_check "Disk space"
    
    local disk_usage=$(df -h "$CONFIG_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
    local available_space=$(df -h "$CONFIG_DIR" | awk 'NR==2 {print $4}')
    
    if [[ $disk_usage -ge $ERROR_THRESHOLD_DISK ]]; then
        log_error "Disk usage critical: ${disk_usage}% used (${available_space} available)"
    elif [[ $disk_usage -ge $WARNING_THRESHOLD_DISK ]]; then
        log_warning "Disk usage high: ${disk_usage}% used (${available_space} available)"
    else
        log_ok "Disk usage: ${disk_usage}% used (${available_space} available)"
    fi
}

# Check memory usage
check_memory() {
    log_check "Memory usage"
    
    local mem_total=$(free -m | awk '/^Mem:/ {print $2}')
    local mem_used=$(free -m | awk '/^Mem:/ {print $3}')
    local mem_percent=$((mem_used * 100 / mem_total))
    
    if [[ $mem_percent -ge $ERROR_THRESHOLD_MEM ]]; then
        log_error "Memory usage critical: ${mem_percent}% (${mem_used}MB/${mem_total}MB)"
    elif [[ $mem_percent -ge $WARNING_THRESHOLD_MEM ]]; then
        log_warning "Memory usage high: ${mem_percent}% (${mem_used}MB/${mem_total}MB)"
    else
        log_ok "Memory usage: ${mem_percent}% (${mem_used}MB/${mem_total}MB)"
    fi
}

# Check CPU usage
check_cpu() {
    log_check "CPU usage"
    
    # Get 5 second average
    local cpu_usage=$(top -bn2 -d5 | grep "Cpu(s)" | tail -1 | awk '{print 100 - $8}' | cut -d'.' -f1)
    
    if [[ $cpu_usage -ge $ERROR_THRESHOLD_CPU ]]; then
        log_error "CPU usage critical: ${cpu_usage}%"
    elif [[ $cpu_usage -ge $WARNING_THRESHOLD_CPU ]]; then
        log_warning "CPU usage high: ${cpu_usage}%"
    else
        log_ok "CPU usage: ${cpu_usage}%"
    fi
}

# Check running processes
check_processes() {
    log_check "Batman processes"
    
    local batman_procs=$(pgrep -f "batman.py" | wc -l)
    
    if [[ $batman_procs -gt 0 ]]; then
        log_ok "Found $batman_procs Batman process(es) running"
    else
        log_warning "No Batman processes currently running"
    fi
}

# Check log files
check_logs() {
    log_check "Log files"
    
    if [[ -d "$LOG_DIR" ]]; then
        local log_count=$(find "$LOG_DIR" -name "*.log" -type f 2>/dev/null | wc -l)
        local total_size=$(du -sh "$LOG_DIR" 2>/dev/null | cut -f1)
        
        if [[ $log_count -gt 0 ]]; then
            log_ok "Found $log_count log file(s) (Total size: ${total_size:-unknown})"
            
            # Check for recent errors
            local recent_errors=$(find "$LOG_DIR" -name "*.log" -mmin -60 -exec grep -i "error\|exception" {} \; 2>/dev/null | wc -l)
            if [[ $recent_errors -gt 0 ]]; then
                log_warning "Found $recent_errors error(s) in logs within last hour"
            fi
        else
            log_warning "No log files found"
        fi
    else
        log_warning "Log directory not found"
    fi
}

# Check Claude CLI availability
check_claude_cli() {
    log_check "Claude CLI"
    
    if command -v claude &>/dev/null; then
        local claude_version=$(claude --version 2>&1 | head -1 || echo "unknown")
        log_ok "Claude CLI available: $claude_version"
    else
        log_error "Claude CLI not found (required for real agents)"
    fi
}

# Check external dependencies
check_dependencies() {
    log_check "External dependencies"
    
    local tools=("git" "python3" "pip3")
    local missing_tools=()
    
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &>/dev/null; then
            missing_tools+=("$tool")
        fi
    done
    
    if [[ ${#missing_tools[@]} -eq 0 ]]; then
        log_ok "All required system tools available"
    else
        log_error "Missing system tools: ${missing_tools[*]}"
    fi
    
    # Check optional Arsenal tools
    local arsenal_tools=("rg" "fd" "bat" "jq" "gh")
    local available_arsenal=()
    
    for tool in "${arsenal_tools[@]}"; do
        if command -v "$tool" &>/dev/null; then
            available_arsenal+=("$tool")
        fi
    done
    
    if [[ ${#available_arsenal[@]} -gt 0 ]]; then
        log_ok "Arsenal tools available: ${available_arsenal[*]}"
    else
        log_warning "No Arsenal tools found (optional but recommended)"
    fi
}

# Check network connectivity
check_network() {
    log_check "Network connectivity"
    
    # Check internet connectivity
    if timeout $CHECK_TIMEOUT ping -c 1 8.8.8.8 &>/dev/null; then
        log_ok "Internet connectivity confirmed"
    else
        log_warning "No internet connectivity detected"
    fi
    
    # Check GitHub access (if gh is available)
    if command -v gh &>/dev/null; then
        if timeout $CHECK_TIMEOUT gh api user &>/dev/null; then
            log_ok "GitHub API access confirmed"
        else
            log_warning "GitHub API access not configured"
        fi
    fi
}

# Generate health report
generate_report() {
    local report_file="$CONFIG_DIR/health-report-$(date +%Y%m%d-%H%M%S).txt"
    
    {
        echo "Batman Incorporated Health Report"
        echo "================================="
        echo "Generated: $(date)"
        echo "Host: $(hostname)"
        echo "User: $(whoami)"
        echo ""
        echo "Summary:"
        echo "- Overall Status: ${health_status[overall]}"
        echo "- Warnings: ${health_status[warnings]}"
        echo "- Errors: ${health_status[errors]}"
        echo ""
        echo "System Info:"
        echo "- OS: $(uname -a)"
        echo "- Python: $(python3 --version 2>&1)"
        echo "- Uptime: $(uptime -p)"
        echo ""
    } > "$report_file"
    
    echo -e "\nReport saved to: $report_file"
}

# Main health check
main() {
    display_header
    
    # Run all checks
    check_python
    check_batman_cli
    check_configuration
    check_directories
    check_disk_space
    check_memory
    check_cpu
    check_processes
    check_logs
    check_claude_cli
    check_dependencies
    check_network
    
    # Summary
    echo -e "\n${BLUE}═══ Health Check Summary ═══${NC}"
    
    if [[ ${health_status[errors]} -gt 0 ]]; then
        echo -e "${RED}Overall Status: ERROR${NC}"
        echo -e "Errors: ${health_status[errors]}, Warnings: ${health_status[warnings]}"
        exit $EXIT_ERROR
    elif [[ ${health_status[warnings]} -gt 0 ]]; then
        echo -e "${YELLOW}Overall Status: WARNING${NC}"
        echo -e "Warnings: ${health_status[warnings]}"
        exit $EXIT_WARNING
    else
        echo -e "${GREEN}Overall Status: HEALTHY${NC}"
        echo -e "All checks passed!"
        exit $EXIT_SUCCESS
    fi
    
    # Optional: generate detailed report
    if [[ "${1:-}" == "--report" ]]; then
        generate_report
    fi
}

# Run health check
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi