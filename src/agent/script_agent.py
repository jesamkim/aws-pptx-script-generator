"""Script Generation Agent.

This module implements an intelligent agent for coordinating presentation
script generation with persona adaptation and quality control.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json
from loguru import logger

from .workflow_orchestrator import WorkflowOrchestrator, WorkflowDefinition, WorkflowTask
from src.analysis.multimodal_analyzer import MultimodalAnalyzer, SlideAnalysis
from src.mcp_integration.knowledge_enhancer import KnowledgeEnhancer, EnhancedContent
from src.utils.logger import log_execution_time, performance_monitor


@dataclass
class PersonaProfile:
    """SA persona profile for script customization.
    
    Attributes:
        full_name: SA full name
        job_title: Job title/role
        experience_level: Experience level (Junior, Senior, Principal, Distinguished)
        presentation_style: Preferred presentation style
        specializations: Areas of expertise
        language: Preferred language (Korean, English)
        cultural_context: Cultural presentation preferences
    """
    full_name: str
    job_title: str
    experience_level: str
    presentation_style: str
    specializations: List[str]
    language: str
    cultural_context: Dict[str, Any]


@dataclass
class PresentationContext:
    """Presentation context and requirements.
    
    Attributes:
        duration: Total presentation duration in minutes
        target_audience: Target audience type
        technical_depth: Technical depth level (1-5)
        interaction_level: Expected interaction level
        objectives: Presentation objectives
        constraints: Any constraints or requirements
    """
    duration: int
    target_audience: str
    technical_depth: int
    interaction_level: str
    objectives: List[str]
    constraints: Dict[str, Any]


@dataclass
class ScriptGenerationResult:
    """Result of script generation process.
    
    Attributes:
        success: Whether generation was successful
        script_content: Generated script content
        time_allocations: Time allocation per slide
        quality_score: Overall quality score (0-1)
        persona_adaptation: Persona adaptation details
        enhancement_summary: Content enhancement summary
        recommendations: Improvement recommendations
        metadata: Additional metadata
    """
    success: bool
    script_content: str
    time_allocations: Dict[int, float]
    quality_score: float
    persona_adaptation: Dict[str, Any]
    enhancement_summary: Dict[str, Any]
    recommendations: List[str]
    metadata: Dict[str, Any]


class ScriptAgent:
    """Intelligent agent for presentation script generation.
    
    This agent coordinates the complex process of generating personalized
    presentation scripts using multimodal AI analysis and MCP integration.
    """
    
    def __init__(self):
        """Initialize script generation agent."""
        self.orchestrator = WorkflowOrchestrator()
        self.multimodal_analyzer = MultimodalAnalyzer()
        self.knowledge_enhancer = KnowledgeEnhancer()
        
        # Register script generation workflow
        self._register_script_generation_workflow()
        
        logger.info("Initialized script generation agent")
    
    def _register_script_generation_workflow(self):
        """Register the script generation workflow."""
        try:
            # Define workflow tasks
            tasks = [
                WorkflowTask(
                    task_id="analyze_slides",
                    name="Multimodal Slide Analysis",
                    function=self._analyze_slides_task,
                    dependencies=[],
                    parameters={},
                    timeout=600  # 10 minutes
                ),
                WorkflowTask(
                    task_id="enhance_content",
                    name="AWS Content Enhancement",
                    function=self._enhance_content_task,
                    dependencies=["analyze_slides"],
                    parameters={},
                    timeout=300  # 5 minutes
                ),
                WorkflowTask(
                    task_id="allocate_time",
                    name="Time Allocation",
                    function=self._allocate_time_task,
                    dependencies=["analyze_slides"],
                    parameters={},
                    timeout=60  # 1 minute
                ),
                WorkflowTask(
                    task_id="generate_script",
                    name="Script Generation",
                    function=self._generate_script_task,
                    dependencies=["analyze_slides", "enhance_content", "allocate_time"],
                    parameters={},
                    timeout=600  # 10 minutes
                ),
                WorkflowTask(
                    task_id="quality_check",
                    name="Quality Assurance",
                    function=self._quality_check_task,
                    dependencies=["generate_script"],
                    parameters={},
                    timeout=120  # 2 minutes
                )
            ]
            
            # Create workflow definition
            workflow_def = WorkflowDefinition(
                workflow_id="script_generation",
                name="Presentation Script Generation",
                description="Complete workflow for generating personalized presentation scripts",
                tasks=tasks,
                max_parallel_tasks=3,
                total_timeout=1800  # 30 minutes
            )
            
            self.orchestrator.register_workflow(workflow_def)
            logger.info("Registered script generation workflow")
            
        except Exception as e:
            logger.error(f"Failed to register script generation workflow: {str(e)}")
            raise
    
    @log_execution_time
    def generate_script(
        self,
        slides_data: List[Tuple[int, bytes, List[str]]],
        persona: PersonaProfile,
        context: PresentationContext,
        progress_callback: Optional[callable] = None
    ) -> ScriptGenerationResult:
        """Generate presentation script using agent workflow.
        
        Args:
            slides_data: List of (slide_number, image_data, text_content)
            persona: SA persona profile
            context: Presentation context
            progress_callback: Progress update callback
            
        Returns:
            ScriptGenerationResult with generated script and metadata
        """
        performance_monitor.start_operation("generate_script")
        
        try:
            # Prepare workflow parameters
            workflow_params = {
                'slides_data': slides_data,
                'persona': persona,
                'context': context
            }
            
            # Execute workflow
            execution_id = self.orchestrator.execute_workflow(
                workflow_id="script_generation",
                parameters=workflow_params,
                progress_callback=progress_callback
            )
            
            # Wait for completion (in production, this would be async)
            result = self._wait_for_workflow_completion(execution_id)
            
            performance_monitor.end_operation("generate_script", result.success)
            logger.info(f"Script generation completed: success={result.success}")
            return result
            
        except Exception as e:
            performance_monitor.end_operation("generate_script", False)
            logger.error(f"Script generation failed: {str(e)}")
            return ScriptGenerationResult(
                success=False,
                script_content="",
                time_allocations={},
                quality_score=0.0,
                persona_adaptation={},
                enhancement_summary={},
                recommendations=[f"Generation failed: {str(e)}"],
                metadata={"error": str(e)}
            )
    
    def _wait_for_workflow_completion(self, execution_id: str) -> ScriptGenerationResult:
        """Wait for workflow completion and return results.
        
        Args:
            execution_id: Workflow execution ID
            
        Returns:
            ScriptGenerationResult with workflow results
        """
        import time
        
        # Poll for completion (simplified for demo)
        max_wait_time = 1800  # 30 minutes
        poll_interval = 5  # 5 seconds
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            status = self.orchestrator.get_workflow_status(execution_id)
            
            if not status:
                break
            
            if status['status'] in ['completed', 'failed', 'cancelled']:
                return self._process_workflow_results(execution_id, status)
            
            time.sleep(poll_interval)
            elapsed_time += poll_interval
        
        # Timeout
        return ScriptGenerationResult(
            success=False,
            script_content="",
            time_allocations={},
            quality_score=0.0,
            persona_adaptation={},
            enhancement_summary={},
            recommendations=["Workflow execution timed out"],
            metadata={"timeout": True}
        )
    
    def _process_workflow_results(self, execution_id: str, status: Dict[str, Any]) -> ScriptGenerationResult:
        """Process workflow results into ScriptGenerationResult.
        
        Args:
            execution_id: Workflow execution ID
            status: Workflow status
            
        Returns:
            ScriptGenerationResult with processed results
        """
        try:
            execution = self.orchestrator.active_workflows.get(execution_id)
            
            if not execution or status['status'] != 'completed':
                return ScriptGenerationResult(
                    success=False,
                    script_content="",
                    time_allocations={},
                    quality_score=0.0,
                    persona_adaptation={},
                    enhancement_summary={},
                    recommendations=status.get('errors', []),
                    metadata={"workflow_status": status['status']}
                )
            
            # Extract results from completed tasks
            results = execution.results
            
            script_content = results.get('generate_script', {}).get('script', '')
            time_allocations = results.get('allocate_time', {})
            quality_data = results.get('quality_check', {})
            enhancement_summary = results.get('enhance_content', {}).get('summary', {})
            
            return ScriptGenerationResult(
                success=True,
                script_content=script_content,
                time_allocations=time_allocations,
                quality_score=quality_data.get('score', 0.8),
                persona_adaptation=quality_data.get('persona_adaptation', {}),
                enhancement_summary=enhancement_summary,
                recommendations=quality_data.get('recommendations', []),
                metadata={
                    'execution_id': execution_id,
                    'duration': status.get('duration', 0),
                    'workflow_status': status['status']
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to process workflow results: {str(e)}")
            return ScriptGenerationResult(
                success=False,
                script_content="",
                time_allocations={},
                quality_score=0.0,
                persona_adaptation={},
                enhancement_summary={},
                recommendations=[f"Result processing failed: {str(e)}"],
                metadata={"error": str(e)}
            )
    
    def _analyze_slides_task(self, slides_data: List[Tuple], **kwargs) -> Dict[str, Any]:
        """Task: Analyze slides using multimodal AI.
        
        Args:
            slides_data: Slide data tuples
            **kwargs: Additional parameters
            
        Returns:
            Analysis results
        """
        try:
            logger.info(f"Starting multimodal analysis of {len(slides_data)} slides")
            
            # Perform multimodal analysis
            presentation_analysis = self.multimodal_analyzer.analyze_complete_presentation(slides_data)
            
            # Generate analysis summary
            analysis_summary = self.multimodal_analyzer.get_analysis_summary(presentation_analysis)
            
            return {
                'presentation_analysis': presentation_analysis,
                'analysis_summary': analysis_summary,
                'slide_count': len(slides_data)
            }
            
        except Exception as e:
            logger.error(f"Slide analysis task failed: {str(e)}")
            raise
    
    def _enhance_content_task(self, analyze_slides_result: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Task: Enhance content with AWS documentation.
        
        Args:
            analyze_slides_result: Results from slide analysis
            **kwargs: Additional parameters
            
        Returns:
            Enhancement results
        """
        try:
            presentation_analysis = analyze_slides_result['presentation_analysis']
            
            logger.info("Starting content enhancement with AWS documentation")
            
            # Extract slide content for enhancement
            slides_content = []
            for slide_analysis in presentation_analysis.slide_analyses:
                content = f"{slide_analysis.content_summary}\n{slide_analysis.visual_description}"
                slides_content.append(content)
            
            # Enhance content
            enhanced_contents = self.knowledge_enhancer.enhance_presentation_content(
                slides_content, enhancement_level="moderate"
            )
            
            # Generate enhancement summary
            enhancement_summary = self.knowledge_enhancer.get_enhancement_summary(enhanced_contents)
            
            return {
                'enhanced_contents': enhanced_contents,
                'summary': enhancement_summary
            }
            
        except Exception as e:
            logger.error(f"Content enhancement task failed: {str(e)}")
            raise
    
    def _allocate_time_task(self, analyze_slides_result: Dict[str, Any], context: PresentationContext, **kwargs) -> Dict[int, float]:
        """Task: Allocate time across slides.
        
        Args:
            analyze_slides_result: Results from slide analysis
            context: Presentation context
            **kwargs: Additional parameters
            
        Returns:
            Time allocations per slide
        """
        try:
            presentation_analysis = analyze_slides_result['presentation_analysis']
            total_duration = context.duration
            
            logger.info(f"Allocating {total_duration} minutes across {len(presentation_analysis.slide_analyses)} slides")
            
            # Calculate time allocations based on complexity and importance
            time_allocations = {}
            total_complexity = sum(analysis.technical_depth for analysis in presentation_analysis.slide_analyses)
            
            # Reserve time for introduction and conclusion
            reserved_time = min(total_duration * 0.2, 5)  # 20% or 5 minutes max
            available_time = total_duration - reserved_time
            
            for analysis in presentation_analysis.slide_analyses:
                # Base allocation on complexity
                complexity_ratio = analysis.technical_depth / max(total_complexity, 1)
                base_time = available_time * complexity_ratio
                
                # Adjust based on slide type
                if analysis.slide_type == 'title':
                    allocated_time = min(base_time, 2.0)
                elif analysis.slide_type == 'summary':
                    allocated_time = min(base_time, 3.0)
                elif analysis.slide_type == 'demo':
                    allocated_time = base_time * 1.5  # More time for demos
                else:
                    allocated_time = base_time
                
                # Ensure minimum time
                allocated_time = max(allocated_time, 1.0)
                
                time_allocations[analysis.slide_number] = round(allocated_time, 1)
            
            # Normalize to match total duration
            total_allocated = sum(time_allocations.values())
            if total_allocated != total_duration:
                adjustment_factor = total_duration / total_allocated
                for slide_num in time_allocations:
                    time_allocations[slide_num] = round(
                        time_allocations[slide_num] * adjustment_factor, 1
                    )
            
            return time_allocations
            
        except Exception as e:
            logger.error(f"Time allocation task failed: {str(e)}")
            raise
    
    def _generate_script_task(
        self,
        analyze_slides_result: Dict[str, Any],
        enhance_content_result: Dict[str, Any],
        allocate_time_result: Dict[int, float],
        persona: PersonaProfile,
        context: PresentationContext,
        **kwargs
    ) -> Dict[str, Any]:
        """Task: Generate presentation script.
        
        Args:
            analyze_slides_result: Analysis results
            enhance_content_result: Enhancement results
            allocate_time_result: Time allocations
            persona: SA persona
            context: Presentation context
            **kwargs: Additional parameters
            
        Returns:
            Generated script and metadata
        """
        try:
            presentation_analysis = analyze_slides_result['presentation_analysis']
            enhanced_contents = enhance_content_result['enhanced_contents']
            time_allocations = allocate_time_result
            
            logger.info("Generating personalized presentation script")
            
            # Generate script content
            script_parts = []
            
            # Add presentation header
            script_parts.append(self._generate_script_header(persona, context))
            
            # Generate script for each slide
            for i, slide_analysis in enumerate(presentation_analysis.slide_analyses):
                slide_number = slide_analysis.slide_number
                allocated_time = time_allocations.get(slide_number, 2.0)
                enhanced_content = enhanced_contents[i] if i < len(enhanced_contents) else None
                
                slide_script = self._generate_slide_script(
                    slide_analysis, enhanced_content, allocated_time, persona, context
                )
                script_parts.append(slide_script)
            
            # Add presentation footer
            script_parts.append(self._generate_script_footer(persona, context))
            
            # Combine all parts
            full_script = "\n\n".join(script_parts)
            
            return {
                'script': full_script,
                'slide_count': len(presentation_analysis.slide_analyses),
                'total_duration': sum(time_allocations.values()),
                'language': persona.language
            }
            
        except Exception as e:
            logger.error(f"Script generation task failed: {str(e)}")
            raise
    
    def _quality_check_task(self, generate_script_result: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Task: Perform quality assurance on generated script.
        
        Args:
            generate_script_result: Script generation results
            **kwargs: Additional parameters
            
        Returns:
            Quality assessment results
        """
        try:
            script = generate_script_result['script']
            
            logger.info("Performing quality check on generated script")
            
            # Basic quality metrics
            word_count = len(script.split())
            slide_count = generate_script_result['slide_count']
            avg_words_per_slide = word_count / max(slide_count, 1)
            
            # Quality score calculation
            quality_factors = {
                'length_appropriate': 1.0 if 50 <= avg_words_per_slide <= 200 else 0.7,
                'structure_present': 1.0 if '##' in script else 0.8,
                'time_mentions': 1.0 if 'minute' in script.lower() else 0.9,
                'persona_elements': 1.0 if any(word in script.lower() 
                    for word in ['experience', 'recommend', 'suggest']) else 0.8
            }
            
            quality_score = sum(quality_factors.values()) / len(quality_factors)
            
            # Generate recommendations
            recommendations = []
            if avg_words_per_slide < 50:
                recommendations.append("Consider adding more detail to slide scripts")
            elif avg_words_per_slide > 200:
                recommendations.append("Consider condensing slide scripts for better pacing")
            
            if quality_score < 0.8:
                recommendations.append("Review script for completeness and flow")
            
            return {
                'score': quality_score,
                'word_count': word_count,
                'avg_words_per_slide': avg_words_per_slide,
                'quality_factors': quality_factors,
                'recommendations': recommendations,
                'persona_adaptation': {
                    'language': generate_script_result.get('language', 'English'),
                    'style_applied': True
                }
            }
            
        except Exception as e:
            logger.error(f"Quality check task failed: {str(e)}")
            raise
    
    def _generate_script_header(self, persona: PersonaProfile, context: PresentationContext) -> str:
        """Generate script header with presentation introduction.
        
        Args:
            persona: SA persona profile
            context: Presentation context
            
        Returns:
            Script header content
        """
        if persona.language.lower() == 'korean':
            return f"""# {persona.full_name}의 프레젠테이션 스크립트

## 프레젠테이션 개요
- **발표자**: {persona.full_name}, {persona.job_title}
- **소요 시간**: {context.duration}분
- **대상 청중**: {context.target_audience}
- **기술 수준**: {context.technical_depth}/5

## 발표 시작

안녕하세요, 여러분. 저는 {persona.full_name}이고, {persona.job_title}로 근무하고 있습니다. 
오늘 {context.duration}분 동안 여러분과 함께 AWS 솔루션에 대해 알아보는 시간을 갖겠습니다."""
        else:
            return f"""# Presentation Script for {persona.full_name}

## Presentation Overview
- **Presenter**: {persona.full_name}, {persona.job_title}
- **Duration**: {context.duration} minutes
- **Audience**: {context.target_audience}
- **Technical Level**: {context.technical_depth}/5

## Opening

Good morning/afternoon, everyone. My name is {persona.full_name}, and I'm a {persona.job_title} here at AWS. 
Today, I'll be spending the next {context.duration} minutes with you exploring AWS solutions that can help transform your business."""
    
    def _generate_slide_script(
        self,
        slide_analysis: SlideAnalysis,
        enhanced_content: Optional[EnhancedContent],
        allocated_time: float,
        persona: PersonaProfile,
        context: PresentationContext
    ) -> str:
        """Generate script for individual slide.
        
        Args:
            slide_analysis: Slide analysis results
            enhanced_content: Enhanced content (if available)
            allocated_time: Time allocated for this slide
            persona: SA persona profile
            context: Presentation context
            
        Returns:
            Slide script content
        """
        slide_num = slide_analysis.slide_number
        
        if persona.language.lower() == 'korean':
            script = f"""## 슬라이드 {slide_num}: {slide_analysis.content_summary[:50]}... ({allocated_time}분)

{slide_analysis.content_summary}

{slide_analysis.visual_description}"""
            
            if enhanced_content and enhanced_content.best_practices:
                script += f"\n\n**모범 사례**: {enhanced_content.best_practices[0]}"
                
        else:
            script = f"""## Slide {slide_num}: {slide_analysis.content_summary[:50]}... ({allocated_time} minutes)

{slide_analysis.content_summary}

{slide_analysis.visual_description}"""
            
            if enhanced_content and enhanced_content.best_practices:
                script += f"\n\n**Best Practice**: {enhanced_content.best_practices[0]}"
        
        return script
    
    def _generate_script_footer(self, persona: PersonaProfile, context: PresentationContext) -> str:
        """Generate script footer with conclusion.
        
        Args:
            persona: SA persona profile
            context: Presentation context
            
        Returns:
            Script footer content
        """
        if persona.language.lower() == 'korean':
            return """## 마무리

오늘 발표를 통해 AWS 솔루션이 어떻게 여러분의 비즈니스 목표 달성에 도움이 될 수 있는지 보여드렸습니다. 
질문이 있으시면 언제든지 말씀해 주세요. 감사합니다."""
        else:
            return """## Conclusion

Today, we've explored how AWS solutions can help you achieve your business objectives with greater efficiency, security, and scale. 
I'm happy to take any questions you might have. Thank you for your time and attention."""


# Global script agent instance
script_agent = ScriptAgent()
