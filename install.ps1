# AWS PowerPoint Script Generator - Windows Installation Script
# Version: 2.0.0
# Last Updated: July 31, 2025

# Set error action preference
$ErrorActionPreference = "Stop"

# Colors for output
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if command exists
function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Check Python version
function Test-PythonVersion {
    Write-Info "Checking Python version..."
    
    $pythonCmd = $null
    if (Test-Command "python") {
        $pythonCmd = "python"
    }
    elseif (Test-Command "python3") {
        $pythonCmd = "python3"
    }
    else {
        Write-Error "Python not found. Please install Python 3.10 or higher from python.org"
        exit 1
    }
    
    try {
        $versionOutput = & $pythonCmd --version 2>&1
        $version = $versionOutput -replace "Python ", ""
        $versionParts = $version.Split(".")
        $major = [int]$versionParts[0]
        $minor = [int]$versionParts[1]
        
        if ($major -eq 3 -and $minor -ge 10) {
            Write-Success "Python $version found (compatible)"
            return $pythonCmd
        }
        else {
            Write-Error "Python 3.10+ required. Found: $version"
            Write-Info "Please install Python 3.10 or higher from python.org"
            exit 1
        }
    }
    catch {
        Write-Error "Failed to check Python version: $_"
        exit 1
    }
}

# Check AWS CLI
function Test-AwsCli {
    Write-Info "Checking AWS CLI..."
    
    if (Test-Command "aws") {
        try {
            $awsVersion = & aws --version 2>&1
            Write-Success "AWS CLI found: $awsVersion"
            
            # Check AWS credentials
            try {
                & aws sts get-caller-identity | Out-Null
                Write-Success "AWS credentials configured"
            }
            catch {
                Write-Warning "AWS credentials not configured"
                Write-Info "Please run: aws configure"
            }
        }
        catch {
            Write-Warning "AWS CLI found but not working properly"
        }
    }
    else {
        Write-Warning "AWS CLI not found"
        Write-Info "Please install AWS CLI from aws.amazon.com/cli/"
    }
}

# Create virtual environment
function New-VirtualEnvironment {
    param([string]$PythonCmd)
    
    Write-Info "Creating virtual environment..."
    
    if (Test-Path "aws-venv") {
        Write-Warning "Virtual environment already exists"
        $response = Read-Host "Remove existing environment and create new one? (y/N)"
        if ($response -eq "y" -or $response -eq "Y") {
            Remove-Item -Recurse -Force "aws-venv"
        }
        else {
            Write-Info "Using existing virtual environment"
            return
        }
    }
    
    try {
        & $PythonCmd -m venv aws-venv
        Write-Success "Virtual environment created"
    }
    catch {
        Write-Error "Failed to create virtual environment: $_"
        exit 1
    }
}

# Activate virtual environment
function Enable-VirtualEnvironment {
    Write-Info "Activating virtual environment..."
    
    $activateScript = "aws-venv\Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        try {
            & $activateScript
            Write-Success "Virtual environment activated"
        }
        catch {
            Write-Error "Failed to activate virtual environment: $_"
            exit 1
        }
    }
    else {
        Write-Error "Virtual environment activation script not found"
        exit 1
    }
}

# Install dependencies
function Install-Dependencies {
    Write-Info "Installing dependencies..."
    
    try {
        # Upgrade pip
        Write-Info "Upgrading pip..."
        & python -m pip install --upgrade pip
        
        # Install core dependencies
        Write-Info "Installing core dependencies from requirements.txt..."
        & pip install -r requirements.txt
        
        # Install MCP server
        Write-Info "Installing AWS Documentation MCP Server..."
        & pip install awslabs-aws-documentation-mcp-server
        
        # Install additional MCP client
        Write-Info "Installing Python MCP Client..."
        & pip install python-mcp-client
        
        # Install pydantic-settings
        Write-Info "Installing pydantic-settings..."
        & pip install pydantic-settings
        
        Write-Success "All dependencies installed"
    }
    catch {
        Write-Error "Failed to install dependencies: $_"
        exit 1
    }
}

# Create environment file
function New-EnvFile {
    Write-Info "Creating .env file..."
    
    if (Test-Path ".env") {
        Write-Warning ".env file already exists"
        return
    }
    
    $envContent = @"
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
"@
    
    try {
        $envContent | Out-File -FilePath ".env" -Encoding UTF8
        Write-Success ".env file created"
    }
    catch {
        Write-Error "Failed to create .env file: $_"
    }
}

# Verify MCP configuration
function Test-McpConfiguration {
    Write-Info "Verifying MCP configuration..."
    
    if (Test-Path "mcp-settings.json") {
        Write-Success "mcp-settings.json found"
    }
    else {
        Write-Warning "mcp-settings.json not found, creating default configuration..."
        
        $mcpConfig = @"
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
"@
        
        try {
            $mcpConfig | Out-File -FilePath "mcp-settings.json" -Encoding UTF8
            Write-Success "Default mcp-settings.json created"
        }
        catch {
            Write-Error "Failed to create mcp-settings.json: $_"
        }
    }
}

# Run tests
function Invoke-Tests {
    Write-Info "Running installation tests..."
    
    # Test installation
    try {
        & python tests/test_installation.py
        Write-Success "Installation test passed"
    }
    catch {
        Write-Warning "Installation test failed (some components may need manual setup)"
    }
    
    # Test MCP connection
    try {
        & python tests/test_mcp_connection.py
        Write-Success "MCP connection test passed"
    }
    catch {
        Write-Warning "MCP connection test failed (MCP server may need manual setup)"
    }
}

# Main installation function
function Main {
    Write-Host "🚀 AWS PowerPoint Script Generator - Windows Installation" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    
    try {
        # Check prerequisites
        $pythonCmd = Test-PythonVersion
        Test-AwsCli
        
        # Create and activate virtual environment
        New-VirtualEnvironment -PythonCmd $pythonCmd
        Enable-VirtualEnvironment
        
        # Install dependencies
        Install-Dependencies
        
        # Create configuration files
        New-EnvFile
        Test-McpConfiguration
        
        # Run tests
        Invoke-Tests
        
        Write-Host ""
        Write-Host "============================================================" -ForegroundColor Cyan
        Write-Success "Installation completed!"
        Write-Host ""
        Write-Host "Next steps:"
        Write-Host "1. Activate the virtual environment:"
        Write-Host "   aws-venv\Scripts\Activate.ps1"
        Write-Host ""
        Write-Host "2. Configure AWS credentials (if not done already):"
        Write-Host "   aws configure"
        Write-Host ""
        Write-Host "3. Start the application:"
        Write-Host "   streamlit run streamlit_app.py"
        Write-Host ""
        Write-Host "4. Open your browser to: http://localhost:8501"
        Write-Host ""
        Write-Host "For troubleshooting, run:"
        Write-Host "   python tests/test_installation.py"
        Write-Host "   python tests/test_mcp_connection.py"
        Write-Host ""
    }
    catch {
        Write-Error "Installation failed: $_"
        exit 1
    }
}

# Run main function
Main
