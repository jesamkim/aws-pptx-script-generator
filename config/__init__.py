"""Configuration package for AWS SA Presentation Script Generator."""

from .aws_config import AWSConfig, BedrockClient, aws_config, bedrock_client
from .mcp_config import MCPConfig, MCPClient, mcp_config, mcp_client

__all__ = [
    "AWSConfig",
    "BedrockClient", 
    "aws_config",
    "bedrock_client",
    "MCPConfig",
    "MCPClient",
    "mcp_config", 
    "mcp_client",
]
