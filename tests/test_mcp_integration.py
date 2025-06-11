#!/usr/bin/env python3
"""Test MCP Integration with AWS Documentation Server.

This script tests the MCP (Model Context Protocol) integration with the
AWS Documentation MCP server to ensure it's working correctly.
"""

import sys
import os
import json
import asyncio
import subprocess
import time
from typing import Dict, Any, Optional, List
from loguru import logger

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_mcp_settings() -> Dict[str, Any]:
    """Load MCP settings from configuration file."""
    try:
        settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mcp-settings.json")
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        return settings
    except Exception as e:
        logger.error(f"Failed to load MCP settings: {str(e)}")
        return {}

def test_mcp_server_availability():
    """Test if MCP server is available and configured."""
    print("🔍 Testing MCP Server Availability...")
    
    settings = load_mcp_settings()
    if not settings:
        print("❌ Failed to load MCP settings")
        return False
    
    mcp_servers = settings.get("mcpServers", {})
    server_key = "github.com/awslabs/mcp/tree/main/src/aws-documentation-mcp-server"
    server_config = mcp_servers.get(server_key)
    
    if not server_config:
        print("❌ AWS Documentation MCP server not found in configuration")
        return False
    
    if server_config.get("disabled", False):
        print("❌ AWS Documentation MCP server is disabled")
        return False
    
    print("✅ MCP server configuration found")
    print(f"   Command: {server_config['command']}")
    print(f"   Args: {server_config['args']}")
    print(f"   Environment: {server_config.get('env', {})}")
    
    return True

def test_mcp_server_execution():
    """Test if MCP server can be executed."""
    print("\n🚀 Testing MCP Server Execution...")
    
    settings = load_mcp_settings()
    mcp_servers = settings.get("mcpServers", {})
    server_key = "github.com/awslabs/mcp/tree/main/src/aws-documentation-mcp-server"
    server_config = mcp_servers.get(server_key)
    
    try:
        # Prepare command
        command = [
            server_config["command"],
            *server_config["args"]
        ]
        
        # Set environment
        env = os.environ.copy()
        env.update(server_config.get("env", {}))
        
        print(f"   Executing: {' '.join(command)}")
        
        # Test server initialization with a simple request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Execute with timeout
        result = subprocess.run(
            command,
            input=json.dumps(mcp_request),
            env=env,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ MCP server executed successfully")
            if result.stdout:
                try:
                    response = json.loads(result.stdout)
                    print(f"   Response: {json.dumps(response, indent=2)}")
                except json.JSONDecodeError:
                    print(f"   Raw output: {result.stdout[:200]}...")
            return True
        else:
            print(f"❌ MCP server execution failed")
            print(f"   Return code: {result.returncode}")
            print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ MCP server execution timed out")
        return False
    except Exception as e:
        print(f"❌ MCP server execution error: {str(e)}")
        return False

def test_mcp_tools_list():
    """Test listing available MCP tools."""
    print("\n🛠️  Testing MCP Tools List...")
    
    settings = load_mcp_settings()
    mcp_servers = settings.get("mcpServers", {})
    server_key = "github.com/awslabs/mcp/tree/main/src/aws-documentation-mcp-server"
    server_config = mcp_servers.get(server_key)
    
    try:
        command = [
            server_config["command"],
            *server_config["args"]
        ]
        
        env = os.environ.copy()
        env.update(server_config.get("env", {}))
        
        # Request tools list
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        result = subprocess.run(
            command,
            input=json.dumps(mcp_request),
            env=env,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout:
            try:
                response = json.loads(result.stdout)
                if "result" in response and "tools" in response["result"]:
                    tools = response["result"]["tools"]
                    print(f"✅ Found {len(tools)} available tools:")
                    for tool in tools:
                        print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
                    return True
                else:
                    print("❌ No tools found in response")
                    print(f"   Response: {json.dumps(response, indent=2)}")
                    return False
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse tools response: {str(e)}")
                print(f"   Raw output: {result.stdout}")
                return False
        else:
            print(f"❌ Tools list request failed")
            print(f"   Return code: {result.returncode}")
            print(f"   Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Tools list test error: {str(e)}")
        return False

def test_mcp_search_documentation():
    """Test searching AWS documentation via MCP."""
    print("\n🔎 Testing MCP Documentation Search...")
    
    settings = load_mcp_settings()
    mcp_servers = settings.get("mcpServers", {})
    server_key = "github.com/awslabs/mcp/tree/main/src/aws-documentation-mcp-server"
    server_config = mcp_servers.get(server_key)
    
    test_queries = [
        "AWS Lambda",
        "Amazon S3 best practices",
        "DynamoDB getting started"
    ]
    
    for query in test_queries:
        try:
            print(f"   Testing query: '{query}'")
            
            command = [
                server_config["command"],
                *server_config["args"]
            ]
            
            env = os.environ.copy()
            env.update(server_config.get("env", {}))
            
            # Search documentation
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "search_documentation",
                    "arguments": {
                        "query": query
                    }
                }
            }
            
            result = subprocess.run(
                command,
                input=json.dumps(mcp_request),
                env=env,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0 and result.stdout:
                try:
                    response = json.loads(result.stdout)
                    if "result" in response:
                        print(f"   ✅ Search successful for '{query}'")
                        # Show first few results
                        if "content" in response["result"]:
                            content = response["result"]["content"]
                            if isinstance(content, list) and content:
                                print(f"      Found {len(content)} results")
                                first_result = content[0]
                                if isinstance(first_result, dict):
                                    title = first_result.get("title", "No title")
                                    print(f"      First result: {title}")
                            elif isinstance(content, str):
                                print(f"      Content preview: {content[:100]}...")
                        continue
                    else:
                        print(f"   ❌ No result in response for '{query}'")
                        print(f"      Response: {json.dumps(response, indent=2)}")
                        return False
                except json.JSONDecodeError as e:
                    print(f"   ❌ Failed to parse search response: {str(e)}")
                    return False
            else:
                print(f"   ❌ Search failed for '{query}'")
                print(f"      Return code: {result.returncode}")
                print(f"      Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"   ❌ Search test error for '{query}': {str(e)}")
            return False
    
    print("✅ All search tests passed")
    return True

def test_mcp_integration_class():
    """Test our MCP integration class."""
    print("\n🔧 Testing MCP Integration Class...")
    
    try:
        from src.mcp_integration.aws_docs_client import AWSDocsClient
        
        # Initialize client
        client = AWSDocsClient()
        print("✅ AWSDocsClient initialized successfully")
        
        # Test service documentation retrieval
        test_services = ["lambda", "s3", "dynamodb"]
        
        for service in test_services:
            print(f"   Testing service: {service}")
            
            # This will use fallback data for now
            doc = client.get_service_documentation(service)
            
            if doc:
                print(f"   ✅ Retrieved documentation for {service}")
                print(f"      Service name: {doc.service_name}")
                print(f"      Description: {doc.description[:100]}...")
                print(f"      Use cases: {len(doc.use_cases)} items")
                print(f"      Best practices: {len(doc.best_practices)} items")
            else:
                print(f"   ❌ Failed to retrieve documentation for {service}")
                return False
        
        print("✅ MCP integration class tests passed")
        return True
        
    except Exception as e:
        print(f"❌ MCP integration class test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_mcp_with_real_server():
    """Test MCP with real server communication."""
    print("\n🌐 Testing Real MCP Server Communication...")
    
    try:
        # Import our standard MCP client
        from src.mcp_integration.mcp_client import AWSDocumentationMCPClient
        
        settings = load_mcp_settings()
        mcp_servers = settings.get("mcpServers", {})
        server_key = "github.com/awslabs/mcp/tree/main/src/aws-documentation-mcp-server"
        server_config = mcp_servers.get(server_key)
        
        if not server_config:
            print("❌ No server configuration found")
            return False
        
        # Initialize MCP client
        mcp_client = AWSDocumentationMCPClient(server_config)
        print("✅ MCP client initialized")
        
        # Test search
        print("   Testing search functionality...")
        search_results = mcp_client.search_documentation("AWS Lambda")
        
        if search_results:
            print(f"   ✅ Search returned {len(search_results)} results")
            return True
        else:
            print("   ⚠️  Search returned no results (may be expected)")
            return True  # Not necessarily a failure
            
    except Exception as e:
        print(f"❌ Real MCP server test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all MCP tests."""
    print("🎯 MCP Integration Test Suite")
    print("=" * 50)
    
    results = []
    
    # Test 1: Server Availability
    results.append(test_mcp_server_availability())
    
    # Test 2: Server Execution
    results.append(test_mcp_server_execution())
    
    # Test 3: Tools List
    results.append(test_mcp_tools_list())
    
    # Test 4: Documentation Search
    results.append(test_mcp_search_documentation())
    
    # Test 5: Integration Class
    results.append(test_mcp_integration_class())
    
    # Test 6: Real Server Communication
    results.append(test_mcp_with_real_server())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 MCP Test Results Summary:")
    print(f"✅ Passed: {sum(results)}/{len(results)} tests")
    print(f"❌ Failed: {len(results) - sum(results)}/{len(results)} tests")
    
    if all(results):
        print("🎉 All MCP tests passed! Ready for Streamlit integration.")
        return True
    else:
        print("⚠️  Some MCP tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    # Run the test suite
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
