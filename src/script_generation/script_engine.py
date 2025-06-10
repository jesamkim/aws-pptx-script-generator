"""Script Generation Engine.

This module provides the core script generation capabilities with AI integration,
persona customization, and quality assurance.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import re
from loguru import logger

from src.analysis.multimodal_analyzer import SlideAnalysis, PresentationAnalysis
from src.mcp_integration.knowledge_enhancer import EnhancedContent
from src.utils.logger import log_execution_time, performance_monitor


@dataclass
class ScriptSection:
    """Individual script section for a slide.
    
    Attributes:
        slide_number: Slide number
        title: Section title
        content: Main script content
        speaker_notes: Additional speaker notes
        time_allocation: Allocated time in minutes
        transitions: Transition text to next slide
        key_points: Key points to emphasize
        interaction_cues: Audience interaction cues
    """
    slide_number: int
    title: str
    content: str
    speaker_notes: str
    time_allocation: float
    transitions: str
    key_points: List[str]
    interaction_cues: List[str]


@dataclass
class GeneratedScript:
    """Complete generated presentation script.
    
    Attributes:
        title: Presentation title
        presenter_info: Presenter information
        overview: Presentation overview
        sections: List of script sections
        conclusion: Conclusion section
        total_duration: Total estimated duration
        language: Script language
        quality_metrics: Quality assessment metrics
        metadata: Additional metadata
    """
    title: str
    presenter_info: Dict[str, str]
    overview: str
    sections: List[ScriptSection]
    conclusion: str
    total_duration: float
    language: str
    quality_metrics: Dict[str, Any]
    metadata: Dict[str, Any]


class ScriptEngine:
    """Core script generation engine with AI integration."""
    
    def __init__(self):
        """Initialize script generation engine."""
        # Script templates for different languages
        self.templates = {
            'english': {
                'opening': "Good {time_of_day}, everyone. My name is {name}, and I'm a {title} here at AWS.",
                'transition': "Now, let's move on to {next_topic}.",
                'emphasis': "This is particularly important because {reason}.",
                'interaction': "Let me ask you a question: {question}",
                'conclusion': "To summarize what we've covered today...",
                'closing': "Thank you for your time and attention. I'm happy to take any questions."
            },
            'korean': {
                'opening': "안녕하세요, 여러분. 저는 {name}이고, AWS에서 {title}로 근무하고 있습니다.",
                'transition': "이제 {next_topic}에 대해 알아보겠습니다.",
                'emphasis': "이것이 특히 중요한 이유는 {reason} 때문입니다.",
                'interaction': "질문을 하나 드리겠습니다: {question}",
                'conclusion': "오늘 다룬 내용을 정리하면...",
                'closing': "시간 내주셔서 감사합니다. 질문이 있으시면 언제든지 말씀해 주세요."
            }
        }
        
        # Persona adaptation patterns
        self.persona_patterns = {
            'junior': {
                'style': 'collaborative',
                'phrases': ['Let me walk you through', 'As we explore together', 'You might find'],
                'confidence': 'moderate'
            },
            'senior': {
                'style': 'authoritative',
                'phrases': ['Based on my experience', 'I recommend', 'The best approach is'],
                'confidence': 'high'
            },
            'principal': {
                'style': 'strategic',
                'phrases': ['From a strategic perspective', 'Consider the implications', 'The key insight is'],
                'confidence': 'very_high'
            },
            'distinguished': {
                'style': 'visionary',
                'phrases': ['Looking at the bigger picture', 'This transforms how we think', 'The future direction'],
                'confidence': 'expert'
            }
        }
        
        logger.info("Initialized script generation engine")
    
    @log_execution_time
    def generate_complete_script(
        self,
        presentation_analysis: PresentationAnalysis,
        enhanced_contents: List[EnhancedContent],
        time_allocations: Dict[int, float],
        persona: Dict[str, Any],
        context: Dict[str, Any]
    ) -> GeneratedScript:
        """Generate complete presentation script.
        
        Args:
            presentation_analysis: Multimodal analysis results
            enhanced_contents: MCP-enhanced content
            time_allocations: Time allocation per slide
            persona: Presenter persona information
            context: Presentation context
            
        Returns:
            GeneratedScript object with complete script
        """
        performance_monitor.start_operation("generate_complete_script")
        
        try:
            language = persona.get('language', 'english').lower()
            
            # Generate script sections
            sections = []
            for i, slide_analysis in enumerate(presentation_analysis.slide_analyses):
                enhanced_content = enhanced_contents[i] if i < len(enhanced_contents) else None
                time_allocation = time_allocations.get(slide_analysis.slide_number, 2.0)
                
                section = self._generate_slide_section(
                    slide_analysis, enhanced_content, time_allocation, persona, context, language
                )
                sections.append(section)
            
            # Generate presentation overview
            overview = self._generate_overview(presentation_analysis, persona, context, language)
            
            # Generate conclusion
            conclusion = self._generate_conclusion(presentation_analysis, persona, context, language)
            
            # Calculate quality metrics
            quality_metrics = self._assess_script_quality(sections, persona, context)
            
            # Create complete script
            script = GeneratedScript(
                title=presentation_analysis.overall_theme,
                presenter_info={
                    'name': persona.get('full_name', ''),
                    'title': persona.get('job_title', ''),
                    'experience': persona.get('experience_level', '')
                },
                overview=overview,
                sections=sections,
                conclusion=conclusion,
                total_duration=sum(time_allocations.values()),
                language=language,
                quality_metrics=quality_metrics,
                metadata={
                    'slide_count': len(sections),
                    'generation_timestamp': time.time(),
                    'persona_style': persona.get('presentation_style', ''),
                    'technical_depth': context.get('technical_depth', 3)
                }
            )
            
            performance_monitor.end_operation("generate_complete_script", True)
            logger.info(f"Generated complete script: {len(sections)} sections, {script.total_duration} minutes")
            return script
            
        except Exception as e:
            performance_monitor.end_operation("generate_complete_script", False)
            logger.error(f"Script generation failed: {str(e)}")
            raise
    
    def _generate_slide_section(
        self,
        slide_analysis: SlideAnalysis,
        enhanced_content: Optional[EnhancedContent],
        time_allocation: float,
        persona: Dict[str, Any],
        context: Dict[str, Any],
        language: str
    ) -> ScriptSection:
        """Generate script section for individual slide.
        
        Args:
            slide_analysis: Slide analysis results
            enhanced_content: Enhanced content (if available)
            time_allocation: Time allocated for slide
            persona: Presenter persona
            context: Presentation context
            language: Script language
            
        Returns:
            ScriptSection object
        """
        try:
            # Generate main content
            content_parts = []
            
            # Add slide introduction
            intro = self._generate_slide_introduction(slide_analysis, persona, language)
            content_parts.append(intro)
            
            # Add main content explanation
            explanation = self._generate_content_explanation(
                slide_analysis, enhanced_content, persona, context, language
            )
            content_parts.append(explanation)
            
            # Add AWS-specific insights if available
            if enhanced_content and enhanced_content.best_practices:
                aws_insights = self._generate_aws_insights(enhanced_content, language)
                content_parts.append(aws_insights)
            
            # Generate speaker notes
            speaker_notes = self._generate_speaker_notes(
                slide_analysis, enhanced_content, time_allocation, language
            )
            
            # Generate transitions
            transitions = self._generate_transitions(slide_analysis, language)
            
            # Extract key points
            key_points = self._extract_key_points(slide_analysis, enhanced_content)
            
            # Generate interaction cues
            interaction_cues = self._generate_interaction_cues(
                slide_analysis, context, language
            )
            
            return ScriptSection(
                slide_number=slide_analysis.slide_number,
                title=slide_analysis.content_summary[:50] + "..." if len(slide_analysis.content_summary) > 50 else slide_analysis.content_summary,
                content="\n\n".join(content_parts),
                speaker_notes=speaker_notes,
                time_allocation=time_allocation,
                transitions=transitions,
                key_points=key_points,
                interaction_cues=interaction_cues
            )
            
        except Exception as e:
            logger.error(f"Failed to generate slide section {slide_analysis.slide_number}: {str(e)}")
            raise
    
    def _generate_slide_introduction(
        self,
        slide_analysis: SlideAnalysis,
        persona: Dict[str, Any],
        language: str
    ) -> str:
        """Generate introduction for slide.
        
        Args:
            slide_analysis: Slide analysis
            persona: Presenter persona
            language: Script language
            
        Returns:
            Slide introduction text
        """
        experience_level = persona.get('experience_level', 'senior').lower()
        persona_style = self.persona_patterns.get(experience_level, self.persona_patterns['senior'])
        
        if language == 'korean':
            if slide_analysis.slide_type == 'title':
                return f"오늘 프레젠테이션의 주제는 {slide_analysis.content_summary}입니다."
            elif slide_analysis.slide_type == 'agenda':
                return "오늘 다룰 주요 내용들을 살펴보겠습니다."
            else:
                phrase = persona_style['phrases'][0] if persona_style['phrases'] else "이제"
                return f"{phrase} {slide_analysis.content_summary}에 대해 알아보겠습니다."
        else:
            if slide_analysis.slide_type == 'title':
                return f"Today's presentation focuses on {slide_analysis.content_summary}."
            elif slide_analysis.slide_type == 'agenda':
                return "Let me walk you through what we'll be covering today."
            else:
                phrase = persona_style['phrases'][0] if persona_style['phrases'] else "Now let's explore"
                return f"{phrase} {slide_analysis.content_summary}."
    
    def _generate_content_explanation(
        self,
        slide_analysis: SlideAnalysis,
        enhanced_content: Optional[EnhancedContent],
        persona: Dict[str, Any],
        context: Dict[str, Any],
        language: str
    ) -> str:
        """Generate detailed content explanation.
        
        Args:
            slide_analysis: Slide analysis
            enhanced_content: Enhanced content
            persona: Presenter persona
            context: Presentation context
            language: Script language
            
        Returns:
            Content explanation text
        """
        explanation_parts = []
        
        # Add visual description context
        if slide_analysis.visual_description:
            if language == 'korean':
                explanation_parts.append(f"화면에 보시는 바와 같이, {slide_analysis.visual_description}")
            else:
                explanation_parts.append(f"As you can see on the slide, {slide_analysis.visual_description}")
        
        # Add key concepts explanation
        if slide_analysis.key_concepts:
            concepts_text = ", ".join(slide_analysis.key_concepts[:3])  # Top 3 concepts
            if language == 'korean':
                explanation_parts.append(f"여기서 핵심 개념은 {concepts_text}입니다.")
            else:
                explanation_parts.append(f"The key concepts here are {concepts_text}.")
        
        # Add AWS services context
        if slide_analysis.aws_services:
            services_text = ", ".join(slide_analysis.aws_services[:2])  # Top 2 services
            if language == 'korean':
                explanation_parts.append(f"이는 {services_text}와 관련이 있습니다.")
            else:
                explanation_parts.append(f"This relates to {services_text}.")
        
        # Add enhanced content if available
        if enhanced_content and enhanced_content.added_information:
            info = enhanced_content.added_information[0]  # First piece of added info
            explanation_parts.append(info)
        
        return " ".join(explanation_parts)
    
    def _generate_aws_insights(self, enhanced_content: EnhancedContent, language: str) -> str:
        """Generate AWS-specific insights from enhanced content.
        
        Args:
            enhanced_content: Enhanced content with AWS information
            language: Script language
            
        Returns:
            AWS insights text
        """
        insights = []
        
        # Add best practices
        if enhanced_content.best_practices:
            practice = enhanced_content.best_practices[0]
            if language == 'korean':
                insights.append(f"💡 **모범 사례**: {practice}")
            else:
                insights.append(f"💡 **Best Practice**: {practice}")
        
        # Add code examples context
        if enhanced_content.code_examples:
            if language == 'korean':
                insights.append("실제 구현 예제도 함께 살펴보겠습니다.")
            else:
                insights.append("Let's also look at a practical implementation example.")
        
        # Add related services
        if enhanced_content.related_services:
            services = ", ".join(enhanced_content.related_services[:2])
            if language == 'korean':
                insights.append(f"관련 서비스로는 {services}가 있습니다.")
            else:
                insights.append(f"Related services include {services}.")
        
        return "\n\n".join(insights)
    
    def _generate_speaker_notes(
        self,
        slide_analysis: SlideAnalysis,
        enhanced_content: Optional[EnhancedContent],
        time_allocation: float,
        language: str
    ) -> str:
        """Generate speaker notes for slide.
        
        Args:
            slide_analysis: Slide analysis
            enhanced_content: Enhanced content
            time_allocation: Time allocation
            language: Script language
            
        Returns:
            Speaker notes text
        """
        notes = []
        
        # Add timing note
        if language == 'korean':
            notes.append(f"⏱️ 예상 소요 시간: {time_allocation}분")
        else:
            notes.append(f"⏱️ Estimated time: {time_allocation} minutes")
        
        # Add technical depth note
        if slide_analysis.technical_depth >= 4:
            if language == 'korean':
                notes.append("🔧 기술적 세부사항이 많으니 청중의 이해도를 확인하세요")
            else:
                notes.append("🔧 Technical content - check audience understanding")
        
        # Add interaction suggestions
        if slide_analysis.audience_level in ['beginner', 'intermediate']:
            if language == 'korean':
                notes.append("❓ 질문을 받을 준비를 하세요")
            else:
                notes.append("❓ Be prepared for questions")
        
        # Add enhancement notes
        if enhanced_content and enhanced_content.corrections:
            if language == 'korean':
                notes.append("⚠️ 내용 정확성 확인됨")
            else:
                notes.append("⚠️ Content accuracy verified")
        
        return "\n".join(notes)
    
    def _generate_transitions(self, slide_analysis: SlideAnalysis, language: str) -> str:
        """Generate transition text to next slide.
        
        Args:
            slide_analysis: Current slide analysis
            language: Script language
            
        Returns:
            Transition text
        """
        if language == 'korean':
            if slide_analysis.slide_type == 'title':
                return "그럼 시작해보겠습니다."
            elif slide_analysis.slide_type == 'agenda':
                return "첫 번째 주제부터 살펴보겠습니다."
            else:
                return "다음으로 넘어가겠습니다."
        else:
            if slide_analysis.slide_type == 'title':
                return "Let's get started."
            elif slide_analysis.slide_type == 'agenda':
                return "Let's dive into our first topic."
            else:
                return "Moving on to our next point."
    
    def _extract_key_points(
        self,
        slide_analysis: SlideAnalysis,
        enhanced_content: Optional[EnhancedContent]
    ) -> List[str]:
        """Extract key points to emphasize.
        
        Args:
            slide_analysis: Slide analysis
            enhanced_content: Enhanced content
            
        Returns:
            List of key points
        """
        key_points = []
        
        # Add key concepts
        key_points.extend(slide_analysis.key_concepts[:3])
        
        # Add AWS services
        key_points.extend(slide_analysis.aws_services[:2])
        
        # Add enhanced information
        if enhanced_content:
            key_points.extend(enhanced_content.added_information[:2])
        
        return key_points[:5]  # Limit to 5 key points
    
    def _generate_interaction_cues(
        self,
        slide_analysis: SlideAnalysis,
        context: Dict[str, Any],
        language: str
    ) -> List[str]:
        """Generate audience interaction cues.
        
        Args:
            slide_analysis: Slide analysis
            context: Presentation context
            language: Script language
            
        Returns:
            List of interaction cues
        """
        cues = []
        
        interaction_level = context.get('interaction_level', 'moderate').lower()
        
        if interaction_level in ['moderate', 'high']:
            if slide_analysis.technical_depth >= 3:
                if language == 'korean':
                    cues.append("이 부분에 대해 질문이 있으신가요?")
                else:
                    cues.append("Any questions about this technical aspect?")
            
            if slide_analysis.slide_type == 'demo':
                if language == 'korean':
                    cues.append("실제로 어떻게 작동하는지 보여드리겠습니다.")
                else:
                    cues.append("Let me show you how this works in practice.")
        
        return cues
    
    def _generate_overview(
        self,
        presentation_analysis: PresentationAnalysis,
        persona: Dict[str, Any],
        context: Dict[str, Any],
        language: str
    ) -> str:
        """Generate presentation overview.
        
        Args:
            presentation_analysis: Complete presentation analysis
            persona: Presenter persona
            context: Presentation context
            language: Script language
            
        Returns:
            Overview text
        """
        if language == 'korean':
            return f"""오늘 {context.get('duration', 30)}분 동안 {presentation_analysis.overall_theme}에 대해 
{len(presentation_analysis.slide_analyses)}개의 주제로 나누어 설명드리겠습니다. 
{context.get('target_audience', '기술팀')} 대상으로 준비된 내용입니다."""
        else:
            return f"""Today, over the next {context.get('duration', 30)} minutes, we'll explore {presentation_analysis.overall_theme} 
through {len(presentation_analysis.slide_analyses)} key topics. This presentation is designed for {context.get('target_audience', 'technical teams')}."""
    
    def _generate_conclusion(
        self,
        presentation_analysis: PresentationAnalysis,
        persona: Dict[str, Any],
        context: Dict[str, Any],
        language: str
    ) -> str:
        """Generate presentation conclusion.
        
        Args:
            presentation_analysis: Complete presentation analysis
            persona: Presenter persona
            context: Presentation context
            language: Script language
            
        Returns:
            Conclusion text
        """
        if language == 'korean':
            return f"""오늘 {presentation_analysis.overall_theme}에 대해 함께 살펴보았습니다. 
핵심은 AWS 솔루션을 통해 여러분의 비즈니스 목표를 달성하는 것입니다. 
질문이 있으시면 언제든지 말씀해 주세요. 감사합니다."""
        else:
            return f"""Today we've explored {presentation_analysis.overall_theme} and how AWS solutions can help you achieve your business objectives. 
The key takeaway is leveraging these services to drive innovation and efficiency in your organization. 
I'm happy to take any questions you might have. Thank you."""
    
    def _assess_script_quality(
        self,
        sections: List[ScriptSection],
        persona: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess generated script quality.
        
        Args:
            sections: List of script sections
            persona: Presenter persona
            context: Presentation context
            
        Returns:
            Quality metrics dictionary
        """
        try:
            total_words = sum(len(section.content.split()) for section in sections)
            avg_words_per_section = total_words / max(len(sections), 1)
            
            # Quality factors
            quality_factors = {
                'content_length': 1.0 if 50 <= avg_words_per_section <= 200 else 0.7,
                'time_allocation': 1.0 if all(section.time_allocation > 0 for section in sections) else 0.8,
                'persona_adaptation': 1.0 if persona.get('experience_level') else 0.9,
                'language_consistency': 1.0,  # Assume consistent for now
                'technical_depth': 1.0 if context.get('technical_depth', 3) >= 2 else 0.8
            }
            
            overall_score = sum(quality_factors.values()) / len(quality_factors)
            
            return {
                'overall_score': overall_score,
                'total_words': total_words,
                'avg_words_per_section': avg_words_per_section,
                'quality_factors': quality_factors,
                'sections_count': len(sections)
            }
            
        except Exception as e:
            logger.error(f"Failed to assess script quality: {str(e)}")
            return {'overall_score': 0.5, 'error': str(e)}
    
    def format_script_as_markdown(self, script: GeneratedScript) -> str:
        """Format generated script as markdown.
        
        Args:
            script: Generated script object
            
        Returns:
            Formatted markdown string
        """
        try:
            markdown_parts = []
            
            # Add header
            markdown_parts.append(f"# {script.title}")
            markdown_parts.append(f"**Presenter**: {script.presenter_info['name']}, {script.presenter_info['title']}")
            markdown_parts.append(f"**Duration**: {script.total_duration} minutes")
            markdown_parts.append(f"**Language**: {script.language.title()}")
            markdown_parts.append("")
            
            # Add overview
            markdown_parts.append("## Overview")
            markdown_parts.append(script.overview)
            markdown_parts.append("")
            
            # Add sections
            for section in script.sections:
                markdown_parts.append(f"## Slide {section.slide_number}: {section.title}")
                markdown_parts.append(f"*Time: {section.time_allocation} minutes*")
                markdown_parts.append("")
                markdown_parts.append(section.content)
                
                if section.speaker_notes:
                    markdown_parts.append("")
                    markdown_parts.append("### Speaker Notes")
                    markdown_parts.append(section.speaker_notes)
                
                if section.key_points:
                    markdown_parts.append("")
                    markdown_parts.append("### Key Points")
                    for point in section.key_points:
                        markdown_parts.append(f"- {point}")
                
                markdown_parts.append("")
                markdown_parts.append("---")
                markdown_parts.append("")
            
            # Add conclusion
            markdown_parts.append("## Conclusion")
            markdown_parts.append(script.conclusion)
            markdown_parts.append("")
            
            # Add quality metrics
            markdown_parts.append("## Quality Metrics")
            markdown_parts.append(f"- Overall Score: {script.quality_metrics.get('overall_score', 0):.2f}")
            markdown_parts.append(f"- Total Words: {script.quality_metrics.get('total_words', 0)}")
            markdown_parts.append(f"- Sections: {script.quality_metrics.get('sections_count', 0)}")
            
            return "\n".join(markdown_parts)
            
        except Exception as e:
            logger.error(f"Failed to format script as markdown: {str(e)}")
            return f"# Script Generation Error\n\nFailed to format script: {str(e)}"
