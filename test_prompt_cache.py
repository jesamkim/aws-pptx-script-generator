#!/usr/bin/env python3
"""Test script for Claude 3.7 Sonnet Prompt Caching functionality."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.script_generation.claude_script_generator_cached import ClaudeScriptGeneratorCached
from src.script_generation.prompt_cache_manager import CacheConfig
import time


def test_prompt_caching():
    """Test prompt caching functionality."""
    print("🧪 Testing Claude 3.7 Sonnet Prompt Caching...")
    
    # Initialize generator with caching enabled
    generator = ClaudeScriptGeneratorCached(enable_caching=True)
    
    # Mock presentation data
    class MockSlideAnalysis:
        def __init__(self, slide_num):
            self.slide_number = slide_num
            self.content_summary = f"Slide {slide_num} Content"
            self.visual_description = f"This slide covers important topic {slide_num}"
            self.key_concepts = [f"concept{slide_num}a", f"concept{slide_num}b"]
            self.aws_services = ["EC2", "S3"] if slide_num % 2 == 0 else ["Lambda", "DynamoDB"]
    
    class MockPresentationAnalysis:
        def __init__(self):
            self.overall_theme = "AWS Architecture Best Practices"
            self.slide_analyses = [MockSlideAnalysis(i) for i in range(1, 4)]
    
    # Test data
    presentation_analysis = MockPresentationAnalysis()
    persona_data = {
        'full_name': 'Test Presenter',
        'job_title': 'Senior Solutions Architect',
        'experience_level': 'Senior',
        'presentation_confidence': 'Expert',
        'interaction_style': 'Technical'
    }
    
    presentation_params = {
        'language': 'English',
        'duration': 20,
        'target_audience': 'Technical',
        'technical_level': 'advanced',
        'presentation_type': 'technical_overview',
        'recommended_script_style': 'technical',
        'main_topic': 'AWS Architecture Best Practices',
        'key_themes': ['Scalability', 'Security', 'Cost Optimization'],
        'aws_services_mentioned': ['EC2', 'S3', 'Lambda', 'DynamoDB'],
        'time_per_slide': 2.0,
        'include_qa': True,
        'qa_duration': 5,
        'technical_depth': 4,
        'include_timing': True,
        'include_transitions': True,
        'include_speaker_notes': True,
        'include_qa_prep': True
    }
    
    print("📝 Generating first script (cache miss expected)...")
    start_time = time.time()
    
    try:
        script1 = generator.generate_complete_presentation_script(
            presentation_analysis=presentation_analysis,
            persona_data=persona_data,
            presentation_params=presentation_params
        )
        
        first_generation_time = time.time() - start_time
        print(f"✅ First generation completed in {first_generation_time:.2f} seconds")
        print(f"📊 Script length: {len(script1)} characters")
        
        # Get cache stats after first generation
        cache_stats = generator.get_cache_performance()
        print(f"🚀 Cache stats after first generation: {cache_stats}")
        
        print("\n📝 Generating second script with similar content (cache hit expected)...")
        start_time = time.time()
        
        # Modify only dynamic content slightly
        presentation_params['duration'] = 25  # Small change
        
        script2 = generator.generate_complete_presentation_script(
            presentation_analysis=presentation_analysis,
            persona_data=persona_data,
            presentation_params=presentation_params
        )
        
        second_generation_time = time.time() - start_time
        print(f"✅ Second generation completed in {second_generation_time:.2f} seconds")
        print(f"📊 Script length: {len(script2)} characters")
        
        # Get final cache stats
        final_cache_stats = generator.get_cache_performance()
        print(f"🚀 Final cache stats: {final_cache_stats}")
        
        # Calculate performance improvement
        if first_generation_time > 0:
            speed_improvement = ((first_generation_time - second_generation_time) / first_generation_time) * 100
            print(f"⚡ Speed improvement: {speed_improvement:.1f}%")
        
        # Calculate cache hit rate
        total_requests = final_cache_stats['hits'] + final_cache_stats['misses']
        if total_requests > 0:
            hit_rate = (final_cache_stats['hits'] / total_requests) * 100
            print(f"🎯 Cache hit rate: {hit_rate:.1f}%")
        
        print("\n✨ Prompt caching test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_prompt_caching()
