"""Optimized Script Generation Agent.

This module implements an enhanced intelligent agent for coordinating presentation
script generation with improved performance, caching, and monitoring capabilities.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import json
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger

from .workflow_orchestrator import WorkflowOrchestrator, WorkflowDefinition, WorkflowTask
from src.analysis.multimodal_analyzer import MultimodalAnalyzer, SlideAnalysis
from src.mcp_integration.knowledge_enhancer import KnowledgeEnhancer, EnhancedContent
from src.script_generation.claude_script_generator_cached import ClaudeScriptGeneratorCached
from src.utils.logger import log_execution_time, performance_monitor


@dataclass
class AgentPerformanceMetrics:
    """Agent performance tracking metrics.
    
    Attributes:
        total_executions: Total number of executions
        successful_executions: Number of successful executions
        failed_executions: Number of failed executions
        average_execution_time: Average execution time in seconds
        cache_hit_rate: Cache hit rate percentage
        quality_scores: List of quality scores
        error_patterns: Common error patterns
    """
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    average_execution_time: float = 0.0
    cache_hit_rate: float = 0.0
    quality_scores: List[float] = field(default_factory=list)
    error_patterns: Dict[str, int] = field(default_factory=dict)


@dataclass
class OptimizedPersonaProfile:
    """Enhanced SA persona profile with optimization features.
    
    Attributes:
        full_name: SA full name
        job_title: Job title/role
        experience_level: Experience level (Junior, Senior, Principal, Distinguished)
        presentation_style: Preferred presentation style
        specializations: Areas of expertise
        language: Preferred language (Korean, English)
        cultural_context: Cultural presentation preferences
        optimization_preferences: Agent optimization preferences
        historical_performance: Historical performance data
    """
    full_name: str
    job_title: str
    experience_level: str
    presentation_style: str
    specializations: List[str]
    language: str
    cultural_context: Dict[str, Any]
    optimization_preferences: Dict[str, Any] = field(default_factory=dict)
    historical_performance: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnhancedScriptGenerationResult:
    """Enhanced result of script generation process.
    
    Attributes:
        success: Whether generation was successful
        script_content: Generated script content
        time_allocations: Time allocation per slide
        quality_score: Overall quality score (0-1)
        persona_adaptation: Persona adaptation details
        enhancement_summary: Content enhancement summary
        recommendations: Improvement recommendations
        metadata: Additional metadata
        performance_metrics: Execution performance metrics
        cache_performance: Cache performance data
        optimization_suggestions: Agent optimization suggestions
    """
    success: bool
    script_content: str
    time_allocations: Dict[int, float]
    quality_score: float
    persona_adaptation: Dict[str, Any]
    enhancement_summary: Dict[str, Any]
    recommendations: List[str]
    metadata: Dict[str, Any]
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    cache_performance: Dict[str, Any] = field(default_factory=dict)
    optimization_suggestions: List[str] = field(default_factory=list)


class OptimizedScriptAgent:
    """Enhanced intelligent agent for presentation script generation.
    
    This agent provides improved performance through caching, parallel processing,
    and intelligent workflow optimization.
    """
    
    def __init__(self, enable_caching: bool = True, max_workers: int = 4):
        """Initialize optimized script generation agent.
        
        Args:
            enable_caching: Whether to enable caching optimizations
            max_workers: Maximum number of parallel workers
        """
        self.enable_caching = enable_caching
        self.max_workers = max_workers
        
        # Initialize core components
        self.orchestrator = WorkflowOrchestrator()
        self.multimodal_analyzer = MultimodalAnalyzer()
        self.knowledge_enhancer = KnowledgeEnhancer()
        self.script_generator = ClaudeScriptGeneratorCached(enable_caching=enable_caching)
        
        # Performance tracking
        self.performance_metrics = AgentPerformanceMetrics()
        self.execution_history = []
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Register optimized workflows
        self._register_optimized_workflows()
        
        logger.info(f"Initialized optimized script agent with caching: {enable_caching}, workers: {max_workers}")
    
    def _register_optimized_workflows(self):
        """Register optimized workflow definitions."""
        # Parallel script generation workflow
        parallel_workflow = WorkflowDefinition(
            workflow_id="parallel_script_generation",
            name="Parallel Script Generation",
            description="Generate scripts with parallel processing optimization",
            tasks=[
                WorkflowTask(
                    task_id="analyze_presentation",
                    name="Analyze Presentation Content",
                    function=self._analyze_presentation_parallel,
                    dependencies=[],
                    parameters={},
                    timeout=300
                ),
                WorkflowTask(
                    task_id="enhance_knowledge",
                    name="Enhance with MCP Knowledge",
                    function=self._enhance_knowledge_parallel,
                    dependencies=["analyze_presentation"],
                    parameters={},
                    timeout=180
                ),
                WorkflowTask(
                    task_id="generate_script",
                    name="Generate Script with Caching",
                    function=self._generate_script_cached,
                    dependencies=["analyze_presentation", "enhance_knowledge"],
                    parameters={},
                    timeout=600
                ),
                WorkflowTask(
                    task_id="quality_assessment",
                    name="Assess Script Quality",
                    function=self._assess_script_quality,
                    dependencies=["generate_script"],
                    parameters={},
                    timeout=120
                )
            ],
            max_parallel_tasks=3
        )
        
        self.orchestrator.register_workflow(parallel_workflow)
    
    @log_execution_time
    async def generate_script_optimized(self,
                                      presentation_analysis: Any,
                                      persona_profile: OptimizedPersonaProfile,
                                      presentation_params: Dict[str, Any],
                                      mcp_enhanced_services: Optional[Dict[str, Any]] = None) -> EnhancedScriptGenerationResult:
        """Generate presentation script with optimizations.
        
        Args:
            presentation_analysis: Presentation analysis data
            persona_profile: Enhanced persona profile
            presentation_params: Presentation parameters
            mcp_enhanced_services: Enhanced AWS service information
            
        Returns:
            Enhanced script generation result
        """
        start_time = time.time()
        execution_id = f"exec_{int(start_time)}"
        
        try:
            # Update performance metrics
            self.performance_metrics.total_executions += 1
            
            # Prepare workflow context
            workflow_context = {
                "presentation_analysis": presentation_analysis,
                "persona_profile": persona_profile,
                "presentation_params": presentation_params,
                "mcp_enhanced_services": mcp_enhanced_services,
                "execution_id": execution_id
            }
            
            # Execute optimized workflow
            workflow_result = await self.orchestrator.execute_workflow_async(
                workflow_id="parallel_script_generation",
                context=workflow_context
            )
            
            if workflow_result.status.value == "completed":
                # Extract results
                script_content = workflow_result.results.get("generate_script", {}).get("script_content", "")
                quality_score = workflow_result.results.get("quality_assessment", {}).get("quality_score", 0.0)
                
                # Get cache performance
                cache_performance = self.script_generator.get_cache_performance()
                
                # Calculate execution metrics
                execution_time = time.time() - start_time
                self._update_performance_metrics(execution_time, quality_score, True)
                
                # Generate optimization suggestions
                optimization_suggestions = self._generate_optimization_suggestions(
                    execution_time, cache_performance, quality_score
                )
                
                result = EnhancedScriptGenerationResult(
                    success=True,
                    script_content=script_content,
                    time_allocations=workflow_result.results.get("analyze_presentation", {}).get("time_allocations", {}),
                    quality_score=quality_score,
                    persona_adaptation=workflow_result.results.get("generate_script", {}).get("persona_adaptation", {}),
                    enhancement_summary=workflow_result.results.get("enhance_knowledge", {}).get("enhancement_summary", {}),
                    recommendations=workflow_result.results.get("quality_assessment", {}).get("recommendations", []),
                    metadata={
                        "execution_id": execution_id,
                        "execution_time": execution_time,
                        "workflow_status": workflow_result.status.value
                    },
                    performance_metrics={
                        "execution_time": execution_time,
                        "parallel_tasks": len(workflow_result.task_results),
                        "cache_enabled": self.enable_caching
                    },
                    cache_performance=cache_performance,
                    optimization_suggestions=optimization_suggestions
                )
                
                self.performance_metrics.successful_executions += 1
                logger.info(f"Script generation completed successfully in {execution_time:.2f}s")
                
            else:
                # Handle workflow failure
                self._update_performance_metrics(time.time() - start_time, 0.0, False)
                result = EnhancedScriptGenerationResult(
                    success=False,
                    script_content="",
                    time_allocations={},
                    quality_score=0.0,
                    persona_adaptation={},
                    enhancement_summary={},
                    recommendations=[],
                    metadata={
                        "execution_id": execution_id,
                        "error": "Workflow execution failed",
                        "workflow_status": workflow_result.status.value
                    }
                )
                
                self.performance_metrics.failed_executions += 1
                logger.error(f"Script generation workflow failed: {workflow_result.status}")
            
            # Store execution history
            self.execution_history.append({
                "execution_id": execution_id,
                "timestamp": start_time,
                "success": result.success,
                "execution_time": time.time() - start_time,
                "quality_score": result.quality_score
            })
            
            return result
            
        except Exception as e:
            self._update_performance_metrics(time.time() - start_time, 0.0, False)
            self.performance_metrics.failed_executions += 1
            
            logger.error(f"Script generation failed: {str(e)}")
            
            return EnhancedScriptGenerationResult(
                success=False,
                script_content="",
                time_allocations={},
                quality_score=0.0,
                persona_adaptation={},
                enhancement_summary={},
                recommendations=[],
                metadata={
                    "execution_id": execution_id,
                    "error": str(e)
                }
            )
    
    def _analyze_presentation_parallel(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze presentation with parallel processing optimizations."""
        presentation_analysis = context.get("presentation_analysis")
        if not presentation_analysis:
            raise ValueError("Missing presentation_analysis in context")
        
        # Parallel slide analysis
        slide_analyses = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_slide = {
                executor.submit(self._analyze_single_slide, slide): slide 
                for slide in presentation_analysis.slide_analyses
            }
            
            for future in as_completed(future_to_slide):
                slide = future_to_slide[future]
                try:
                    analysis_result = future.result()
                    slide_analyses.append(analysis_result)
                except Exception as e:
                    logger.error(f"Slide analysis failed for slide {slide.slide_number}: {str(e)}")
        
        # Calculate time allocations
        time_allocations = self._calculate_optimized_time_allocations(
            slide_analyses, context.get("presentation_params", {})
        )
        
        return {
            "slide_analyses": slide_analyses,
            "time_allocations": time_allocations,
            "analysis_metadata": {
                "parallel_processing": True,
                "slides_processed": len(slide_analyses)
            }
        }
    
    def _enhance_knowledge_parallel(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance knowledge with parallel MCP processing."""
        presentation_analysis = context.get("presentation_analysis")
        if not presentation_analysis:
            logger.warning("Missing presentation_analysis in context, skipping knowledge enhancement")
            return {
                "enhanced_services": {},
                "enhancement_summary": {
                    "services_enhanced": 0,
                    "parallel_processing": True,
                    "skipped_reason": "No presentation analysis provided"
                }
            }
        
        # Extract AWS services for parallel enhancement
        aws_services = set()
        try:
            for slide in presentation_analysis.slide_analyses:
                if hasattr(slide, 'aws_services'):
                    aws_services.update(slide.aws_services)
        except Exception as e:
            logger.warning(f"Failed to extract AWS services: {str(e)}")
            aws_services = set()
        
        # Parallel knowledge enhancement
        enhanced_services = {}
        if aws_services:
            with ThreadPoolExecutor(max_workers=min(len(aws_services), self.max_workers)) as executor:
                future_to_service = {
                    executor.submit(self._enhance_single_service, service): service
                    for service in aws_services
                }
                
                for future in as_completed(future_to_service):
                    service = future_to_service[future]
                    try:
                        enhancement = future.result()
                        if enhancement:
                            enhanced_services[service] = enhancement
                    except Exception as e:
                        logger.error(f"Knowledge enhancement failed for {service}: {str(e)}")
        
        return {
            "enhanced_services": enhanced_services,
            "enhancement_summary": {
                "services_enhanced": len(enhanced_services),
                "parallel_processing": True,
                "total_services_found": len(aws_services)
            }
        }
    
    def _enhance_single_service(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Enhance knowledge for a single AWS service.
        
        Args:
            service_name: Name of AWS service
            
        Returns:
            Enhanced service information or None if failed
        """
        try:
            # Use the knowledge enhancer's method
            if hasattr(self.knowledge_enhancer, 'enhance_service_knowledge'):
                return self.knowledge_enhancer.enhance_service_knowledge(service_name)
            else:
                # Fallback to basic enhancement
                return {
                    "service_name": service_name,
                    "description": f"AWS {service_name} service",
                    "use_cases": [],
                    "best_practices": [],
                    "related_services": []
                }
        except Exception as e:
            logger.error(f"Failed to enhance service {service_name}: {str(e)}")
            return None
    
    def _generate_script_cached(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate script using cached Claude generator."""
        presentation_analysis = context.get("presentation_analysis")
        persona_profile = context.get("persona_profile")
        presentation_params = context.get("presentation_params")
        mcp_enhanced_services = context.get("mcp_enhanced_services")
        
        if not all([presentation_analysis, persona_profile, presentation_params]):
            raise ValueError("Missing required context parameters")
        
        # Convert persona profile to dict format
        persona_data = {
            "full_name": persona_profile.full_name,
            "job_title": persona_profile.job_title,
            "experience_level": persona_profile.experience_level,
            "presentation_confidence": persona_profile.optimization_preferences.get("confidence", "Comfortable"),
            "interaction_style": persona_profile.presentation_style
        }
        
        # Generate script with caching
        script_content = self.script_generator.generate_complete_presentation_script(
            presentation_analysis=presentation_analysis,
            persona_data=persona_data,
            presentation_params=presentation_params,
            mcp_enhanced_services=mcp_enhanced_services
        )
        
        return {
            "script_content": script_content,
            "persona_adaptation": {
                "style_applied": persona_profile.presentation_style,
                "experience_level": persona_profile.experience_level,
                "language": persona_profile.language
            },
            "generation_metadata": {
                "caching_enabled": self.enable_caching,
                "script_length": len(script_content)
            }
        }
    
    def _assess_script_quality(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess generated script quality."""
        # Get script content from previous task results
        task_results = context.get("task_results", {})
        generate_script_result = task_results.get("generate_script", {})
        script_content = generate_script_result.get("script_content", "")
        
        presentation_params = context.get("presentation_params", {})
        
        # Quality assessment metrics
        word_count = len(script_content.split())
        target_duration = presentation_params.get("duration", 30)
        estimated_time = word_count / 165  # words per minute
        
        # Calculate quality score
        time_accuracy = 1.0 - min(abs(estimated_time - target_duration) / target_duration, 1.0)
        content_completeness = min(word_count / (target_duration * 100), 1.0)  # ~100 words per minute target
        
        quality_score = (time_accuracy * 0.4 + content_completeness * 0.6)
        
        # Generate recommendations
        recommendations = []
        if time_accuracy < 0.8:
            if estimated_time > target_duration:
                recommendations.append("Consider shortening the script to match target duration")
            else:
                recommendations.append("Consider adding more detail to reach target duration")
        
        if content_completeness < 0.7:
            recommendations.append("Script may be too brief for the allocated time")
        
        return {
            "quality_score": quality_score,
            "time_accuracy": time_accuracy,
            "content_completeness": content_completeness,
            "recommendations": recommendations,
            "assessment_metadata": {
                "word_count": word_count,
                "estimated_time": estimated_time,
                "target_duration": target_duration
            }
        }
    
    def _analyze_single_slide(self, slide_analysis: SlideAnalysis) -> Dict[str, Any]:
        """Analyze a single slide with optimizations."""
        return {
            "slide_number": slide_analysis.slide_number,
            "content_summary": slide_analysis.content_summary,
            "key_concepts": slide_analysis.key_concepts,
            "aws_services": slide_analysis.aws_services,
            "complexity_score": len(slide_analysis.key_concepts) + len(slide_analysis.aws_services)
        }
    
    def _calculate_optimized_time_allocations(self, 
                                           slide_analyses: List[Dict[str, Any]], 
                                           presentation_params: Dict[str, Any]) -> Dict[int, float]:
        """Calculate optimized time allocations for slides."""
        duration = presentation_params.get("duration", 30)
        qa_duration = presentation_params.get("qa_duration", 0) if presentation_params.get("include_qa", False) else 0
        content_duration = duration - qa_duration
        
        # Calculate complexity-based time allocation
        total_complexity = sum(slide.get("complexity_score", 1) for slide in slide_analyses)
        
        time_allocations = {}
        for slide in slide_analyses:
            complexity_ratio = slide.get("complexity_score", 1) / total_complexity
            allocated_time = content_duration * complexity_ratio
            time_allocations[slide["slide_number"]] = max(allocated_time, 1.0)  # Minimum 1 minute
        
        return time_allocations
    
    def _update_performance_metrics(self, execution_time: float, quality_score: float, success: bool):
        """Update agent performance metrics."""
        # Update average execution time
        total_time = (self.performance_metrics.average_execution_time * 
                     (self.performance_metrics.total_executions - 1) + execution_time)
        self.performance_metrics.average_execution_time = total_time / self.performance_metrics.total_executions
        
        # Update quality scores
        if success:
            self.performance_metrics.quality_scores.append(quality_score)
        
        # Update cache hit rate if caching is enabled
        if self.enable_caching:
            cache_stats = self.script_generator.get_cache_performance()
            total_requests = cache_stats.get('hits', 0) + cache_stats.get('misses', 0)
            if total_requests > 0:
                self.performance_metrics.cache_hit_rate = (cache_stats.get('hits', 0) / total_requests) * 100
    
    def _generate_optimization_suggestions(self, 
                                         execution_time: float, 
                                         cache_performance: Dict[str, Any], 
                                         quality_score: float) -> List[str]:
        """Generate optimization suggestions based on performance."""
        suggestions = []
        
        # Execution time optimization
        if execution_time > 60:  # More than 1 minute
            suggestions.append("Consider enabling more parallel processing to reduce execution time")
        
        # Cache optimization
        if self.enable_caching:
            hit_rate = cache_performance.get('hits', 0) / max(
                cache_performance.get('hits', 0) + cache_performance.get('misses', 0), 1
            ) * 100
            
            if hit_rate < 50:
                suggestions.append("Low cache hit rate detected. Consider optimizing prompt structure for better reuse")
        else:
            suggestions.append("Enable caching to improve performance and reduce costs")
        
        # Quality optimization
        if quality_score < 0.7:
            suggestions.append("Script quality could be improved. Consider refining presentation parameters")
        
        return suggestions
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        avg_quality = sum(self.performance_metrics.quality_scores) / len(self.performance_metrics.quality_scores) if self.performance_metrics.quality_scores else 0
        
        return {
            "total_executions": self.performance_metrics.total_executions,
            "success_rate": (self.performance_metrics.successful_executions / max(self.performance_metrics.total_executions, 1)) * 100,
            "average_execution_time": self.performance_metrics.average_execution_time,
            "average_quality_score": avg_quality,
            "cache_hit_rate": self.performance_metrics.cache_hit_rate,
            "optimization_enabled": {
                "caching": self.enable_caching,
                "parallel_processing": self.max_workers > 1
            }
        }
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)
