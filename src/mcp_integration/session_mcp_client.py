"""Session-based MCP Client for AWS Documentation.

This module provides a proper session-based MCP client that maintains
persistent communication with the AWS Documentation MCP server.
"""

import json
import asyncio
import os
from typing import Dict, Any, Optional, List
from loguru import logger


class SessionMCPClient:
    """Session-based MCP client for proper communication."""
    
    def __init__(self, server_config: Dict[str, Any]):
        """Initialize MCP session client.
        
        Args:
            server_config: MCP server configuration
        """
        self.server_config = server_config
        self.process = None
        self.request_id = 0
        self.initialized = False
    
    async def start(self) -> bool:
        """Start MCP server process and initialize session."""
        try:
            # Start server process
            command = [
                self.server_config["command"],
                *self.server_config["args"]
            ]
            
            env = os.environ.copy()
            env.update(self.server_config.get("env", {}))
            
            self.process = await asyncio.create_subprocess_exec(
                *command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            # Initialize session
            await self._initialize()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start MCP session: {str(e)}")
            return False
    
    async def _initialize(self):
        """Initialize MCP session."""
        init_request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "aws-pptx-script-generator",
                    "version": "1.0.0"
                }
            }
        }
        
        response = await self._send_request(init_request)
        if response and "result" in response:
            self.initialized = True
            logger.info("MCP session initialized successfully")
            
            # Send initialized notification
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            await self._send_notification(initialized_notification)
            
        else:
            raise Exception("Failed to initialize MCP session")
    
    def _next_id(self) -> int:
        """Get next request ID."""
        self.request_id += 1
        return self.request_id
    
    async def _send_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send request and wait for response."""
        if not self.process:
            return None
        
        try:
            # Send request
            request_json = json.dumps(request) + "\n"
            self.process.stdin.write(request_json.encode())
            await self.process.stdin.drain()
            
            # Read response
            response_line = await self.process.stdout.readline()
            if response_line:
                response = json.loads(response_line.decode().strip())
                return response
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to send MCP request: {str(e)}")
            return None
    
    async def _send_notification(self, notification: Dict[str, Any]):
        """Send notification (no response expected)."""
        if not self.process:
            return
        
        try:
            notification_json = json.dumps(notification) + "\n"
            self.process.stdin.write(notification_json.encode())
            await self.process.stdin.drain()
        except Exception as e:
            logger.error(f"Failed to send MCP notification: {str(e)}")
    
    async def search_documentation(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """Search AWS documentation."""
        if not self.initialized:
            return None
        
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": "search_documentation",
                "arguments": {
                    "query": query
                }
            }
        }
        
        response = await self._send_request(request)
        if response and "result" in response and "content" in response["result"]:
            return response["result"]["content"]
        
        return None
    
    async def read_documentation(self, url: str) -> Optional[str]:
        """Read AWS documentation page."""
        if not self.initialized:
            return None
        
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": "read_documentation",
                "arguments": {
                    "url": url
                }
            }
        }
        
        response = await self._send_request(request)
        if response and "result" in response and "content" in response["result"]:
            return response["result"]["content"]
        
        return None
    
    async def close(self):
        """Close MCP session."""
        if self.process:
            try:
                self.process.stdin.close()
                await self.process.wait()
            except Exception as e:
                logger.error(f"Error closing MCP session: {str(e)}")


class AWSDocsMCPClient:
    """High-level AWS Documentation MCP client."""
    
    def __init__(self):
        """Initialize AWS Docs MCP client."""
        self.session = None
        self.server_config = None
        self._load_config()
    
    def _load_config(self):
        """Load MCP server configuration."""
        try:
            settings_path = os.path.join(os.getcwd(), "mcp-settings.json")
            with open(settings_path, 'r') as f:
                settings = json.load(f)
            
            mcp_servers = settings.get("mcpServers", {})
            server_key = "github.com/awslabs/mcp/tree/main/src/aws-documentation-mcp-server"
            self.server_config = mcp_servers.get(server_key)
            
        except Exception as e:
            logger.error(f"Failed to load MCP configuration: {str(e)}")
    
    async def get_service_documentation(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get AWS service documentation via MCP.
        
        Args:
            service_name: AWS service name
            
        Returns:
            Service documentation or None if failed
        """
        if not self.server_config:
            logger.warning("No MCP server configuration available")
            return None
        
        try:
            # Start session if not already started
            if not self.session:
                self.session = SessionMCPClient(self.server_config)
                if not await self.session.start():
                    logger.error("Failed to start MCP session")
                    return None
            
            # Search for service documentation
            search_results = await self.session.search_documentation(f"{service_name} user guide")
            
            if not search_results:
                logger.warning(f"No search results for {service_name}")
                return None
            
            # Get the first result
            first_result = search_results[0] if search_results else None
            if not first_result:
                return None
            
            # Extract information
            return {
                "service_name": service_name,
                "title": first_result.get("title", ""),
                "url": first_result.get("url", ""),
                "content": first_result.get("content", ""),
                "description": first_result.get("description", "")
            }
            
        except Exception as e:
            logger.error(f"Failed to get service documentation for {service_name}: {str(e)}")
            return None
    
    async def close(self):
        """Close MCP client."""
        if self.session:
            await self.session.close()
            self.session = None
