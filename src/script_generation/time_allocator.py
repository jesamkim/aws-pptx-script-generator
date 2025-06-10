"""Time Allocation Algorithm.

This module provides intelligent time distribution across presentation slides
based on content complexity, importance, and presentation context.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import math
from loguru import logger

from src.analysis.multimodal_analyzer import SlideAnalysis, PresentationAnalysis
from src.utils.logger import log_execution_time


@dataclass
class TimeAllocation:
    """Time allocation for a single slide.
    
    Attributes:
        slide_number: Slide number
        allocated_time: Allocated time in minutes
        min_time: Minimum recommended time
        max_time: Maximum recommended time
        complexity_factor: Complexity-based factor
        importance_factor: Importance-based factor
        adjustment_reason: Reason for time adjustment
    """
    slide_number: int
    allocated_time: float
    min_time: float
    max_time: float
    complexity_factor: float
    importance_factor: float
    adjustment_reason: str


class TimeAllocator:
    """Intelligent time allocation algorithm for presentation slides."""
    
    def __init__(self):
        """Initialize time allocator with allocation rules."""
        # Base time allocations by slide type (in minutes)
        self.base_times = {
            'title': 1.5,
            'agenda': 2.0,
            'content': 3.0,
            'technical': 4.0,
            'architecture': 5.0,
            'demo': 6.0,
            'comparison': 3.5,
            'summary': 2.5,
            'conclusion': 2.0,
            'qa': 1.0
        }
        
        # Complexity multipliers
        self.complexity_multipliers = {
            1: 0.7,  # Very simple
            2: 0.85, # Simple
            3: 1.0,  # Moderate
            4: 1.3,  # Complex
            5: 1.6   # Very complex
        }
        
        # Audience level adjustments
        self.audience_adjustments = {
            'beginner': 1.3,
            'intermediate': 1.0,
            'advanced': 0.8,
            'expert': 0.7
        }
        
        logger.info("Initialized time allocator with allocation rules")
    
    @log_execution_time
    def calculate_time_allocations(
        self,
        presentation_analysis: PresentationAnalysis,
        total_duration: int,
        context: Dict[str, Any]
    ) -> Dict[int, TimeAllocation]:
        """Calculate optimal time allocations for all slides.
        
        Args:
            presentation_analysis: Complete presentation analysis
            total_duration: Total presentation duration in minutes
            context: Presentation context (audience, interaction level, etc.)
            
        Returns:
            Dictionary mapping slide numbers to TimeAllocation objects
        """
        try:
            slides = presentation_analysis.slide_analyses
            
            # Step 1: Calculate base allocations
            base_allocations = self._calculate_base_allocations(slides, context)
            
            # Step 2: Apply complexity adjustments
            complexity_allocations = self._apply_complexity_adjustments(
                base_allocations, slides
            )
            
            # Step 3: Apply importance weighting
            importance_allocations = self._apply_importance_weighting(
                complexity_allocations, slides, presentation_analysis
            )
            
            # Step 4: Normalize to total duration
            normalized_allocations = self._normalize_to_total_duration(
                importance_allocations, total_duration
            )
            
            # Step 5: Apply constraints and validate
            final_allocations = self._apply_constraints_and_validate(
                normalized_allocations, slides, total_duration, context
            )
            
            logger.info(f"Calculated time allocations for {len(slides)} slides, "
                       f"total: {sum(alloc.allocated_time for alloc in final_allocations.values()):.1f} minutes")
            
            return final_allocations
            
        except Exception as e:
            logger.error(f"Failed to calculate time allocations: {str(e)}")
            raise
    
    def _calculate_base_allocations(
        self,
        slides: List[SlideAnalysis],
        context: Dict[str, Any]
    ) -> Dict[int, float]:
        """Calculate base time allocations based on slide types.
        
        Args:
            slides: List of slide analyses
            context: Presentation context
            
        Returns:
            Dictionary mapping slide numbers to base times
        """
        base_allocations = {}
        
        for slide in slides:
            # Get base time for slide type
            slide_type = slide.slide_type.lower()
            base_time = self.base_times.get(slide_type, self.base_times['content'])
            
            # Adjust for audience level
            audience_level = context.get('target_audience', 'intermediate').lower()
            if audience_level in self.audience_adjustments:
                base_time *= self.audience_adjustments[audience_level]
            
            # Adjust for interaction level
            interaction_level = context.get('interaction_level', 'moderate').lower()
            if interaction_level == 'high':
                base_time *= 1.2
            elif interaction_level == 'minimal':
                base_time *= 0.9
            
            base_allocations[slide.slide_number] = base_time
        
        logger.debug(f"Calculated base allocations for {len(slides)} slides")
        return base_allocations
    
    def _apply_complexity_adjustments(
        self,
        base_allocations: Dict[int, float],
        slides: List[SlideAnalysis]
    ) -> Dict[int, float]:
        """Apply complexity-based adjustments to time allocations.
        
        Args:
            base_allocations: Base time allocations
            slides: List of slide analyses
            
        Returns:
            Complexity-adjusted allocations
        """
        complexity_allocations = {}
        
        for slide in slides:
            base_time = base_allocations[slide.slide_number]
            complexity = slide.technical_depth
            
            # Apply complexity multiplier
            multiplier = self.complexity_multipliers.get(complexity, 1.0)
            adjusted_time = base_time * multiplier
            
            complexity_allocations[slide.slide_number] = adjusted_time
        
        logger.debug("Applied complexity adjustments to time allocations")
        return complexity_allocations
    
    def _apply_importance_weighting(
        self,
        complexity_allocations: Dict[int, float],
        slides: List[SlideAnalysis],
        presentation_analysis: PresentationAnalysis
    ) -> Dict[int, float]:
        """Apply importance weighting based on slide significance.
        
        Args:
            complexity_allocations: Complexity-adjusted allocations
            slides: List of slide analyses
            presentation_analysis: Complete presentation analysis
            
        Returns:
            Importance-weighted allocations
        """
        importance_allocations = {}
        
        # Calculate importance scores
        importance_scores = self._calculate_importance_scores(slides, presentation_analysis)
        
        for slide in slides:
            adjusted_time = complexity_allocations[slide.slide_number]
            importance_score = importance_scores.get(slide.slide_number, 1.0)
            
            # Apply importance weighting (0.8 to 1.3 range)
            importance_factor = 0.8 + (importance_score * 0.5)
            weighted_time = adjusted_time * importance_factor
            
            importance_allocations[slide.slide_number] = weighted_time
        
        logger.debug("Applied importance weighting to time allocations")
        return importance_allocations
    
    def _calculate_importance_scores(
        self,
        slides: List[SlideAnalysis],
        presentation_analysis: PresentationAnalysis
    ) -> Dict[int, float]:
        """Calculate importance scores for slides.
        
        Args:
            slides: List of slide analyses
            presentation_analysis: Complete presentation analysis
            
        Returns:
            Dictionary mapping slide numbers to importance scores (0-1)
        """
        importance_scores = {}
        
        for slide in slides:
            score = 0.5  # Base score
            
            # Boost for key slide types
            if slide.slide_type in ['architecture', 'demo', 'technical']:
                score += 0.3
            elif slide.slide_type in ['title', 'agenda', 'summary']:
                score += 0.1
            
            # Boost for AWS service mentions
            if slide.aws_services:
                score += min(0.2, len(slide.aws_services) * 0.1)
            
            # Boost for key concepts
            if slide.key_concepts:
                score += min(0.2, len(slide.key_concepts) * 0.05)
            
            # Boost for high confidence analysis
            if slide.confidence_score > 0.8:
                score += 0.1
            
            # Normalize to 0-1 range
            importance_scores[slide.slide_number] = min(1.0, score)
        
        return importance_scores
    
    def _normalize_to_total_duration(
        self,
        importance_allocations: Dict[int, float],
        total_duration: int
    ) -> Dict[int, float]:
        """Normalize allocations to match total duration.
        
        Args:
            importance_allocations: Importance-weighted allocations
            total_duration: Target total duration
            
        Returns:
            Normalized allocations
        """
        # Calculate current total
        current_total = sum(importance_allocations.values())
        
        # Calculate normalization factor
        normalization_factor = total_duration / current_total
        
        # Apply normalization
        normalized_allocations = {}
        for slide_num, time_alloc in importance_allocations.items():
            normalized_allocations[slide_num] = time_alloc * normalization_factor
        
        logger.debug(f"Normalized allocations: {current_total:.1f} -> {total_duration} minutes")
        return normalized_allocations
    
    def _apply_constraints_and_validate(
        self,
        normalized_allocations: Dict[int, float],
        slides: List[SlideAnalysis],
        total_duration: int,
        context: Dict[str, Any]
    ) -> Dict[int, TimeAllocation]:
        """Apply constraints and validate final allocations.
        
        Args:
            normalized_allocations: Normalized time allocations
            slides: List of slide analyses
            total_duration: Total duration
            context: Presentation context
            
        Returns:
            Final TimeAllocation objects with constraints applied
        """
        final_allocations = {}
        adjustments_made = []
        
        for slide in slides:
            slide_num = slide.slide_number
            allocated_time = normalized_allocations[slide_num]
            
            # Calculate min/max constraints
            min_time, max_time = self._calculate_time_constraints(slide, context)
            
            # Apply constraints
            original_time = allocated_time
            allocated_time = max(min_time, min(max_time, allocated_time))
            
            # Track adjustments
            adjustment_reason = ""
            if allocated_time != original_time:
                if allocated_time == min_time:
                    adjustment_reason = f"Increased to minimum time ({min_time} min)"
                    adjustments_made.append(f"Slide {slide_num}: increased to minimum")
                elif allocated_time == max_time:
                    adjustment_reason = f"Reduced to maximum time ({max_time} min)"
                    adjustments_made.append(f"Slide {slide_num}: reduced to maximum")
            
            # Calculate factors for transparency
            complexity_factor = self.complexity_multipliers.get(slide.technical_depth, 1.0)
            importance_factor = 0.8 + (0.5 * min(1.0, slide.confidence_score))
            
            final_allocations[slide_num] = TimeAllocation(
                slide_number=slide_num,
                allocated_time=round(allocated_time, 1),
                min_time=min_time,
                max_time=max_time,
                complexity_factor=complexity_factor,
                importance_factor=importance_factor,
                adjustment_reason=adjustment_reason
            )
        
        # Final validation and rebalancing if needed
        total_allocated = sum(alloc.allocated_time for alloc in final_allocations.values())
        if abs(total_allocated - total_duration) > 0.5:  # Allow 0.5 minute tolerance
            final_allocations = self._rebalance_allocations(
                final_allocations, total_duration
            )
        
        if adjustments_made:
            logger.info(f"Applied constraints: {', '.join(adjustments_made)}")
        
        return final_allocations
    
    def _calculate_time_constraints(
        self,
        slide: SlideAnalysis,
        context: Dict[str, Any]
    ) -> Tuple[float, float]:
        """Calculate min/max time constraints for a slide.
        
        Args:
            slide: Slide analysis
            context: Presentation context
            
        Returns:
            Tuple of (min_time, max_time)
        """
        # Base constraints by slide type
        type_constraints = {
            'title': (0.5, 3.0),
            'agenda': (1.0, 4.0),
            'content': (1.5, 8.0),
            'technical': (2.0, 10.0),
            'architecture': (3.0, 12.0),
            'demo': (3.0, 15.0),
            'summary': (1.0, 5.0),
            'conclusion': (1.0, 4.0)
        }
        
        slide_type = slide.slide_type.lower()
        min_time, max_time = type_constraints.get(slide_type, (1.5, 8.0))
        
        # Adjust based on technical depth
        if slide.technical_depth >= 4:
            min_time *= 1.2
            max_time *= 1.3
        elif slide.technical_depth <= 2:
            min_time *= 0.8
            max_time *= 0.9
        
        # Adjust based on audience level
        audience_level = context.get('target_audience', 'intermediate').lower()
        if audience_level == 'beginner':
            min_time *= 1.2
            max_time *= 1.4
        elif audience_level == 'expert':
            min_time *= 0.8
            max_time *= 0.8
        
        return round(min_time, 1), round(max_time, 1)
    
    def _rebalance_allocations(
        self,
        allocations: Dict[int, TimeAllocation],
        target_duration: int
    ) -> Dict[int, TimeAllocation]:
        """Rebalance allocations to match target duration exactly.
        
        Args:
            allocations: Current allocations
            target_duration: Target total duration
            
        Returns:
            Rebalanced allocations
        """
        current_total = sum(alloc.allocated_time for alloc in allocations.values())
        difference = target_duration - current_total
        
        if abs(difference) < 0.1:  # Close enough
            return allocations
        
        # Distribute difference proportionally
        rebalanced = {}
        for slide_num, allocation in allocations.items():
            proportion = allocation.allocated_time / current_total
            adjustment = difference * proportion
            new_time = allocation.allocated_time + adjustment
            
            # Ensure constraints are still met
            new_time = max(allocation.min_time, min(allocation.max_time, new_time))
            
            rebalanced[slide_num] = TimeAllocation(
                slide_number=allocation.slide_number,
                allocated_time=round(new_time, 1),
                min_time=allocation.min_time,
                max_time=allocation.max_time,
                complexity_factor=allocation.complexity_factor,
                importance_factor=allocation.importance_factor,
                adjustment_reason=allocation.adjustment_reason + " (rebalanced)"
            )
        
        logger.debug(f"Rebalanced allocations: {current_total:.1f} -> {target_duration} minutes")
        return rebalanced
    
    def get_allocation_summary(
        self,
        allocations: Dict[int, TimeAllocation]
    ) -> Dict[str, Any]:
        """Generate summary of time allocations.
        
        Args:
            allocations: Time allocations
            
        Returns:
            Summary dictionary
        """
        try:
            total_time = sum(alloc.allocated_time for alloc in allocations.values())
            
            # Calculate distribution by time ranges
            time_distribution = {
                'short (< 2 min)': 0,
                'medium (2-5 min)': 0,
                'long (> 5 min)': 0
            }
            
            for allocation in allocations.values():
                if allocation.allocated_time < 2:
                    time_distribution['short (< 2 min)'] += 1
                elif allocation.allocated_time <= 5:
                    time_distribution['medium (2-5 min)'] += 1
                else:
                    time_distribution['long (> 5 min)'] += 1
            
            # Find slides with constraints applied
            constrained_slides = [
                alloc.slide_number for alloc in allocations.values()
                if alloc.adjustment_reason
            ]
            
            summary = {
                'total_slides': len(allocations),
                'total_time': round(total_time, 1),
                'average_time': round(total_time / len(allocations), 1),
                'time_distribution': time_distribution,
                'constrained_slides': constrained_slides,
                'min_time': min(alloc.allocated_time for alloc in allocations.values()),
                'max_time': max(alloc.allocated_time for alloc in allocations.values())
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate allocation summary: {str(e)}")
            return {}
