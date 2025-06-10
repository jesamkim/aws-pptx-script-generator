"""AWS Configuration Module.

This module manages AWS service configurations, including Bedrock and MCP integration settings.
"""

from typing import Dict, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
import boto3
from botocore.config import Config
from loguru import logger


class AWSConfig(BaseSettings):
    """AWS Configuration Settings.

    Attributes:
        region: AWS region for service endpoints
        bedrock_model_id: Claude 3.7 Sonnet model identifier
        profile_name: AWS credential profile name
        max_retries: Maximum number of API retry attempts
        timeout: API request timeout in seconds
    """

    region: str = Field(default="us-west-2", description="AWS region for services")
    bedrock_model_id: str = Field(
        default="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        description="Claude 3.7 Sonnet model ID",
    )
    profile_name: Optional[str] = Field(default=None, description="AWS profile name")
    max_retries: int = Field(default=3, description="Maximum API retries")
    timeout: int = Field(default=30, description="API timeout in seconds")

    class Config:
        env_prefix = "AWS_"


class BedrockClient:
    """Amazon Bedrock Client Manager.

    Manages Bedrock client initialization and API interactions.

    Attributes:
        config: AWSConfig instance with service settings
        client: boto3 Bedrock client
    """

    def __init__(self, config: AWSConfig):
        """Initialize Bedrock client with configuration.

        Args:
            config: AWSConfig instance with service settings
        """
        self.config = config
        self.client = self._initialize_client()

    def _initialize_client(self) -> "boto3.client":
        """Initialize boto3 Bedrock client with retry configuration.

        Returns:
            Configured boto3 Bedrock client

        Raises:
            Exception: If client initialization fails
        """
        try:
            session = boto3.Session(
                profile_name=self.config.profile_name,
                region_name=self.config.region,
            )
            client = session.client(
                "bedrock-runtime",
                config=Config(
                    retries={"max_attempts": self.config.max_retries},
                    connect_timeout=self.config.timeout,
                ),
            )
            logger.info(f"Initialized Bedrock client in {self.config.region}")
            return client
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {str(e)}")
            raise

    def invoke_model(self, prompt: str, image_data: Optional[bytes] = None) -> Dict:
        """Invoke Claude 3.7 Sonnet model with text and optional image.

        Args:
            prompt: Text prompt for the model
            image_data: Optional bytes of image data for multimodal analysis

        Returns:
            Model response as dictionary

        Raises:
            Exception: If model invocation fails
        """
        try:
            # Construct request body based on presence of image
            request_body = {
                "modelId": self.config.bedrock_model_id,
                "contentType": "application/json",
                "accept": "application/json",
                "body": {
                    "prompt": prompt,
                    "max_tokens": 4096,
                    "temperature": 0.7,
                    "top_p": 0.9,
                },
            }

            if image_data:
                request_body["body"]["image"] = image_data.decode("utf-8")

            response = self.client.invoke_model(**request_body)
            logger.debug(f"Successfully invoked Bedrock model: {self.config.bedrock_model_id}")
            return response

        except Exception as e:
            logger.error(f"Failed to invoke Bedrock model: {str(e)}")
            raise


# Global AWS configuration instance
aws_config = AWSConfig()

# Global Bedrock client instance
bedrock_client = BedrockClient(aws_config)
