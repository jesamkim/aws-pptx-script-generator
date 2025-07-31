# Quick Start Guide

Get the AWS PowerPoint Script Generator running in **5 minutes** with real MCP integration!

## 🚀 One-Command Installation

### Linux/macOS
```bash
git clone https://github.com/jesamkim/aws-pptx-script-generator.git
cd aws-pptx-script-generator
./install.sh
```

### Windows (PowerShell)
```powershell
git clone https://github.com/jesamkim/aws-pptx-script-generator.git
cd aws-pptx-script-generator
.\install.ps1
```

## ⚡ Manual Quick Setup

### 1. Prerequisites Check
```bash
# Check Python version (must be 3.10+)
python --version

# Check AWS CLI
aws --version
aws sts get-caller-identity
```

### 2. Install & Run
```bash
# Clone and setup
git clone https://github.com/jesamkim/aws-pptx-script-generator.git
cd aws-pptx-script-generator

# Create environment
python -m venv aws-venv
source aws-venv/bin/activate  # Linux/macOS
# aws-venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
pip install awslabs-aws-documentation-mcp-server pydantic-settings

# Start application
streamlit run streamlit_app.py
```

### 3. Open Browser
Navigate to: **http://localhost:8501**

## 🧪 Verify Installation

```bash
# Test everything is working
python tests/test_installation.py
python tests/test_mcp_connection.py
```

## 🔧 Quick Configuration

### AWS Setup (Required)
```bash
# Configure AWS credentials
aws configure
# Enter: Access Key, Secret Key, Region (us-west-2), Format (json)

# Verify Bedrock access
aws bedrock list-foundation-models --region us-west-2
```

### Environment Variables
Create `.env` file:
```env
AWS_REGION=us-west-2
AWS_DEFAULT_REGION=us-west-2
BEDROCK_MODEL_ID=us.anthropic.claude-3-7-sonnet-20250219-v1:0
```

## 🎯 First Use

1. **Upload PowerPoint**: Drag & drop your .pptx file
2. **Enter Presenter Info**: Name, title, experience level
3. **Set Parameters**: Duration, language, audience
4. **Generate Script**: Click "Generate Script" button
5. **Review Results**: Get professional presentation script with timing

## 🔍 Troubleshooting

### Common Issues

#### Python Version Error
```bash
# Install Python 3.10+
# macOS: brew install python@3.10
# Ubuntu: sudo apt install python3.10
# Windows: Download from python.org
```

#### AWS Credentials Error
```bash
aws configure
# Or set environment variables:
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-west-2
```

#### MCP Connection Error
```bash
# Test MCP server
python -c "from awslabs.aws_documentation_mcp_server.server import main; print('MCP OK')"

# Check configuration
cat mcp-settings.json

# Test connection
python tests/test_mcp_connection.py
```

#### Missing Dependencies
```bash
pip install awslabs-aws-documentation-mcp-server
pip install pydantic-settings
pip install python-mcp-client
```

## 📋 System Requirements

- **Python**: 3.10+ (required for MCP server)
- **Memory**: 4GB minimum, 8GB recommended
- **AWS**: Configured credentials with Bedrock access
- **Network**: Internet connection for AWS services

## 🆘 Quick Fixes

```bash
# Reset everything
rm -rf aws-venv .env
python -m venv aws-venv
source aws-venv/bin/activate
pip install -r requirements.txt
pip install awslabs-aws-documentation-mcp-server pydantic-settings

# Test installation
python tests/test_installation.py

# Start fresh
streamlit run streamlit_app.py
```

## 📚 Next Steps

- **Read Full Documentation**: [README.md](README.md)
- **Detailed Installation**: [docs/INSTALLATION.md](docs/INSTALLATION.md)
- **Run All Tests**: `python tests/run_tests.py`
- **Explore Features**: Try different script styles and languages

## 🎉 Success Indicators

✅ **Installation Test Passes**: `python tests/test_installation.py`  
✅ **MCP Connection Works**: `python tests/test_mcp_connection.py`  
✅ **Streamlit Starts**: Application loads at http://localhost:8501  
✅ **AWS Integration**: Can upload and analyze PowerPoint files  
✅ **Script Generation**: Produces professional presentation scripts  

---

**Need Help?** Check the [Troubleshooting Guide](docs/INSTALLATION.md#troubleshooting) or run the diagnostic tests.
