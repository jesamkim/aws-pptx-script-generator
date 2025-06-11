"""Standard MCP Client Implementation.

This module provides a standard Model Context Protocol (MCP) client
for communicating with MCP servers following the official specification.
"""

import json
import asyncio
import subprocess
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from loguru import logger


@dataclass
class MCPRequest:
    """MCP request structure."""
    jsonrpc: str = "2.0"
    id: int = 1
    method: str = ""
    params: Dict[str, Any] = None


@dataclass
class MCPResponse:
    """MCP response structure."""
    jsonrpc: str
    id: int
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class StandardMCPClient:
    """Standard MCP client following official protocol."""
    
    def __init__(self, server_config: Dict[str, Any]):
        """Initialize MCP client.
        
        Args:
            server_config: MCP server configuration
        """
        self.server_config = server_config
        self.request_id = 1
        
    def _get_next_id(self) -> int:
        """Get next request ID."""
        self.request_id += 1
        return self.request_id
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call MCP tool asynchronously.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool response or None if failed
        """
        try:
            # Create MCP request
            request = MCPRequest(
                id=self._get_next_id(),
                method="tools/call",
                params={
                    "name": tool_name,
                    "arguments": arguments
                }
            )
            
            # Execute via subprocess (for now)
            command = [
                self.server_config["command"],
                *self.server_config["args"]
            ]
            
            # Set environment
            import os
            env = os.environ.copy()
            env.update(self.server_config.get("env", {}))
            
            # Run command
            process = await asyncio.create_subprocess_exec(
                *command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            # Send request
            request_json = json.dumps(request.__dict__)
            stdout, stderr = await process.communicate(request_json.encode())
            
            if process.returncode != 0:
                logger.error(f"MCP tool call failed: {stderr.decode()}")
                return None
            
            # Parse response
            response_data = json.loads(stdout.decode())
            response = MCPResponse(**response_data)
            
            if response.error:
                logger.error(f"MCP tool error: {response.error}")
                return None
            
            return response.result
            
        except Exception as e:
            logger.error(f"MCP tool call failed: {str(e)}")
            return None
    
    def call_tool_sync(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call MCP tool synchronously.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool response or None if failed
        """
        try:
            return asyncio.run(self.call_tool(tool_name, arguments))
        except Exception as e:
            logger.error(f"Sync MCP tool call failed: {str(e)}")
            return None


class AWSDocumentationMCPClient(StandardMCPClient):
    """AWS Documentation specific MCP client."""
    
    def search_documentation(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """Search AWS documentation.
        
        Args:
            query: Search query
            
        Returns:
            Search results or None if failed
        """
        result = self.call_tool_sync("search_documentation", {"query": query})
        if result and "content" in result:
            return result["content"]
        return None
    
    def get_page(self, page_id: str) -> Optional[Dict[str, Any]]:
        """Get documentation page.
        
        Args:
            page_id: Page identifier
            
        Returns:
            Page content or None if failed
        """
        result = self.call_tool_sync("get_page", {"page_id": page_id})
        if result and "content" in result:
            return result["content"]
        return None
    
    def list_tools(self) -> Optional[List[Dict[str, Any]]]:
        """List available tools.
        
        Returns:
            List of available tools or None if failed
        """
        result = self.call_tool_sync("tools/list", {})
        if result and "tools" in result:
            return result["tools"]
        return None
