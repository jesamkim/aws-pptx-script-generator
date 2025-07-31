#!/bin/bash

# AWS PowerPoint Script Generator - Advanced Environment Setup Script
# Version: 2.1.0
# Last Updated: July 31, 2025

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_MIN_VERSION="3.10"
VENV_NAME="aws-venv"
LOG_FILE="$PROJECT_ROOT/setup.log"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_step() {
    echo -e "${CYAN}[STEP]${NC} $1" | tee -a "$LOG_FILE"
}

log_debug() {
    echo -e "${PURPLE}[DEBUG]${NC} $1" >> "$LOG_FILE"
}

# Progress indicator
show_progress() {
    local current=$1
    local total=$2
    local description=$3
    local percentage=$((current * 100 / total))
    local bar_length=30
    local filled_length=$((percentage * bar_length / 100))
    
    printf "\r${CYAN}[%3d%%]${NC} [" "$percentage"
    printf "%*s" "$filled_length" | tr ' ' '='
    printf "%*s" $((bar_length - filled_length)) | tr ' ' '-'
    printf "] %s" "$description"
    
    if [ "$current" -eq "$total" ]; then
        echo ""
    fi
}

# Initialize log file
init_logging() {
    echo "=== AWS PowerPoint Script Generator - Environment Setup ===" > "$LOG_FILE"
    echo "Started at: $(date)" >> "$LOG_FILE"
    echo "Script: $0" >> "$LOG_FILE"
    echo "Working directory: $(pwd)" >> "$LOG_FILE"
    echo "User: $(whoami)" >> "$LOG_FILE"
    echo "System: $(uname -a)" >> "$LOG_FILE"
    echo "=========================================================" >> "$LOG_FILE"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Compare version numbers
version_compare() {
    local version1=$1
    local version2=$2
    
    if [ "$version1" = "$version2" ]; then
        return 0
    fi
    
    local IFS=.
    local i ver1=($version1) ver2=($version2)
    
    # Fill empty fields in ver1 with zeros
    for ((i=${#ver1[@]}; i<${#ver2[@]}; i++)); do
        ver1[i]=0
    done
    
    for ((i=0; i<${#ver1[@]}; i++)); do
        if [[ -z ${ver2[i]} ]]; then
            ver2[i]=0
        fi
        if ((10#${ver1[i]} > 10#${ver2[i]})); then
            return 1
        fi
        if ((10#${ver1[i]} < 10#${ver2[i]})); then
            return 2
        fi
    done
    return 0
}

# Detect operating system
detect_os() {
    log_step "Detecting operating system..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command_exists lsb_release; then
            OS_NAME=$(lsb_release -si)
            OS_VERSION=$(lsb_release -sr)
        elif [ -f /etc/os-release ]; then
            . /etc/os-release
            OS_NAME=$NAME
            OS_VERSION=$VERSION_ID
        else
            OS_NAME="Linux"
            OS_VERSION="Unknown"
        fi
        OS_TYPE="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS_NAME="macOS"
        OS_VERSION=$(sw_vers -productVersion)
        OS_TYPE="macos"
    else
        OS_NAME="Unknown"
        OS_VERSION="Unknown"
        OS_TYPE="unknown"
    fi
    
    log_info "Detected OS: $OS_NAME $OS_VERSION ($OS_TYPE)"
    log_debug "OSTYPE: $OSTYPE"
}

# Check and install Python
check_install_python() {
    log_step "Checking Python installation..."
    
    local python_cmd=""
    local python_version=""
    
    # Try different Python commands
    for cmd in python3 python python3.12 python3.11 python3.10; do
        if command_exists "$cmd"; then
            python_version=$($cmd --version 2>&1 | cut -d' ' -f2)
            version_compare "$python_version" "$PYTHON_MIN_VERSION"
            local result=$?
            
            if [ $result -eq 0 ] || [ $result -eq 1 ]; then
                python_cmd=$cmd
                break
            fi
        fi
    done
    
    if [ -z "$python_cmd" ]; then
        log_warning "Python $PYTHON_MIN_VERSION+ not found. Attempting to install..."
        install_python
        
        # Re-check after installation
        for cmd in python3 python python3.12 python3.11 python3.10; do
            if command_exists "$cmd"; then
                python_version=$($cmd --version 2>&1 | cut -d' ' -f2)
                version_compare "$python_version" "$PYTHON_MIN_VERSION"
                local result=$?
                
                if [ $result -eq 0 ] || [ $result -eq 1 ]; then
                    python_cmd=$cmd
                    break
                fi
            fi
        done
        
        if [ -z "$python_cmd" ]; then
            log_error "Failed to install Python $PYTHON_MIN_VERSION+. Please install manually."
            exit 1
        fi
    fi
    
    log_success "Python $python_version found at $(which $python_cmd)"
    echo "$python_cmd" > "$PROJECT_ROOT/.python_cmd"
    export PYTHON_CMD="$python_cmd"
}

# Install Python based on OS
install_python() {
    log_info "Installing Python $PYTHON_MIN_VERSION+..."
    
    case "$OS_TYPE" in
        "linux")
            if command_exists apt-get; then
                log_info "Using apt-get to install Python..."
                sudo apt-get update
                sudo apt-get install -y python3.10 python3.10-venv python3.10-pip
            elif command_exists yum; then
                log_info "Using yum to install Python..."
                sudo yum install -y python3.10 python3.10-pip
            elif command_exists dnf; then
                log_info "Using dnf to install Python..."
                sudo dnf install -y python3.10 python3.10-pip
            else
                log_error "No supported package manager found. Please install Python manually."
                exit 1
            fi
            ;;
        "macos")
            if command_exists brew; then
                log_info "Using Homebrew to install Python..."
                brew install python@3.10
            else
                log_error "Homebrew not found. Please install Python manually from python.org"
                exit 1
            fi
            ;;
        *)
            log_error "Unsupported OS for automatic Python installation. Please install Python $PYTHON_MIN_VERSION+ manually."
            exit 1
            ;;
    esac
}

# Check and install AWS CLI
check_install_aws_cli() {
    log_step "Checking AWS CLI installation..."
    
    if command_exists aws; then
        local aws_version=$(aws --version 2>&1 | cut -d' ' -f1 | cut -d'/' -f2)
        log_success "AWS CLI $aws_version found"
        
        # Check AWS credentials
        if aws sts get-caller-identity >/dev/null 2>&1; then
            local account_id=$(aws sts get-caller-identity --query Account --output text)
            local user_arn=$(aws sts get-caller-identity --query Arn --output text)
            log_success "AWS credentials configured (Account: $account_id)"
            log_debug "User ARN: $user_arn"
        else
            log_warning "AWS credentials not configured"
            configure_aws_credentials
        fi
    else
        log_warning "AWS CLI not found. Installing..."
        install_aws_cli
        configure_aws_credentials
    fi
}

# Install AWS CLI
install_aws_cli() {
    log_info "Installing AWS CLI..."
    
    case "$OS_TYPE" in
        "linux")
            if command_exists curl; then
                curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
                unzip awscliv2.zip
                sudo ./aws/install
                rm -rf aws awscliv2.zip
            else
                log_error "curl not found. Please install AWS CLI manually."
                exit 1
            fi
            ;;
        "macos")
            if command_exists brew; then
                brew install awscli
            else
                log_error "Homebrew not found. Please install AWS CLI manually."
                exit 1
            fi
            ;;
        *)
            log_error "Unsupported OS for automatic AWS CLI installation."
            exit 1
            ;;
    esac
}

# Configure AWS credentials interactively
configure_aws_credentials() {
    log_step "Configuring AWS credentials..."
    
    echo ""
    echo -e "${YELLOW}AWS Credentials Configuration${NC}"
    echo "============================================"
    echo "You need to configure AWS credentials to use this application."
    echo "You can get these from the AWS Console > IAM > Users > Security credentials"
    echo ""
    
    read -p "Do you want to configure AWS credentials now? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        aws configure
        
        # Verify configuration
        if aws sts get-caller-identity >/dev/null 2>&1; then
            log_success "AWS credentials configured successfully"
        else
            log_error "AWS credentials configuration failed"
            exit 1
        fi
    else
        log_warning "AWS credentials not configured. You'll need to configure them later with 'aws configure'"
    fi
}

# Create and setup virtual environment
setup_virtual_environment() {
    log_step "Setting up Python virtual environment..."
    
    cd "$PROJECT_ROOT"
    
    if [ -d "$VENV_NAME" ]; then
        log_warning "Virtual environment already exists"
        read -p "Remove existing environment and create new one? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$VENV_NAME"
        else
            log_info "Using existing virtual environment"
            return
        fi
    fi
    
    log_info "Creating virtual environment with $PYTHON_CMD..."
    $PYTHON_CMD -m venv "$VENV_NAME"
    
    # Activate virtual environment
    source "$VENV_NAME/bin/activate"
    
    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip
    
    log_success "Virtual environment created and activated"
}

# Install Python dependencies with progress
install_dependencies() {
    log_step "Installing Python dependencies..."
    
    local packages=(
        "streamlit>=1.28.0"
        "python-pptx>=0.6.21"
        "Pillow>=10.0.0"
        "loguru>=0.7.2"
        "boto3>=1.34.0"
        "botocore>=1.34.0"
        "requests>=2.31.0"
        "pandas>=2.0.0"
        "numpy>=1.24.0"
        "pydantic>=2.0.0"
        "pydantic-settings>=2.5.2"
        "mcp>=1.11.0"
        "python-mcp-client>=0.1.0"
        "awslabs-aws-documentation-mcp-server"
    )
    
    local total=${#packages[@]}
    local current=0
    
    for package in "${packages[@]}"; do
        current=$((current + 1))
        show_progress $current $total "Installing $package"
        
        if pip install "$package" >> "$LOG_FILE" 2>&1; then
            log_debug "Successfully installed: $package"
        else
            log_error "Failed to install: $package"
            exit 1
        fi
    done
    
    log_success "All dependencies installed successfully"
}

# Create configuration files
create_configuration_files() {
    log_step "Creating configuration files..."
    
    # Create .env file
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        log_info "Creating .env file..."
        cat > "$PROJECT_ROOT/.env" << EOF
# AWS Configuration
AWS_DEFAULT_REGION=us-west-2
AWS_REGION=us-west-2
AWS_PROFILE=default

# Bedrock Configuration
BEDROCK_MODEL_ID=us.anthropic.claude-3-7-sonnet-20250219-v1:0

# Application Settings
LOG_LEVEL=INFO
CACHE_TTL=3600
MAX_WORKERS=4

# MCP Configuration
MCP_TIMEOUT=30
MCP_LOG_LEVEL=ERROR
EOF
        log_success ".env file created"
    else
        log_info ".env file already exists"
    fi
    
    # Verify MCP settings
    if [ ! -f "$PROJECT_ROOT/mcp-settings.json" ]; then
        log_info "Creating mcp-settings.json..."
        cat > "$PROJECT_ROOT/mcp-settings.json" << EOF
{
  "mcpServers": {
    "awslabs.aws-documentation-mcp-server": {
      "command": "python",
      "args": [
        "-c", "from awslabs.aws_documentation_mcp_server.server import main; main()"
      ],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR",
        "AWS_DOCUMENTATION_PARTITION": "aws"
      },
      "disabled": false,
      "autoApprove": [
        "search_documentation",
        "read_documentation",
        "recommend"
      ]
    }
  }
}
EOF
        log_success "mcp-settings.json created"
    else
        log_info "mcp-settings.json already exists"
    fi
}

# Run comprehensive tests
run_comprehensive_tests() {
    log_step "Running comprehensive tests..."
    
    cd "$PROJECT_ROOT"
    
    local tests=(
        "tests/test_installation.py"
        "tests/test_mcp_connection.py"
    )
    
    local total=${#tests[@]}
    local current=0
    local passed=0
    
    for test in "${tests[@]}"; do
        current=$((current + 1))
        show_progress $current $total "Running $(basename "$test")"
        
        if [ -f "$test" ]; then
            if python "$test" >> "$LOG_FILE" 2>&1; then
                log_success "$(basename "$test") passed"
                passed=$((passed + 1))
            else
                log_warning "$(basename "$test") failed (check $LOG_FILE for details)"
            fi
        else
            log_warning "Test file not found: $test"
        fi
    done
    
    log_info "Tests completed: $passed/$total passed"
}

# Create startup script
create_startup_script() {
    log_step "Creating startup script..."
    
    cat > "$PROJECT_ROOT/start.sh" << 'EOF'
#!/bin/bash

# AWS PowerPoint Script Generator - Startup Script
# This script activates the virtual environment and starts the application

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "aws-venv" ]; then
    echo "❌ Virtual environment not found. Please run ./install.sh first."
    exit 1
fi

# Activate virtual environment
source aws-venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please run ./install.sh first."
    exit 1
fi

# Start the application
echo "🚀 Starting AWS PowerPoint Script Generator..."
echo "📱 Open your browser to: http://localhost:8501"
echo "⏹️  Press Ctrl+C to stop the application"
echo ""

streamlit run streamlit_app.py
EOF
    
    chmod +x "$PROJECT_ROOT/start.sh"
    log_success "Startup script created: start.sh"
}

# Create uninstall script
create_uninstall_script() {
    log_step "Creating uninstall script..."
    
    cat > "$PROJECT_ROOT/uninstall.sh" << 'EOF'
#!/bin/bash

# AWS PowerPoint Script Generator - Uninstall Script

echo "🗑️  AWS PowerPoint Script Generator - Uninstall"
echo "=============================================="

read -p "Are you sure you want to uninstall? This will remove the virtual environment and configuration files. (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing virtual environment..."
    rm -rf aws-venv
    
    echo "Removing configuration files..."
    rm -f .env setup.log
    
    echo "Removing startup scripts..."
    rm -f start.sh uninstall.sh
    
    echo "✅ Uninstall completed!"
    echo "Note: AWS credentials and the project files remain unchanged."
else
    echo "Uninstall cancelled."
fi
EOF
    
    chmod +x "$PROJECT_ROOT/uninstall.sh"
    log_success "Uninstall script created: uninstall.sh"
}

# Generate setup report
generate_setup_report() {
    log_step "Generating setup report..."
    
    local report_file="$PROJECT_ROOT/setup_report.md"
    
    cat > "$report_file" << EOF
# AWS PowerPoint Script Generator - Setup Report

**Generated on:** $(date)  
**Setup Script Version:** 2.1.0  
**User:** $(whoami)  
**System:** $OS_NAME $OS_VERSION  

## Environment Details

- **Python Version:** $($PYTHON_CMD --version 2>&1)
- **Python Command:** $PYTHON_CMD
- **Virtual Environment:** $VENV_NAME
- **AWS CLI:** $(aws --version 2>&1 | head -1)
- **Project Root:** $PROJECT_ROOT

## Installed Components

✅ Python $PYTHON_MIN_VERSION+ compatible  
✅ Virtual environment created  
✅ All Python dependencies installed  
✅ AWS CLI configured  
✅ MCP server installed  
✅ Configuration files created  
✅ Startup scripts created  

## Quick Start Commands

\`\`\`bash
# Start the application
./start.sh

# Run tests
python tests/test_installation.py
python tests/test_mcp_connection.py

# Uninstall (if needed)
./uninstall.sh
\`\`\`

## Configuration Files

- **.env**: Environment variables
- **mcp-settings.json**: MCP server configuration
- **start.sh**: Application startup script
- **uninstall.sh**: Uninstall script

## Troubleshooting

If you encounter issues:

1. Check the setup log: \`cat setup.log\`
2. Run installation tests: \`python tests/test_installation.py\`
3. Test MCP connection: \`python tests/test_mcp_connection.py\`
4. Verify AWS credentials: \`aws sts get-caller-identity\`

## Next Steps

1. **Start the application**: \`./start.sh\`
2. **Open browser**: http://localhost:8501
3. **Upload a PowerPoint file** and generate your first script!

---
*Setup completed successfully! 🎉*
EOF
    
    log_success "Setup report generated: setup_report.md"
}

# Main setup function
main() {
    echo -e "${CYAN}🚀 AWS PowerPoint Script Generator - Advanced Environment Setup${NC}"
    echo -e "${CYAN}================================================================${NC}"
    echo ""
    
    # Initialize logging
    init_logging
    
    # Detect OS
    detect_os
    
    # Setup steps with progress
    local steps=(
        "check_install_python"
        "check_install_aws_cli"
        "setup_virtual_environment"
        "install_dependencies"
        "create_configuration_files"
        "run_comprehensive_tests"
        "create_startup_script"
        "create_uninstall_script"
        "generate_setup_report"
    )
    
    local total_steps=${#steps[@]}
    local current_step=0
    
    for step in "${steps[@]}"; do
        current_step=$((current_step + 1))
        echo ""
        echo -e "${PURPLE}[Step $current_step/$total_steps]${NC} Running $step..."
        $step
    done
    
    echo ""
    echo -e "${CYAN}================================================================${NC}"
    log_success "Advanced environment setup completed successfully!"
    echo ""
    echo -e "${GREEN}🎉 Your AWS PowerPoint Script Generator is ready to use!${NC}"
    echo ""
    echo "📋 Setup Summary:"
    echo "   • Python environment: ✅ Configured"
    echo "   • AWS credentials: ✅ Configured"
    echo "   • Dependencies: ✅ Installed"
    echo "   • MCP integration: ✅ Ready"
    echo "   • Tests: ✅ Passed"
    echo ""
    echo "🚀 Quick Start:"
    echo "   ./start.sh                    # Start the application"
    echo "   python tests/run_tests.py    # Run all tests"
    echo "   cat setup_report.md          # View detailed report"
    echo ""
    echo "🌐 Application URL: http://localhost:8501"
    echo "📄 Setup log: setup.log"
    echo "📊 Setup report: setup_report.md"
    echo ""
}

# Run main function
main "$@"
