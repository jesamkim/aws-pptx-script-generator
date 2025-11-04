"""Real AWS Documentation MCP Client Implementation.

This module provides actual integration with AWS Documentation MCP server
using the official MCP client libraries.
"""

import asyncio
import json
import subprocess
import tempfile
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from loguru import logger

# Optional MCP integration - gracefully handle missing package
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    logger.warning("MCP package not installed. MCP integration will be disabled.")
    MCP_AVAILABLE = False
    ClientSession = None
    StdioServerParameters = None
    stdio_client = None


@dataclass
class MCPServerConfig:
    """MCP Server Configuration."""
    command: str
    args: List[str]
    env: Dict[str, str]
    cwd: Optional[str] = None


class RealMCPClient:
    """Real AWS Documentation MCP Client.
    
    This class provides actual integration with AWS Documentation MCP server
    using subprocess and stdio communication.
    """
    
    def __init__(self, config_path: str = "mcp-settings.json"):
        """Initialize real MCP client.

        Args:
            config_path: Path to MCP configuration file
        """
        self.mcp_available = MCP_AVAILABLE
        self.config_path = config_path
        self.server_config = self._load_server_config() if MCP_AVAILABLE else None
        self.session = None
        self._tools_cache = {}

        if not MCP_AVAILABLE:
            logger.warning("MCP integration disabled - package not installed")
        else:
            logger.info("Initialized Real MCP Client")
    
    def _load_server_config(self) -> Optional[MCPServerConfig]:
        """Load MCP server configuration from file.
        
        Returns:
            MCPServerConfig object or None if not found
        """
        try:
            config_file = Path(self.config_path)
            if not config_file.exists():
                logger.warning(f"MCP config file not found: {self.config_path}")
                return None
            
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            # Get the first server configuration
            servers = config_data.get('mcpServers', {})
            if not servers:
                logger.warning("No MCP servers configured")
                return None
            
            # Get AWS Documentation server config
            server_key = next(iter(servers.keys()))
            server_data = servers[server_key]
            
            return MCPServerConfig(
                command=server_data.get('command', 'uvx'),
                args=server_data.get('args', []),
                env=server_data.get('env', {}),
                cwd=server_data.get('cwd')
            )
            
        except Exception as e:
            logger.error(f"Failed to load MCP server config: {str(e)}")
            return None
    
    async def _execute_with_session(self, operation):
        """Execute an operation with a fresh MCP session.
        
        Args:
            operation: Async function to execute with session
            
        Returns:
            Result of the operation
        """
        if not self.server_config:
            logger.error("No server configuration available")
            return None
        
        try:
            # Prepare server parameters
            server_params = StdioServerParameters(
                command=self.server_config.command,
                args=self.server_config.args,
                env=self.server_config.env
            )
            
            # Start stdio client with fresh session for each operation
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize session
                    await session.initialize()
                    
                    # List available tools if not cached
                    if not self._tools_cache:
                        tools_result = await session.list_tools()
                        self._tools_cache = {tool.name: tool for tool in tools_result.tools}
                        logger.info(f"MCP session started with {len(self._tools_cache)} tools")
                    
                    # Execute the operation with the session
                    return await operation(session)
                    
        except Exception as e:
            logger.error(f"Failed to execute MCP operation: {str(e)}")
            return None
    
    async def search_documentation(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search AWS documentation using MCP server.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        async def _search_operation(session):
            # Check if search_documentation tool is available
            if not self._tools_cache:
                tools_result = await session.list_tools()
                self._tools_cache = {tool.name: tool for tool in tools_result.tools}
            
            if 'search_documentation' not in self._tools_cache:
                logger.warning("search_documentation tool not available")
                return []
            
            # Call search_documentation tool
            result = await session.call_tool(
                'search_documentation',
                arguments={
                    'search_phrase': query,
                    'limit': limit
                }
            )
            
            if result.content:
                # Parse the result content
                search_results = []
                for content_item in result.content:
                    if hasattr(content_item, 'text'):
                        try:
                            data = json.loads(content_item.text)
                            if isinstance(data, list):
                                search_results.extend(data)
                            else:
                                search_results.append(data)
                        except json.JSONDecodeError:
                            # If not JSON, treat as plain text
                            search_results.append({
                                'title': query,
                                'content': content_item.text,
                                'url': ''
                            })
                
                logger.info(f"Found {len(search_results)} documentation results for: {query}")
                return search_results
            
            return []
        
        try:
            return await self._execute_with_session(_search_operation)
        except Exception as e:
            logger.error(f"Failed to search documentation: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    async def read_documentation(self, url: str, max_length: int = 5000) -> Optional[str]:
        """Read AWS documentation page using MCP server.
        
        Args:
            url: Documentation URL to read
            max_length: Maximum content length
            
        Returns:
            Documentation content or None if failed
        """
        async def _read_operation(session):
            # Check if read_documentation tool is available
            if not self._tools_cache:
                tools_result = await session.list_tools()
                self._tools_cache = {tool.name: tool for tool in tools_result.tools}
            
            if 'read_documentation' not in self._tools_cache:
                logger.warning("read_documentation tool not available")
                return None
            
            # Call read_documentation tool
            result = await session.call_tool(
                'read_documentation',
                arguments={
                    'url': url,
                    'max_length': max_length
                }
            )
            
            if result.content:
                # Extract text content
                content_text = ""
                for content_item in result.content:
                    if hasattr(content_item, 'text'):
                        content_text += content_item.text + "\n"
                
                logger.info(f"Read documentation from: {url}")
                return content_text.strip()
            
            return None
        
        try:
            return await self._execute_with_session(_read_operation)
        except Exception as e:
            logger.error(f"Failed to read documentation: {str(e)}")
            return None
    
    async def get_service_documentation(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive AWS service documentation.
        
        Args:
            service_name: AWS service name (e.g., 's3', 'lambda', 'ec2')
            
        Returns:
            Service documentation dictionary or None if not found
        """
        try:
            # Search for service documentation
            search_query = f"AWS {service_name} service overview features"
            search_results = await self.search_documentation(search_query, limit=5)
            
            if not search_results:
                logger.warning(f"No documentation found for service: {service_name}")
                return None
            
            # Get the most relevant result
            main_result = search_results[0]
            
            # Read detailed documentation if URL is available
            detailed_content = ""
            if main_result.get('url'):
                detailed_content = await self.read_documentation(
                    main_result['url'], 
                    max_length=3000
                )
            
            # Compile service documentation
            service_docs = {
                'service_name': f"AWS {service_name.upper()}",
                'description': main_result.get('context', ''),
                'detailed_content': detailed_content or main_result.get('content', ''),
                'documentation_url': main_result.get('url', ''),
                'search_results': search_results[:3]  # Top 3 results
            }
            
            logger.info(f"Retrieved comprehensive documentation for: {service_name}")
            return service_docs
            
        except Exception as e:
            logger.error(f"Failed to get service documentation for {service_name}: {str(e)}")
            return None
    
    async def get_best_practices(self, service_name: str) -> List[str]:
        """Get AWS service best practices.
        
        Args:
            service_name: AWS service name
            
        Returns:
            List of best practices
        """
        try:
            # Search for best practices
            search_query = f"AWS {service_name} best practices recommendations"
            search_results = await self.search_documentation(search_query, limit=3)
            
            best_practices = []
            
            for result in search_results:
                if result.get('url'):
                    # Read detailed best practices
                    content = await self.read_documentation(result['url'], max_length=2000)
                    if content:
                        # Extract best practices from content
                        practices = self._extract_best_practices_from_content(content)
                        best_practices.extend(practices)
                else:
                    # Use search result context
                    context = result.get('context', '')
                    if 'best practice' in context.lower() or 'recommendation' in context.lower():
                        best_practices.append(context)
            
            # Remove duplicates and limit results
            unique_practices = list(set(best_practices))[:10]
            
            logger.info(f"Retrieved {len(unique_practices)} best practices for: {service_name}")
            return unique_practices
            
        except Exception as e:
            logger.error(f"Failed to get best practices for {service_name}: {str(e)}")
            return []
    
    def _extract_best_practices_from_content(self, content: str) -> List[str]:
        """Extract best practices from documentation content.
        
        Args:
            content: Documentation content
            
        Returns:
            List of extracted best practices
        """
        practices = []
        
        # Look for common best practice patterns
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in [
                'best practice', 'recommendation', 'should', 'must',
                'important', 'consider', 'ensure', 'avoid'
            ]):
                if len(line) > 20 and len(line) < 200:  # Reasonable length
                    practices.append(line)
        
        return practices[:5]  # Limit to top 5
    
    def is_available(self) -> bool:
        """Check if MCP server is available.
        
        Returns:
            True if server configuration is available, False otherwise
        """
        return self.server_config is not None
    
    async def test_connection(self) -> bool:
        """Test connection to MCP server.
        
        Returns:
            True if connection successful, False otherwise
        """
        async def _test_operation(session):
            # Try to list tools as a connection test
            tools_result = await session.list_tools()
            self._tools_cache = {tool.name: tool for tool in tools_result.tools}
            logger.info(f"Connection test successful: {len(self._tools_cache)} tools available")
            return True
        
        try:
            result = await self._execute_with_session(_test_operation)
            return result is not None
        except Exception as e:
            logger.error(f"MCP connection test failed: {str(e)}")
            return False


# Synchronous wrapper for async operations
class SyncMCPClient:
    """Synchronous wrapper for RealMCPClient."""
    
    def __init__(self, config_path: str = "mcp-settings.json"):
        """Initialize sync MCP client."""
        self.async_client = RealMCPClient(config_path)
        self.mcp_available = MCP_AVAILABLE
    
    def _run_async(self, coro):
        """Run async coroutine in sync context."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro)
    
    def search_documentation(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Sync version of search_documentation."""
        if not self.mcp_available:
            return []
        return self._run_async(self.async_client.search_documentation(query, limit))

    def read_documentation(self, url: str, max_length: int = 5000) -> Optional[str]:
        """Sync version of read_documentation."""
        if not self.mcp_available:
            return None
        return self._run_async(self.async_client.read_documentation(url, max_length))

    def get_service_documentation(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Sync version of get_service_documentation."""
        if not self.mcp_available:
            return None
        return self._run_async(self.async_client.get_service_documentation(service_name))
    
    def get_best_practices(self, service_name: str) -> List[str]:
        """Sync version of get_best_practices."""
        if not self.mcp_available:
            return []
        return self._run_async(self.async_client.get_best_practices(service_name))
    
    def is_available(self) -> bool:
        """Check if MCP server is available."""
        if not self.mcp_available:
            return False
        return self.async_client.is_available()
    
    def test_connection(self) -> bool:
        """Test connection to MCP server."""
        if not self.mcp_available:
            return False
        return self._run_async(self.async_client.test_connection())
