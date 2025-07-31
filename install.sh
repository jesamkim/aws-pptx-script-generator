#!/bin/bash

# AWS PowerPoint Script Generator - Automated Installation Script
# Version: 2.0.0
# Last Updated: July 31, 2025

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
check_python_version() {
    log_info "Checking Python version..."
    
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        log_error "Python not found. Please install Python 3.10 or higher."
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
        log_success "Python $PYTHON_VERSION found (compatible)"
    else
        log_error "Python 3.10+ required. Found: $PYTHON_VERSION"
        log_info "Please install Python 3.10 or higher:"
        log_info "  macOS: brew install python@3.10"
        log_info "  Ubuntu: sudo apt install python3.10"
        log_info "  Windows: Download from python.org"
        exit 1
    fi
}

# Check AWS CLI
check_aws_cli() {
    log_info "Checking AWS CLI..."
    
    if command_exists aws; then
        AWS_VERSION=$(aws --version 2>&1 | cut -d' ' -f1 | cut -d'/' -f2)
        log_success "AWS CLI $AWS_VERSION found"
        
        # Check AWS credentials
        if aws sts get-caller-identity >/dev/null 2>&1; then
            log_success "AWS credentials configured"
        else
            log_warning "AWS credentials not configured"
            log_info "Please run: aws configure"
        fi
    else
        log_warning "AWS CLI not found"
        log_info "Please install AWS CLI:"
        log_info "  macOS: brew install awscli"
        log_info "  Ubuntu: sudo apt install awscli"
        log_info "  Windows: Download from aws.amazon.com/cli/"
    fi
}

# Create virtual environment
create_virtual_environment() {
    log_info "Creating virtual environment..."
    
    if [ -d "aws-venv" ]; then
        log_warning "Virtual environment already exists"
        read -p "Remove existing environment and create new one? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf aws-venv
        else
            log_info "Using existing virtual environment"
            return
        fi
    fi
    
    $PYTHON_CMD -m venv aws-venv
    log_success "Virtual environment created"
}

# Activate virtual environment
activate_virtual_environment() {
    log_info "Activating virtual environment..."
    
    if [ -f "aws-venv/bin/activate" ]; then
        source aws-venv/bin/activate
        log_success "Virtual environment activated"
    elif [ -f "aws-venv/Scripts/activate" ]; then
        source aws-venv/Scripts/activate
        log_success "Virtual environment activated"
    else
        log_error "Virtual environment activation script not found"
        exit 1
    fi
}

# Install dependencies
install_dependencies() {
    log_info "Installing dependencies..."
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install core dependencies
    log_info "Installing core dependencies from requirements.txt..."
    pip install -r requirements.txt
    
    # Install MCP server
    log_info "Installing AWS Documentation MCP Server..."
    pip install awslabs-aws-documentation-mcp-server
    
    # Install additional MCP client
    log_info "Installing Python MCP Client..."
    pip install python-mcp-client
    
    # Install pydantic-settings if not already installed
    log_info "Installing pydantic-settings..."
    pip install pydantic-settings
    
    log_success "All dependencies installed"
}

# Create environment file
create_env_file() {
    log_info "Creating .env file..."
    
    if [ -f ".env" ]; then
        log_warning ".env file already exists"
        return
    fi
    
    cat > .env << EOF
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
}

# Verify MCP configuration
verify_mcp_configuration() {
    log_info "Verifying MCP configuration..."
    
    if [ -f "mcp-settings.json" ]; then
        log_success "mcp-settings.json found"
    else
        log_warning "mcp-settings.json not found, creating default configuration..."
        
        cat > mcp-settings.json << EOF
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
        log_success "Default mcp-settings.json created"
    fi
}

# Run tests
run_tests() {
    log_info "Running installation tests..."
    
    # Test installation
    if python tests/test_installation.py; then
        log_success "Installation test passed"
    else
        log_warning "Installation test failed (some components may need manual setup)"
    fi
    
    # Test MCP connection
    if python tests/test_mcp_connection.py; then
        log_success "MCP connection test passed"
    else
        log_warning "MCP connection test failed (MCP server may need manual setup)"
    fi
}

# Main installation function
main() {
    echo "🚀 AWS PowerPoint Script Generator - Automated Installation"
    echo "============================================================"
    
    # Check prerequisites
    check_python_version
    check_aws_cli
    
    # Create and activate virtual environment
    create_virtual_environment
    activate_virtual_environment
    
    # Install dependencies
    install_dependencies
    
    # Create configuration files
    create_env_file
    verify_mcp_configuration
    
    # Run tests
    run_tests
    
    echo ""
    echo "============================================================"
    log_success "Installation completed!"
    echo ""
    echo "Next steps:"
    echo "1. Activate the virtual environment:"
    echo "   source aws-venv/bin/activate  # Linux/macOS"
    echo "   aws-venv\\Scripts\\activate     # Windows"
    echo ""
    echo "2. Configure AWS credentials (if not done already):"
    echo "   aws configure"
    echo ""
    echo "3. Start the application:"
    echo "   streamlit run streamlit_app.py"
    echo ""
    echo "4. Open your browser to: http://localhost:8501"
    echo ""
    echo "For troubleshooting, run:"
    echo "   python tests/test_installation.py"
    echo "   python tests/test_mcp_connection.py"
    echo ""
}

# Run main function
main "$@"
