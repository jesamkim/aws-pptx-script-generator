# API Documentation

## Core Components

### Script Generation

#### `generate_content_aware_script()`
Basic script generation with caching.

**Parameters:**
- `analysis_result`: Presentation analysis data
- `persona_data`: Presenter profile information  
- `presentation_params`: Generation parameters

**Returns:** Generated script string

#### `generate_content_aware_script_optimized()`
Advanced script generation with agent-based processing.

**Parameters:**
- `analysis_result`: Presentation analysis data
- `persona_data`: Presenter profile information
- `presentation_params`: Generation parameters

**Returns:** Generated script string with enhanced AWS knowledge

### MCP Integration

#### `AWSDocsClient.get_service_documentation()`
Retrieves AWS service documentation via MCP.

**Parameters:**
- `service_name`: AWS service name (e.g., "lambda", "s3")

**Returns:** `ServiceDocumentation` object or None

#### `SessionMCPClient.search_documentation()`
Searches AWS documentation using MCP server.

**Parameters:**
- `query`: Search query string

**Returns:** List of search results or None

### Caching System

#### `PromptCacheManager`
Manages prompt caching for performance optimization.

**Methods:**
- `get_cached_response()`: Retrieve cached response
- `store_response()`: Store response in cache
- `get_cache_stats()`: Get cache performance metrics

### Configuration

#### Environment Variables
- `AWS_DEFAULT_REGION`: AWS region (default: us-west-2)
- `BEDROCK_MODEL_ID`: Claude model ID
- `LOG_LEVEL`: Logging level (INFO, DEBUG, ERROR)
- `CACHE_TTL`: Cache time-to-live in seconds
- `MAX_WORKERS`: Maximum parallel workers

#### MCP Configuration
Located in `mcp-settings.json`:
```json
{
  "mcpServers": {
    "github.com/awslabs/mcp/tree/main/src/aws-documentation-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.aws-documentation-mcp-server@latest"],
      "env": {"FASTMCP_LOG_LEVEL": "ERROR"},
      "disabled": false
    }
  }
}
```

## Error Handling

All API functions include comprehensive error handling with fallback mechanisms:

- **MCP failures**: Automatic fallback to cached AWS service data
- **Bedrock timeouts**: Retry logic with exponential backoff  
- **Cache misses**: Graceful degradation to direct API calls
- **Network issues**: Offline mode with local knowledge base

## Performance Metrics

- **Cache hit rate**: 60-80% for repeated operations
- **Script generation**: 20-60 seconds depending on complexity
- **MCP response time**: 3-8 seconds per service query
- **Memory usage**: 200-500MB during processing
