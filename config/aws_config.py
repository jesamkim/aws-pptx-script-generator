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
        default="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
        description="Claude Sonnet 4.5 inference profile ID",
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
            # Ensure region is properly set
            region = self.config.region or "us-west-2"
            
            session = boto3.Session(
                profile_name=self.config.profile_name,
                region_name=region,
            )
            
            client = session.client(
                "bedrock-runtime",
                region_name=region,  # Explicitly set region
                config=Config(
                    retries={"max_attempts": self.config.max_retries},
                    connect_timeout=self.config.timeout,
                ),
            )
            logger.info(f"Initialized Bedrock client in {region}")
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
            import json
            
            # Construct messages for Claude 3.7 Sonnet
            messages = [{"role": "user", "content": prompt}]
            
            # Add image if provided
            if image_data:
                # For multimodal input, we need to format the content differently
                content = [
                    {"type": "text", "text": prompt},
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_data.decode("utf-8")}}
                ]
                messages = [{"role": "user", "content": content}]
            
            # Construct request body for Claude Sonnet 4.5
            request_body = {
                "messages": messages,
                "max_tokens": 4096,
                "temperature": 0.7,
                "anthropic_version": "bedrock-2023-05-31"
            }

            response = self.client.invoke_model(
                modelId=self.config.bedrock_model_id,
                body=json.dumps(request_body),
                contentType="application/json",
                accept="application/json"
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            logger.debug(f"Successfully invoked Bedrock model: {self.config.bedrock_model_id}")
            return response_body

        except Exception as e:
            logger.error(f"Failed to invoke Bedrock model: {str(e)}")
            raise


# Global AWS configuration instance
aws_config = AWSConfig()

# Global Bedrock client instance
bedrock_client = BedrockClient(aws_config)
