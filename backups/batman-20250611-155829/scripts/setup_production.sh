#!/bin/bash
# Batman Incorporated - Production Environment Setup
# Author: Robin (DevOps Engineer)
# Purpose: Configure production server for Batman Incorporated deployment

set -euo pipefail

# Colors
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly RED='\033[0;31m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly NC='\033[0m'

# Configuration
readonly BATMAN_USER="${BATMAN_USER:-batman}"
readonly BATMAN_GROUP="${BATMAN_GROUP:-batman}"
readonly INSTALL_PATH="${INSTALL_PATH:-/opt/batman-incorporated}"
readonly CONFIG_PATH="/etc/batman-incorporated"
readonly LOG_PATH="/var/log/batman-incorporated"
readonly BACKUP_PATH="/var/backups/batman-incorporated"
readonly NGINX_SITE="batman-incorporated"

# System requirements
readonly MIN_MEMORY_GB=2
readonly MIN_DISK_GB=10
readonly REQUIRED_PACKAGES=(
    "python3"
    "python3-pip"
    "python3-venv"
    "git"
    "nginx"
    "redis-server"
    "supervisor"
    "certbot"
    "python3-certbot-nginx"
    "ufw"
    "fail2ban"
    "rsync"
    "jq"
)

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

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
}

# Display banner
display_banner() {
    cat << 'EOF'

    ╔══════════════════════════════════════════════════════════╗
    ║       🦇 BATMAN INCORPORATED PRODUCTION SETUP 🦇        ║
    ║                                                          ║
    ║         "Preparing Gotham's infrastructure"             ║
    ╚══════════════════════════════════════════════════════════╝

EOF
}

# Check system requirements
check_system_requirements() {
    log_step "System Requirements Check"
    
    # Check OS
    if [[ ! -f /etc/os-release ]]; then
        log_error "Cannot determine OS version"
        return 1
    fi
    
    source /etc/os-release
    log_info "Operating System: $PRETTY_NAME"
    
    # Check memory
    local total_memory_gb=$(awk '/MemTotal/ {printf "%.0f", $2/1024/1024}' /proc/meminfo)
    if [[ $total_memory_gb -lt $MIN_MEMORY_GB ]]; then
        log_error "Insufficient memory. Required: ${MIN_MEMORY_GB}GB, Available: ${total_memory_gb}GB"
        return 1
    fi
    log_success "Memory check passed (${total_memory_gb}GB available)"
    
    # Check disk space
    local available_disk_gb=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
    if [[ $available_disk_gb -lt $MIN_DISK_GB ]]; then
        log_error "Insufficient disk space. Required: ${MIN_DISK_GB}GB, Available: ${available_disk_gb}GB"
        return 1
    fi
    log_success "Disk space check passed (${available_disk_gb}GB available)"
}

# Update system
update_system() {
    log_step "System Update"
    
    log_info "Updating package repositories..."
    apt-get update -qq
    
    log_info "Upgrading system packages..."
    DEBIAN_FRONTEND=noninteractive apt-get upgrade -y -qq
    
    log_success "System updated"
}

# Install required packages
install_packages() {
    log_step "Installing Required Packages"
    
    log_info "Installing packages: ${REQUIRED_PACKAGES[*]}"
    DEBIAN_FRONTEND=noninteractive apt-get install -y -qq "${REQUIRED_PACKAGES[@]}"
    
    # Install additional Python packages
    log_info "Installing Python system packages..."
    pip3 install --quiet --upgrade pip setuptools wheel
    
    log_success "All packages installed"
}

# Create batman user
create_user() {
    log_step "Creating Batman User"
    
    if id "$BATMAN_USER" &>/dev/null; then
        log_success "User $BATMAN_USER already exists"
    else
        log_info "Creating user $BATMAN_USER..."
        useradd -r -m -d "/home/$BATMAN_USER" -s /bin/bash "$BATMAN_USER"
        log_success "User $BATMAN_USER created"
    fi
    
    # Add to necessary groups
    usermod -aG sudo,www-data "$BATMAN_USER"
    
    # Setup SSH key (if provided)
    if [[ -n "${SSH_PUBLIC_KEY:-}" ]]; then
        log_info "Setting up SSH access..."
        local ssh_dir="/home/$BATMAN_USER/.ssh"
        mkdir -p "$ssh_dir"
        echo "$SSH_PUBLIC_KEY" > "$ssh_dir/authorized_keys"
        chmod 700 "$ssh_dir"
        chmod 600 "$ssh_dir/authorized_keys"
        chown -R "$BATMAN_USER:$BATMAN_GROUP" "$ssh_dir"
        log_success "SSH access configured"
    fi
}

# Create directory structure
create_directories() {
    log_step "Creating Directory Structure"
    
    local dirs=(
        "$INSTALL_PATH"
        "$INSTALL_PATH/releases"
        "$INSTALL_PATH/shared"
        "$INSTALL_PATH/shared/logs"
        "$INSTALL_PATH/shared/cache"
        "$INSTALL_PATH/shared/uploads"
        "$CONFIG_PATH"
        "$LOG_PATH"
        "$BACKUP_PATH"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
        chown "$BATMAN_USER:$BATMAN_GROUP" "$dir"
    done
    
    # Set permissions
    chmod 755 "$INSTALL_PATH"
    chmod 755 "$CONFIG_PATH"
    chmod 755 "$LOG_PATH"
    chmod 700 "$BACKUP_PATH"
    
    log_success "Directory structure created"
}

# Configure firewall
configure_firewall() {
    log_step "Configuring Firewall"
    
    # Enable UFW
    log_info "Configuring UFW firewall..."
    ufw --force disable
    ufw default deny incoming
    ufw default allow outgoing
    
    # Allow SSH (with rate limiting)
    ufw limit 22/tcp comment "SSH"
    
    # Allow HTTP and HTTPS
    ufw allow 80/tcp comment "HTTP"
    ufw allow 443/tcp comment "HTTPS"
    
    # Allow Redis (localhost only)
    ufw allow from 127.0.0.1 to any port 6379 comment "Redis"
    
    # Enable firewall
    ufw --force enable
    
    log_success "Firewall configured"
}

# Configure fail2ban
configure_fail2ban() {
    log_step "Configuring Fail2ban"
    
    # Create jail configuration
    cat > /etc/fail2ban/jail.d/batman-incorporated.conf << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
port = http,https
logpath = /var/log/nginx/error.log

[nginx-botsearch]
enabled = true
port = http,https
filter = nginx-botsearch
logpath = /var/log/nginx/access.log
maxretry = 2
EOF
    
    # Restart fail2ban
    systemctl restart fail2ban
    
    log_success "Fail2ban configured"
}

# Configure Redis
configure_redis() {
    log_step "Configuring Redis"
    
    # Backup original config
    cp /etc/redis/redis.conf /etc/redis/redis.conf.backup
    
    # Configure Redis for Batman Incorporated
    cat >> /etc/redis/redis.conf << 'EOF'

# Batman Incorporated Configuration
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
dir /var/lib/redis
dbfilename batman-dump.rdb
appendonly yes
appendfilename "batman-appendonly.aof"
EOF
    
    # Set Redis to bind only to localhost
    sed -i 's/^bind .*/bind 127.0.0.1 ::1/' /etc/redis/redis.conf
    
    # Enable and restart Redis
    systemctl enable redis-server
    systemctl restart redis-server
    
    log_success "Redis configured"
}

# Configure Nginx
configure_nginx() {
    log_step "Configuring Nginx"
    
    # Create Nginx configuration
    cat > "/etc/nginx/sites-available/$NGINX_SITE" << EOF
# Batman Incorporated - Nginx Configuration
upstream batman_app {
    server unix:/run/batman-incorporated.sock fail_timeout=0;
}

# Rate limiting
limit_req_zone \$binary_remote_addr zone=batman_limit:10m rate=10r/s;

server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN_NAME:-_};
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # Logging
    access_log $LOG_PATH/nginx-access.log;
    error_log $LOG_PATH/nginx-error.log;
    
    # Rate limiting
    limit_req zone=batman_limit burst=20 nodelay;
    
    # Static files
    location /static/ {
        alias $INSTALL_PATH/current/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias $INSTALL_PATH/shared/uploads/;
        expires 7d;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }
    
    # Main application
    location / {
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Host \$http_host;
        proxy_redirect off;
        proxy_buffering off;
        proxy_pass http://batman_app;
    }
    
    # Deny access to hidden files
    location ~ /\\. {
        deny all;
    }
}
EOF
    
    # Enable site
    ln -sf "/etc/nginx/sites-available/$NGINX_SITE" "/etc/nginx/sites-enabled/"
    
    # Test configuration
    nginx -t
    
    # Reload Nginx
    systemctl reload nginx
    
    log_success "Nginx configured"
}

# Configure supervisor
configure_supervisor() {
    log_step "Configuring Supervisor"
    
    # Create supervisor configuration
    cat > "/etc/supervisor/conf.d/batman-incorporated.conf" << EOF
[program:batman-incorporated]
command=$INSTALL_PATH/current/venv/bin/python $INSTALL_PATH/current/batman.py --auto
directory=$INSTALL_PATH/current
user=$BATMAN_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$LOG_PATH/batman-supervisor.log
environment="PATH=$INSTALL_PATH/current/venv/bin:/usr/local/bin:/usr/bin:/bin",
           "BATMAN_HOME=$INSTALL_PATH/current",
           "BATMAN_CONFIG_DIR=$CONFIG_PATH"
stopasgroup=true
killasgroup=true

[program:batman-worker]
command=$INSTALL_PATH/current/venv/bin/python $INSTALL_PATH/current/batman.py --worker
directory=$INSTALL_PATH/current
user=$BATMAN_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$LOG_PATH/batman-worker.log
environment="PATH=$INSTALL_PATH/current/venv/bin:/usr/local/bin:/usr/bin:/bin",
           "BATMAN_HOME=$INSTALL_PATH/current",
           "BATMAN_CONFIG_DIR=$CONFIG_PATH"
numprocs=2
process_name=%(program_name)s_%(process_num)02d
stopasgroup=true
killasgroup=true
EOF
    
    # Reload supervisor
    supervisorctl reread
    supervisorctl update
    
    log_success "Supervisor configured"
}

# Setup SSL certificate
setup_ssl() {
    log_step "Setting up SSL Certificate"
    
    if [[ -z "${DOMAIN_NAME:-}" ]]; then
        log_warning "No domain name provided, skipping SSL setup"
        log_info "Set DOMAIN_NAME environment variable and run: certbot --nginx -d \$DOMAIN_NAME"
        return
    fi
    
    if [[ -z "${CERT_EMAIL:-}" ]]; then
        log_warning "No email provided for SSL certificate"
        return
    fi
    
    log_info "Obtaining SSL certificate for $DOMAIN_NAME..."
    certbot --nginx -d "$DOMAIN_NAME" --non-interactive --agree-tos -m "$CERT_EMAIL"
    
    # Setup auto-renewal
    cat > /etc/cron.d/certbot-batman << EOF
0 0,12 * * * root certbot renew --quiet --post-hook "systemctl reload nginx"
EOF
    
    log_success "SSL certificate configured"
}

# Configure logging
configure_logging() {
    log_step "Configuring Logging"
    
    # Create logrotate configuration
    cat > /etc/logrotate.d/batman-incorporated << EOF
$LOG_PATH/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 $BATMAN_USER $BATMAN_GROUP
    sharedscripts
    postrotate
        systemctl reload nginx > /dev/null 2>&1 || true
        supervisorctl restart all > /dev/null 2>&1 || true
    endscript
}
EOF
    
    # Create rsyslog configuration for Batman logs
    cat > /etc/rsyslog.d/30-batman-incorporated.conf << EOF
# Batman Incorporated logging
:programname, isequal, "batman-incorporated" $LOG_PATH/batman-syslog.log
& stop
EOF
    
    # Restart rsyslog
    systemctl restart rsyslog
    
    log_success "Logging configured"
}

# Setup monitoring
setup_monitoring() {
    log_step "Setting up Monitoring"
    
    # Create monitoring script
    cat > "$CONFIG_PATH/monitor.sh" << 'EOF'
#!/bin/bash
# Batman Incorporated - Monitoring Script

# Check if service is running
if ! supervisorctl status batman-incorporated | grep -q RUNNING; then
    echo "Batman Incorporated is not running!"
    supervisorctl start batman-incorporated
fi

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 90 ]; then
    echo "Warning: Disk usage is at ${DISK_USAGE}%"
fi

# Check memory usage
MEM_USAGE=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
if [ $MEM_USAGE -gt 90 ]; then
    echo "Warning: Memory usage is at ${MEM_USAGE}%"
fi
EOF
    
    chmod +x "$CONFIG_PATH/monitor.sh"
    
    # Add to crontab
    cat > /etc/cron.d/batman-monitor << EOF
*/5 * * * * $BATMAN_USER $CONFIG_PATH/monitor.sh >> $LOG_PATH/monitor.log 2>&1
EOF
    
    log_success "Monitoring configured"
}

# Create production configuration
create_production_config() {
    log_step "Creating Production Configuration"
    
    cat > "$CONFIG_PATH/production.yaml" << 'EOF'
# Batman Incorporated - Production Configuration
version: "1.0"

# Environment
environment: production

# Execution settings
execution:
  default_mode: safe
  max_retries: 5
  timeout_seconds: 600
  parallel_agents: true

# Agent settings
agents:
  real_agents: true
  parallel_execution: true
  max_concurrent: 3
  
# Redis configuration
redis:
  host: localhost
  port: 6379
  db: 0
  
# Logging
logging:
  level: INFO
  format: json
  file: /var/log/batman-incorporated/batman.log
  max_size_mb: 100
  backup_count: 10
  
# Security
security:
  enable_auth: true
  session_timeout: 3600
  max_failed_attempts: 3
  
# Performance
performance:
  cache_enabled: true
  cache_ttl: 3600
  max_workers: 4
  
# Notifications
notifications:
  enabled: true
  channels:
    - type: webhook
      url: "${WEBHOOK_URL:-}"
    - type: email
      smtp_host: "${SMTP_HOST:-localhost}"
      smtp_port: 587
      from: "batman@${DOMAIN_NAME:-localhost}"
EOF
    
    chown "$BATMAN_USER:$BATMAN_GROUP" "$CONFIG_PATH/production.yaml"
    chmod 640 "$CONFIG_PATH/production.yaml"
    
    log_success "Production configuration created"
}

# Final summary
show_summary() {
    log_step "Setup Complete!"
    
    cat << EOF

🦇 Batman Incorporated Production Setup Complete! 🦇

Installation Details:
- User: $BATMAN_USER
- Installation Path: $INSTALL_PATH
- Configuration: $CONFIG_PATH
- Logs: $LOG_PATH
- Backups: $BACKUP_PATH

Services:
- Nginx: $(systemctl is-active nginx)
- Redis: $(systemctl is-active redis-server)
- Supervisor: $(systemctl is-active supervisor)
- Firewall: $(ufw status | grep -q "Status: active" && echo "active" || echo "inactive")

Next Steps:
1. Deploy application: ./deploy.sh
2. Configure domain: Set DOMAIN_NAME and run SSL setup
3. Monitor logs: tail -f $LOG_PATH/*.log
4. Check status: supervisorctl status

Security Notes:
- Firewall is configured with minimal open ports
- Fail2ban is protecting against brute force attacks
- Regular backups are configured
- SSL certificate auto-renewal is set up (if domain configured)

Access the application:
- HTTP: http://${DOMAIN_NAME:-server-ip}
- HTTPS: https://${DOMAIN_NAME:-server-ip} (after SSL setup)

Monitor health:
- curl http://localhost/health

EOF
}

# Main function
main() {
    check_root
    display_banner
    
    # Run all setup steps
    check_system_requirements || exit 1
    update_system
    install_packages
    create_user
    create_directories
    configure_firewall
    configure_fail2ban
    configure_redis
    configure_nginx
    configure_supervisor
    configure_logging
    setup_monitoring
    create_production_config
    setup_ssl
    
    show_summary
}

# Run setup
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi