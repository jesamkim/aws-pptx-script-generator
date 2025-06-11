#!/usr/bin/env python3
"""Test MCP Session-based Communication.

This script tests proper session-based communication with the MCP server
following the MCP protocol specification.
"""

import sys
import os
import json
import asyncio
import subprocess
from typing import Dict, Any, Optional, List
from loguru import logger

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MCPSession:
    """Session-based MCP client for proper communication."""
    
    def __init__(self, server_config: Dict[str, Any]):
        """Initialize MCP session.
        
        Args:
            server_config: MCP server configuration
        """
        self.server_config = server_config
        self.process = None
        self.request_id = 0
        self.initialized = False
    
    async def start(self):
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
    
    async def list_tools(self) -> Optional[List[Dict[str, Any]]]:
        """List available tools."""
        if not self.initialized:
            return None
        
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/list"
        }
        
        response = await self._send_request(request)
        if response and "result" in response and "tools" in response["result"]:
            return response["result"]["tools"]
        
        return None
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call a tool."""
        if not self.initialized:
            return None
        
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        response = await self._send_request(request)
        if response and "result" in response:
            return response["result"]
        
        return None
    
    async def close(self):
        """Close MCP session."""
        if self.process:
            try:
                self.process.stdin.close()
                await self.process.wait()
            except Exception as e:
                logger.error(f"Error closing MCP session: {str(e)}")

async def test_mcp_session():
    """Test session-based MCP communication."""
    print("🔗 Testing Session-based MCP Communication...")
    
    # Load settings
    try:
        settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mcp-settings.json")
        with open(settings_path, 'r') as f:
            settings = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load MCP settings: {str(e)}")
        return False
    
    mcp_servers = settings.get("mcpServers", {})
    server_key = "github.com/awslabs/mcp/tree/main/src/aws-documentation-mcp-server"
    server_config = mcp_servers.get(server_key)
    
    if not server_config:
        print("❌ No server configuration found")
        return False
    
    # Test session
    session = MCPSession(server_config)
    
    try:
        # Start session
        print("   Starting MCP session...")
        if not await session.start():
            print("❌ Failed to start MCP session")
            return False
        
        print("✅ MCP session started and initialized")
        
        # List tools
        print("   Listing available tools...")
        tools = await session.list_tools()
        
        if tools:
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')[:100]}...")
        else:
            print("⚠️  No tools returned")
        
        # Test search
        print("   Testing search_documentation tool...")
        search_result = await session.call_tool("search_documentation", {
            "query": "AWS Lambda getting started"
        })
        
        if search_result:
            print("✅ Search tool executed successfully")
            if "content" in search_result:
                content = search_result["content"]
                if isinstance(content, list):
                    print(f"   Found {len(content)} search results")
                elif isinstance(content, str):
                    print(f"   Content length: {len(content)} characters")
            else:
                print(f"   Result keys: {list(search_result.keys())}")
        else:
            print("⚠️  Search tool returned no results")
        
        # Test recommend
        print("   Testing recommend tool...")
        recommend_result = await session.call_tool("recommend", {
            "url": "https://docs.aws.amazon.com/lambda/"
        })
        
        if recommend_result:
            print("✅ Recommend tool executed successfully")
        else:
            print("⚠️  Recommend tool returned no results")
        
        return True
        
    except Exception as e:
        print(f"❌ Session test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        await session.close()

async def main():
    """Run session-based MCP tests."""
    print("🎯 Session-based MCP Test")
    print("=" * 40)
    
    success = await test_mcp_session()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 Session-based MCP test passed!")
        print("✅ Ready to integrate with Streamlit")
    else:
        print("❌ Session-based MCP test failed")
        print("⚠️  Will continue using fallback data")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
