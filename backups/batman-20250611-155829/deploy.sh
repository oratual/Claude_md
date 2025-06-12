#!/bin/bash
# Batman Incorporated - Deployment Script
# Author: Robin (DevOps Engineer)
# Purpose: Deploy Batman Incorporated to production/staging environments

set -euo pipefail

# Colors
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly RED='\033[0;31m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly NC='\033[0m'

# Deployment configuration
readonly SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
readonly DEPLOY_ENV="${DEPLOY_ENV:-production}"
readonly DEPLOY_USER="${DEPLOY_USER:-batman}"
readonly DEPLOY_HOST="${DEPLOY_HOST:-}"
readonly DEPLOY_PATH="${DEPLOY_PATH:-/opt/batman-incorporated}"
readonly BACKUP_DIR="${BACKUP_DIR:-/var/backups/batman-incorporated}"
readonly SERVICE_NAME="batman-incorporated"

# Version info
readonly VERSION_FILE="$SCRIPT_DIR/VERSION"
readonly CURRENT_VERSION=$(git describe --tags --always 2>/dev/null || echo "dev")

# Logging functions
log_info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} ${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} ${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} ${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} ${RED}[ERROR]${NC} $1" >&2
}

log_step() {
    echo -e "\n${PURPLE}═══ $1 ═══${NC}\n"
}

# Display deployment banner
display_banner() {
    cat << 'EOF'

    ╔══════════════════════════════════════════════════════════╗
    ║          🦇 BATMAN INCORPORATED DEPLOYMENT 🦇           ║
    ║                                                          ║
    ║        "Deploying justice across the network"           ║
    ╚══════════════════════════════════════════════════════════╝

EOF
    log_info "Environment: ${DEPLOY_ENV}"
    log_info "Version: ${CURRENT_VERSION}"
    log_info "Target: ${DEPLOY_HOST:-localhost}:${DEPLOY_PATH}"
}

# Pre-deployment checks
pre_deployment_checks() {
    log_step "Pre-deployment Checks"
    
    # Check if running from git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Not in a git repository"
        return 1
    fi
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        log_warning "Uncommitted changes detected"
        read -p "Continue with uncommitted changes? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_error "Deployment cancelled"
            return 1
        fi
    fi
    
    # Run tests
    log_info "Running tests..."
    if [[ -f "$SCRIPT_DIR/run_tests.py" ]]; then
        if python "$SCRIPT_DIR/run_tests.py" --quiet; then
            log_success "All tests passed"
        else
            log_error "Tests failed"
            return 1
        fi
    else
        log_warning "No tests found"
    fi
    
    # Check deployment target
    if [[ -n "$DEPLOY_HOST" ]]; then
        log_info "Checking connection to ${DEPLOY_HOST}..."
        if ssh -o ConnectTimeout=5 "${DEPLOY_USER}@${DEPLOY_HOST}" "echo 'Connection successful'" &>/dev/null; then
            log_success "Connection to ${DEPLOY_HOST} successful"
        else
            log_error "Cannot connect to ${DEPLOY_HOST}"
            return 1
        fi
    fi
    
    log_success "Pre-deployment checks passed"
}

# Build deployment package
build_package() {
    log_step "Building Deployment Package"
    
    local build_dir="/tmp/batman-inc-build-$$"
    local package_name="batman-incorporated-${CURRENT_VERSION}.tar.gz"
    
    # Create build directory
    mkdir -p "$build_dir"
    
    # Copy files
    log_info "Copying files..."
    rsync -av --exclude-from='.gitignore' \
        --exclude='.git' \
        --exclude='venv' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='logs/*' \
        --exclude='tasks/*' \
        --exclude='.env*' \
        "$SCRIPT_DIR/" "$build_dir/"
    
    # Create version file
    echo "$CURRENT_VERSION" > "$build_dir/VERSION"
    
    # Create deployment info
    cat > "$build_dir/DEPLOY_INFO" << EOF
Deployment Information
=====================
Version: ${CURRENT_VERSION}
Date: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
Environment: ${DEPLOY_ENV}
Git Commit: $(git rev-parse HEAD)
Deployed By: $(whoami)@$(hostname)
EOF
    
    # Create package
    log_info "Creating deployment package..."
    tar -czf "/tmp/${package_name}" -C "$build_dir" .
    
    # Cleanup
    rm -rf "$build_dir"
    
    log_success "Package created: /tmp/${package_name}"
    echo "/tmp/${package_name}"
}

# Deploy locally
deploy_local() {
    log_step "Local Deployment"
    
    local package_path="$1"
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    
    # Create deployment directory
    sudo mkdir -p "$DEPLOY_PATH"
    
    # Backup current deployment
    if [[ -d "$DEPLOY_PATH/current" ]]; then
        log_info "Backing up current deployment..."
        sudo mkdir -p "$BACKUP_DIR"
        sudo tar -czf "$BACKUP_DIR/backup-${timestamp}.tar.gz" -C "$DEPLOY_PATH/current" .
    fi
    
    # Extract new deployment
    log_info "Extracting deployment package..."
    sudo mkdir -p "$DEPLOY_PATH/releases/${timestamp}"
    sudo tar -xzf "$package_path" -C "$DEPLOY_PATH/releases/${timestamp}"
    
    # Install dependencies
    log_info "Installing dependencies..."
    cd "$DEPLOY_PATH/releases/${timestamp}"
    sudo python3 -m venv venv
    sudo venv/bin/pip install -r requirements.txt
    
    # Update symlink
    log_info "Updating current symlink..."
    sudo ln -sfn "$DEPLOY_PATH/releases/${timestamp}" "$DEPLOY_PATH/current"
    
    # Set permissions
    sudo chown -R "${DEPLOY_USER}:${DEPLOY_USER}" "$DEPLOY_PATH"
    
    log_success "Local deployment completed"
}

# Deploy remotely
deploy_remote() {
    log_step "Remote Deployment"
    
    local package_path="$1"
    local package_name=$(basename "$package_path")
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    
    # Upload package
    log_info "Uploading package to ${DEPLOY_HOST}..."
    scp "$package_path" "${DEPLOY_USER}@${DEPLOY_HOST}:/tmp/${package_name}"
    
    # Execute remote deployment
    log_info "Executing remote deployment..."
    ssh "${DEPLOY_USER}@${DEPLOY_HOST}" bash << EOF
set -euo pipefail

# Create directories
sudo mkdir -p ${DEPLOY_PATH}/releases/${timestamp}
sudo mkdir -p ${BACKUP_DIR}

# Backup current deployment
if [[ -d ${DEPLOY_PATH}/current ]]; then
    echo "Backing up current deployment..."
    sudo tar -czf ${BACKUP_DIR}/backup-${timestamp}.tar.gz -C ${DEPLOY_PATH}/current .
fi

# Extract new deployment
echo "Extracting deployment package..."
sudo tar -xzf /tmp/${package_name} -C ${DEPLOY_PATH}/releases/${timestamp}

# Install dependencies
echo "Installing dependencies..."
cd ${DEPLOY_PATH}/releases/${timestamp}
sudo python3 -m venv venv
sudo venv/bin/pip install -q -r requirements.txt

# Update symlink
echo "Updating current symlink..."
sudo ln -sfn ${DEPLOY_PATH}/releases/${timestamp} ${DEPLOY_PATH}/current

# Set permissions
sudo chown -R ${DEPLOY_USER}:${DEPLOY_USER} ${DEPLOY_PATH}

# Cleanup
rm -f /tmp/${package_name}

echo "Remote deployment completed"
EOF
    
    log_success "Remote deployment completed"
}

# Setup systemd service
setup_service() {
    log_step "Setting up SystemD Service"
    
    local service_file="/etc/systemd/system/${SERVICE_NAME}.service"
    
    # Create service file
    sudo tee "$service_file" > /dev/null << EOF
[Unit]
Description=Batman Incorporated - Automated Task Execution System
Documentation=https://github.com/oratual/Batman-Incorporated
After=network.target

[Service]
Type=simple
User=${DEPLOY_USER}
Group=${DEPLOY_USER}
WorkingDirectory=${DEPLOY_PATH}/current
Environment="PATH=${DEPLOY_PATH}/current/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="BATMAN_HOME=${DEPLOY_PATH}/current"
Environment="BATMAN_CONFIG_DIR=/etc/batman-incorporated"
ExecStart=${DEPLOY_PATH}/current/venv/bin/python ${DEPLOY_PATH}/current/batman.py --auto
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=${SERVICE_NAME}

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=${DEPLOY_PATH} /var/log/batman-incorporated

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    # Enable and start service
    sudo systemctl enable "${SERVICE_NAME}.service"
    
    log_success "SystemD service configured"
}

# Post-deployment tasks
post_deployment() {
    log_step "Post-deployment Tasks"
    
    # Run health check
    log_info "Running health check..."
    if [[ -f "$SCRIPT_DIR/scripts/health_check.sh" ]]; then
        if "$SCRIPT_DIR/scripts/health_check.sh"; then
            log_success "Health check passed"
        else
            log_warning "Health check failed"
        fi
    fi
    
    # Restart service
    if systemctl is-active --quiet "${SERVICE_NAME}"; then
        log_info "Restarting ${SERVICE_NAME} service..."
        sudo systemctl restart "${SERVICE_NAME}"
        sleep 3
        if systemctl is-active --quiet "${SERVICE_NAME}"; then
            log_success "Service restarted successfully"
        else
            log_error "Service failed to start"
            sudo journalctl -u "${SERVICE_NAME}" -n 20
        fi
    fi
    
    # Clean old releases (keep last 5)
    if [[ -d "${DEPLOY_PATH}/releases" ]]; then
        log_info "Cleaning old releases..."
        local releases_to_delete=$(ls -t "${DEPLOY_PATH}/releases" | tail -n +6)
        for release in $releases_to_delete; do
            log_info "Removing old release: $release"
            sudo rm -rf "${DEPLOY_PATH}/releases/$release"
        done
    fi
    
    # Send notification (if configured)
    if command -v notify-send &> /dev/null; then
        notify-send "Batman Incorporated" "Deployment completed: v${CURRENT_VERSION}"
    fi
    
    log_success "Post-deployment tasks completed"
}

# Rollback deployment
rollback() {
    log_step "Rollback Deployment"
    
    local previous_release=$(ls -t "${DEPLOY_PATH}/releases" | sed -n '2p')
    
    if [[ -z "$previous_release" ]]; then
        log_error "No previous release found"
        return 1
    fi
    
    log_info "Rolling back to: $previous_release"
    
    # Update symlink
    sudo ln -sfn "${DEPLOY_PATH}/releases/${previous_release}" "${DEPLOY_PATH}/current"
    
    # Restart service
    if systemctl is-active --quiet "${SERVICE_NAME}"; then
        sudo systemctl restart "${SERVICE_NAME}"
    fi
    
    log_success "Rollback completed"
}

# Main deployment function
main() {
    local action="${1:-deploy}"
    
    case "$action" in
        deploy)
            display_banner
            pre_deployment_checks || exit 1
            
            local package_path=$(build_package)
            
            if [[ -z "$DEPLOY_HOST" ]]; then
                deploy_local "$package_path"
                setup_service
            else
                deploy_remote "$package_path"
            fi
            
            post_deployment
            
            # Cleanup
            rm -f "$package_path"
            
            log_success "Deployment completed successfully!"
            ;;
            
        rollback)
            log_warning "Starting rollback..."
            rollback
            ;;
            
        status)
            log_info "Deployment status:"
            echo "Current version: $(cat ${DEPLOY_PATH}/current/VERSION 2>/dev/null || echo 'Unknown')"
            echo "Service status: $(systemctl is-active ${SERVICE_NAME} 2>/dev/null || echo 'Not installed')"
            echo "Available releases:"
            ls -la "${DEPLOY_PATH}/releases" 2>/dev/null || echo "No releases found"
            ;;
            
        *)
            echo "Usage: $0 [deploy|rollback|status]"
            echo "Environment variables:"
            echo "  DEPLOY_ENV    - Deployment environment (default: production)"
            echo "  DEPLOY_HOST   - Remote host for deployment (default: local)"
            echo "  DEPLOY_USER   - User for deployment (default: batman)"
            echo "  DEPLOY_PATH   - Deployment path (default: /opt/batman-incorporated)"
            exit 1
            ;;
    esac
}

# Run deployment
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi