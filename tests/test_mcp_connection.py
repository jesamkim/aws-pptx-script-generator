"""Simple MCP Connection Test.

This script provides a quick test of MCP server connectivity and basic functionality.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.mcp_integration.real_mcp_client import SyncMCPClient
from src.mcp_integration.aws_docs_client import AWSDocsClient


def test_mcp_connection():
    """Test MCP server connection and basic functionality."""
    print("🔗 Testing MCP Server Connection...")
    print("=" * 50)
    
    # Set up environment
    os.environ['AWS_REGION'] = 'us-west-2'
    os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'
    
    try:
        # Test 1: MCP Client Creation
        print("\n1. Creating MCP Client...")
        client = SyncMCPClient()
        print(f"   ✅ Client created successfully")
        print(f"   📋 Configuration available: {client.is_available()}")
        
        if not client.is_available():
            print("   ⚠️  MCP server configuration not found")
            print("   💡 Check mcp-settings.json file")
            return False
        
        # Test 2: Connection Test
        print("\n2. Testing Connection...")
        connection_ok = client.test_connection()
        print(f"   {'✅' if connection_ok else '❌'} Connection: {'SUCCESS' if connection_ok else 'FAILED'}")
        
        if not connection_ok:
            print("   💡 Make sure AWS Documentation MCP server is installed:")
            print("      pip install awslabs-aws-documentation-mcp-server")
            return False
        
        # Test 3: Search Functionality
        print("\n3. Testing Search Functionality...")
        results = client.search_documentation("AWS S3", limit=2)
        print(f"   📊 Search results: {len(results)} found")
        
        for i, result in enumerate(results[:2]):
            title = result.get('title', 'No title')
            url = result.get('url', 'No URL')
            print(f"   {i+1}. {title[:60]}...")
            if url:
                print(f"      🔗 {url}")
        
        # Test 4: Documentation Reading
        if results and results[0].get('url'):
            print("\n4. Testing Documentation Reading...")
            url = results[0]['url']
            content = client.read_documentation(url, max_length=200)
            if content:
                print(f"   ✅ Read {len(content)} characters from documentation")
                print(f"   📄 Preview: {content[:100]}...")
            else:
                print("   ⚠️  Could not read documentation content")
        
        # Test 5: Service Documentation
        print("\n5. Testing Service Documentation...")
        service_docs = client.get_service_documentation('lambda')
        if service_docs:
            print(f"   ✅ Retrieved Lambda documentation")
            print(f"   📋 Service: {service_docs.get('service_name', 'Unknown')}")
            print(f"   📄 Description: {service_docs.get('description', 'No description')[:100]}...")
        else:
            print("   ⚠️  Could not retrieve service documentation")
        
        print("\n🎉 All MCP connection tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integrated_client():
    """Test the integrated AWS Documentation client."""
    print("\n" + "=" * 50)
    print("🔧 Testing Integrated AWS Documentation Client...")
    print("=" * 50)
    
    try:
        # Test integrated client
        print("\n1. Creating Integrated Client...")
        aws_client = AWSDocsClient()
        print(f"   ✅ AWS Documentation client created")
        print(f"   🔗 Real MCP available: {aws_client.use_real_mcp}")
        
        # Test service documentation
        print("\n2. Testing Service Documentation...")
        s3_docs = aws_client.get_service_documentation('s3')
        
        if s3_docs:
            print(f"   ✅ Retrieved S3 documentation")
            print(f"   📋 Service: {s3_docs.service_name}")
            print(f"   📄 Description: {s3_docs.description[:150]}...")
            print(f"   🔧 Best practices: {len(s3_docs.best_practices)} found")
            print(f"   🔗 URL: {s3_docs.documentation_url}")
        else:
            print("   ❌ Failed to retrieve S3 documentation")
            return False
        
        # Test best practices
        print("\n3. Testing Best Practices...")
        practices = aws_client.get_best_practices('ec2')
        print(f"   📊 EC2 best practices: {len(practices)} found")
        
        for i, practice in enumerate(practices[:3]):
            print(f"   {i+1}. {practice[:80]}...")
        
        print("\n🎉 Integrated client tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Integrated client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all connection tests."""
    print("🧪 MCP Connection Test Suite")
    print("=" * 50)
    
    # Test basic MCP connection
    mcp_success = test_mcp_connection()
    
    # Test integrated client
    integrated_success = test_integrated_client()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   MCP Connection: {'✅ PASSED' if mcp_success else '❌ FAILED'}")
    print(f"   Integrated Client: {'✅ PASSED' if integrated_success else '❌ FAILED'}")
    
    if mcp_success and integrated_success:
        print("\n🎉 All tests passed! MCP integration is working correctly.")
        return True
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
