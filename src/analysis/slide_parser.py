"""Slide Content Parser.

This module provides advanced slide content parsing and structure analysis
to support multimodal AI analysis and script generation.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import re
from loguru import logger


@dataclass
class ContentHierarchy:
    """Represents hierarchical content structure of a slide.
    
    Attributes:
        title: Main slide title
        subtitles: List of subtitle elements
        bullet_points: Nested bullet point structure
        key_messages: Identified key messages
        supporting_details: Supporting information
    """
    title: str
    subtitles: List[str]
    bullet_points: Dict[int, List[str]]  # level -> content
    key_messages: List[str]
    supporting_details: List[str]


@dataclass
class SlideRelationship:
    """Represents relationship between slides.
    
    Attributes:
        slide_number: Current slide number
        previous_slide: Previous slide number (if any)
        next_slide: Next slide number (if any)
        relationship_type: Type of relationship (continuation, transition, etc.)
        shared_concepts: Concepts shared with related slides
    """
    slide_number: int
    previous_slide: Optional[int]
    next_slide: Optional[int]
    relationship_type: str
    shared_concepts: List[str]


class SlideParser:
    """Advanced slide content parser for structure analysis."""
    
    def __init__(self):
        """Initialize slide parser with pattern recognition."""
        # Common slide title patterns
        self.title_patterns = [
            r'^(agenda|outline|overview)$',
            r'^(introduction|intro)$',
            r'^(conclusion|summary|wrap.?up)$',
            r'^(demo|demonstration)$',
            r'^(architecture|design)$',
            r'^(benefits|advantages)$',
            r'^(challenges|issues|problems)$',
            r'^(next steps|action items)$',
            r'^(q&a|questions)$'
        ]
        
        # AWS service patterns for enhanced detection
        self.aws_service_patterns = {
            'compute': [r'ec2', r'lambda', r'fargate', r'batch', r'elastic beanstalk'],
            'storage': [r's3', r'ebs', r'efs', r'fsx', r'glacier'],
            'database': [r'rds', r'dynamodb', r'aurora', r'redshift', r'documentdb'],
            'networking': [r'vpc', r'cloudfront', r'route 53', r'api gateway', r'elb'],
            'security': [r'iam', r'cognito', r'secrets manager', r'kms', r'waf'],
            'analytics': [r'athena', r'emr', r'kinesis', r'quicksight', r'glue'],
            'ml_ai': [r'sagemaker', r'bedrock', r'comprehend', r'rekognition', r'textract'],
            'devops': [r'codepipeline', r'codebuild', r'codecommit', r'cloudformation', r'cdk']
        }
        
        logger.info("Initialized slide parser with pattern recognition")
    
    def parse_content_hierarchy(self, text_elements: List[Dict[str, Any]]) -> ContentHierarchy:
        """Parse text elements into hierarchical content structure.
        
        Args:
            text_elements: List of text elements with hierarchy information
            
        Returns:
            ContentHierarchy object
        """
        try:
            title = ""
            subtitles = []
            bullet_points = {}
            key_messages = []
            supporting_details = []
            
            # Sort elements by hierarchy level
            sorted_elements = sorted(text_elements, key=lambda x: x.get('level', 0))
            
            for element in sorted_elements:
                text = element.get('text', '').strip()
                level = element.get('level', 0)
                
                if not text:
                    continue
                
                # Identify title (level 0 or first significant text)
                if level == 0 and not title:
                    title = text
                elif level == 0:
                    subtitles.append(text)
                
                # Organize bullet points by level
                elif level > 0:
                    if level not in bullet_points:
                        bullet_points[level] = []
                    bullet_points[level].append(text)
                    
                    # Identify key messages (short, impactful statements)
                    if len(text.split()) <= 8 and any(keyword in text.lower() 
                        for keyword in ['key', 'important', 'critical', 'main', 'primary']):
                        key_messages.append(text)
                    else:
                        supporting_details.append(text)
            
            hierarchy = ContentHierarchy(
                title=title,
                subtitles=subtitles,
                bullet_points=bullet_points,
                key_messages=key_messages,
                supporting_details=supporting_details
            )
            
            logger.debug(f"Parsed content hierarchy: title='{title[:50]}...', "
                        f"{len(bullet_points)} bullet levels, {len(key_messages)} key messages")
            return hierarchy
            
        except Exception as e:
            logger.error(f"Failed to parse content hierarchy: {str(e)}")
            return ContentHierarchy("", [], {}, [], [])
    
    def identify_slide_purpose(self, hierarchy: ContentHierarchy, slide_number: int) -> str:
        """Identify the primary purpose of a slide.
        
        Args:
            hierarchy: Parsed content hierarchy
            slide_number: Slide number for context
            
        Returns:
            Slide purpose classification
        """
        try:
            title_lower = hierarchy.title.lower()
            all_text = ' '.join([hierarchy.title] + hierarchy.subtitles + 
                              [item for sublist in hierarchy.bullet_points.values() for item in sublist])
            all_text_lower = all_text.lower()
            
            # Check for specific slide types
            for pattern in self.title_patterns:
                if re.search(pattern, title_lower, re.IGNORECASE):
                    if 'agenda' in pattern or 'outline' in pattern:
                        return 'agenda'
                    elif 'intro' in pattern:
                        return 'introduction'
                    elif 'conclusion' in pattern or 'summary' in pattern:
                        return 'conclusion'
                    elif 'demo' in pattern:
                        return 'demonstration'
                    elif 'architecture' in pattern:
                        return 'architecture'
                    elif 'q&a' in pattern:
                        return 'qa'
            
            # Analyze content characteristics
            if slide_number == 1:
                return 'title'
            elif 'architecture' in all_text_lower or 'diagram' in all_text_lower:
                return 'architecture'
            elif len(hierarchy.bullet_points) > 2:
                return 'detailed_content'
            elif any('benefit' in text.lower() or 'advantage' in text.lower() 
                    for text in hierarchy.key_messages):
                return 'benefits'
            elif any('step' in text.lower() or 'process' in text.lower() 
                    for text in hierarchy.supporting_details):
                return 'process'
            else:
                return 'content'
                
        except Exception as e:
            logger.warning(f"Failed to identify slide purpose: {str(e)}")
            return 'content'
    
    def extract_aws_service_context(self, text_content: List[str]) -> Dict[str, List[str]]:
        """Extract AWS services with their usage context.
        
        Args:
            text_content: List of text content from slide
            
        Returns:
            Dictionary mapping service categories to services with context
        """
        try:
            service_context = {}
            all_text = ' '.join(text_content).lower()
            
            for category, patterns in self.aws_service_patterns.items():
                found_services = []
                
                for pattern in patterns:
                    matches = re.finditer(pattern, all_text, re.IGNORECASE)
                    for match in matches:
                        service_name = match.group(0)
                        
                        # Extract context around the service mention
                        start = max(0, match.start() - 30)
                        end = min(len(all_text), match.end() + 30)
                        context = all_text[start:end].strip()
                        
                        found_services.append({
                            'service': service_name,
                            'context': context
                        })
                
                if found_services:
                    service_context[category] = found_services
            
            logger.debug(f"Extracted AWS service context: {len(service_context)} categories")
            return service_context
            
        except Exception as e:
            logger.error(f"Failed to extract AWS service context: {str(e)}")
            return {}
    
    def analyze_content_complexity(self, hierarchy: ContentHierarchy) -> Dict[str, Any]:
        """Analyze content complexity metrics.
        
        Args:
            hierarchy: Parsed content hierarchy
            
        Returns:
            Dictionary with complexity metrics
        """
        try:
            # Count various complexity indicators
            total_words = 0
            technical_terms = 0
            bullet_depth = max(hierarchy.bullet_points.keys()) if hierarchy.bullet_points else 0
            
            all_text = [hierarchy.title] + hierarchy.subtitles + hierarchy.key_messages + hierarchy.supporting_details
            
            # Technical term patterns
            technical_patterns = [
                r'\b\w+(?:API|SDK|CLI|JSON|XML|HTTP|HTTPS|REST|GraphQL)\b',
                r'\b(?:microservices?|serverless|containerization|orchestration)\b',
                r'\b(?:scalability|availability|durability|consistency)\b',
                r'\b(?:encryption|authentication|authorization|compliance)\b'
            ]
            
            for text in all_text:
                if text:
                    words = text.split()
                    total_words += len(words)
                    
                    # Count technical terms
                    for pattern in technical_patterns:
                        technical_terms += len(re.findall(pattern, text, re.IGNORECASE))
            
            # Calculate complexity score
            complexity_factors = {
                'word_count': total_words,
                'technical_term_ratio': technical_terms / max(total_words, 1),
                'bullet_depth': bullet_depth,
                'key_message_count': len(hierarchy.key_messages),
                'supporting_detail_count': len(hierarchy.supporting_details)
            }
            
            # Overall complexity score (1-5)
            complexity_score = min(5, max(1, 
                1 + (complexity_factors['technical_term_ratio'] * 2) +
                (bullet_depth * 0.5) +
                (min(total_words, 200) / 50)
            ))
            
            complexity_analysis = {
                'score': round(complexity_score, 1),
                'factors': complexity_factors,
                'level': 'basic' if complexity_score < 2 else
                        'intermediate' if complexity_score < 3.5 else
                        'advanced' if complexity_score < 4.5 else 'expert'
            }
            
            logger.debug(f"Analyzed content complexity: score={complexity_score:.1f}")
            return complexity_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze content complexity: {str(e)}")
            return {'score': 3.0, 'factors': {}, 'level': 'intermediate'}
    
    def identify_slide_relationships(self, slides_data: List[Dict[str, Any]]) -> List[SlideRelationship]:
        """Identify relationships between slides in presentation.
        
        Args:
            slides_data: List of slide data with parsed content
            
        Returns:
            List of SlideRelationship objects
        """
        try:
            relationships = []
            
            for i, slide_data in enumerate(slides_data):
                slide_number = i + 1
                hierarchy = slide_data.get('hierarchy')
                
                if not hierarchy:
                    continue
                
                # Determine relationship type
                relationship_type = 'standalone'
                shared_concepts = []
                
                # Check relationships with adjacent slides
                if i > 0:  # Has previous slide
                    prev_hierarchy = slides_data[i-1].get('hierarchy')
                    if prev_hierarchy:
                        # Find shared concepts
                        current_concepts = set(hierarchy.key_messages + hierarchy.supporting_details)
                        prev_concepts = set(prev_hierarchy.key_messages + prev_hierarchy.supporting_details)
                        shared = current_concepts.intersection(prev_concepts)
                        
                        if shared:
                            shared_concepts.extend(list(shared))
                            relationship_type = 'continuation'
                
                if i < len(slides_data) - 1:  # Has next slide
                    next_hierarchy = slides_data[i+1].get('hierarchy')
                    if next_hierarchy and relationship_type == 'standalone':
                        # Check if this is a transition slide
                        if len(hierarchy.key_messages) <= 2 and 'next' in hierarchy.title.lower():
                            relationship_type = 'transition'
                
                relationship = SlideRelationship(
                    slide_number=slide_number,
                    previous_slide=i if i > 0 else None,
                    next_slide=i + 2 if i < len(slides_data) - 1 else None,
                    relationship_type=relationship_type,
                    shared_concepts=shared_concepts
                )
                
                relationships.append(relationship)
            
            logger.info(f"Identified relationships for {len(relationships)} slides")
            return relationships
            
        except Exception as e:
            logger.error(f"Failed to identify slide relationships: {str(e)}")
            return []
    
    def generate_content_summary(self, hierarchy: ContentHierarchy) -> str:
        """Generate a concise summary of slide content.
        
        Args:
            hierarchy: Parsed content hierarchy
            
        Returns:
            Content summary string
        """
        try:
            summary_parts = []
            
            # Add title
            if hierarchy.title:
                summary_parts.append(f"Title: {hierarchy.title}")
            
            # Add key messages
            if hierarchy.key_messages:
                key_msg = "; ".join(hierarchy.key_messages[:3])  # Top 3 key messages
                summary_parts.append(f"Key points: {key_msg}")
            
            # Add main bullet points
            if hierarchy.bullet_points:
                level_1_points = hierarchy.bullet_points.get(1, [])
                if level_1_points:
                    main_points = "; ".join(level_1_points[:3])  # Top 3 main points
                    summary_parts.append(f"Main content: {main_points}")
            
            summary = " | ".join(summary_parts)
            
            # Limit summary length
            if len(summary) > 200:
                summary = summary[:197] + "..."
            
            logger.debug(f"Generated content summary: {len(summary)} characters")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate content summary: {str(e)}")
            return "Content summary unavailable"
