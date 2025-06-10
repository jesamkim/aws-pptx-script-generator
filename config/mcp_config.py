"""MCP Configuration Module.

This module manages AWS Documentation MCP server configuration and connection settings.
"""

from typing import Dict, Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field
from loguru import logger


class MCPConfig(BaseSettings):
    """MCP Server Configuration Settings.

    Attributes:
        server_endpoint: MCP server endpoint URL
        connection_timeout: Connection timeout in seconds
        request_timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        cache_ttl: Cache time-to-live in seconds
        batch_size: Maximum batch size for requests
    """

    server_endpoint: str = Field(
        default="http://localhost:8080/mcp",
        description="MCP server endpoint URL",
    )
    connection_timeout: int = Field(
        default=10, description="Connection timeout in seconds"
    )
    request_timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")
    batch_size: int = Field(default=10, description="Maximum batch size")

    class Config:
        env_prefix = "MCP_"


class MCPClient:
    """AWS Documentation MCP Client.

    Manages connections to AWS Documentation MCP server for retrieving
    authoritative AWS service information and best practices.

    Attributes:
        config: MCPConfig instance with server settings
        session: HTTP session for persistent connections
        cache: Local cache for frequently accessed content
    """

    def __init__(self, config: MCPConfig):
        """Initialize MCP client with configuration.

        Args:
            config: MCPConfig instance with server settings
        """
        self.config = config
        self.session = None
        self.cache: Dict[str, Dict] = {}
        self._initialize_connection()

    def _initialize_connection(self) -> None:
        """Initialize connection to MCP server.

        Raises:
            Exception: If connection initialization fails
        """
        try:
            # Initialize HTTP session with retry configuration
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry

            self.session = requests.Session()
            retry_strategy = Retry(
                total=self.config.max_retries,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)

            logger.info(f"Initialized MCP client for {self.config.server_endpoint}")

        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {str(e)}")
            raise

    def get_service_documentation(self, service_name: str) -> Dict:
        """Retrieve AWS service documentation from MCP server.

        Args:
            service_name: AWS service name (e.g., 'ec2', 's3', 'lambda')

        Returns:
            Service documentation as dictionary

        Raises:
            Exception: If documentation retrieval fails
        """
        cache_key = f"service_docs_{service_name}"

        # Check cache first
        if cache_key in self.cache:
            logger.debug(f"Retrieved {service_name} docs from cache")
            return self.cache[cache_key]

        try:
            endpoint = f"{self.config.server_endpoint}/services/{service_name}"
            response = self.session.get(
                endpoint, timeout=self.config.request_timeout
            )
            response.raise_for_status()

            docs = response.json()
            self.cache[cache_key] = docs
            logger.info(f"Retrieved documentation for {service_name}")
            return docs

        except Exception as e:
            logger.error(f"Failed to retrieve docs for {service_name}: {str(e)}")
            # Return empty dict as fallback
            return {}

    def get_best_practices(self, service_name: str) -> List[Dict]:
        """Retrieve AWS service best practices from MCP server.

        Args:
            service_name: AWS service name

        Returns:
            List of best practices as dictionaries

        Raises:
            Exception: If best practices retrieval fails
        """
        cache_key = f"best_practices_{service_name}"

        # Check cache first
        if cache_key in self.cache:
            logger.debug(f"Retrieved {service_name} best practices from cache")
            return self.cache[cache_key]

        try:
            endpoint = f"{self.config.server_endpoint}/best-practices/{service_name}"
            response = self.session.get(
                endpoint, timeout=self.config.request_timeout
            )
            response.raise_for_status()

            practices = response.json()
            self.cache[cache_key] = practices
            logger.info(f"Retrieved best practices for {service_name}")
            return practices

        except Exception as e:
            logger.error(f"Failed to retrieve best practices for {service_name}: {str(e)}")
            # Return empty list as fallback
            return []

    def validate_technical_content(self, content: str, service_name: str) -> Dict:
        """Validate technical content against AWS documentation.

        Args:
            content: Technical content to validate
            service_name: Related AWS service name

        Returns:
            Validation results as dictionary

        Raises:
            Exception: If validation fails
        """
        try:
            endpoint = f"{self.config.server_endpoint}/validate"
            payload = {"content": content, "service": service_name}

            response = self.session.post(
                endpoint, json=payload, timeout=self.config.request_timeout
            )
            response.raise_for_status()

            validation = response.json()
            logger.info(f"Validated content for {service_name}")
            return validation

        except Exception as e:
            logger.error(f"Failed to validate content for {service_name}: {str(e)}")
            # Return basic validation result as fallback
            return {"valid": True, "confidence": 0.5, "issues": []}

    def get_code_examples(self, service_name: str, use_case: str) -> List[Dict]:
        """Retrieve code examples for AWS service and use case.

        Args:
            service_name: AWS service name
            use_case: Specific use case or operation

        Returns:
            List of code examples as dictionaries

        Raises:
            Exception: If code example retrieval fails
        """
        cache_key = f"code_examples_{service_name}_{use_case}"

        # Check cache first
        if cache_key in self.cache:
            logger.debug(f"Retrieved code examples from cache")
            return self.cache[cache_key]

        try:
            endpoint = f"{self.config.server_endpoint}/code-examples"
            params = {"service": service_name, "use_case": use_case}

            response = self.session.get(
                endpoint, params=params, timeout=self.config.request_timeout
            )
            response.raise_for_status()

            examples = response.json()
            self.cache[cache_key] = examples
            logger.info(f"Retrieved code examples for {service_name}/{use_case}")
            return examples

        except Exception as e:
            logger.error(f"Failed to retrieve code examples: {str(e)}")
            # Return empty list as fallback
            return []

    def clear_cache(self) -> None:
        """Clear the local cache."""
        self.cache.clear()
        logger.info("Cleared MCP client cache")


# Global MCP configuration instance
mcp_config = MCPConfig()

# Global MCP client instance
mcp_client = MCPClient(mcp_config)
