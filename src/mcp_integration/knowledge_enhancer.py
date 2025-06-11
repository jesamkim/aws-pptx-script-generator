"""Knowledge Enhancement Module.

This module enhances slide content with authoritative AWS information
retrieved from MCP documentation sources.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import re
from loguru import logger

from .aws_docs_client import AWSDocsClient, ServiceDocumentation
from src.utils.logger import log_execution_time, performance_monitor


@dataclass
class EnhancedContent:
    """Enhanced content with AWS documentation integration.
    
    Attributes:
        original_content: Original slide content
        enhanced_content: Content enhanced with AWS information
        added_information: List of information added
        corrections: List of corrections made
        best_practices: Relevant best practices added
        code_examples: Relevant code examples
        related_services: Related AWS services mentioned
        confidence_score: Enhancement confidence (0-1)
    """
    original_content: str
    enhanced_content: str
    added_information: List[str]
    corrections: List[str]
    best_practices: List[str]
    code_examples: List[Dict[str, str]]
    related_services: List[str]
    confidence_score: float


@dataclass
class ServiceContext:
    """Context information for AWS service usage.
    
    Attributes:
        service_name: AWS service name
        usage_context: How service is used in presentation
        importance_score: Importance in presentation (0-1)
        related_concepts: Related technical concepts
    """
    service_name: str
    usage_context: str
    importance_score: float
    related_concepts: List[str]


class KnowledgeEnhancer:
    """Enhances presentation content with authoritative AWS information."""
    
    def __init__(self):
        """Initialize knowledge enhancer."""
        self.aws_docs_client = AWSDocsClient()
        
        # Service name normalization mapping
        self.service_aliases = {
            'simple storage service': 's3',
            'elastic compute cloud': 'ec2',
            'relational database service': 'rds',
            'elastic load balancer': 'elb',
            'elastic load balancing': 'elb',
            'virtual private cloud': 'vpc',
            'identity and access management': 'iam',
            'key management service': 'kms',
            'simple notification service': 'sns',
            'simple queue service': 'sqs',
            'cloudformation': 'cloudformation',
            'elastic container service': 'ecs',
            'elastic kubernetes service': 'eks'
        }
        
        # Enhancement templates
        self.enhancement_templates = {
            'service_intro': "**{service_name}** is {description}",
            'use_case': "Common use cases include: {use_cases}",
            'best_practice': "💡 **Best Practice**: {practice}",
            'related_service': "🔗 **Related Service**: {service} - {description}",
            'code_example': "```{language}\n{code}\n```\n*{description}*"
        }
        
        logger.info("Initialized knowledge enhancer with AWS documentation integration")
    
    def enhance_service_knowledge(self, service_name: str) -> Dict[str, Any]:
        """Enhance knowledge about a specific AWS service.
        
        Args:
            service_name: Name of AWS service
            
        Returns:
            Enhanced service information
        """
        try:
            # Normalize service name
            normalized_name = self._normalize_service_name(service_name)
            
            # Get service documentation from MCP
            service_docs = self.aws_docs_client.get_service_documentation(normalized_name)
            
            if not service_docs:
                logger.warning(f"No documentation found for service: {service_name}")
                return {
                    "service_name": service_name,
                    "description": "AWS service (documentation not available)",
                    "use_cases": [],
                    "best_practices": [],
                    "related_services": []
                }
            
            # Extract key information from ServiceDocumentation object
            enhanced_info = {
                "service_name": service_name,
                "description": service_docs.description or "",
                "use_cases": service_docs.use_cases or [],
                "best_practices": service_docs.best_practices or [],
                "related_services": service_docs.related_services or [],
                "documentation_url": service_docs.documentation_url or ""
            }
            
            # Format using templates
            if enhanced_info["description"]:
                enhanced_info["formatted_intro"] = self.enhancement_templates["service_intro"].format(
                    service_name=service_name,
                    description=enhanced_info["description"]
                )
            
            if enhanced_info["use_cases"]:
                enhanced_info["formatted_use_cases"] = self.enhancement_templates["use_case"].format(
                    use_cases=", ".join(enhanced_info["use_cases"][:3])
                )
            
            if enhanced_info["best_practices"]:
                enhanced_info["formatted_practices"] = [
                    self.enhancement_templates["best_practice"].format(practice=practice)
                    for practice in enhanced_info["best_practices"][:3]
                ]
            
            return enhanced_info
            
        except Exception as e:
            logger.error(f"Failed to enhance knowledge for {service_name}: {str(e)}")
            return {
                "service_name": service_name,
                "error": str(e)
            }
    
    def _normalize_service_name(self, service_mention: str) -> str:
        """Normalize service name to standard format.
        
        Args:
            service_mention: Service name as mentioned in content
            
        Returns:
            Normalized service name
        """
        service_lower = service_mention.lower().strip()
        
        # Check direct match in aliases
        if service_lower in self.service_aliases:
            return self.service_aliases[service_lower]
        
        # Check partial matches
        for alias, normalized in self.service_aliases.items():
            if service_lower in alias or alias in service_lower:
                return normalized
        
        # Return original if no match found
        return service_mention.strip()
    
    def enhance_content(self, content: str, aws_services: List[str]) -> EnhancedContent:
        """Enhance content with AWS documentation.
        
        Args:
            content: Original content
            aws_services: List of AWS services mentioned
            
        Returns:
            Enhanced content with AWS documentation
        """
        try:
            enhanced_services = {}
            
            # Enhance knowledge for each service
            for service in aws_services:
                enhanced_info = self.enhance_service_knowledge(service)
                if enhanced_info and not enhanced_info.get("error"):
                    enhanced_services[service] = enhanced_info
            
            # Create enhanced content
            return EnhancedContent(
                original_content=content,
                enhanced_services=enhanced_services,
                enhancement_metadata={
                    "services_enhanced": len(enhanced_services),
                    "enhancement_timestamp": time.time()
                }
            )
            
        except Exception as e:
            logger.error(f"Content enhancement failed: {str(e)}")
            return EnhancedContent(
                original_content=content,
                enhanced_services={},
                enhancement_metadata={
                    "error": str(e),
                    "enhancement_timestamp": time.time()
                }
            )
        
        # Check aliases first
        if service_lower in self.service_aliases:
            return self.service_aliases[service_lower]
        
        # Remove common prefixes
        service_lower = re.sub(r'^(amazon|aws)\s+', '', service_lower)
        
        # Handle common variations
        service_lower = service_lower.replace(' ', '').replace('-', '')
        
        return service_lower
    
    def _extract_service_contexts(self, content: str) -> List[ServiceContext]:
        """Extract AWS services and their usage context from content.
        
        Args:
            content: Slide content to analyze
            
        Returns:
            List of ServiceContext objects
        """
        try:
            service_contexts = []
            
            # AWS service patterns with context
            service_patterns = [
                r'(Amazon|AWS)\s+([A-Z][A-Za-z0-9\s]+?)(?:\s+(?:is|provides|offers|enables))\s+([^.!?]+)',
                r'([A-Z][A-Za-z0-9\s]+?)\s+(?:service|platform)\s+([^.!?]+)',
                r'using\s+(Amazon|AWS)\s+([A-Z][A-Za-z0-9\s]+?)\s+(?:for|to)\s+([^.!?]+)'
            ]
            
            for pattern in service_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    if len(match.groups()) >= 3:
                        service_name = match.group(2).strip()
                        context = match.group(3).strip()
                    else:
                        service_name = match.group(1).strip()
                        context = match.group(2).strip() if len(match.groups()) > 1 else ""
                    
                    # Calculate importance based on context length and position
                    importance = min(1.0, len(context) / 100 + 0.3)
                    
                    # Extract related concepts
                    related_concepts = self._extract_related_concepts(context)
                    
                    service_context = ServiceContext(
                        service_name=self._normalize_service_name(service_name),
                        usage_context=context,
                        importance_score=importance,
                        related_concepts=related_concepts
                    )
                    
                    service_contexts.append(service_context)
            
            logger.debug(f"Extracted {len(service_contexts)} service contexts")
            return service_contexts
            
        except Exception as e:
            logger.error(f"Failed to extract service contexts: {str(e)}")
            return []
    
    def _extract_related_concepts(self, context: str) -> List[str]:
        """Extract related technical concepts from context.
        
        Args:
            context: Context text to analyze
            
        Returns:
            List of related concepts
        """
        concept_patterns = [
            r'\b(scalability|availability|durability|consistency|performance)\b',
            r'\b(encryption|security|authentication|authorization)\b',
            r'\b(backup|disaster recovery|replication|failover)\b',
            r'\b(monitoring|logging|alerting|metrics)\b',
            r'\b(cost optimization|pricing|billing)\b'
        ]
        
        concepts = []
        context_lower = context.lower()
        
        for pattern in concept_patterns:
            matches = re.findall(pattern, context_lower)
            concepts.extend(matches)
        
        return list(set(concepts))  # Remove duplicates
    
    @log_execution_time
    def enhance_slide_content(
        self,
        content: str,
        slide_number: int,
        enhancement_level: str = "moderate"
    ) -> EnhancedContent:
        """Enhance slide content with AWS documentation.
        
        Args:
            content: Original slide content
            slide_number: Slide number for context
            enhancement_level: Level of enhancement (minimal, moderate, comprehensive)
            
        Returns:
            EnhancedContent object with enhanced information
        """
        performance_monitor.start_operation(f"enhance_slide_{slide_number}")
        
        try:
            # Extract service contexts
            service_contexts = self._extract_service_contexts(content)
            
            if not service_contexts:
                # No AWS services found, return original content
                performance_monitor.end_operation(f"enhance_slide_{slide_number}", True)
                return EnhancedContent(
                    original_content=content,
                    enhanced_content=content,
                    added_information=[],
                    corrections=[],
                    best_practices=[],
                    code_examples=[],
                    related_services=[],
                    confidence_score=1.0
                )
            
            enhanced_content = content
            added_information = []
            corrections = []
            best_practices = []
            code_examples = []
            related_services = []
            
            # Process each service context
            for service_context in service_contexts:
                service_name = service_context.service_name
                
                # Get service documentation
                service_docs = self.aws_docs_client.get_service_documentation(service_name)
                
                if service_docs:
                    # Add service information based on enhancement level
                    enhancements = self._generate_service_enhancements(
                        service_docs, service_context, enhancement_level
                    )
                    
                    # Apply enhancements
                    enhanced_content += "\n\n" + enhancements['content']
                    added_information.extend(enhancements['information'])
                    best_practices.extend(enhancements['practices'])
                    code_examples.extend(enhancements['examples'])
                    related_services.extend(enhancements['related'])
                    
                    # Validate and correct content
                    validation = self.aws_docs_client.validate_technical_content(
                        enhanced_content, service_name
                    )
                    
                    if validation.corrections:
                        corrections.extend(validation.corrections)
                        enhanced_content = validation.updated_content
            
            # Calculate confidence score
            confidence_score = self._calculate_enhancement_confidence(
                service_contexts, len(added_information), len(corrections)
            )
            
            enhanced_result = EnhancedContent(
                original_content=content,
                enhanced_content=enhanced_content,
                added_information=added_information,
                corrections=corrections,
                best_practices=best_practices,
                code_examples=code_examples,
                related_services=list(set(related_services)),  # Remove duplicates
                confidence_score=confidence_score
            )
            
            performance_monitor.end_operation(f"enhance_slide_{slide_number}", True)
            logger.info(f"Enhanced slide {slide_number}: added {len(added_information)} pieces of information")
            return enhanced_result
            
        except Exception as e:
            performance_monitor.end_operation(f"enhance_slide_{slide_number}", False)
            logger.error(f"Failed to enhance slide {slide_number}: {str(e)}")
            return EnhancedContent(
                original_content=content,
                enhanced_content=content,
                added_information=[],
                corrections=[f"Enhancement failed: {str(e)}"],
                best_practices=[],
                code_examples=[],
                related_services=[],
                confidence_score=0.0
            )
    
    def _generate_service_enhancements(
        self,
        service_docs: ServiceDocumentation,
        service_context: ServiceContext,
        enhancement_level: str
    ) -> Dict[str, List[str]]:
        """Generate enhancements for a specific service.
        
        Args:
            service_docs: Service documentation
            service_context: Service usage context
            enhancement_level: Level of enhancement
            
        Returns:
            Dictionary with enhancement content
        """
        enhancements = {
            'content': "",
            'information': [],
            'practices': [],
            'examples': [],
            'related': []
        }
        
        content_parts = []
        
        # Add service description (always included)
        if service_docs.description:
            desc_text = self.enhancement_templates['service_intro'].format(
                service_name=service_docs.service_name,
                description=service_docs.description
            )
            content_parts.append(desc_text)
            enhancements['information'].append(f"Added description for {service_docs.service_name}")
        
        # Add use cases (moderate and comprehensive)
        if enhancement_level in ['moderate', 'comprehensive'] and service_docs.use_cases:
            use_cases_text = self.enhancement_templates['use_case'].format(
                use_cases=", ".join(service_docs.use_cases[:3])
            )
            content_parts.append(use_cases_text)
            enhancements['information'].append(f"Added use cases for {service_docs.service_name}")
        
        # Add best practices (comprehensive)
        if enhancement_level == 'comprehensive' and service_docs.best_practices:
            for practice in service_docs.best_practices[:2]:  # Top 2 practices
                practice_text = self.enhancement_templates['best_practice'].format(
                    practice=practice
                )
                content_parts.append(practice_text)
                enhancements['practices'].append(practice)
        
        # Add code examples (comprehensive)
        if enhancement_level == 'comprehensive' and service_docs.code_examples:
            for example in service_docs.code_examples[:1]:  # One example
                example_text = self.enhancement_templates['code_example'].format(
                    language=example.get('language', 'text'),
                    code=example.get('code', ''),
                    description=example.get('description', 'Code example')
                )
                content_parts.append(example_text)
                enhancements['examples'].append(example)
        
        # Add related services (moderate and comprehensive)
        if enhancement_level in ['moderate', 'comprehensive'] and service_docs.related_services:
            for related in service_docs.related_services[:2]:  # Top 2 related
                enhancements['related'].append(related)
        
        enhancements['content'] = "\n\n".join(content_parts)
        return enhancements
    
    def _calculate_enhancement_confidence(
        self,
        service_contexts: List[ServiceContext],
        added_info_count: int,
        correction_count: int
    ) -> float:
        """Calculate confidence score for enhancement.
        
        Args:
            service_contexts: List of service contexts
            added_info_count: Number of information pieces added
            correction_count: Number of corrections made
            
        Returns:
            Confidence score (0-1)
        """
        # Base confidence from service recognition
        base_confidence = min(1.0, len(service_contexts) * 0.3)
        
        # Boost from successful information addition
        info_boost = min(0.4, added_info_count * 0.1)
        
        # Penalty for corrections needed
        correction_penalty = min(0.3, correction_count * 0.1)
        
        confidence = base_confidence + info_boost - correction_penalty
        return max(0.0, min(1.0, confidence))
    
    @log_execution_time
    def enhance_presentation_content(
        self,
        slides_content: List[str],
        enhancement_level: str = "moderate"
    ) -> List[EnhancedContent]:
        """Enhance content for entire presentation.
        
        Args:
            slides_content: List of slide content strings
            enhancement_level: Level of enhancement
            
        Returns:
            List of EnhancedContent objects
        """
        performance_monitor.start_operation("enhance_presentation")
        
        try:
            enhanced_slides = []
            
            for i, content in enumerate(slides_content):
                slide_number = i + 1
                enhanced_content = self.enhance_slide_content(
                    content, slide_number, enhancement_level
                )
                enhanced_slides.append(enhanced_content)
            
            performance_monitor.end_operation("enhance_presentation", True)
            logger.info(f"Enhanced {len(enhanced_slides)} slides with AWS documentation")
            return enhanced_slides
            
        except Exception as e:
            performance_monitor.end_operation("enhance_presentation", False)
            logger.error(f"Failed to enhance presentation content: {str(e)}")
            return []
    
    def get_enhancement_summary(self, enhanced_contents: List[EnhancedContent]) -> Dict[str, Any]:
        """Generate summary of enhancement results.
        
        Args:
            enhanced_contents: List of enhanced content objects
            
        Returns:
            Dictionary with enhancement summary
        """
        try:
            summary = {
                'total_slides_enhanced': len(enhanced_contents),
                'total_information_added': 0,
                'total_corrections_made': 0,
                'total_best_practices': 0,
                'total_code_examples': 0,
                'unique_services_covered': set(),
                'average_confidence': 0.0,
                'enhancement_distribution': {
                    'high_confidence': 0,  # > 0.8
                    'medium_confidence': 0,  # 0.5 - 0.8
                    'low_confidence': 0  # < 0.5
                }
            }
            
            for enhanced in enhanced_contents:
                summary['total_information_added'] += len(enhanced.added_information)
                summary['total_corrections_made'] += len(enhanced.corrections)
                summary['total_best_practices'] += len(enhanced.best_practices)
                summary['total_code_examples'] += len(enhanced.code_examples)
                summary['unique_services_covered'].update(enhanced.related_services)
                summary['average_confidence'] += enhanced.confidence_score
                
                # Categorize by confidence
                if enhanced.confidence_score > 0.8:
                    summary['enhancement_distribution']['high_confidence'] += 1
                elif enhanced.confidence_score > 0.5:
                    summary['enhancement_distribution']['medium_confidence'] += 1
                else:
                    summary['enhancement_distribution']['low_confidence'] += 1
            
            # Calculate averages
            if enhanced_contents:
                summary['average_confidence'] /= len(enhanced_contents)
            
            # Convert set to list for JSON serialization
            summary['unique_services_covered'] = list(summary['unique_services_covered'])
            
            logger.info(f"Generated enhancement summary: {summary['total_slides_enhanced']} slides enhanced")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate enhancement summary: {str(e)}")
            return {}
