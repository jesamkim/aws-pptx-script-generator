#!/usr/bin/env python3
"""Simple test script to verify Bedrock connection."""

import os
import sys
import boto3
import json
from botocore.config import Config

# Set environment variables
os.environ['AWS_REGION'] = 'us-west-2'
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'

def test_bedrock_connection():
    """Test Bedrock connection with correct inference profile ID."""
    try:
        # Initialize Bedrock client
        client = boto3.client(
            'bedrock-runtime',
            region_name='us-west-2',
            config=Config(
                retries={'max_attempts': 3},
                connect_timeout=30,
            )
        )
        
        print("✅ Bedrock client initialized successfully")
        
        # Test model invocation with inference profile ID
        model_id = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
        
        # Simple test prompt
        prompt = "Hello, please respond with 'Connection successful!'"
        
        # Prepare request body for Claude 3.7 Sonnet
        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 100,
            "temperature": 0.1,
            "anthropic_version": "bedrock-2023-05-31"
        }
        
        # Invoke model
        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body),
            contentType='application/json',
            accept='application/json'
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        
        print("✅ Model invocation successful")
        print(f"✅ Model ID: {model_id}")
        print(f"✅ Response: {response_body.get('content', [{}])[0].get('text', 'No response text')}")
        print("✅ Bedrock connection test passed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Bedrock connection test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_bedrock_connection()
    sys.exit(0 if success else 1)
