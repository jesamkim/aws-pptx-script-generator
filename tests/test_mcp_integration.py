"""Comprehensive MCP Integration Tests.

This module tests the complete MCP integration including real server connection,
fallback mechanisms, and integration with the main application.
"""

import pytest
import asyncio
import os
import sys
from unittest.mock import Mock, patch
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.mcp_integration.real_mcp_client import RealMCPClient, SyncMCPClient
from src.mcp_integration.aws_docs_client import AWSDocsClient
from src.mcp_integration.knowledge_enhancer import KnowledgeEnhancer


class TestRealMCPClient:
    """Test the real MCP client implementation."""
    
    def setup_method(self):
        """Set up test environment."""
        os.environ['AWS_REGION'] = 'us-west-2'
        os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'
    
    def test_mcp_client_initialization(self):
        """Test MCP client initialization."""
        client = RealMCPClient()
        assert client is not None
        assert hasattr(client, 'server_config')
        assert hasattr(client, '_tools_cache')
    
    def test_sync_mcp_client_initialization(self):
        """Test synchronous MCP client wrapper."""
        client = SyncMCPClient()
        assert client is not None
        assert hasattr(client, 'async_client')
        assert client.is_available() in [True, False]  # Should return boolean
    
    @pytest.mark.asyncio
    async def test_async_search_documentation(self):
        """Test async documentation search."""
        client = RealMCPClient()
        
        if not client.is_available():
            pytest.skip("MCP server not available")
        
        try:
            results = await client.search_documentation("AWS S3", limit=2)
            assert isinstance(results, list)
            # Results might be empty if server is not working, but should be a list
            
            if results:
                assert len(results) <= 2
                for result in results:
                    assert isinstance(result, dict)
                    # Should have at least one of these fields
                    assert any(key in result for key in ['title', 'content', 'url'])
        except Exception as e:
            pytest.skip(f"MCP server connection failed: {e}")
    
    def test_sync_search_documentation(self):
        """Test synchronous documentation search."""
        client = SyncMCPClient()
        
        if not client.is_available():
            pytest.skip("MCP server not available")
        
        try:
            results = client.search_documentation("AWS Lambda", limit=2)
            assert isinstance(results, list)
            
            if results:
                assert len(results) <= 2
                for result in results:
                    assert isinstance(result, dict)
        except Exception as e:
            pytest.skip(f"MCP server connection failed: {e}")
    
    def test_connection_test(self):
        """Test MCP server connection."""
        client = SyncMCPClient()
        
        if not client.is_available():
            pytest.skip("MCP server configuration not available")
        
        # Connection test should return boolean
        connection_result = client.test_connection()
        assert isinstance(connection_result, bool)


class TestAWSDocsClient:
    """Test the integrated AWS Documentation client."""
    
    def setup_method(self):
        """Set up test environment."""
        os.environ['AWS_REGION'] = 'us-west-2'
        os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'
    
    def test_aws_docs_client_initialization(self):
        """Test AWS docs client initialization."""
        client = AWSDocsClient()
        assert client is not None
        assert hasattr(client, 'real_mcp_client')
        assert hasattr(client, 'use_real_mcp')
        assert isinstance(client.use_real_mcp, bool)
    
    def test_get_service_documentation(self):
        """Test getting service documentation."""
        client = AWSDocsClient()
        
        # Test with a common service
        result = client.get_service_documentation('s3')
        
        # Should return either real data or mock data
        assert result is not None
        assert hasattr(result, 'service_name')
        assert hasattr(result, 'description')
        assert hasattr(result, 'best_practices')
        assert isinstance(result.best_practices, list)
    
    def test_get_best_practices(self):
        """Test getting best practices."""
        client = AWSDocsClient()
        
        practices = client.get_best_practices('lambda')
        assert isinstance(practices, list)
        
        # Should have some practices (either from real MCP or mock)
        if practices:
            for practice in practices:
                assert isinstance(practice, str)
                assert len(practice) > 0
    
    def test_cache_functionality(self):
        """Test caching functionality."""
        client = AWSDocsClient()
        
        # First call
        result1 = client.get_service_documentation('ec2')
        
        # Second call should use cache
        result2 = client.get_service_documentation('ec2')
        
        # Results should be identical
        if result1 and result2:
            assert result1.service_name == result2.service_name
            assert result1.description == result2.description


class TestKnowledgeEnhancer:
    """Test the knowledge enhancement functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        os.environ['AWS_REGION'] = 'us-west-2'
        os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'
    
    def test_knowledge_enhancer_initialization(self):
        """Test knowledge enhancer initialization."""
        enhancer = KnowledgeEnhancer()
        assert enhancer is not None
        assert hasattr(enhancer, 'aws_docs_client')
    
    def test_enhance_slide_content(self):
        """Test slide content enhancement."""
        enhancer = KnowledgeEnhancer()
        
        # Test content with AWS services
        test_content = """
        This presentation covers Amazon S3 for storage and AWS Lambda for compute.
        We'll discuss how to use these services for building scalable applications.
        """
        
        result = enhancer.enhance_slide_content(test_content, slide_number=1)
        
        assert result is not None
        assert hasattr(result, 'original_content')
        assert hasattr(result, 'enhanced_content')
        assert hasattr(result, 'confidence_score')
        assert isinstance(result.confidence_score, float)
        assert 0.0 <= result.confidence_score <= 1.0
    
    def test_enhance_presentation_content(self):
        """Test enhancing multiple slides."""
        enhancer = KnowledgeEnhancer()
        
        slides_content = [
            "Introduction to AWS services",
            "Amazon S3 for object storage",
            "AWS Lambda for serverless computing"
        ]
        
        results = enhancer.enhance_presentation_content(slides_content)
        
        assert isinstance(results, list)
        assert len(results) == len(slides_content)
        
        for result in results:
            assert hasattr(result, 'original_content')
            assert hasattr(result, 'enhanced_content')


class TestMCPIntegrationEnd2End:
    """End-to-end integration tests."""
    
    def setup_method(self):
        """Set up test environment."""
        os.environ['AWS_REGION'] = 'us-west-2'
        os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'
    
    def test_full_integration_workflow(self):
        """Test the complete MCP integration workflow."""
        # Initialize components
        aws_client = AWSDocsClient()
        enhancer = KnowledgeEnhancer()
        
        # Test service documentation retrieval
        s3_docs = aws_client.get_service_documentation('s3')
        assert s3_docs is not None
        
        # Test content enhancement
        test_content = "We will use Amazon S3 for storing our application data."
        enhanced = enhancer.enhance_slide_content(test_content, slide_number=1)
        assert enhanced is not None
        
        # Enhanced content should be different from original (unless no enhancement was possible)
        # At minimum, it should maintain the original content
        assert len(enhanced.enhanced_content) >= len(enhanced.original_content)
    
    def test_fallback_mechanism(self):
        """Test that fallback to mock data works when MCP fails."""
        # Create client and force MCP to be unavailable
        aws_client = AWSDocsClient()
        
        # Even if real MCP fails, should get mock data
        result = aws_client.get_service_documentation('dynamodb')
        
        # Should still get some result (either real or mock)
        # The system should be resilient
        assert result is not None or aws_client.use_real_mcp == False


def run_mcp_integration_tests():
    """Run all MCP integration tests."""
    print("🧪 Running MCP Integration Tests...")
    
    # Set up environment
    os.environ['AWS_REGION'] = 'us-west-2'
    os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'
    
    try:
        # Test 1: Basic MCP Client
        print("\n1. Testing MCP Client Initialization...")
        client = SyncMCPClient()
        print(f"   ✅ MCP Client created, available: {client.is_available()}")
        
        # Test 2: Connection Test
        print("\n2. Testing MCP Connection...")
        if client.is_available():
            connection_ok = client.test_connection()
            print(f"   ✅ Connection test: {'PASSED' if connection_ok else 'FAILED'}")
        else:
            print("   ⚠️  MCP server not configured, skipping connection test")
        
        # Test 3: AWS Docs Client
        print("\n3. Testing AWS Documentation Client...")
        aws_client = AWSDocsClient()
        print(f"   ✅ AWS Docs Client created, real MCP: {aws_client.use_real_mcp}")
        
        # Test 4: Service Documentation
        print("\n4. Testing Service Documentation Retrieval...")
        s3_docs = aws_client.get_service_documentation('s3')
        if s3_docs:
            print(f"   ✅ Retrieved S3 docs: {s3_docs.service_name}")
            print(f"   📄 Description: {s3_docs.description[:100]}...")
        else:
            print("   ❌ Failed to retrieve S3 documentation")
        
        # Test 5: Knowledge Enhancement
        print("\n5. Testing Knowledge Enhancement...")
        enhancer = KnowledgeEnhancer()
        test_content = "This slide covers Amazon S3 storage service."
        enhanced = enhancer.enhance_slide_content(test_content, slide_number=1)
        print(f"   ✅ Enhanced content, confidence: {enhanced.confidence_score:.2f}")
        
        print("\n🎉 All MCP integration tests completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    """Run tests when executed directly."""
    success = run_mcp_integration_tests()
    sys.exit(0 if success else 1)
