"""MCP Integration Package.

This package provides integration with AWS Documentation MCP server for
retrieving authoritative AWS service information and enhancing content.
"""

from .aws_docs_client import (
    AWSDocsClient,
    ServiceDocumentation,
    ValidationResult
)
from .knowledge_enhancer import (
    KnowledgeEnhancer,
    EnhancedContent,
    ServiceContext
)

__all__ = [
    "AWSDocsClient",
    "ServiceDocumentation",
    "ValidationResult",
    "KnowledgeEnhancer",
    "EnhancedContent",
    "ServiceContext",
]
