#!/usr/bin/env python3
"""Test Dynamic Slide Timing Allocation.

This script tests the intelligent slide time planning functionality
using Claude 3.7 Sonnet for dynamic time allocation.
"""

import sys
import os
from typing import Dict, Any
from loguru import logger

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_mock_presentation_analysis():
    """Create mock presentation analysis for testing."""
    class MockSlideAnalysis:
        def __init__(self, slide_number: int, slide_type: str, content: str):
            self.slide_number = slide_number
            self.content_summary = f"{slide_type.title()} Slide {slide_number}"
            self.visual_description = content
            self.key_concepts = ["concept1", "concept2", "concept3"]
            self.aws_services = ["Lambda", "S3"] if "technical" in slide_type else []
    
    class MockPresentationAnalysis:
        def __init__(self):
            self.overall_theme = "AWS Serverless Architecture Best Practices"
            self.technical_complexity = 4.2
            self.slide_analyses = [
                MockSlideAnalysis(1, "title", "Title slide with presenter introduction"),
                MockSlideAnalysis(2, "agenda", "Agenda and overview of topics to be covered"),
                MockSlideAnalysis(3, "technical", "Deep dive into AWS Lambda functions and best practices with code examples"),
                MockSlideAnalysis(4, "technical", "Amazon S3 storage patterns and optimization strategies"),
                MockSlideAnalysis(5, "content", "Integration patterns between Lambda and S3"),
                MockSlideAnalysis(6, "technical", "Monitoring and observability with CloudWatch"),
                MockSlideAnalysis(7, "content", "Cost optimization strategies"),
                MockSlideAnalysis(8, "summary", "Key takeaways and recommendations"),
                MockSlideAnalysis(9, "transition", "Questions and next steps")
            ]
    
    return MockPresentationAnalysis()

def test_slide_time_planner():
    """Test the SlideTimePlanner functionality."""
    print("🕐 Testing Intelligent Slide Time Planning...")
    
    try:
        from src.analysis.slide_time_planner import SlideTimePlanner
        
        # Initialize planner
        planner = SlideTimePlanner()
        print("✅ SlideTimePlanner initialized")
        
        # Create mock presentation
        presentation_analysis = create_mock_presentation_analysis()
        
        # Test time planning
        print("   Creating time plan for 25-minute presentation...")
        time_plan = planner.create_time_plan(
            presentation_analysis=presentation_analysis,
            total_duration=25,
            qa_duration=5,
            buffer_percentage=0.1
        )
        
        print(f"✅ Time plan created successfully")
        print(f"   Strategy: {time_plan.timing_strategy}")
        print(f"   Content Duration: {time_plan.content_duration} minutes")
        print(f"   Buffer Time: {time_plan.buffer_time:.1f} minutes")
        print(f"   Number of Slides: {len(time_plan.slide_allocations)}")
        
        # Display time allocations
        print("\n📊 Slide Time Allocations:")
        total_allocated = 0
        for allocation in time_plan.slide_allocations:
            print(f"   Slide {allocation.slide_number} ({allocation.slide_type}): "
                  f"{allocation.allocated_minutes:.1f} min - {allocation.rationale}")
            total_allocated += allocation.allocated_minutes
        
        print(f"\n⏱️  Total Allocated: {total_allocated:.1f} minutes")
        print(f"   Target Time: {time_plan.content_duration - time_plan.buffer_time:.1f} minutes")
        
        # Validate allocations
        if abs(total_allocated - (time_plan.content_duration - time_plan.buffer_time)) < 0.5:
            print("✅ Time allocation is well-balanced")
        else:
            print("⚠️  Time allocation may need adjustment")
        
        return True
        
    except Exception as e:
        print(f"❌ Slide time planning test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_script_generation_with_timing():
    """Test script generation with dynamic timing."""
    print("\n📝 Testing Script Generation with Dynamic Timing...")
    
    try:
        from src.script_generation.claude_script_generator_cached import ClaudeScriptGeneratorCached
        
        # Initialize generator
        generator = ClaudeScriptGeneratorCached(enable_caching=True)
        print("✅ Script generator initialized")
        
        # Create test data
        presentation_analysis = create_mock_presentation_analysis()
        
        persona_data = {
            'full_name': 'Alex Kim',
            'job_title': 'Senior Solutions Architect',
            'experience_level': 'Senior',
            'presentation_confidence': 'Expert',
            'interaction_style': 'Conversational'
        }
        
        presentation_params = {
            'duration': 20,
            'target_audience': 'Technical',
            'language': 'English',
            'technical_level': 'advanced',
            'presentation_type': 'technical_deep_dive',
            'recommended_script_style': 'technical',
            'main_topic': 'AWS Serverless Best Practices',
            'include_qa': True,
            'qa_duration': 5,
            'technical_depth': 4,
            'include_timing': True,
            'include_transitions': True,
            'include_speaker_notes': True,
            'include_qa_prep': True
        }
        
        print("   Generating script with dynamic timing...")
        script = generator.generate_complete_presentation_script(
            presentation_analysis=presentation_analysis,
            persona_data=persona_data,
            presentation_params=presentation_params
        )
        
        print(f"✅ Script generated successfully")
        print(f"   Script length: {len(script)} characters")
        print(f"   Word count: {len(script.split())} words")
        
        # Check for timing information in script
        if "Dynamic Timing Plan" in script:
            print("✅ Dynamic timing plan included in script")
        else:
            print("⚠️  Dynamic timing plan not found in script")
        
        if "Slide Time Allocations:" in script:
            print("✅ Individual slide time allocations included")
        else:
            print("⚠️  Slide time allocations not found")
        
        # Save script for review
        with open("test_dynamic_timing_output.md", "w", encoding="utf-8") as f:
            f.write(script)
        print("✅ Script saved to test_dynamic_timing_output.md")
        
        return True
        
    except Exception as e:
        print(f"❌ Script generation with timing test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run dynamic timing tests."""
    print("🎯 Dynamic Slide Timing Test Suite")
    print("=" * 50)
    
    results = []
    
    # Test 1: Slide Time Planner
    results.append(test_slide_time_planner())
    
    # Test 2: Script Generation with Dynamic Timing
    results.append(test_script_generation_with_timing())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Dynamic Timing Test Results:")
    print(f"✅ Passed: {sum(results)}/{len(results)} tests")
    print(f"❌ Failed: {len(results) - sum(results)}/{len(results)} tests")
    
    if all(results):
        print("🎉 All dynamic timing tests passed!")
        print("✅ Ready for Streamlit integration")
        return True
    else:
        print("⚠️  Some tests failed, check the errors above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
