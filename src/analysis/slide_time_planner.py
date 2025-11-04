"""Intelligent Slide Time Planning Module.

This module uses Claude 3.7 Sonnet to analyze presentation structure
and dynamically allocate time for each slide based on content importance,
complexity, and slide type.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from loguru import logger
import json

from config.aws_config import bedrock_client
from src.utils.logger import log_execution_time


@dataclass
class SlideTimeAllocation:
    """Time allocation for a single slide.
    
    Attributes:
        slide_number: Slide number
        slide_type: Type of slide (title, agenda, content, etc.)
        importance_score: Importance score (1-10)
        complexity_score: Content complexity score (1-10)
        allocated_minutes: Allocated time in minutes
        rationale: Explanation for time allocation
    """
    slide_number: int
    slide_type: str
    importance_score: int
    complexity_score: int
    allocated_minutes: float
    rationale: str


@dataclass
class PresentationTimePlan:
    """Complete presentation time plan.
    
    Attributes:
        total_duration: Total presentation duration in minutes
        content_duration: Duration excluding Q&A
        slide_allocations: List of slide time allocations
        timing_strategy: Overall timing strategy description
        buffer_time: Reserved buffer time in minutes
    """
    total_duration: int
    content_duration: int
    slide_allocations: List[SlideTimeAllocation]
    timing_strategy: str
    buffer_time: float


class SlideTimePlanner:
    """Intelligent slide time planning using Claude 3.7 Sonnet."""
    
    def __init__(self):
        """Initialize slide time planner."""
        # Use the same model ID as the main script generator
        from config.aws_config import bedrock_client
        self.model_id = bedrock_client.config.bedrock_model_id
        logger.info(f"Initialized intelligent slide time planner with model: {self.model_id}")
    
    @log_execution_time
    def create_time_plan(self, 
                        presentation_analysis: Any,
                        total_duration: int,
                        qa_duration: int = 0,
                        buffer_percentage: float = 0.1) -> PresentationTimePlan:
        """Create intelligent time allocation plan for presentation.
        
        Args:
            presentation_analysis: Complete presentation analysis
            total_duration: Total presentation duration in minutes
            qa_duration: Q&A duration in minutes
            buffer_percentage: Percentage of time to reserve as buffer
            
        Returns:
            PresentationTimePlan with optimized time allocations
        """
        try:
            # Calculate available content time
            content_duration = total_duration - qa_duration
            buffer_time = content_duration * buffer_percentage
            effective_content_time = content_duration - buffer_time
            
            # Prepare slide information for Claude analysis
            slide_info = []
            for slide in presentation_analysis.slide_analyses:
                slide_info.append({
                    "slide_number": slide.slide_number,
                    "title": slide.content_summary[:100] if slide.content_summary else f"Slide {slide.slide_number}",
                    "content": slide.visual_description[:200] if slide.visual_description else "",
                    "key_concepts": slide.key_concepts[:5],
                    "aws_services": slide.aws_services[:3],
                    "text_length": len(slide.visual_description) if slide.visual_description else 0
                })
            
            # Create planning prompt
            planning_prompt = self._create_planning_prompt(
                slide_info=slide_info,
                total_slides=len(presentation_analysis.slide_analyses),
                effective_content_time=effective_content_time,
                presentation_theme=presentation_analysis.overall_theme,
                technical_complexity=presentation_analysis.technical_complexity
            )
            
            # Get time allocation plan from Claude
            response = self._invoke_claude_for_planning(planning_prompt)
            
            if response:
                # Parse Claude's response
                time_plan = self._parse_planning_response(
                    response=response,
                    total_duration=total_duration,
                    content_duration=content_duration,
                    buffer_time=buffer_time
                )
                
                logger.info(f"Created time plan with {len(time_plan.slide_allocations)} slide allocations")
                return time_plan
            else:
                # Fallback to equal distribution
                logger.warning("Claude planning failed, using fallback equal distribution")
                return self._create_fallback_plan(
                    presentation_analysis=presentation_analysis,
                    total_duration=total_duration,
                    content_duration=content_duration,
                    buffer_time=buffer_time
                )
                
        except Exception as e:
            logger.error(f"Time planning failed: {str(e)}")
            return self._create_fallback_plan(
                presentation_analysis=presentation_analysis,
                total_duration=total_duration,
                content_duration=content_duration,
                buffer_time=buffer_time
            )
    
    def _create_planning_prompt(self,
                              slide_info: List[Dict[str, Any]],
                              total_slides: int,
                              effective_content_time: float,
                              presentation_theme: str,
                              technical_complexity: float) -> str:
        """Create prompt for Claude time planning.
        
        Args:
            slide_info: Information about each slide
            total_slides: Total number of slides
            effective_content_time: Available content time in minutes
            presentation_theme: Overall presentation theme
            technical_complexity: Technical complexity score
            
        Returns:
            Planning prompt string
        """
        slides_json = json.dumps(slide_info, indent=2)
        
        prompt = f"""You are an expert presentation coach and time management specialist. Analyze the following presentation structure and create an optimal time allocation plan.

**Presentation Overview:**
- Theme: {presentation_theme}
- Total Slides: {total_slides}
- Available Content Time: {effective_content_time:.1f} minutes
- Technical Complexity: {technical_complexity:.1f}/5.0

**Slide Information:**
{slides_json}

**Your Task:**
Create a strategic time allocation plan that considers:

1. **Slide Types & Importance:**
   - Title/Cover slides: Quick introduction (0.5-1 minute)
   - Agenda/Overview slides: Brief outline (1-1.5 minutes)
   - Section dividers: Quick transition (0.5-1 minute)
   - Core content slides: Detailed explanation (2-4 minutes)
   - Technical deep-dive slides: Extended discussion (3-5 minutes)
   - Summary/Conclusion slides: Moderate time (1.5-2.5 minutes)

2. **Content Complexity:**
   - Simple concepts: Less time needed
   - Complex technical topics: More time required
   - AWS service explanations: Moderate to high time
   - Code examples or demos: Extended time

3. **Presentation Flow:**
   - Front-load important concepts
   - Allow more time for key messages
   - Maintain audience engagement rhythm
   - Build complexity gradually

**Output Format:**
Provide your response as a JSON object with this exact structure:

```json
{{
  "timing_strategy": "Brief description of your overall timing approach",
  "slide_allocations": [
    {{
      "slide_number": 1,
      "slide_type": "title|agenda|content|technical|summary|transition",
      "importance_score": 1-10,
      "complexity_score": 1-10,
      "allocated_minutes": 2.5,
      "rationale": "Explanation for this time allocation"
    }}
  ]
}}
```

**Important Guidelines:**
- Total allocated time should equal {effective_content_time:.1f} minutes
- Be realistic about what can be covered in each timeframe
- Consider audience attention span and engagement
- Prioritize key messages and technical concepts
- Ensure smooth pacing throughout presentation

Analyze each slide carefully and provide thoughtful time allocations."""

        return prompt
    
    def _invoke_claude_for_planning(self, prompt: str) -> Optional[str]:
        """Invoke Claude for time planning analysis.
        
        Args:
            prompt: Planning prompt
            
        Returns:
            Claude's response or None if failed
        """
        try:
            messages = [
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ]
            
            response = bedrock_client.client.converse(
                modelId=self.model_id,
                messages=messages,
                inferenceConfig={
                    "maxTokens": 4000,
                    "temperature": 0.3  # Lower temperature for more consistent planning
                }
            )
            
            if response and "output" in response:
                content = response["output"]["message"]["content"][0]["text"]
                return content
            
            return None
            
        except Exception as e:
            logger.error(f"Claude planning invocation failed: {str(e)}")
            return None
    
    def _parse_planning_response(self,
                               response: str,
                               total_duration: int,
                               content_duration: int,
                               buffer_time: float) -> PresentationTimePlan:
        """Parse Claude's planning response.
        
        Args:
            response: Claude's response text
            total_duration: Total presentation duration
            content_duration: Content duration excluding Q&A
            buffer_time: Reserved buffer time
            
        Returns:
            PresentationTimePlan object
        """
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                planning_data = json.loads(json_str)
                
                # Create slide allocations
                slide_allocations = []
                for allocation_data in planning_data.get("slide_allocations", []):
                    allocation = SlideTimeAllocation(
                        slide_number=allocation_data.get("slide_number", 1),
                        slide_type=allocation_data.get("slide_type", "content"),
                        importance_score=allocation_data.get("importance_score", 5),
                        complexity_score=allocation_data.get("complexity_score", 5),
                        allocated_minutes=float(allocation_data.get("allocated_minutes", 2.0)),
                        rationale=allocation_data.get("rationale", "Standard allocation")
                    )
                    slide_allocations.append(allocation)
                
                # Validate and adjust total time if needed
                total_allocated = sum(alloc.allocated_minutes for alloc in slide_allocations)
                target_time = content_duration - buffer_time
                
                if abs(total_allocated - target_time) > 0.5:  # If off by more than 30 seconds
                    # Proportionally adjust all allocations
                    adjustment_factor = target_time / total_allocated
                    for allocation in slide_allocations:
                        allocation.allocated_minutes *= adjustment_factor
                
                return PresentationTimePlan(
                    total_duration=total_duration,
                    content_duration=content_duration,
                    slide_allocations=slide_allocations,
                    timing_strategy=planning_data.get("timing_strategy", "Balanced time allocation"),
                    buffer_time=buffer_time
                )
            else:
                raise ValueError("No valid JSON found in response")
                
        except Exception as e:
            logger.error(f"Failed to parse planning response: {str(e)}")
            # Return fallback plan
            return self._create_simple_fallback_plan(total_duration, content_duration, buffer_time)
    
    def _create_fallback_plan(self,
                            presentation_analysis: Any,
                            total_duration: int,
                            content_duration: int,
                            buffer_time: float) -> PresentationTimePlan:
        """Create fallback time plan with equal distribution.
        
        Args:
            presentation_analysis: Presentation analysis
            total_duration: Total duration
            content_duration: Content duration
            buffer_time: Buffer time
            
        Returns:
            Fallback PresentationTimePlan
        """
        effective_time = content_duration - buffer_time
        num_slides = len(presentation_analysis.slide_analyses)
        time_per_slide = effective_time / num_slides if num_slides > 0 else 2.0
        
        slide_allocations = []
        for slide in presentation_analysis.slide_analyses:
            allocation = SlideTimeAllocation(
                slide_number=slide.slide_number,
                slide_type="content",
                importance_score=5,
                complexity_score=5,
                allocated_minutes=time_per_slide,
                rationale="Equal distribution fallback"
            )
            slide_allocations.append(allocation)
        
        return PresentationTimePlan(
            total_duration=total_duration,
            content_duration=content_duration,
            slide_allocations=slide_allocations,
            timing_strategy="Equal time distribution (fallback)",
            buffer_time=buffer_time
        )
    
    def _create_simple_fallback_plan(self,
                                   total_duration: int,
                                   content_duration: int,
                                   buffer_time: float) -> PresentationTimePlan:
        """Create simple fallback plan.
        
        Args:
            total_duration: Total duration
            content_duration: Content duration  
            buffer_time: Buffer time
            
        Returns:
            Simple fallback plan
        """
        return PresentationTimePlan(
            total_duration=total_duration,
            content_duration=content_duration,
            slide_allocations=[],
            timing_strategy="Fallback plan - manual timing required",
            buffer_time=buffer_time
        )
