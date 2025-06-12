#!/bin/bash
# Batman Incorporated - Complete Installation Script
# Author: Robin (DevOps Engineer)
# Purpose: Production-ready installation with all dependencies and configurations

set -euo pipefail

# Colors for output
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly RED='\033[0;31m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Installation configuration
readonly BATMAN_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
readonly INSTALL_PREFIX="${INSTALL_PREFIX:-$HOME/.local}"
readonly CONFIG_DIR="${CONFIG_DIR:-$HOME/.glados/batman-incorporated}"
readonly MIN_PYTHON_VERSION="3.8"
readonly REQUIRED_DISK_SPACE_MB=500

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} ✅ $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} ⚠️  $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} ❌ $1" >&2
}

# Display banner
display_banner() {
    cat << 'EOF'

    ╔══════════════════════════════════════════════════════════╗
    ║        🦇 BATMAN INCORPORATED INSTALLATION 🦇           ║
    ║                                                          ║
    ║  "I am vengeance. I am the night. I am Batman Inc!"    ║
    ╚══════════════════════════════════════════════════════════╝

EOF
}

# Check system requirements
check_system_requirements() {
    log_info "Checking system requirements..."
    
    # Check OS
    if [[ "$OSTYPE" != "linux-gnu"* ]] && [[ "$OSTYPE" != "darwin"* ]]; then
        log_error "Unsupported operating system: $OSTYPE"
        return 1
    fi
    
    # Check disk space
    local available_space_mb=$(df -m "$BATMAN_DIR" | awk 'NR==2 {print $4}')
    if [[ $available_space_mb -lt $REQUIRED_DISK_SPACE_MB ]]; then
        log_error "Insufficient disk space. Required: ${REQUIRED_DISK_SPACE_MB}MB, Available: ${available_space_mb}MB"
        return 1
    fi
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        return 1
    fi
    
    local python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (${MIN_PYTHON_VERSION//./, }) else 1)"; then
        log_error "Python ${MIN_PYTHON_VERSION}+ required, found ${python_version}"
        return 1
    fi
    
    log_success "System requirements met (Python ${python_version}, ${available_space_mb}MB available)"
}

# Install Python dependencies
install_python_deps() {
    log_info "Setting up Python environment..."
    
    # Create virtual environment
    if [[ ! -d "$BATMAN_DIR/venv" ]]; then
        python3 -m venv "$BATMAN_DIR/venv"
        log_success "Virtual environment created"
    else
        log_success "Virtual environment already exists"
    fi
    
    # Activate and upgrade pip
    source "$BATMAN_DIR/venv/bin/activate"
    python -m pip install --quiet --upgrade pip setuptools wheel
    
    # Install dependencies
    if [[ -f "$BATMAN_DIR/requirements.txt" ]]; then
        log_info "Installing Python dependencies..."
        python -m pip install --quiet -r "$BATMAN_DIR/requirements.txt"
        log_success "Python dependencies installed"
    else
        log_error "requirements.txt not found"
        return 1
    fi
}

# Create directory structure
create_directory_structure() {
    log_info "Creating directory structure..."
    
    local dirs=(
        "$CONFIG_DIR"
        "$CONFIG_DIR/logs"
        "$CONFIG_DIR/tasks"
        "$CONFIG_DIR/reports"
        "$CONFIG_DIR/cache"
        "$CONFIG_DIR/worktrees"
        "$CONFIG_DIR/sessions"
        "$CONFIG_DIR/backups"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
    done
    
    log_success "Directory structure created"
}

# Install configuration files
install_config_files() {
    log_info "Installing configuration files..."
    
    # Copy default config if not exists
    if [[ ! -f "$CONFIG_DIR/config.yaml" ]]; then
        if [[ -f "$BATMAN_DIR/config/default_config.yaml" ]]; then
            cp "$BATMAN_DIR/config/default_config.yaml" "$CONFIG_DIR/config.yaml"
            log_success "Configuration file installed"
        else
            log_warning "Default configuration not found, creating minimal config"
            cat > "$CONFIG_DIR/config.yaml" << 'EOF'
# Batman Incorporated Configuration
version: "1.0"

# Execution settings
execution:
  default_mode: safe
  max_retries: 3
  timeout_seconds: 300

# Agent settings
agents:
  real_agents: false
  parallel_execution: true
  
# Logging
logging:
  level: INFO
  format: narrative
  
# Arsenal tools
arsenal:
  auto_install: true
  prefer_local: true
EOF
            log_success "Minimal configuration created"
        fi
    else
        log_success "Configuration already exists"
    fi
}

# Install command-line interface
install_cli() {
    log_info "Installing command-line interface..."
    
    local bin_dir="$INSTALL_PREFIX/bin"
    mkdir -p "$bin_dir"
    
    # Create wrapper script
    cat > "$bin_dir/batman" << EOF
#!/bin/bash
# Batman Incorporated CLI wrapper
# Auto-generated by install.sh

# Set environment
export BATMAN_HOME="$BATMAN_DIR"
export BATMAN_CONFIG_DIR="$CONFIG_DIR"

# Activate virtual environment and run
source "$BATMAN_DIR/venv/bin/activate"
exec python "$BATMAN_DIR/batman.py" "\$@"
EOF
    
    chmod +x "$bin_dir/batman"
    
    # Check PATH
    if [[ ":$PATH:" != *":$bin_dir:"* ]]; then
        log_warning "Add $bin_dir to your PATH:"
        echo "    echo 'export PATH=\"$bin_dir:\$PATH\"' >> ~/.bashrc"
        echo "    source ~/.bashrc"
    else
        log_success "CLI installed and available in PATH"
    fi
}

# Install shell completions
install_completions() {
    log_info "Installing shell completions..."
    
    local completion_dir="$INSTALL_PREFIX/share/bash-completion/completions"
    mkdir -p "$completion_dir"
    
    cat > "$completion_dir/batman" << 'EOF'
# Batman Incorporated bash completion
_batman_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Main options
    opts="--help --status --auto --off --install-tools --real-agents --mode --verbose"
    
    # Mode options
    if [[ ${prev} == "--mode" ]]; then
        COMPREPLY=( $(compgen -W "safe fast redundant infinity" -- ${cur}) )
        return 0
    fi
    
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
}

complete -F _batman_completion batman
EOF
    
    log_success "Shell completions installed"
}

# Check optional tools
check_optional_tools() {
    log_info "Checking optional Arsenal tools..."
    
    local tools=("rg" "fd" "bat" "jq" "gh" "delta" "sd" "procs" "exa" "tldr")
    local missing_tools=()
    
    echo -e "\nArsenal status:"
    for tool in "${tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            echo -e "  ${GREEN}✅ $tool${NC} - $(command -v "$tool")"
        else
            echo -e "  ${YELLOW}⚠️  $tool${NC} - not found"
            missing_tools+=("$tool")
        fi
    done
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_info "Install missing tools with: batman --install-tools"
    else
        log_success "All Arsenal tools available"
    fi
}

# Run installation tests
run_tests() {
    log_info "Running installation tests..."
    
    source "$BATMAN_DIR/venv/bin/activate"
    
    # Test 1: Import test
    if python -c "import sys; sys.path.insert(0, '$BATMAN_DIR'); from src.core import batman" 2>/dev/null; then
        log_success "Module import test passed"
    else
        log_error "Module import test failed"
        return 1
    fi
    
    # Test 2: CLI test
    if python "$BATMAN_DIR/batman.py" --help &>/dev/null; then
        log_success "CLI test passed"
    else
        log_error "CLI test failed"
        return 1
    fi
    
    # Test 3: Config test
    if [[ -r "$CONFIG_DIR/config.yaml" ]]; then
        log_success "Configuration test passed"
    else
        log_error "Configuration test failed"
        return 1
    fi
}

# Main installation function
main() {
    display_banner
    
    # Run all installation steps
    check_system_requirements || exit 1
    install_python_deps || exit 1
    create_directory_structure || exit 1
    install_config_files || exit 1
    install_cli || exit 1
    install_completions || exit 1
    check_optional_tools
    run_tests || exit 1
    
    # Success message
    echo -e "\n${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║     🦇 BATMAN INCORPORATED INSTALLATION COMPLETE! 🦇     ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo -e "\nUsage:"
    echo -e "  ${YELLOW}batman${NC} \"create REST API\"    # Execute task"
    echo -e "  ${YELLOW}batman --status${NC}             # View status"
    echo -e "  ${YELLOW}batman --auto${NC}               # Automatic mode"
    echo -e "  ${YELLOW}batman --help${NC}               # Show help"
    echo -e "\nConfiguration: $CONFIG_DIR/config.yaml"
    echo -e "Logs: $CONFIG_DIR/logs/"
    echo -e "\n${BLUE}Ready to fight crime in Gotham!${NC} 🦇"
}

# Run installation
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi