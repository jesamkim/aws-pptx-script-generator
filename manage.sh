#!/bin/bash

# AWS PowerPoint Script Generator - Comprehensive Management Script
# Version: 2.1.0
# Last Updated: July 31, 2025

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_NAME="aws-venv"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# Check if virtual environment is activated
check_venv() {
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        return 0
    else
        return 1
    fi
}

# Activate virtual environment
activate_venv() {
    if [ -f "$PROJECT_ROOT/$VENV_NAME/bin/activate" ]; then
        source "$PROJECT_ROOT/$VENV_NAME/bin/activate"
        log_success "Virtual environment activated"
    elif [ -f "$PROJECT_ROOT/$VENV_NAME/Scripts/activate" ]; then
        source "$PROJECT_ROOT/$VENV_NAME/Scripts/activate"
        log_success "Virtual environment activated"
    else
        log_error "Virtual environment not found. Run 'install' command first."
        exit 1
    fi
}

# Show help
show_help() {
    echo -e "${CYAN}AWS PowerPoint Script Generator - Management Tool${NC}"
    echo -e "${CYAN}=================================================${NC}"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo -e "  ${GREEN}install${NC}     - Full installation with environment setup"
    echo -e "  ${GREEN}start${NC}       - Start the Streamlit application"
    echo -e "  ${GREEN}stop${NC}        - Stop the running application"
    echo -e "  ${GREEN}restart${NC}     - Restart the application"
    echo -e "  ${GREEN}status${NC}      - Show application and environment status"
    echo -e "  ${GREEN}validate${NC}    - Validate environment configuration"
    echo -e "  ${GREEN}repair${NC}      - Automatically repair environment issues"
    echo -e "  ${GREEN}test${NC}        - Run all tests"
    echo -e "  ${GREEN}update${NC}      - Update dependencies"
    echo -e "  ${GREEN}clean${NC}       - Clean temporary files and caches"
    echo -e "  ${GREEN}uninstall${NC}   - Remove virtual environment and configs"
    echo -e "  ${GREEN}logs${NC}        - Show application logs"
    echo -e "  ${GREEN}backup${NC}      - Create backup of configuration"
    echo -e "  ${GREEN}restore${NC}     - Restore configuration from backup"
    echo -e "  ${GREEN}help${NC}        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 install          # Full installation"
    echo "  $0 start             # Start application"
    echo "  $0 validate          # Check environment"
    echo "  $0 repair            # Fix issues automatically"
    echo ""
}

# Install command
cmd_install() {
    log_step "Starting comprehensive installation..."
    
    if [ -f "$PROJECT_ROOT/scripts/setup_environment.sh" ]; then
        log_info "Running advanced environment setup..."
        bash "$PROJECT_ROOT/scripts/setup_environment.sh"
    else
        log_info "Running basic installation..."
        bash "$PROJECT_ROOT/install.sh"
    fi
    
    log_success "Installation completed!"
}

# Start command
cmd_start() {
    log_step "Starting AWS PowerPoint Script Generator..."
    
    cd "$PROJECT_ROOT"
    
    # Check if virtual environment exists
    if [ ! -d "$VENV_NAME" ]; then
        log_error "Virtual environment not found. Run '$0 install' first."
        exit 1
    fi
    
    # Activate virtual environment if not already active
    if ! check_venv; then
        activate_venv
    fi
    
    # Check if application is already running
    if pgrep -f "streamlit run streamlit_app.py" > /dev/null; then
        log_warning "Application appears to be already running"
        log_info "Use '$0 stop' to stop it first, or '$0 restart' to restart"
        exit 1
    fi
    
    # Start the application
    log_info "Starting Streamlit application..."
    log_info "Application will be available at: http://localhost:8501"
    log_info "Press Ctrl+C to stop the application"
    echo ""
    
    streamlit run streamlit_app.py
}

# Stop command
cmd_stop() {
    log_step "Stopping AWS PowerPoint Script Generator..."
    
    # Find and kill streamlit processes
    pids=$(pgrep -f "streamlit run streamlit_app.py" || true)
    
    if [ -z "$pids" ]; then
        log_info "No running application found"
        return 0
    fi
    
    for pid in $pids; do
        log_info "Stopping process $pid..."
        kill "$pid"
        sleep 2
        
        # Force kill if still running
        if kill -0 "$pid" 2>/dev/null; then
            log_warning "Force stopping process $pid..."
            kill -9 "$pid"
        fi
    done
    
    log_success "Application stopped"
}

# Restart command
cmd_restart() {
    log_step "Restarting AWS PowerPoint Script Generator..."
    
    cmd_stop
    sleep 2
    cmd_start
}

# Status command
cmd_status() {
    log_step "Checking system status..."
    echo ""
    
    # Check virtual environment
    if [ -d "$VENV_NAME" ]; then
        log_success "Virtual environment: ✅ Present"
    else
        log_error "Virtual environment: ❌ Missing"
    fi
    
    # Check if activated
    if check_venv; then
        log_success "Virtual environment: ✅ Activated"
    else
        log_warning "Virtual environment: ⚠️  Not activated"
    fi
    
    # Check configuration files
    config_files=(".env" "mcp-settings.json" "requirements.txt")
    for file in "${config_files[@]}"; do
        if [ -f "$file" ]; then
            log_success "Configuration: ✅ $file present"
        else
            log_error "Configuration: ❌ $file missing"
        fi
    done
    
    # Check if application is running
    if pgrep -f "streamlit run streamlit_app.py" > /dev/null; then
        log_success "Application: ✅ Running"
        log_info "URL: http://localhost:8501"
    else
        log_info "Application: ⏹️  Stopped"
    fi
    
    # Check AWS credentials
    if command -v aws >/dev/null 2>&1; then
        if aws sts get-caller-identity >/dev/null 2>&1; then
            log_success "AWS credentials: ✅ Configured"
        else
            log_warning "AWS credentials: ⚠️  Not configured"
        fi
    else
        log_error "AWS CLI: ❌ Not installed"
    fi
    
    echo ""
}

# Validate command
cmd_validate() {
    log_step "Running environment validation..."
    
    cd "$PROJECT_ROOT"
    
    if [ -f "scripts/validate_environment.py" ]; then
        python scripts/validate_environment.py
    else
        log_warning "Advanced validation script not found, running basic tests..."
        if [ -f "tests/test_installation.py" ]; then
            python tests/test_installation.py
        else
            log_error "No validation tests found"
            exit 1
        fi
    fi
}

# Repair command
cmd_repair() {
    log_step "Running automatic environment repair..."
    
    cd "$PROJECT_ROOT"
    
    if [ -f "scripts/repair_environment.py" ]; then
        python scripts/repair_environment.py --validate-first
    else
        log_error "Repair script not found"
        log_info "Try running '$0 install' to reinstall the environment"
        exit 1
    fi
}

# Test command
cmd_test() {
    log_step "Running comprehensive tests..."
    
    cd "$PROJECT_ROOT"
    
    # Activate virtual environment if not already active
    if ! check_venv; then
        activate_venv
    fi
    
    if [ -f "tests/run_tests.py" ]; then
        python tests/run_tests.py
    else
        log_warning "Comprehensive test runner not found, running individual tests..."
        
        test_files=(
            "tests/test_installation.py"
            "tests/test_mcp_connection.py"
            "tests/test_basic.py"
        )
        
        for test_file in "${test_files[@]}"; do
            if [ -f "$test_file" ]; then
                log_info "Running $(basename "$test_file")..."
                python "$test_file"
            fi
        done
    fi
}

# Update command
cmd_update() {
    log_step "Updating dependencies..."
    
    cd "$PROJECT_ROOT"
    
    # Activate virtual environment if not already active
    if ! check_venv; then
        activate_venv
    fi
    
    # Update pip
    log_info "Updating pip..."
    pip install --upgrade pip
    
    # Update requirements
    if [ -f "requirements.txt" ]; then
        log_info "Updating requirements..."
        pip install --upgrade -r requirements.txt
    fi
    
    # Update critical packages
    critical_packages=(
        "awslabs-aws-documentation-mcp-server"
        "pydantic-settings"
        "streamlit"
    )
    
    for package in "${critical_packages[@]}"; do
        log_info "Updating $package..."
        pip install --upgrade "$package"
    done
    
    log_success "Dependencies updated successfully"
}

# Clean command
cmd_clean() {
    log_step "Cleaning temporary files and caches..."
    
    cd "$PROJECT_ROOT"
    
    # Clean Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # Clean logs
    if [ -d "logs" ]; then
        log_info "Cleaning log files..."
        rm -f logs/*.log
    fi
    
    # Clean temporary files
    temp_files=(
        "setup.log"
        "validation.log"
        "repair.log"
        "*.tmp"
        ".DS_Store"
    )
    
    for pattern in "${temp_files[@]}"; do
        rm -f $pattern 2>/dev/null || true
    done
    
    # Clean pip cache
    if command -v pip >/dev/null 2>&1; then
        log_info "Cleaning pip cache..."
        pip cache purge 2>/dev/null || true
    fi
    
    log_success "Cleanup completed"
}

# Uninstall command
cmd_uninstall() {
    log_step "Uninstalling AWS PowerPoint Script Generator..."
    
    echo -e "${YELLOW}This will remove:${NC}"
    echo "  • Virtual environment ($VENV_NAME)"
    echo "  • Configuration files (.env)"
    echo "  • Log files"
    echo "  • Temporary files"
    echo ""
    echo -e "${GREEN}This will NOT remove:${NC}"
    echo "  • Source code"
    echo "  • AWS credentials"
    echo "  • System packages"
    echo ""
    
    read -p "Are you sure you want to uninstall? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Stop application if running
        cmd_stop
        
        # Remove virtual environment
        if [ -d "$VENV_NAME" ]; then
            log_info "Removing virtual environment..."
            rm -rf "$VENV_NAME"
        fi
        
        # Remove configuration files
        config_files=(".env" "setup.log" "validation.log" "repair.log")
        for file in "${config_files[@]}"; do
            if [ -f "$file" ]; then
                log_info "Removing $file..."
                rm -f "$file"
            fi
        done
        
        # Clean temporary files
        cmd_clean
        
        log_success "Uninstallation completed!"
        log_info "To reinstall, run: $0 install"
    else
        log_info "Uninstallation cancelled"
    fi
}

# Logs command
cmd_logs() {
    log_step "Showing application logs..."
    
    log_files=(
        "setup.log"
        "validation.log"
        "repair.log"
        "logs/app.log"
        "logs/error.log"
    )
    
    found_logs=false
    
    for log_file in "${log_files[@]}"; do
        if [ -f "$log_file" ]; then
            echo -e "${CYAN}=== $log_file ===${NC}"
            tail -20 "$log_file"
            echo ""
            found_logs=true
        fi
    done
    
    if [ "$found_logs" = false ]; then
        log_info "No log files found"
    fi
}

# Backup command
cmd_backup() {
    log_step "Creating configuration backup..."
    
    backup_dir="backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup configuration files
    config_files=(".env" "mcp-settings.json" "requirements.txt")
    
    for file in "${config_files[@]}"; do
        if [ -f "$file" ]; then
            cp "$file" "$backup_dir/"
            log_info "Backed up: $file"
        fi
    done
    
    # Create backup info
    cat > "$backup_dir/backup_info.txt" << EOF
Backup created: $(date)
System: $(uname -a)
Python: $(python --version 2>&1)
Project root: $PROJECT_ROOT
EOF
    
    log_success "Backup created: $backup_dir"
}

# Restore command
cmd_restore() {
    log_step "Restoring configuration from backup..."
    
    # Find latest backup
    latest_backup=$(ls -1d backup_* 2>/dev/null | sort -r | head -1)
    
    if [ -z "$latest_backup" ]; then
        log_error "No backup found"
        exit 1
    fi
    
    log_info "Found backup: $latest_backup"
    
    read -p "Restore from this backup? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Restore configuration files
        for file in "$latest_backup"/*; do
            if [ -f "$file" ] && [ "$(basename "$file")" != "backup_info.txt" ]; then
                cp "$file" .
                log_info "Restored: $(basename "$file")"
            fi
        done
        
        log_success "Configuration restored from $latest_backup"
    else
        log_info "Restore cancelled"
    fi
}

# Main function
main() {
    case "${1:-help}" in
        install)
            cmd_install
            ;;
        start)
            cmd_start
            ;;
        stop)
            cmd_stop
            ;;
        restart)
            cmd_restart
            ;;
        status)
            cmd_status
            ;;
        validate)
            cmd_validate
            ;;
        repair)
            cmd_repair
            ;;
        test)
            cmd_test
            ;;
        update)
            cmd_update
            ;;
        clean)
            cmd_clean
            ;;
        uninstall)
            cmd_uninstall
            ;;
        logs)
            cmd_logs
            ;;
        backup)
            cmd_backup
            ;;
        restore)
            cmd_restore
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
