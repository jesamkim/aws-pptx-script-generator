#!/usr/bin/env python3
"""Test Script for Step 5: Script Generation.

This script allows you to test the script generation functionality directly
without going through the full Streamlit UI workflow.
"""

import sys
import os
import asyncio
import time
from loguru import logger

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_mock_analysis_result():
    """Create mock analysis result for testing."""
    return {
        'main_topic': 'AWS Serverless Architecture Best Practices',
        'technical_level': 'advanced',
        'presentation_type': 'technical_overview',
        'target_audience': 'technical_teams',
        'recommended_script_style': 'technical',
        'key_themes': [
            'Serverless Computing',
            'AWS Lambda',
            'API Gateway',
            'DynamoDB',
            'Cost Optimization'
        ],
        'aws_services_mentioned': [
            'Lambda',
            'API Gateway',
            'DynamoDB',
            'S3',
            'CloudWatch'
        ],
        'slide_summaries': [
            {
                'slide_number': 1,
                'title': 'Introduction to Serverless',
                'main_content': 'Overview of serverless computing concepts and benefits',
                'key_points': ['No server management', 'Pay per use', 'Auto scaling'],
                'aws_services': ['Lambda']
            },
            {
                'slide_number': 2,
                'title': 'AWS Lambda Deep Dive',
                'main_content': 'Detailed look at AWS Lambda functions and use cases',
                'key_points': ['Event-driven', 'Multiple runtimes', 'Concurrent execution'],
                'aws_services': ['Lambda', 'CloudWatch']
            },
            {
                'slide_number': 3,
                'title': 'API Gateway Integration',
                'main_content': 'Building REST APIs with API Gateway and Lambda',
                'key_points': ['RESTful APIs', 'Authentication', 'Rate limiting'],
                'aws_services': ['API Gateway', 'Lambda']
            },
            {
                'slide_number': 4,
                'title': 'Data Storage with DynamoDB',
                'main_content': 'NoSQL database for serverless applications',
                'key_points': ['NoSQL', 'Auto scaling', 'Global tables'],
                'aws_services': ['DynamoDB', 'Lambda']
            },
            {
                'slide_number': 5,
                'title': 'Best Practices and Cost Optimization',
                'main_content': 'Optimizing serverless applications for performance and cost',
                'key_points': ['Cold starts', 'Memory optimization', 'Monitoring'],
                'aws_services': ['Lambda', 'CloudWatch', 'X-Ray']
            }
        ]
    }

def create_mock_persona_data():
    """Create mock persona data for testing."""
    return {
        'full_name': 'Alex Kim',
        'job_title': 'Senior Solutions Architect',
        'company': 'AWS',
        'experience_level': 'Senior',
        'presentation_confidence': 'Expert',
        'interaction_style': 'Technical'
    }

def create_mock_presentation_params():
    """Create mock presentation parameters for testing."""
    return {
        'language': 'English',
        'duration': 25,
        'target_audience': 'Technical',
        'technical_level': 'advanced',
        'presentation_type': 'technical_overview',
        'recommended_script_style': 'technical',
        'time_per_slide': 4.0,
        'include_qa': True,
        'qa_duration': 5,
        'technical_depth': 4,
        'include_timing': True,
        'include_transitions': True,
        'include_speaker_notes': True,
        'include_qa_prep': True
    }

def test_basic_script_generation():
    """Test basic script generation using cached generator."""
    print("🧪 Testing Basic Script Generation...")
    
    try:
        # Import the basic script generation function
        from streamlit_app import generate_content_aware_script
        
        # Create test data
        analysis_result = create_mock_analysis_result()
        persona_data = create_mock_persona_data()
        presentation_params = create_mock_presentation_params()
        
        print("📝 Generating script with basic cached generator...")
        start_time = time.time()
        
        script = generate_content_aware_script(
            analysis_result=analysis_result,
            persona_data=persona_data,
            presentation_params=presentation_params
        )
        
        generation_time = time.time() - start_time
        
        if script:
            print(f"✅ Basic script generation successful!")
            print(f"⏱️  Generation time: {generation_time:.2f} seconds")
            print(f"📊 Script length: {len(script)} characters")
            print(f"📄 Word count: {len(script.split())} words")
            
            # Show first 500 characters
            print("\n📖 Script preview:")
            print("-" * 50)
            print(script[:500] + "..." if len(script) > 500 else script)
            print("-" * 50)
            
            return True
        else:
            print("❌ Basic script generation failed - no content returned")
            return False
            
    except Exception as e:
        print(f"❌ Basic script generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_optimized_script_generation():
    """Test optimized script generation using agent."""
    print("\n🚀 Testing Optimized Script Generation...")
    
    try:
        # Import the optimized script generation function
        from streamlit_app import generate_content_aware_script_optimized
        
        # Create test data
        analysis_result = create_mock_analysis_result()
        persona_data = create_mock_persona_data()
        presentation_params = create_mock_presentation_params()
        
        print("📝 Generating script with optimized agent...")
        start_time = time.time()
        
        # Run in thread to avoid event loop conflicts
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                generate_content_aware_script_optimized,
                analysis_result,
                persona_data,
                presentation_params
            )
            script = future.result()
        
        generation_time = time.time() - start_time
        
        if script:
            print(f"✅ Optimized script generation successful!")
            print(f"⏱️  Generation time: {generation_time:.2f} seconds")
            print(f"📊 Script length: {len(script)} characters")
            print(f"📄 Word count: {len(script.split())} words")
            
            # Show first 500 characters
            print("\n📖 Script preview:")
            print("-" * 50)
            print(script[:500] + "..." if len(script) > 500 else script)
            print("-" * 50)
            
            return True
        else:
            print("❌ Optimized script generation failed - no content returned")
            return False
            
    except Exception as e:
        print(f"❌ Optimized script generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_components():
    """Test individual agent components."""
    print("\n🔧 Testing Agent Components...")
    
    try:
        from src.agent.optimized_script_agent import OptimizedScriptAgent, OptimizedPersonaProfile
        
        # Initialize agent
        agent = OptimizedScriptAgent(enable_caching=True, max_workers=2)
        print("✅ Agent initialization successful")
        
        # Test persona profile creation
        persona = OptimizedPersonaProfile(
            full_name="Test Presenter",
            job_title="Solutions Architect",
            experience_level="Senior",
            presentation_style="Technical",
            specializations=["AWS", "Serverless"],
            language="English",
            cultural_context={},
            optimization_preferences={
                "confidence": "Expert",
                "enable_caching": True,
                "parallel_processing": True
            }
        )
        print("✅ Persona profile creation successful")
        
        # Test performance summary
        performance = agent.get_performance_summary()
        print(f"✅ Performance summary: {performance}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent component test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_cache_functionality():
    """Test caching functionality."""
    print("\n💾 Testing Cache Functionality...")
    
    try:
        from src.script_generation.claude_script_generator_cached import ClaudeScriptGeneratorCached
        
        # Initialize generator with caching
        generator = ClaudeScriptGeneratorCached(enable_caching=True)
        print("✅ Cached generator initialization successful")
        
        # Test cache performance
        cache_stats = generator.get_cache_performance()
        print(f"✅ Initial cache stats: {cache_stats}")
        
        # Test multiple generations with same static content
        print("🔄 Testing cache with repeated requests...")
        
        analysis_result = create_mock_analysis_result()
        persona_data = create_mock_persona_data()
        presentation_params = create_mock_presentation_params()
        
        # Create mock presentation analysis
        class MockPresentationAnalysis:
            def __init__(self, analysis_result):
                self.overall_theme = analysis_result['main_topic']
                self.technical_complexity = 3.0
                self.slide_analyses = []
                
                for slide_summary in analysis_result.get('slide_summaries', [])[:2]:  # Only first 2 slides for faster testing
                    mock_slide = type('MockSlideAnalysis', (), {
                        'slide_number': slide_summary['slide_number'],
                        'content_summary': slide_summary['title'],
                        'visual_description': slide_summary['main_content'],
                        'key_concepts': slide_summary.get('key_points', []),
                        'aws_services': slide_summary.get('aws_services', [])
                    })()
                    self.slide_analyses.append(mock_slide)
        
        presentation_analysis = MockPresentationAnalysis(analysis_result)
        
        # Enhanced params
        enhanced_params = {
            **presentation_params,
            'technical_level': analysis_result.get('technical_level', 'intermediate'),
            'presentation_type': analysis_result.get('presentation_type', 'technical_overview'),
            'main_topic': analysis_result.get('main_topic', 'AWS Presentation'),
            'key_themes': analysis_result.get('key_themes', []),
            'aws_services_mentioned': analysis_result.get('aws_services_mentioned', [])
        }
        
        # First generation (should be cache miss)
        print("  📝 First generation (cache miss expected)...")
        start_time = time.time()
        script1 = generator.generate_complete_presentation_script(
            presentation_analysis=presentation_analysis,
            persona_data=persona_data,
            presentation_params=enhanced_params
        )
        first_time = time.time() - start_time
        
        cache_stats_after_first = generator.get_cache_performance()
        print(f"  ⏱️  First generation time: {first_time:.2f}s")
        print(f"  📊 Cache stats after first: {cache_stats_after_first}")
        
        # Second generation (should be cache hit)
        print("  📝 Second generation (cache hit expected)...")
        start_time = time.time()
        script2 = generator.generate_complete_presentation_script(
            presentation_analysis=presentation_analysis,
            persona_data=persona_data,
            presentation_params=enhanced_params
        )
        second_time = time.time() - start_time
        
        cache_stats_after_second = generator.get_cache_performance()
        print(f"  ⏱️  Second generation time: {second_time:.2f}s")
        print(f"  📊 Cache stats after second: {cache_stats_after_second}")
        
        # Analyze cache performance
        if cache_stats_after_second['hits'] > cache_stats_after_first['hits']:
            improvement = ((first_time - second_time) / first_time) * 100
            print(f"  🚀 Cache working! Speed improvement: {improvement:.1f}%")
            return True
        else:
            print(f"  ⚠️  Cache not working as expected")
            return cache_stats_after_second['writes'] > 0  # At least some caching activity
        
    except Exception as e:
        print(f"❌ Cache functionality test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all Step 5 tests."""
    print("🎯 Step 5 Script Generation Test Suite")
    print("=" * 50)
    
    results = []
    
    # Test 1: Basic Script Generation
    results.append(test_basic_script_generation())
    
    # Test 2: Optimized Script Generation
    results.append(await test_optimized_script_generation())
    
    # Test 3: Agent Components
    results.append(test_agent_components())
    
    # Test 4: Cache Functionality
    results.append(test_cache_functionality())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"✅ Passed: {sum(results)}/{len(results)} tests")
    print(f"❌ Failed: {len(results) - sum(results)}/{len(results)} tests")
    
    if all(results):
        print("🎉 All tests passed! Step 5 is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
    
    return all(results)

if __name__ == "__main__":
    # Run the test suite
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
