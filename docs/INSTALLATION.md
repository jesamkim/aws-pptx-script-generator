# Installation Guide

This guide provides detailed installation instructions for the AWS PowerPoint Script Generator.

## System Requirements

### Minimum Requirements
- **Operating System**: macOS 10.15+, Ubuntu 18.04+, Windows 10+
- **Python**: 3.10 or higher (required for AWS Documentation MCP server)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 2GB free space
- **Network**: Internet connection for AWS Bedrock and MCP services

### Recommended Requirements
- **Memory**: 16GB RAM for optimal performance
- **CPU**: Multi-core processor for parallel processing
- **Storage**: SSD for faster caching operations

## Prerequisites Installation

### 1. Python Environment

#### macOS
```bash
# Install Python 3.10+ via Homebrew
brew install python@3.10

# Verify installation (should be 3.10 or higher)
python3 --version
```

#### Ubuntu/Debian
```bash
# Update package list
sudo apt update

# Install Python 3.10 (required for MCP server compatibility)
sudo apt install python3.10 python3.10-venv python3.10-pip

# Verify installation
python3.10 --version
```

#### Windows
1. Download Python 3.10+ from [python.org](https://www.python.org/downloads/)
2. **Important**: Select Python 3.10 or higher for MCP server compatibility
3. Run installer with "Add Python to PATH" checked
4. Verify in Command Prompt: `python --version` (should show 3.10+)

### 2. UV Package Manager (Recommended)

UV is a fast Python package manager that significantly improves installation speed.

#### Installation
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uv --version
```

### 3. AWS CLI

#### Installation
```bash
# macOS
brew install awscli

# Ubuntu/Debian
sudo apt install awscli

# Windows
# Download from https://aws.amazon.com/cli/
```

#### Configuration
```bash
# Configure AWS credentials
aws configure

# Enter the following when prompted:
# AWS Access Key ID: [Your Access Key]
# AWS Secret Access Key: [Your Secret Key]
# Default region name: us-west-2
# Default output format: json
```

## Application Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd aws-pptx-script-generator
```

### 2. Create Virtual Environment

#### Using UV (Recommended)
```bash
# Create virtual environment
uv venv aws-venv

# Activate environment
# macOS/Linux:
source aws-venv/bin/activate
# Windows:
aws-venv\Scripts\activate
```

#### Using Standard Python
```bash
# Create virtual environment
python -m venv aws-venv

# Activate environment
# macOS/Linux:
source aws-venv/bin/activate
# Windows:
aws-venv\Scripts\activate
```

### 3. Install Dependencies

#### Using UV (Faster)
```bash
# Install all dependencies
uv pip install -r requirements.txt

# Install development dependencies (optional)
uv pip install -r requirements-dev.txt
```

#### Using Pip
```bash
# Upgrade pip first
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

## AWS Documentation MCP Server Setup

The application integrates with AWS Documentation MCP server for real-time AWS service information.

### 1. Install MCP Server

**Important**: The AWS Documentation MCP server requires Python 3.10 or higher.

```bash
# Verify Python version first (must be 3.10+)
python --version

# Install globally using uvx
uvx install awslabs.aws-documentation-mcp-server@latest

# Verify installation
uvx awslabs.aws-documentation-mcp-server@latest --help
```

If you encounter Python version errors, ensure you have Python 3.10+ installed before proceeding.

### 2. Configure MCP Settings

Create or verify `mcp-settings.json` in the project root:

```json
{
  "mcpServers": {
    "github.com/awslabs/mcp/tree/main/src/aws-documentation-mcp-server": {
      "command": "uvx",
      "args": [
        "awslabs.aws-documentation-mcp-server@latest"
      ],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
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
```

### 3. Test MCP Integration

```bash
# Run MCP integration test
python tests/test_mcp_session.py

# Expected output should show successful connection and tool discovery
```

## AWS Bedrock Setup

### 1. Enable Claude 3.7 Sonnet

1. **Access AWS Console**
   - Navigate to AWS Bedrock service
   - Go to "Model access" in the left sidebar

2. **Request Model Access**
   - Find "Anthropic Claude 3.7 Sonnet"
   - Click "Request model access"
   - Fill out the access request form
   - Wait for approval (usually within 24 hours)

3. **Verify Access**
   ```bash
   # List available models
   aws bedrock list-foundation-models --region us-west-2
   
   # Look for: anthropic.claude-3-7-sonnet-20241022-v1:0
   ```

### 2. Set Up IAM Permissions

Create an IAM policy with the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-7-sonnet-*"
      ]
    }
  ]
}
```

Attach this policy to your AWS user or role.

## Configuration

### 1. Environment Variables

Create a `.env` file in the project root:

```env
# AWS Configuration
AWS_DEFAULT_REGION=us-west-2
AWS_PROFILE=default

# Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-7-sonnet-20241022-v1:0

# Application Settings
LOG_LEVEL=INFO
CACHE_TTL=3600
MAX_WORKERS=4

# MCP Configuration
MCP_TIMEOUT=30
MCP_LOG_LEVEL=ERROR
```

### 2. Application Configuration

The application uses `config/` directory for configuration files:

- `aws_config.py`: AWS Bedrock client configuration
- `mcp_config.py`: MCP client configuration
- `app_config.py`: General application settings

## Verification

### 1. Run Installation Tests

```bash
# Test basic functionality
python tests/test_basic.py

# Test AWS integration
python tests/test_integration.py

# Test MCP integration
python tests/test_mcp_integration.py

# Test script generation
python tests/test_step5_script_generation.py
```

### 2. Start Application

```bash
# Start Streamlit application
streamlit run streamlit_app.py

# Application should be available at http://localhost:8501
```

### 3. Verify Features

1. **Upload a test PowerPoint file**
2. **Configure presenter profile**
3. **Generate a script using basic generation**
4. **Verify MCP integration in logs**
5. **Check script quality and timing**

## Troubleshooting

### Common Installation Issues

#### Python Version Issues
```bash
# Check Python version (must be 3.10+)
python --version

# If version is < 3.10, install newer version for MCP compatibility
# Follow Python installation steps above
```

#### UV Installation Issues
```bash
# If UV fails, use pip instead
pip install -r requirements.txt
```

#### AWS Credentials Issues
```bash
# Verify AWS configuration
aws sts get-caller-identity

# If fails, reconfigure
aws configure
```

#### MCP Server Issues
```bash
# Test MCP server directly
uvx awslabs.aws-documentation-mcp-server@latest

# Check MCP configuration
cat mcp-settings.json
```

#### Bedrock Access Issues
```bash
# Check model access
aws bedrock list-foundation-models --region us-west-2

# If Claude not listed, request access in AWS Console
```

### Performance Optimization

#### Memory Issues
```bash
# Reduce max workers in .env
MAX_WORKERS=2

# Enable swap if needed (Linux)
sudo swapon --show
```

#### Slow Performance
```bash
# Enable caching
CACHE_TTL=7200

# Use SSD storage for cache
# Ensure adequate RAM (8GB+)
```

## Next Steps

After successful installation:

1. **Read the [Usage Guide](../FINAL_README.md#usage-guide)**
2. **Try the example presentations in `examples/`**
3. **Explore advanced configuration options**
4. **Set up monitoring and logging**

## Support

If you encounter issues during installation:

1. **Check the [Troubleshooting](#troubleshooting) section**
2. **Review log files in `logs/` directory**
3. **Run diagnostic tests in `tests/` directory**
4. **Create an issue in the GitHub repository**

---

**Installation Guide Version**: 2.0.0  
**Last Updated**: December 2024  
**Compatibility**: Python 3.10+ (required), AWS Bedrock, MCP 2024-11-05
