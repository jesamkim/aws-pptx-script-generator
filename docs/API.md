# API Documentation

## Overview

This document provides comprehensive API documentation for the AWS PowerPoint Script Generator, including core components, integration points, and configuration options.

## Core Components

### Script Generation

#### `generate_content_aware_script()`
Basic script generation with intelligent caching and dynamic time allocation.

**Parameters:**
- `analysis_result`: Presentation analysis data containing slide information
- `persona_data`: Presenter profile information (name, experience, confidence)
- `presentation_params`: Generation parameters (duration, language, technical depth)

**Returns:** Generated script string with timing guidance and speaker notes

**Example:**
```python
script = generate_content_aware_script(
    analysis_result=presentation_analysis,
    persona_data={
        'full_name': 'John Smith',
        'job_title': 'Senior Solutions Architect',
        'presentation_confidence': 'Expert'
    },
    presentation_params={
        'duration': 30,
        'language': 'English',
        'technical_depth': 4
    }
)
```

#### `generate_content_aware_script_optimized()`
Advanced script generation with multi-agent processing and real-time AWS knowledge enhancement.

**Parameters:**
- `analysis_result`: Presentation analysis data
- `persona_data`: Presenter profile information
- `presentation_params`: Generation parameters
- `mcp_enhanced_services`: Optional enhanced AWS service information

**Returns:** Generated script string with enhanced AWS knowledge and dynamic timing

**Features:**
- Multi-agent parallel processing
- Real-time MCP integration
- Dynamic time allocation per slide
- Enhanced AWS service accuracy

### Multimodal Analysis

#### `MultimodalAnalyzer.analyze_presentation()`
Analyzes PowerPoint slides using Claude 3.7 Sonnet multimodal capabilities.

**Parameters:**
- `slide_images`: List of slide images (PIL Image objects)
- `slide_texts`: List of extracted text content per slide
- `presentation_metadata`: Metadata about the presentation

**Returns:** `PresentationAnalysis` object containing:
- Overall theme and technical complexity
- Per-slide analysis with key concepts
- AWS service identification
- Content structure and flow

#### `SlideTimePlanner.create_time_plan()`
Creates intelligent time allocation plan using AI analysis.

**Parameters:**
- `presentation_analysis`: Complete presentation analysis
- `total_duration`: Total presentation duration in minutes
- `qa_duration`: Q&A duration in minutes
- `buffer_percentage`: Percentage of time to reserve as buffer

**Returns:** `PresentationTimePlan` with optimized slide time allocations

### MCP Integration

#### `AWSDocsClient.get_service_documentation()`
Retrieves AWS service documentation via MCP server integration.

**Parameters:**
- `service_name`: AWS service name (e.g., "lambda", "s3", "dynamodb")

**Returns:** `ServiceDocumentation` object containing:
- Service description and overview
- Use cases and best practices
- Related services and integration patterns
- Documentation URLs

#### `SessionMCPClient.search_documentation()`
Searches AWS documentation using session-based MCP communication.

**Parameters:**
- `query`: Search query string

**Returns:** List of search results with relevant documentation

**Example:**
```python
mcp_client = SessionMCPClient(server_config)
await mcp_client.start()
results = await mcp_client.search_documentation("AWS Lambda best practices")
```

### Caching System

#### `PromptCacheManager`
Manages intelligent caching for performance optimization.

**Methods:**
- `get_cached_response(cache_key)`: Retrieve cached response
- `store_response(cache_key, response, ttl)`: Store response in cache
- `get_cache_stats()`: Get cache performance metrics
- `clear_expired_cache()`: Remove expired cache entries

**Cache Types:**
- **Ephemeral**: In-memory caching for current session
- **Persistent**: File-based caching across sessions
- **Prompt**: Claude API prompt caching for repeated requests

### Configuration

#### Environment Variables
```bash
# AWS Configuration
AWS_DEFAULT_REGION=us-west-2
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

#### MCP Configuration
Located in `mcp-settings.json`:
```json
{
  "mcpServers": {
    "github.com/awslabs/mcp/tree/main/src/aws-documentation-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.aws-documentation-mcp-server@latest"],
      "env": {"FASTMCP_LOG_LEVEL": "ERROR"},
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

## Data Models

### PresentationAnalysis
```python
@dataclass
class PresentationAnalysis:
    overall_theme: str
    technical_complexity: float
    slide_analyses: List[SlideAnalysis]
    aws_services_mentioned: List[str]
    estimated_duration: int
```

### SlideAnalysis
```python
@dataclass
class SlideAnalysis:
    slide_number: int
    content_summary: str
    visual_description: str
    key_concepts: List[str]
    aws_services: List[str]
    technical_complexity: float
```

### SlideTimeAllocation
```python
@dataclass
class SlideTimeAllocation:
    slide_number: int
    slide_type: str  # title, agenda, content, technical, summary, transition
    importance_score: int  # 1-10
    complexity_score: int  # 1-10
    allocated_minutes: float
    rationale: str
```

## Error Handling

All API functions include comprehensive error handling:

### Common Error Types
- **ValidationError**: Invalid input parameters
- **TimeoutError**: API or MCP server timeout
- **AuthenticationError**: AWS credentials or permissions issue
- **ProcessingError**: Slide analysis or script generation failure

### Error Response Format
```python
{
    "success": False,
    "error": {
        "type": "ValidationError",
        "message": "Invalid presentation file format",
        "details": {...}
    }
}
```

### Fallback Mechanisms
- **MCP failures**: Automatic fallback to cached AWS service data
- **Bedrock timeouts**: Retry logic with exponential backoff
- **Cache misses**: Graceful degradation to direct API calls
- **Network issues**: Offline mode with local knowledge base

## Performance Metrics

### Typical Performance
- **Cache hit rate**: 60-80% for repeated operations
- **Script generation**: 20-60 seconds depending on complexity
- **MCP response time**: 3-8 seconds per service query
- **Memory usage**: 200-500MB during processing
- **Concurrent users**: Up to 10 simultaneous presentations

### Optimization Features
- **Parallel processing**: Multi-worker slide analysis
- **Intelligent caching**: Multi-layer caching strategy
- **Resource pooling**: Efficient AWS client management
- **Memory optimization**: Automatic cleanup and garbage collection

## Integration Examples

### Basic Usage
```python
from src.script_generation.claude_script_generator_cached import ClaudeScriptGeneratorCached
from src.analysis.multimodal_analyzer import MultimodalAnalyzer

# Initialize components
analyzer = MultimodalAnalyzer()
generator = ClaudeScriptGeneratorCached(enable_caching=False)

# Analyze presentation
analysis = analyzer.analyze_presentation(slide_images, slide_texts)

# Generate script
script = generator.generate_complete_presentation_script(
    presentation_analysis=analysis,
    persona_data=persona_info,
    presentation_params=params
)
```

### Advanced Usage with MCP
```python
from src.agent.optimized_script_agent import OptimizedScriptAgent

# Initialize optimized agent
agent = OptimizedScriptAgent(enable_caching=False, max_workers=4)

# Generate enhanced script
result = await agent.generate_script_optimized(
    presentation_analysis=analysis,
    persona_profile=profile,
    presentation_params=params
)
```

## Testing

### Unit Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test suites
python tests/test_mcp_integration.py
python tests/test_dynamic_timing.py
python tests/test_korean_script.py
```

### Integration Tests
```bash
# Test MCP integration
python tests/test_mcp_session.py

# Test end-to-end workflow
python tests/test_integrated_mcp.py
```

---

**API Documentation Version**: 2.0.0  
**Last Updated**: June 11, 2025  
**Compatibility**: Python 3.10+, AWS Bedrock, MCP 2024-11-05
