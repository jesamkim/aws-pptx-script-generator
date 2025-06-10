"""Content Classification Module.

This module provides advanced content classification capabilities for
slide content, including technical depth assessment and audience targeting.
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
import re
from loguru import logger


@dataclass
class ContentClassification:
    """Results of content classification analysis.
    
    Attributes:
        slide_type: Classified slide type
        technical_depth: Technical depth score (1-5)
        audience_level: Target audience level
        content_density: Content density score (1-5)
        key_topics: Main topics identified
        aws_focus_areas: AWS service categories covered
        presentation_style: Suggested presentation style
        time_requirement: Estimated time needed
    """
    slide_type: str
    technical_depth: int
    audience_level: str
    content_density: int
    key_topics: List[str]
    aws_focus_areas: List[str]
    presentation_style: str
    time_requirement: float


class ContentClassifier:
    """Advanced content classifier for presentation slides."""
    
    def __init__(self):
        """Initialize content classifier with classification rules."""
        # Slide type classification rules
        self.slide_type_rules = {
            'title': {
                'patterns': [r'^title', r'^overview', r'^introduction'],
                'position_rules': [1],  # Slide numbers where this type is common
                'content_rules': {'max_bullets': 3, 'max_words': 50}
            },
            'agenda': {
                'patterns': [r'^agenda', r'^outline', r'^topics'],
                'position_rules': [2, 3],
                'content_rules': {'min_bullets': 3, 'max_depth': 2}
            },
            'technical': {
                'patterns': [r'architecture', r'implementation', r'configuration'],
                'content_rules': {'min_technical_terms': 5}
            },
            'demo': {
                'patterns': [r'^demo', r'demonstration', r'walkthrough'],
                'content_rules': {'has_steps': True}
            },
            'summary': {
                'patterns': [r'^summary', r'^conclusion', r'^wrap.?up'],
                'position_rules': [-1, -2],  # Last or second-to-last slides
                'content_rules': {'max_depth': 2}
            }
        }
        
        # Technical term categories
        self.technical_terms = {
            'architecture': {
                'high_availability', 'fault tolerance', 'scalability', 'reliability',
                'disaster recovery', 'redundancy', 'failover', 'load balancing'
            },
            'development': {
                'api', 'sdk', 'cli', 'git', 'ci/cd', 'pipeline', 'deployment',
                'containerization', 'microservices', 'serverless'
            },
            'security': {
                'encryption', 'authentication', 'authorization', 'iam', 'compliance',
                'audit', 'security group', 'nacl', 'ssl/tls', 'certificate'
            },
            'database': {
                'acid', 'nosql', 'sharding', 'replication', 'indexing', 'partitioning',
                'consistency', 'transaction', 'query', 'backup'
            },
            'networking': {
                'vpc', 'subnet', 'routing', 'gateway', 'endpoint', 'dns', 'cdn',
                'firewall', 'proxy', 'latency'
            }
        }
        
        # AWS service categories
        self.aws_categories = {
            'compute': {'ec2', 'lambda', 'ecs', 'eks', 'fargate', 'batch'},
            'storage': {'s3', 'ebs', 'efs', 'fsx', 'glacier', 'storage gateway'},
            'database': {'rds', 'dynamodb', 'aurora', 'redshift', 'documentdb'},
            'networking': {'vpc', 'cloudfront', 'route53', 'api gateway', 'elb'},
            'security': {'iam', 'kms', 'waf', 'shield', 'guardduty', 'macie'},
            'analytics': {'athena', 'emr', 'kinesis', 'quicksight', 'glue'},
            'ml_ai': {'sagemaker', 'comprehend', 'rekognition', 'textract'},
            'devops': {'codecommit', 'codebuild', 'codepipeline', 'cloudformation'}
        }
        
        logger.info("Initialized content classifier with classification rules")
    
    def _count_technical_terms(self, text: str) -> Dict[str, int]:
        """Count technical terms by category in text.
        
        Args:
            text: Text content to analyze
            
        Returns:
            Dictionary mapping categories to term counts
        """
        term_counts = {}
        text_lower = text.lower()
        
        for category, terms in self.technical_terms.items():
            count = sum(1 for term in terms if term in text_lower)
            if count > 0:
                term_counts[category] = count
        
        return term_counts
    
    def _identify_aws_services(self, text: str) -> Dict[str, Set[str]]:
        """Identify AWS services mentioned in text.
        
        Args:
            text: Text content to analyze
            
        Returns:
            Dictionary mapping categories to service sets
        """
        services_found = {}
        text_lower = text.lower()
        
        for category, services in self.aws_categories.items():
            found = {service for service in services if service in text_lower}
            if found:
                services_found[category] = found
        
        return services_found
    
    def _assess_technical_depth(self, text: str, term_counts: Dict[str, int]) -> int:
        """Assess technical depth of content.
        
        Args:
            text: Text content to analyze
            term_counts: Pre-computed technical term counts
            
        Returns:
            Technical depth score (1-5)
        """
        # Base score from term counts
        total_terms = sum(term_counts.values())
        base_score = min(5, 1 + (total_terms / 3))
        
        # Adjust based on content characteristics
        adjustments = 0
        
        # Check for code snippets or configuration examples
        if re.search(r'```.*```', text, re.DOTALL) or re.search(r'<code>.*</code>', text, re.DOTALL):
            adjustments += 1
        
        # Check for architectural diagrams references
        if 'architecture' in text.lower() or 'diagram' in text.lower():
            adjustments += 0.5
        
        # Check for deep technical concepts
        deep_technical = {'latency', 'throughput', 'consistency', 'durability', 'encryption'}
        if any(concept in text.lower() for concept in deep_technical):
            adjustments += 0.5
        
        final_score = min(5, max(1, base_score + adjustments))
        return round(final_score)
    
    def _determine_audience_level(self, technical_depth: int, aws_services: Dict[str, Set[str]]) -> str:
        """Determine appropriate audience level.
        
        Args:
            technical_depth: Technical depth score
            aws_services: Identified AWS services by category
            
        Returns:
            Audience level classification
        """
        # Count total services and categories
        total_services = sum(len(services) for services in aws_services.values())
        total_categories = len(aws_services)
        
        if technical_depth >= 4 and total_categories >= 3:
            return "expert"
        elif technical_depth >= 3 or total_services >= 5:
            return "advanced"
        elif technical_depth >= 2 or total_services >= 2:
            return "intermediate"
        else:
            return "beginner"
    
    def _calculate_content_density(self, text: str, term_counts: Dict[str, int]) -> int:
        """Calculate content density score.
        
        Args:
            text: Text content to analyze
            term_counts: Pre-computed technical term counts
            
        Returns:
            Content density score (1-5)
        """
        # Count words and lines
        words = text.split()
        lines = text.split('\n')
        
        # Base density on word count
        if len(words) < 50:
            base_density = 1
        elif len(words) < 100:
            base_density = 2
        elif len(words) < 150:
            base_density = 3
        elif len(words) < 200:
            base_density = 4
        else:
            base_density = 5
        
        # Adjust for technical term density
        total_terms = sum(term_counts.values())
        term_density = total_terms / max(1, len(words))
        
        # Adjust for bullet point density
        bullet_points = sum(1 for line in lines if line.strip().startswith(('•', '-', '*')))
        bullet_density = bullet_points / max(1, len(lines))
        
        # Calculate final density score
        density_score = min(5, max(1, 
            base_density + 
            (term_density * 2) + 
            (bullet_density * 1.5)
        ))
        
        return round(density_score)
    
    def _estimate_time_requirement(self, content_density: int, technical_depth: int) -> float:
        """Estimate time needed to present content.
        
        Args:
            content_density: Content density score
            technical_depth: Technical depth score
            
        Returns:
            Estimated time in minutes
        """
        # Base time based on density
        base_time = content_density * 0.5  # 0.5 to 2.5 minutes
        
        # Adjust for technical depth
        technical_multiplier = 1 + (technical_depth * 0.1)  # 1.1x to 1.5x
        
        # Calculate final time
        time_estimate = base_time * technical_multiplier
        
        # Round to nearest 0.5 minute
        return round(time_estimate * 2) / 2
    
    def _suggest_presentation_style(
        self,
        slide_type: str,
        technical_depth: int,
        audience_level: str
    ) -> str:
        """Suggest appropriate presentation style.
        
        Args:
            slide_type: Classified slide type
            technical_depth: Technical depth score
            audience_level: Target audience level
            
        Returns:
            Suggested presentation style
        """
        if slide_type in ['demo', 'walkthrough']:
            return "interactive"
        elif technical_depth >= 4:
            return "technical deep-dive"
        elif audience_level in ['beginner', 'intermediate']:
            return "explanatory"
        elif slide_type in ['architecture', 'technical']:
            return "detailed"
        else:
            return "balanced"
    
    def classify_content(
        self,
        text: str,
        slide_number: int,
        total_slides: int
    ) -> ContentClassification:
        """Perform comprehensive content classification.
        
        Args:
            text: Text content to analyze
            slide_number: Current slide number
            total_slides: Total number of slides
            
        Returns:
            ContentClassification object with analysis results
        """
        try:
            # Identify technical terms
            term_counts = self._count_technical_terms(text)
            
            # Identify AWS services
            aws_services = self._identify_aws_services(text)
            
            # Determine slide type
            slide_type = "content"  # default
            for type_name, rules in self.slide_type_rules.items():
                # Check position rules
                if 'position_rules' in rules:
                    if slide_number in rules['position_rules'] or \
                       (slide_number == total_slides and -1 in rules['position_rules']):
                        # Check patterns
                        if any(re.search(pattern, text.lower()) for pattern in rules['patterns']):
                            slide_type = type_name
                            break
                
                # Check patterns if not matched by position
                elif any(re.search(pattern, text.lower()) for pattern in rules['patterns']):
                    slide_type = type_name
                    break
            
            # Assess technical depth
            technical_depth = self._assess_technical_depth(text, term_counts)
            
            # Determine audience level
            audience_level = self._determine_audience_level(technical_depth, aws_services)
            
            # Calculate content density
            content_density = self._calculate_content_density(text, term_counts)
            
            # Extract key topics
            key_topics = [category for category, count in term_counts.items() 
                         if count >= 2][:5]  # Top 5 topics
            
            # Get AWS focus areas
            aws_focus_areas = list(aws_services.keys())
            
            # Suggest presentation style
            presentation_style = self._suggest_presentation_style(
                slide_type, technical_depth, audience_level
            )
            
            # Estimate time requirement
            time_requirement = self._estimate_time_requirement(
                content_density, technical_depth
            )
            
            # Create classification result
            classification = ContentClassification(
                slide_type=slide_type,
                technical_depth=technical_depth,
                audience_level=audience_level,
                content_density=content_density,
                key_topics=key_topics,
                aws_focus_areas=aws_focus_areas,
                presentation_style=presentation_style,
                time_requirement=time_requirement
            )
            
            logger.info(f"Classified slide {slide_number}: {slide_type}, "
                       f"depth={technical_depth}, audience={audience_level}")
            return classification
            
        except Exception as e:
            logger.error(f"Failed to classify content: {str(e)}")
            # Return default classification
            return ContentClassification(
                slide_type="content",
                technical_depth=3,
                audience_level="intermediate",
                content_density=3,
                key_topics=[],
                aws_focus_areas=[],
                presentation_style="balanced",
                time_requirement=2.0
            )
    
    def get_classification_summary(self, classifications: List[ContentClassification]) -> Dict[str, Any]:
        """Generate summary statistics from multiple classifications.
        
        Args:
            classifications: List of content classifications
            
        Returns:
            Dictionary with summary statistics
        """
        try:
            summary = {
                'slide_types': {},
                'avg_technical_depth': 0,
                'audience_distribution': {},
                'avg_content_density': 0,
                'common_topics': {},
                'aws_focus_areas': {},
                'total_time_estimate': 0
            }
            
            for classification in classifications:
                # Count slide types
                slide_type = classification.slide_type
                summary['slide_types'][slide_type] = summary['slide_types'].get(slide_type, 0) + 1
                
                # Sum technical depth and density
                summary['avg_technical_depth'] += classification.technical_depth
                summary['avg_content_density'] += classification.content_density
                
                # Count audience levels
                audience = classification.audience_level
                summary['audience_distribution'][audience] = \
                    summary['audience_distribution'].get(audience, 0) + 1
                
                # Count topics
                for topic in classification.key_topics:
                    summary['common_topics'][topic] = \
                        summary['common_topics'].get(topic, 0) + 1
                
                # Count AWS focus areas
                for area in classification.aws_focus_areas:
                    summary['aws_focus_areas'][area] = \
                        summary['aws_focus_areas'].get(area, 0) + 1
                
                # Sum time estimates
                summary['total_time_estimate'] += classification.time_requirement
            
            # Calculate averages
            count = len(classifications)
            if count > 0:
                summary['avg_technical_depth'] /= count
                summary['avg_content_density'] /= count
            
            # Sort topics and areas by frequency
            summary['common_topics'] = dict(sorted(
                summary['common_topics'].items(),
                key=lambda x: x[1],
                reverse=True
            ))
            
            summary['aws_focus_areas'] = dict(sorted(
                summary['aws_focus_areas'].items(),
                key=lambda x: x[1],
                reverse=True
            ))
            
            logger.info(f"Generated classification summary for {count} slides")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate classification summary: {str(e)}")
            return {}
