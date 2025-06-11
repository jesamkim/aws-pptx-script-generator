# AWS PowerPoint Script Generator

An intelligent presentation script generator that analyzes PowerPoint slides and creates natural, professional presentation scripts using AWS Bedrock and Claude 3.7 Sonnet with advanced caching and MCP integration.

## 🎯 Overview

This application transforms PowerPoint presentations into comprehensive, ready-to-deliver presentation scripts. It combines multimodal AI analysis, AWS service knowledge enhancement, and intelligent script generation to create natural, professional scripts tailored to your presentation style and audience.

## ✨ Key Features

### 🔍 Intelligent Slide Analysis
- **Multimodal Processing**: Analyzes both text content and visual elements
- **AWS Service Detection**: Automatically identifies and categorizes AWS services mentioned
- **Content Summarization**: Extracts key concepts and themes from each slide
- **Technical Complexity Assessment**: Evaluates presentation difficulty level

### 🧠 AI-Powered Script Generation
- **Claude 3.7 Sonnet Integration**: Advanced language model for natural script creation
- **Prompt Caching**: Optimized performance with intelligent caching strategies
- **Persona-Aware Generation**: Adapts to presenter's style and confidence level
- **Slide Flow Continuity**: Ensures smooth transitions between slides

### 📚 AWS Knowledge Enhancement
- **MCP Integration**: Real-time AWS documentation retrieval
- **Service-Specific Information**: Detailed AWS service descriptions and best practices
- **Fallback Knowledge Base**: Comprehensive offline AWS service database
- **Technical Accuracy**: Ensures accurate AWS terminology and concepts

### 🎨 Customizable Output
- **Multiple Script Styles**: Technical, conversational, or formal presentation styles
- **Timing Guidance**: Precise timing recommendations for each slide
- **Speaker Notes**: Detailed presentation tips and guidance
- **Q&A Preparation**: Anticipated questions and suggested answers

## 🏗️ Architecture

### Core Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   Multimodal     │    │   Script        │
│   Frontend      │───▶│   Analyzer       │───▶│   Generator     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   MCP Client     │    │   Cache         │
                       │   (AWS Docs)     │    │   Manager       │
                       └──────────────────┘    └─────────────────┘
```

### Technology Stack
- **Frontend**: Streamlit with responsive UI components
- **AI Models**: Claude 3.7 Sonnet via AWS Bedrock
- **Document Processing**: python-pptx, Pillow for image processing
- **MCP Integration**: Session-based AWS Documentation client
- **Caching**: Multi-layer caching with TTL management
- **Logging**: Structured logging with loguru

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher (required for AWS Documentation MCP server compatibility)
- AWS CLI configured with appropriate permissions
- UV package manager (recommended) or pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd aws-pptx-script-generator
   ```

2. **Set up Python environment**
   ```bash
   # Using UV (recommended)
   uv venv aws-venv
   source aws-venv/bin/activate  # On Windows: aws-venv\Scripts\activate
   uv pip install -r requirements.txt
   
   # Or using pip
   python -m venv aws-venv
   source aws-venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Install AWS Documentation MCP Server**
   ```bash
   # Verify Python version (3.10+ required for MCP server)
   python --version
   
   # Install the MCP server globally
   uvx install awslabs.aws-documentation-mcp-server@latest
   
   # Verify installation
   uvx awslabs.aws-documentation-mcp-server@latest --help
   ```

4. **Configure AWS credentials**
   ```bash
   aws configure
   # Enter your AWS Access Key ID, Secret Access Key, and preferred region
   ```

5. **Set up MCP configuration**
   
   The application uses `mcp-settings.json` for MCP server configuration:
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
           "read_documentation"
         ]
       }
     }
   }
   ```

### Running the Application

```bash
# Start the Streamlit application
streamlit run streamlit_app.py

# The application will be available at http://localhost:8501
```

## 📖 Usage Guide

### Step-by-Step Process

1. **Upload PowerPoint File**
   - Drag and drop your .pptx file or use the file uploader
   - Supported formats: PowerPoint (.pptx) files

2. **Configure Presenter Profile**
   - Enter presenter information (name, title, experience level)
   - Select presentation confidence and interaction style
   - Choose target audience and technical level

3. **Set Presentation Parameters**
   - Define presentation duration and Q&A time
   - Select script style (technical, conversational, formal)
   - Configure timing and speaker notes preferences

4. **AI Analysis**
   - Automatic slide content extraction and analysis
   - AWS service identification and categorization
   - Technical complexity assessment

5. **Script Generation**
   - Choose between basic cached generation or optimized agent-based generation
   - Real-time AWS documentation enhancement via MCP
   - Natural language script creation with proper flow

6. **Review and Export**
   - Review generated script with timing guidance
   - Download as Markdown file
   - Copy to clipboard for immediate use

### Generation Options

#### Basic Cached Generation
- Fast script generation with prompt caching
- Suitable for standard presentations
- Optimized for performance

#### Optimized Agent Generation
- Advanced multi-agent workflow
- Enhanced AWS knowledge integration
- Parallel processing for complex presentations
- Real-time MCP documentation retrieval

## 🔧 Configuration

### Environment Variables

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

### AWS Permissions

Required AWS IAM permissions:

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

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test suites
python tests/test_mcp_integration.py      # MCP integration tests
python tests/test_step5_script_generation.py  # Script generation tests
python tests/test_integrated_mcp.py      # End-to-end MCP tests

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Test Categories

- **Unit Tests**: Individual component testing
- **Integration Tests**: MCP and AWS service integration
- **End-to-End Tests**: Complete workflow validation
- **Performance Tests**: Caching and optimization validation

## 📊 Performance Optimization

### Caching Strategy

The application implements multi-layer caching:

1. **Prompt Caching**: Claude API prompt caching for repeated requests
2. **Response Caching**: In-memory caching of AI responses
3. **MCP Caching**: AWS documentation caching with TTL
4. **Slide Analysis Caching**: Cached multimodal analysis results

### Performance Metrics

- **Script Generation**: 20-60 seconds depending on complexity
- **Cache Hit Rate**: 60-80% for repeated presentations
- **MCP Response Time**: 3-8 seconds per AWS service query
- **Memory Usage**: ~200-500MB during processing

## 🔍 Troubleshooting

### Common Issues

#### MCP Connection Issues
```bash
# Test MCP server availability
python tests/test_mcp_session.py

# Check MCP configuration
cat mcp-settings.json
```

#### AWS Bedrock Access
```bash
# Verify AWS credentials
aws sts get-caller-identity

# Test Bedrock access
aws bedrock list-foundation-models --region us-west-2
```

#### Performance Issues
- Enable caching in configuration
- Reduce max_workers for memory-constrained environments
- Use basic generation for faster results

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
streamlit run streamlit_app.py
```

## 🤝 Contributing

### Development Setup

1. **Fork and clone the repository**
2. **Install development dependencies**
   ```bash
   uv pip install -r requirements-dev.txt
   ```
3. **Run pre-commit hooks**
   ```bash
   pre-commit install
   ```
4. **Run tests before submitting**
   ```bash
   python -m pytest tests/ -v
   ```

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Add docstrings for public methods
- Maintain test coverage above 80%

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **AWS Bedrock Team** for Claude 3.7 Sonnet access
- **Anthropic** for the Claude language model
- **AWS Labs** for the MCP Documentation server
- **Streamlit Team** for the excellent web framework

## 📞 Support

For issues and questions:
- Create an issue in the GitHub repository
- Check the troubleshooting section
- Review test examples in the `tests/` directory

---

**Version**: 2.0.0  
**Last Updated**: December 2024  
**Compatibility**: Python 3.10+, AWS Bedrock, Claude 3.7 Sonnet, AWS Documentation MCP Server
