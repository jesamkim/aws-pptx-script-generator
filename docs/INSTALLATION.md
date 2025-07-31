# Installation Guide

This guide provides detailed installation instructions for the AWS PowerPoint Script Generator with **real AWS Documentation MCP integration**.

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

### 2. AWS CLI

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
git clone https://github.com/jesamkim/aws-pptx-script-generator.git
cd aws-pptx-script-generator
```

### 2. Create Virtual Environment

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

```bash
# Upgrade pip first
pip install --upgrade pip

# Install core dependencies
pip install -r requirements.txt

# Install AWS Documentation MCP Server (CRITICAL)
pip install awslabs-aws-documentation-mcp-server

# Install additional MCP client
pip install python-mcp-client

# Install pydantic-settings (if not already installed)
pip install pydantic-settings
```

## AWS Documentation MCP Server Setup

The application integrates with AWS Documentation MCP server for real-time AWS service information.

### 1. Verify MCP Server Installation

```bash
# Check if MCP server is installed
pip show awslabs-aws-documentation-mcp-server

# Test MCP server can be imported
python -c "from awslabs.aws_documentation_mcp_server.server import main; print('MCP server ready')"
```

### 2. Configure MCP Settings

The `mcp-settings.json` file should already be configured correctly:

```json
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
```

### 3. Test MCP Integration

```bash
# Run MCP integration test
python tests/test_mcp_connection.py

# Expected output should show successful connection and tool discovery
```

## AWS Bedrock Setup

### 1. Enable Claude 3.7 Sonnet

1. **Access AWS Console** → Navigate to AWS Bedrock service
2. **Request Model Access** → Go to "Model access" and request access to "Anthropic Claude 3.7 Sonnet"
3. **Wait for Approval** → Usually approved within 24 hours

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
        "arn:aws:bedrock:*::foundation-model/us.anthropic.claude-3-7-sonnet-*"
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
```

### 2. Application Configuration

The application uses `config/` directory for configuration files:

- `aws_config.py`: AWS Bedrock client configuration
- `mcp_config.py`: MCP client configuration

## Verification

### 1. Run Installation Tests

```bash
# Test basic functionality
python tests/test_installation.py

# Test MCP integration
python tests/test_mcp_connection.py

# Test complete integration
python tests/test_mcp_integration.py

# Run all tests
python tests/run_tests.py
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

#### Missing Dependencies
```bash
# Install missing packages
pip install -r requirements.txt
pip install awslabs-aws-documentation-mcp-server
pip install pydantic-settings
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
python -c "from awslabs.aws_documentation_mcp_server.server import main; print('MCP server can be imported')"

# Check MCP configuration
cat mcp-settings.json

# Test MCP connection
python tests/test_mcp_connection.py
```

#### Bedrock Access Issues
```bash
# Check model access
aws bedrock list-foundation-models --region us-west-2

# If Claude not listed, request access in AWS Console
```

#### Environment Variable Issues
```bash
# Check if .env file exists
ls -la .env

# Verify environment variables
cat .env

# Set environment variables manually if needed
export AWS_REGION=us-west-2
export AWS_DEFAULT_REGION=us-west-2
```

### Performance Issues

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

### MCP-Specific Troubleshooting

#### MCP Server Not Starting
```bash
# Check Python version (must be 3.10+)
python --version

# Verify MCP server installation
pip show awslabs-aws-documentation-mcp-server

# Test server import
python -c "from awslabs.aws_documentation_mcp_server.server import main; main()" --help
```

#### MCP Connection Timeout
```bash
# Increase timeout in .env
MCP_TIMEOUT=60

# Check network connectivity
ping docs.aws.amazon.com
```

#### MCP Tools Not Available
```bash
# Check MCP configuration
python tests/test_mcp_connection.py

# Verify autoApprove settings in mcp-settings.json
```

## Next Steps

After successful installation:

1. **Read the [Usage Guide](../README.md#usage-guide)**
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
**Last Updated**: July 31, 2025  
**Compatibility**: Python 3.10+ (required), AWS Bedrock, Claude 3.7 Sonnet, AWS Documentation MCP Server
