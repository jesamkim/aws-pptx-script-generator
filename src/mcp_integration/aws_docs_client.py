"""AWS Documentation MCP Client.

This module integrates with AWS Documentation MCP server to retrieve
authoritative AWS service information and best practices.
"""

import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from loguru import logger

from config.mcp_config import mcp_client
from src.utils.logger import log_execution_time, performance_monitor
from .real_mcp_client import SyncMCPClient


@dataclass
class ServiceDocumentation:
    """AWS service documentation data.
    
    Attributes:
        service_name: Official AWS service name
        description: Service description
        use_cases: Common use cases
        features: Key features and capabilities
        pricing_model: Pricing information
        best_practices: List of best practices
        code_examples: Code examples and snippets
        related_services: Related AWS services
        documentation_url: Official documentation URL
    """
    service_name: str
    description: str
    use_cases: List[str]
    features: List[str]
    pricing_model: str
    best_practices: List[str]
    code_examples: List[Dict[str, str]]
    related_services: List[str]
    documentation_url: str


@dataclass
class ValidationResult:
    """Content validation result.
    
    Attributes:
        is_valid: Whether content is technically accurate
        confidence: Confidence score (0-1)
        issues: List of identified issues
        corrections: Suggested corrections
        updated_content: Content with corrections applied
    """
    is_valid: bool
    confidence: float
    issues: List[str]
    corrections: List[str]
    updated_content: str


class AWSDocsClient:
    """Client for AWS Documentation MCP server integration.
    
    This class provides comprehensive integration with AWS Documentation
    MCP server for retrieving authoritative service information.
    """
    
    def __init__(self):
        """Initialize AWS Documentation MCP client."""
        self.session = requests.Session()
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache
        self._setup_session()
        
        # Initialize real MCP client
        self.real_mcp_client = SyncMCPClient()
        self.use_real_mcp = self.real_mcp_client.is_available()
        
        if self.use_real_mcp:
            logger.info("Initialized AWS Documentation MCP client with real MCP server")
        else:
            logger.warning("Real MCP server not available, using mock data fallback")
            logger.info("Initialized AWS Documentation MCP client")
    
    def _setup_session(self):
        """Set up HTTP session with retry strategy."""
        try:
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
            )
            
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)
            
            # Set default headers
            self.session.headers.update({
                'Content-Type': 'application/json',
                'User-Agent': 'AWS-SA-Script-Generator/1.0'
            })
            
            logger.debug("Set up HTTP session with retry strategy")
            
        except Exception as e:
            logger.error(f"Failed to setup HTTP session: {str(e)}")
            raise
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid.
        
        Args:
            cache_key: Cache key to check
            
        Returns:
            True if cache is valid, False otherwise
        """
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key].get('timestamp', 0)
        return (time.time() - cached_time) < self.cache_ttl
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get data from cache if valid.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached data or None if not valid
        """
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        return None
    
    def _set_cache(self, cache_key: str, data: Any):
        """Set data in cache with timestamp.
        
        Args:
            cache_key: Cache key
            data: Data to cache
        """
        self.cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    @log_execution_time
    def get_service_documentation(self, service_name: str) -> Optional[ServiceDocumentation]:
        """Retrieve comprehensive AWS service documentation.
        
        Args:
            service_name: AWS service name (e.g., 'ec2', 's3', 'lambda')
            
        Returns:
            ServiceDocumentation object or None if not found
        """
        cache_key = f"service_docs_{service_name.lower()}"
        
        # Check cache first
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            logger.debug(f"Retrieved {service_name} documentation from cache")
            return cached_data
        
        performance_monitor.start_operation(f"get_service_docs_{service_name}")
        
        try:
            # Try real MCP client first if available
            if self.use_real_mcp:
                try:
                    real_docs = self.real_mcp_client.get_service_documentation(service_name)
                    if real_docs:
                        # Convert real MCP response to ServiceDocumentation format
                        service_doc = self._convert_real_mcp_to_service_doc(real_docs, service_name)
                        if service_doc:
                            self._set_cache(cache_key, service_doc)
                            performance_monitor.end_operation(f"get_service_docs_{service_name}", True)
                            logger.info(f"Retrieved documentation for {service_name} from real MCP server")
                            return service_doc
                except Exception as e:
                    logger.warning(f"Real MCP client failed for {service_name}: {str(e)}")
                    # Continue to fallback
            
            # Fallback to mock data
            logger.info(f"Using mock data fallback for {service_name}")
            mock_documentation = self._get_mock_service_documentation(service_name)
            
            if mock_documentation:
                self._set_cache(cache_key, mock_documentation)
                performance_monitor.end_operation(f"get_service_docs_{service_name}", True)
                logger.info(f"Retrieved documentation for {service_name}")
                return mock_documentation
            else:
                performance_monitor.end_operation(f"get_service_docs_{service_name}", False)
                logger.warning(f"No documentation found for {service_name}")
                return None
                
        except Exception as e:
            performance_monitor.end_operation(f"get_service_docs_{service_name}", False)
            logger.error(f"Failed to retrieve documentation for {service_name}: {str(e)}")
            return None
    
    def _get_mock_service_documentation(self, service_name: str) -> Optional[ServiceDocumentation]:
        """Get mock service documentation for demonstration.
        
        Args:
            service_name: AWS service name
            
        Returns:
            Mock ServiceDocumentation object
        """
        # Mock data for common AWS services
        mock_services = {
            's3': ServiceDocumentation(
                service_name="Amazon S3",
                description="Object storage service with industry-leading scalability, data availability, security, and performance",
                use_cases=[
                    "Data backup and archiving",
                    "Static website hosting",
                    "Data lakes and analytics",
                    "Content distribution"
                ],
                features=[
                    "99.999999999% (11 9's) durability",
                    "Multiple storage classes",
                    "Lifecycle management",
                    "Cross-region replication",
                    "Server-side encryption"
                ],
                pricing_model="Pay-as-you-go for storage used, requests, and data transfer",
                best_practices=[
                    "Use appropriate storage classes for cost optimization",
                    "Enable versioning for critical data",
                    "Implement lifecycle policies",
                    "Use S3 Transfer Acceleration for global uploads",
                    "Enable access logging for security monitoring"
                ],
                code_examples=[
                    {
                        "language": "python",
                        "description": "Upload file to S3",
                        "code": "import boto3\ns3 = boto3.client('s3')\ns3.upload_file('local_file.txt', 'bucket-name', 'key')"
                    }
                ],
                related_services=["CloudFront", "Lambda", "Athena", "Glue"],
                documentation_url="https://docs.aws.amazon.com/s3/"
            ),
            'lambda': ServiceDocumentation(
                service_name="AWS Lambda",
                description="Serverless compute service that runs code without provisioning or managing servers",
                use_cases=[
                    "Event-driven processing",
                    "Real-time file processing",
                    "API backends",
                    "Data transformation"
                ],
                features=[
                    "Automatic scaling",
                    "Built-in fault tolerance",
                    "Pay per request",
                    "Multiple runtime support",
                    "Integration with AWS services"
                ],
                pricing_model="Pay per request and compute time, with generous free tier",
                best_practices=[
                    "Keep functions small and focused",
                    "Use environment variables for configuration",
                    "Implement proper error handling",
                    "Monitor with CloudWatch",
                    "Use layers for shared dependencies"
                ],
                code_examples=[
                    {
                        "language": "python",
                        "description": "Basic Lambda function",
                        "code": "def lambda_handler(event, context):\n    return {'statusCode': 200, 'body': 'Hello World'}"
                    }
                ],
                related_services=["API Gateway", "S3", "DynamoDB", "EventBridge"],
                documentation_url="https://docs.aws.amazon.com/lambda/"
            ),
            'ec2': ServiceDocumentation(
                service_name="Amazon EC2",
                description="Secure and resizable compute capacity in the cloud",
                use_cases=[
                    "Web applications",
                    "High-performance computing",
                    "Machine learning",
                    "Development environments"
                ],
                features=[
                    "Multiple instance types",
                    "Auto Scaling",
                    "Elastic Load Balancing",
                    "Security groups",
                    "Spot instances for cost savings"
                ],
                pricing_model="Pay for compute capacity by hour or second, multiple pricing models available",
                best_practices=[
                    "Right-size instances for workload",
                    "Use Auto Scaling for variable workloads",
                    "Implement security groups properly",
                    "Regular security updates",
                    "Use IAM roles instead of access keys"
                ],
                code_examples=[
                    {
                        "language": "aws-cli",
                        "description": "Launch EC2 instance",
                        "code": "aws ec2 run-instances --image-id ami-12345678 --count 1 --instance-type t2.micro"
                    }
                ],
                related_services=["VPC", "EBS", "ELB", "Auto Scaling"],
                documentation_url="https://docs.aws.amazon.com/ec2/"
            )
        }
        
        service_key = service_name.lower().replace(' ', '').replace('-', '')
    def _convert_real_mcp_to_service_doc(self, real_docs: Dict[str, Any], service_name: str) -> Optional[ServiceDocumentation]:
        """Convert real MCP response to ServiceDocumentation format.
        
        Args:
            real_docs: Response from real MCP client
            service_name: AWS service name
            
        Returns:
            ServiceDocumentation object or None if conversion fails
        """
        try:
            # Extract information from real MCP response
            service_display_name = real_docs.get('service_name', f"AWS {service_name.upper()}")
            description = real_docs.get('description', '')
            detailed_content = real_docs.get('detailed_content', '')
            documentation_url = real_docs.get('documentation_url', '')
            
            # Parse detailed content for additional information
            use_cases = self._extract_use_cases_from_content(detailed_content)
            features = self._extract_features_from_content(detailed_content)
            
            # Get best practices from real MCP client
            best_practices = []
            try:
                best_practices = self.real_mcp_client.get_best_practices(service_name)
            except Exception as e:
                logger.warning(f"Failed to get best practices from real MCP: {str(e)}")
            
            # Create ServiceDocumentation object
            return ServiceDocumentation(
                service_name=service_display_name,
                description=description or detailed_content[:200] + "..." if detailed_content else f"AWS {service_name} service",
                use_cases=use_cases,
                features=features,
                pricing_model="Pay-as-you-go pricing model",  # Generic pricing info
                best_practices=best_practices,
                code_examples=[],  # Could be enhanced to extract from content
                related_services=[],  # Could be enhanced to extract from content
                documentation_url=documentation_url
            )
            
        except Exception as e:
            logger.error(f"Failed to convert real MCP response: {str(e)}")
            return None
    
    def _extract_use_cases_from_content(self, content: str) -> List[str]:
        """Extract use cases from documentation content.
        
        Args:
            content: Documentation content
            
        Returns:
            List of use cases
        """
        use_cases = []
        if not content:
            return use_cases
        
        # Look for common use case patterns
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in [
                'use case', 'used for', 'ideal for', 'perfect for', 'suitable for'
            ]):
                if len(line) > 10 and len(line) < 150:
                    use_cases.append(line)
        
        return use_cases[:5]  # Limit to top 5
    
    def _extract_features_from_content(self, content: str) -> List[str]:
        """Extract features from documentation content.
        
        Args:
            content: Documentation content
            
        Returns:
            List of features
        """
        features = []
        if not content:
            return features
        
        # Look for common feature patterns
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in [
                'feature', 'capability', 'provides', 'supports', 'includes'
            ]):
                if len(line) > 10 and len(line) < 150:
                    features.append(line)
        
        return features[:5]  # Limit to top 5
    
    @log_execution_time
    def get_best_practices(self, service_name: str, use_case: Optional[str] = None) -> List[str]:
        """Retrieve best practices for AWS service.
        
        Args:
            service_name: AWS service name
            use_case: Specific use case (optional)
            
        Returns:
            List of best practice recommendations
        """
        cache_key = f"best_practices_{service_name.lower()}_{use_case or 'general'}"
        
        # Check cache first
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            logger.debug(f"Retrieved {service_name} best practices from cache")
            return cached_data
        
        try:
            # Try real MCP client first if available
            if self.use_real_mcp:
                try:
                    real_practices = self.real_mcp_client.get_best_practices(service_name)
                    if real_practices:
                        # Add use-case specific practices if available
                        if use_case:
                            specific_practices = self._get_use_case_practices(service_name, use_case)
                            real_practices.extend(specific_practices)
                        
                        self._set_cache(cache_key, real_practices)
                        logger.info(f"Retrieved {len(real_practices)} best practices for {service_name} from real MCP")
                        return real_practices
                except Exception as e:
                    logger.warning(f"Real MCP client failed for best practices {service_name}: {str(e)}")
                    # Continue to fallback
            
            # Fallback to service documentation approach
            service_docs = self.get_service_documentation(service_name)
            
            if service_docs:
                best_practices = service_docs.best_practices
                
                # Add use-case specific practices if available
                if use_case:
                    specific_practices = self._get_use_case_practices(service_name, use_case)
                    best_practices.extend(specific_practices)
                
                self._set_cache(cache_key, best_practices)
                logger.info(f"Retrieved {len(best_practices)} best practices for {service_name}")
                return best_practices
            else:
                logger.warning(f"No best practices found for {service_name}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to retrieve best practices for {service_name}: {str(e)}")
            return []
    
    def _get_use_case_practices(self, service_name: str, use_case: str) -> List[str]:
        """Get use-case specific best practices.
        
        Args:
            service_name: AWS service name
            use_case: Specific use case
            
        Returns:
            List of use-case specific practices
        """
        # Mock use-case specific practices
        use_case_practices = {
            's3': {
                'backup': [
                    "Enable cross-region replication for critical backups",
                    "Use Glacier for long-term archival",
                    "Implement backup verification processes"
                ],
                'website': [
                    "Enable static website hosting",
                    "Use CloudFront for global distribution",
                    "Configure custom error pages"
                ]
            },
            'lambda': {
                'api': [
                    "Use API Gateway for REST APIs",
                    "Implement proper authentication",
                    "Use Lambda Authorizers for custom auth"
                ],
                'processing': [
                    "Use SQS for reliable message processing",
                    "Implement dead letter queues",
                    "Monitor function duration and memory usage"
                ]
            }
        }
        
        service_key = service_name.lower()
        use_case_key = use_case.lower()
        
        return use_case_practices.get(service_key, {}).get(use_case_key, [])
    
    @log_execution_time
    def validate_technical_content(self, content: str, service_name: str) -> ValidationResult:
        """Validate technical content against AWS documentation.
        
        Args:
            content: Technical content to validate
            service_name: Related AWS service name
            
        Returns:
            ValidationResult with accuracy assessment
        """
        performance_monitor.start_operation(f"validate_content_{service_name}")
        
        try:
            # Get service documentation for validation
            service_docs = self.get_service_documentation(service_name)
            
            if not service_docs:
                performance_monitor.end_operation(f"validate_content_{service_name}", False)
                return ValidationResult(
                    is_valid=False,
                    confidence=0.0,
                    issues=[f"No documentation available for {service_name}"],
                    corrections=[],
                    updated_content=content
                )
            
            # Perform validation checks
            issues = []
            corrections = []
            confidence = 1.0
            
            # Check for outdated terminology
            outdated_terms = {
                'simple storage service': 'Amazon S3',
                'elastic compute cloud': 'Amazon EC2',
                'relational database service': 'Amazon RDS'
            }
            
            content_lower = content.lower()
            for old_term, new_term in outdated_terms.items():
                if old_term in content_lower and new_term.lower() not in content_lower:
                    issues.append(f"Consider using '{new_term}' instead of '{old_term}'")
                    corrections.append(f"Replace '{old_term}' with '{new_term}'")
                    confidence -= 0.1
            
            # Check for missing best practices mentions
            important_concepts = {
                's3': ['encryption', 'versioning', 'lifecycle'],
                'lambda': ['error handling', 'monitoring', 'timeout'],
                'ec2': ['security groups', 'auto scaling', 'monitoring']
            }
            
            service_key = service_name.lower()
            if service_key in important_concepts:
                for concept in important_concepts[service_key]:
                    if concept not in content_lower:
                        issues.append(f"Consider mentioning {concept} for {service_name}")
                        confidence -= 0.05
            
            # Apply corrections to content
            updated_content = content
            for old_term, new_term in outdated_terms.items():
                updated_content = updated_content.replace(old_term, new_term)
            
            # Determine if content is valid
            is_valid = confidence >= 0.7 and len(issues) <= 3
            
            validation_result = ValidationResult(
                is_valid=is_valid,
                confidence=max(0.0, confidence),
                issues=issues,
                corrections=corrections,
                updated_content=updated_content
            )
            
            performance_monitor.end_operation(f"validate_content_{service_name}", True)
            logger.info(f"Validated content for {service_name}: valid={is_valid}, confidence={confidence:.2f}")
            return validation_result
            
        except Exception as e:
            performance_monitor.end_operation(f"validate_content_{service_name}", False)
            logger.error(f"Failed to validate content for {service_name}: {str(e)}")
            return ValidationResult(
                is_valid=False,
                confidence=0.0,
                issues=[f"Validation failed: {str(e)}"],
                corrections=[],
                updated_content=content
            )
    
    @log_execution_time
    def get_code_examples(self, service_name: str, language: str = "python") -> List[Dict[str, str]]:
        """Retrieve code examples for AWS service.
        
        Args:
            service_name: AWS service name
            language: Programming language preference
            
        Returns:
            List of code examples
        """
        cache_key = f"code_examples_{service_name.lower()}_{language}"
        
        # Check cache first
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            logger.debug(f"Retrieved {service_name} code examples from cache")
            return cached_data
        
        try:
            # Get service documentation
            service_docs = self.get_service_documentation(service_name)
            
            if service_docs:
                # Filter examples by language
                examples = [
                    example for example in service_docs.code_examples
                    if example.get('language', '').lower() == language.lower()
                ]
                
                # If no examples for specific language, return all
                if not examples:
                    examples = service_docs.code_examples
                
                self._set_cache(cache_key, examples)
                logger.info(f"Retrieved {len(examples)} code examples for {service_name}")
                return examples
            else:
                logger.warning(f"No code examples found for {service_name}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to retrieve code examples for {service_name}: {str(e)}")
            return []
    
    def clear_cache(self):
        """Clear all cached data."""
        self.cache.clear()
        logger.info("Cleared AWS documentation cache")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_entries = len(self.cache)
        valid_entries = sum(1 for key in self.cache.keys() if self._is_cache_valid(key))
        
        return {
            'total_entries': total_entries,
            'valid_entries': valid_entries,
            'cache_hit_ratio': valid_entries / max(1, total_entries),
            'cache_size_mb': sum(len(str(data)) for data in self.cache.values()) / (1024 * 1024)
        }
